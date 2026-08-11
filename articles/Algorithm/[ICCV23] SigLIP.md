# Sigmoid Loss for Language Image Pre-Training  

2026/8/10  

来源：ICCV23  

**Takeaway Message：** SigLIP 想解决的并不是 CLIP 的模型结构问题，而是 CLIP 图文对比学习目标本身带来的训练低效。它发现，没有必要把一个 batch 中的图文匹配建模成“从所有候选中选出正确答案”的 softmax 分类问题，而可以直接把每个 image-text pair 看成一个独立的“匹配/不匹配”二分类问题，用 sigmoid loss 训练。这个看似很小的改变，使图文对比学习不再强依赖全局 batch normalization，既降低了分布式训练的显存和通信开销，又在较小 batch 下取得了更好的效果。论文进一步发现，大 batch 对 CLIP 类模型的重要性其实被高估了：性能大约在 32k batch 左右就已经接近饱和。

SigLIP 的故事要从 CLIP 为什么需要大 batch 讲起。CLIP 的基本思想其实非常自然：给定一批配对的图片和文本，让正确的 image-text pair 在共同 embedding space 中靠近，让错误组合远离。但 CLIP 并不是单独判断每一对图文是否匹配，而是把它做成一个 batch 内的分类问题。对于一张图片，它要求模型从当前 batch 的所有文本中找出唯一正确的那个；反过来，对于一个文本，也要求模型从所有图片中找出正确图片。因此它需要在整个 batch 上做两次 softmax normalization。换句话说，一对图文的 loss 不只取决于这一对本身，还取决于 batch 中所有其他样本。

这就导致 CLIP 对 batch size 有一种结构性的依赖。batch 越大，一方面负样本越多，通常有利于对比学习；但另一方面，每张设备在计算 loss 时需要知道其他设备上的 image/text embedding，分布式训练通常需要 all-gather，而且还需要构造一个随 global batch size 二次增长的相似度矩阵。于是 CLIP 常常需要很大的 batch 和大量加速卡才能高效训练。作者的核心问题就是：图文对比学习真的必须被定义成这样一个全局竞争问题吗？

SigLIP 的核心洞见是，不必如此。对于任意一张图片 (I_i) 和任意一段文本 (T_j)，其实可以直接问一个更简单的问题：“这两个东西是否匹配？”如果 (i=j)，它就是正样本；如果 (i\neq j)，就是负样本。于是原本 CLIP 的“N 个候选里选一个正确答案”，被改写成了大量彼此独立的二分类问题。作者因此用 sigmoid loss 替代 softmax contrastive loss。最关键的变化不是 sigmoid 这个函数本身，而是训练目标的语义发生了变化：CLIP 是“pick the right class”，而 SigLIP 是“rate this pair”。

形式上，SigLIP 仍然保留了 CLIP 非常熟悉的双塔结构：图像经过 image encoder，文本经过 text encoder，两边得到归一化后的 embedding，然后通过点积衡量相似度。所以它并不是提出了一个全新的 vision-language backbone。真正变化发生在这些相似度怎样进入 loss。对于一对 image-text embedding，作者计算一个相似度 logit，然后根据它是真实配对还是错误配对，直接用 sigmoid 做二分类。这样一来，每一个 pair 的 loss 都可以独立计算，不再需要知道整个 batch 上的 softmax denominator。论文的核心技术贡献，本质上就是把“batch-level classification”改造成了“pair-level classification”。

这个变化最直接的价值体现在分布式训练上。因为每个 pair 可以独立处理，SigLIP 不需要像标准 CLIP 那样先把所有设备的 embedding 一次性 all-gather 过来，再构造完整的 global similarity matrix。论文第 3 页 Figure 1 给出了一个很关键的 chunked implementation：每张设备先拿自己的 local image 和 local text 算一个小块的 pairwise loss，然后让 text embedding 在不同设备之间轮换，再继续计算下一块，直到所有 image-text 组合都被覆盖。这样最终仍然利用了整个 global batch 中的正负样本，但任何一个时刻只需要在显存里保存一个 local chunk，而不是完整的 (B\times B) 相似度矩阵。

因此，SigLIP 的“效率提升”并不是因为它少看了很多负样本，也不是因为它改变了 encoder，而是因为 pairwise sigmoid loss 允许作者重新组织 loss 的计算方式。原来的全局矩阵可以被拆成很多独立的小块依次处理。这一点非常重要，因为它意味着 batch size 不再和 loss 的定义强耦合：你可以有很大的 global batch，但不必一次在单个设备上 materialize 整个 pairwise matrix。论文甚至把 SigLiT 的 batch 推到了 100 万，就是为了验证这种可扩展性。

不过，论文接下来的实验却得出了一个比“我们能训练 100 万 batch”更有意思的结论：其实根本没有必要把 batch 做到那么大。作者系统地从很小的 batch 一直测到 1M，发现 sigmoid 在小 batch 下明显优于 softmax；随着 batch 变大，两者差距逐渐缩小，而性能大约在 32k 附近就开始饱和。继续增加到几十万甚至上百万，收益非常有限，某些设置下还会下降。SigLIP 自身的实验里，sigmoid 大约在 32k 达到最佳，而 softmax 要到更大的 batch 才接近自己的峰值，并且最终也没有超过 sigmoid。

这一结果实际上重新解释了 CLIP 时代“大 batch 很重要”这件事情。大 batch 的确能够提供更多负样本，但并不是负样本越多越好，收益很快就会递减。SigLIP 尤其在较小 batch 下表现更好，因此它真正降低的是高质量 language-image pre-training 的资源门槛，而不仅仅是提供一种把 batch 做得更大的技术。论文报告，在固定硬件条件下，同样四张 TPU-v4，Base SigLIP 能放下 4096 batch，而对应的 CLIP 只能放下 2048。

Sigmoid 写法还带来了一个新的问题：正负样本极度不平衡。一个 batch 如果有 (N) 对真实图文，就只有 (N) 个正 pair，却有大约 (N^2-N) 个负 pair。例如 batch 16k 时，只有约 16k 个 positive，却有约 2.68 亿个 negative。作者发现，如果直接从普通初始化开始，训练初期会被海量负样本支配，因此给相似度额外加入了一个可学习 bias，并把它初始化成一个较大的负值，让模型一开始就具有“绝大多数图文对不匹配”的合理先验。这个 bias 是 SigLIP 里一个重要但次一级的设计，它不是论文最核心的思想，却对稳定训练很关键。

有了 pairwise sigmoid formulation 后，作者还顺手研究了一个 CLIP 中不太容易干净研究的问题：到底哪些负样本真正有用。因为每个 pair 的 loss 是独立的，他们可以人为丢弃一部分 negatives。结果发现，随机大量删除负样本会损害性能，只保留 easy negatives 几乎学不到什么，而只保留 hard negatives 却能保住大部分效果。这说明大规模对比学习里的价值并不是简单来自“负样本数量”，真正有信息量的是那些模型容易混淆的 hard negatives。作者没有在这篇论文中进一步设计复杂的 hard-negative mining 方法，但这个实验很好地说明了 sigmoid formulation 提供了更灵活的研究空间。

实验整体上是比较充分地支撑了作者的主张的。最核心的证据不是某一个 SOTA 数字，而是 sigmoid 和 softmax 在多个 batch size 下的系统对照：小 batch 时 sigmoid 优势明显，大 batch 时两者逐渐接近，32k 左右已经基本饱和。这个趋势在 SigLiT、从头训练的 SigLIP，以及 100 多语言的 multilingual SigLIP 中都能观察到，因此“32k 已经足够”并不是单一设置下的偶然现象。多语言实验甚至显示继续增大 batch 会让跨语言 retrieval 变差。

在最终性能上，SigLIP 也不仅仅是“训练更省”，模型质量本身也有竞争力。例如论文 Table 3 中，相同 256 个 image patches 的 Large 模型，SigLIP-L 在 ImageNet 和 COCO retrieval 上整体优于 CLIP、OpenCLIP 和当时很强的 EVA-CLIP；这说明用 sigmoid 替换 softmax 并没有为了效率牺牲 representation quality，反而能获得更好的最终视觉语言表征。

论文还发现了几个有实际价值但不是主线的现象。例如，用已经预训练好的 vision encoder 初始化 SigLIP 时，如果继续对这个 encoder 使用普通 weight decay，会破坏原来的视觉表征；关闭 pretrained backbone 上的 weight decay 会明显改善训练。非常大的 batch 还容易出现 gradient norm spike，作者把 Adam/AdaFactor 的 (\beta_2) 从 0.999 降到 0.95 后训练会稳定很多。另外，SigLIP 对人为加入的 image、text 和 alignment noise 也比 softmax baseline 更鲁棒，这一点对于本身就很嘈杂的 web-scale image-text dataset 很有意义。

所以，从更高层次看，SigLIP 的贡献并不是“提出了一个更强的 CLIP encoder 架构”，而是重新思考了 CLIP 最基础的训练目标。CLIP 把一个 batch 看成一个相互竞争的整体，SigLIP 则认为图文对齐其实完全可以拆成很多局部的 pairwise decisions。这个改变使 loss 从全局耦合变成局部可分解，也就自然带来了更低的内存需求、更简单的分布式实现和更弱的 batch-size 依赖。它是那种“公式变化很小，但工程和概念影响很大”的工作。

它的局限也比较明确。首先，SigLIP 仍然建立在 CLIP 那套“batch 内其他图文都视为 negative”的假设上，而真实的 web data 中可能存在语义上同样正确的 false negatives；sigmoid 并没有解决这个根本问题。其次，它虽然证明 hard negatives 更重要，但并没有真正解决如何高效选择 hard negatives。最后，这篇论文的核心仍然是 representation pre-training，SigLIP 本身不是一个能够理解复杂视觉语言指令并生成文本的 VLM，它得到的仍然主要是一个很好用的视觉/文本对齐 encoder。

放到你现在看的 VLM 架构里，这一点尤其值得区分。之后你会经常看到某个 VLM 使用 “SigLIP vision encoder”。这并不意味着 VLM 的整体架构变成了 SigLIP；它通常只是把经过 SigLIP 图文对齐预训练的 ViT 拿出来作为视觉 backbone，再通过 projector/adapter 把视觉特征接入 LLM。因此从 CLIP 到 SigLIP，你真正应该建立起来的是这样一条认识：二者的双塔视觉语言表示学习范式基本相同，最大的区别在于 pre-training objective，而这个 objective 的改变最终训练出了一个更高效、表现也更强的视觉 backbone。
