# Fast Inference from Transformers via Speculative Decoding  

2026/8/17  

来源：ICML23  

**Takeaway Message：** 这篇论文解决的是自回归 Transformer 推理中一个非常根本的效率问题：模型生成 $K$ 个 token，通常需要串行执行 $K$ 次 decode，而单步 decode 又经常受内存带宽而非纯算力限制。作者提出 speculative decoding：先用一个很便宜的近似模型 $M_q$ 连续“猜”未来若干 token，再让真正的目标模型 $M_p$ 一次并行验证这些猜测，从而把原本“一次大模型调用只生成一个 token”变成“一次大模型调用可能确认多个 token”。它最重要的地方不是“用小模型帮大模型生成”，而是设计了一套 speculative sampling，使这种加速在随机采样条件下仍然**严格保持目标模型原有的输出概率分布**，不需要修改模型结构，也不需要重新训练。作者在 T5-XXL 11B 上实际获得约 2–3 倍的推理加速。

这篇工作的背景来自自回归模型固有的串行生成过程。Transformer 在一次 forward 内部当然具有很强的并行性，但 autoregressive decoding 在 token 这个维度上无法直接并行：只有生成 $x_t$ 以后，才能知道下一步的条件 $x_{\le t}$，从而计算 $x_{t+1}$。因此生成一段长度为 $K$ 的文本，就需要连续进行 $K$ 次模型调用。随着模型越来越大，每一次 decode 都要读取大量模型参数和 KV cache，这使得推理延迟迅速上升。作者特别指出，很多大模型 decode 场景并不是算术计算能力不足，而是受 memory bandwidth 和通信限制，因此设备实际上可能还有没有被充分利用的计算资源。与量化、蒸馏、稀疏化等试图“让每一次模型调用更便宜”的路线不同，这篇论文考虑的是另一条思路：既然一次大模型调用的计算并行度还有富余，那么能否让它一次处理多个未来 token，从而减少串行调用次数？

真正的困难在于，未来 token 本来是未知的。于是作者引入一个更小、更快的 approximation model $M_q$，而真正希望保持其输出行为的大模型记为 target model $M_p$。$M_q$ 首先按照自己的概率分布连续生成 $\gamma$ 个候选 token，把它们看作对未来序列的“推测”；随后 $M_p$ 对包含这些候选 token 的整段序列进行一次计算，同时得到这些位置对应的大模型预测分布。这样，原来必须等 $x_1$ 生成以后才能计算 $x_2$、再等 $x_2$ 才能计算 $x_3$ 的串行过程，被转换成了“小模型先构造出一条可能的未来路径，再让大模型沿这条路径并行检查”。如果这些猜测大量成立，一次大模型调用就能够确认多个新 token。论文 Figure 1 很直观地展示了这一点：一个 6M 参数的小模型为 97M 参数的大模型提供 speculative tokens，一段 38-token 的生成只需要 9 次大模型的串行调用。

如果只考虑 greedy decoding，这个思路其实并不难：小模型猜一个 token，只要它和大模型的 argmax 一致，就可以直接接受。但论文真正要解决的是一般的 stochastic sampling。假设大模型给某个 token 的概率是 $p(x)$，小模型给出的概率是 $q(x)$，如果直接接受小模型采出来的结果，最终输出分布就会从 $p$ 变成 $q$，这意味着 speculative decoding 实际改变了原模型的行为。作者因此提出 speculative sampling：先从 $q(x)$ 中采一个候选 token $x$，然后以

$$
\min\left(1,\frac{p(x)}{q(x)}\right)
$$


的概率接受它。如果 $q(x)\le p(x)$，这个 token 一定接受；如果小模型对它的概率估计高于大模型，即 $q(x)>p(x)$，则只接受其中 $p(x)/q(x)$ 的比例。直观来看，小模型能够直接负责的是 $p$ 和 $q$ 两个分布重叠的那一部分概率质量。如果候选 token 被拒绝，则不能简单重新从 $p$ 采样，而要从

$$
p'(x)=\operatorname{norm}\big(\max(0,p(x)-q(x))\big)
$$

中重新采样，把大模型分布中尚未被小模型覆盖的剩余概率质量补回来。最终“接受的小模型样本”和“拒绝后的 correction sample”加起来恰好恢复 $p(x)$，因此整个过程生成的 token 与直接从目标模型 $M_p$ 采样具有完全相同的概率分布。这个严格的分布保持性质，是本文最核心的方法贡献。

把这一机制推广到实际 speculative decoding 时，小模型首先自回归生成 $\gamma$ 个 token $x_1,\ldots,x_\gamma$，大模型随后一次计算出这些 speculative prefixes 上的多个预测分布，并从前往后逐个判断候选 token 是否被接受。一旦第 $i$ 个 token 被拒绝，它之后的小模型预测也必须全部丢弃，因为后续 token 都是在错误的第 $i$ 个 token 条件下产生的；算法在这个位置使用 correction distribution 重新采样，然后进入下一轮。如果 $\gamma$ 个 speculative tokens 全部被接受，那么大模型这一次 forward 已经顺便得到了再下一个位置的概率分布，因此还能额外生成一个 token。也就是说，一轮 speculative decoding 最少生成一个新 token，最多能够生成 $\gamma+1$ 个，而普通 autoregressive decoding 每轮只能得到一个。即便小模型完全猜错，每轮仍然至少会从正确的目标分布生成一个 token，所以从 target model 的串行调用次数来看，不会退化到比普通 decoding 更差。

论文接下来用 acceptance rate 来解释这种方法什么时候有效。作者把小模型候选 token 被接受的平均概率记为 $\alpha$。$\alpha$ 本质上衡量 $q$ 和 $p$ 两个分布的重合程度：两个模型越一致，draft token 越容易被大模型接受，一轮能够连续确认的 token 数就越多。在一个简化的独立同分布假设下，一轮 speculative decoding 能生成的 token 数期望为

$$
E[N]=1+\alpha+\alpha^2+\cdots+\alpha^\gamma
=\frac{1-\alpha^{\gamma+1}}{1-\alpha}.
$$

因此 $\alpha$ 很高时，让小模型一次向前猜较多 token 很划算；而如果 $\alpha$ 很低，通常第一个或第二个 speculative token 就被拒绝，那么后面的预测基本都会浪费。论文进一步证明 acceptance rate 与两个概率分布的重叠直接相关，所以 speculative decoding 的效果并不是简单由“小模型有多大”决定，而是由它能否以较低成本较好地逼近目标模型决定。

但仅仅追求高 $\alpha$ 还不够，因为小模型本身也需要时间。作者用 $c$ 表示 approximation model 单步运行时间与 target model 单步运行时间之比。因此理想的 draft model 需要同时满足两个条件：一方面足够接近目标模型，使 $\alpha$ 较高；另一方面又必须远比目标模型便宜，使 $c$ 足够小。论文的 wall-time 分析表明，实际加速效果由 $\alpha$、$c$ 和 speculative length $\gamma$ 共同决定，而不是 draft model 越大越好。作者的实验中，近似模型通常比 target model 小几个数量级，$c$ 经常低于 0.05；在这样的条件下，可以获得明显的端到端延迟收益。

这里还有一个非常重要的系统层面认识：speculative decoding 并不是通过减少总 FLOPs 来加速，恰恰相反，它甚至可能执行更多算术运算。当 target model 验证 $\gamma$ 个 speculative positions 时，如果后面的 token 最终因为前面的 rejection 被丢弃，这些计算就属于额外开销。它真正优化的是**串行 latency 和硬件利用率**。普通单 token decode 中，每次都需要读取庞大的模型权重和 KV cache，却只产生一个 token；而 speculative decoding 通过一次处理多个候选位置，使一次模型权重读取能够服务更多 token。因此这种方法尤其适用于 memory-bandwidth-bound、但仍有并行算力余量的环境。如果系统本身已经完全 compute-bound，就未必能得到同样的收益。这也是理解 speculative decoding 时非常重要的一个边界：它本质上是在**用更多并行计算换更少的串行大模型调用**。

实验部分主要是为了验证这个 trade-off 在真实系统中是否成立。作者以 T5-XXL 11B 作为 target model，在 English-to-German translation 和 CNN/DM summarization 上分别用 T5-small 77M、T5-base 250M 和 T5-large 800M 作为 approximation model，并在单 TPU-v4、batch size 1 下测试 greedy 和标准随机采样。最好的结果反而来自最小的 T5-small：在翻译任务上 greedy decoding 达到约 3.4× 加速，随机采样达到约 2.6×；在 summarization 上分别约为 3.1× 和 2.3×。T5-large 虽然与目标模型更加一致、acceptance rate 更高，但因为自身运行成本明显增加，最终 wall-time speedup 反而更低。这很好地验证了作者的核心观点：好的 draft model 并不是“越准越好”，而是要在预测一致性和运行成本之间取得最佳平衡。

论文还进一步说明，approximation model 并不一定必须是一个标准的小型 Transformer。由于最终输出正确性由 target model 和 speculative sampling 保证，$M_q$ 理论上可以采用非常自由的形式，包括更小的 Transformer、n-gram 模型、非自回归模型甚至一些基于上下文重复的简单 heuristic。实验中甚至一个几乎零成本的 bigram 模型，在 T5-XXL 翻译任务上也能取得约 0.2 的 acceptance rate，从而获得约 1.25× 加速。这一点很有意义，因为它说明 speculative decoding 的核心并不是“模型蒸馏”：draft model 不需要学习成为一个高质量的独立语言模型，它只需要以极低成本对目标模型未来输出具有足够预测能力。

因此从研究贡献来看，这篇论文真正重要的并不是单纯提出“small model drafts, large model verifies”这一工程直觉，而是把 speculative execution 从确定性的计算场景推广到了概率采样场景，并给出了一套能够严格保持目标模型输出分布的 sampling correction 机制。在此基础上，它才构造出完整的 speculative decoding：将自回归生成中的一部分 token-level 串行依赖，转化为廉价模型上的串行预测和昂贵模型上的并行验证。相比早期的 blockwise parallel decoding 等方法，它既不要求重新训练专门模型，也不限于 greedy decoding，并且保留了目标模型输出分布不变这一强保证。

这篇工作的主要限制也非常明确。首先，它依赖额外并行算力，因此更适合 bandwidth-bound 的推理场景，而不是所有硬件和 batch 设置都会同样受益。其次，性能高度依赖 draft model 与 target model 的匹配程度以及 $\gamma$ 的选择，过弱的 draft 会导致大量 rejection，过强的 draft 又会使自身成本过高。再次，本文真正完成端到端 wall-time benchmark 的主要是 T5-XXL 场景，其他模型更多用于验证 acceptance rate，因此不能把文中的所有模型结果都理解成完整部署上的 2–3× 加速。作者自己也把动态选择 $\gamma$、设计更适合 speculative decoding 的 approximation model、层级式 speculative model，以及与 beam search 的进一步结合留作后续方向。

从研究启发上看，这篇论文与你目前关注的 VLM/VLA 和具身智能模型推理也有一定关系，但它的价值更多在于**推理系统方法论**而不是直接提供机器人算法。对于端侧运行的大型 VLM/VLA，如果动作生成仍然采用 autoregressive token decoding，并且推理瓶颈主要来自大模型反复读取权重而不是算力完全饱和，那么 speculative decoding 的思想是可以迁移的：用一个便宜的模型或简单预测器先提出未来若干 action tokens，再由主模型批量验证。不过，机器人控制场景与文本又存在一个关键差别——很多 VLA 输出的是连续动作块、action chunk 或 flow/diffusion trajectory，而不是标准离散 token，因此本文的 speculative sampling 公式不能直接照搬。真正值得借鉴的是“**廉价预测未来 → 昂贵模型批量验证 → 在保持目标模型行为的前提下减少串行调用**”这一计算结构。对这篇论文后续精读时，最值得重点看的不是实验表格，而是 Algorithm 1 的具体执行过程、为什么一个 target-model forward 能验证多个 speculative positions，以及它在真实 decoder-only Transformer 中如何与 causal mask 和 KV cache 配合；这三点搞清楚以后，基本就能够从论文层面过渡到实际 speculative decoding 实现。
