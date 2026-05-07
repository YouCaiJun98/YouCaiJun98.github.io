# GQA:Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints

2026/4/22  

来源：ENMLP23  

可以。我们先把这篇 **GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints** 一次性读完，目标不是泛泛总结，而是读到你后面能自己动手写 GQA 为止。全文核心其实很集中：**作者想解决 MHA 推理慢、MQA 虽快但容易掉点的问题，于是提出 GQA 作为两者之间的折中，并给出一种从 MHA checkpoint 低成本“改造+继续预训练”的方法。** 

---

## 1. 先抓住整篇文章的主线

这篇文章实际上回答了两个问题。

第一个问题是：**已经训练好的 MHA 模型，能不能不从头重新训练，就变成更适合推理的 MQA / GQA 模型？**
作者的回答是：可以。做法叫 **uptraining**。先把原来的 MHA checkpoint 按某种规则改成 MQA 或 GQA 结构，再用原始预训练 recipe 继续训练少量步数去适应新结构。作者说只用原始预训练计算量的大约 **5%**，就能把已有 MHA checkpoint 转成效果还不错的模型。

第二个问题是：**如果 MQA 只有 1 个 KV head 太激进，能不能保留多个 KV head，但又比 MHA 少？**
作者提出 **Grouped-Query Attention, GQA**。它的思路是：query 头还是很多个，但把这些 query 头分组，每组共享一套 K/V head。这样：

* 当组数 = 1 时，就是 MQA；
* 当组数 = query head 总数时，就是 MHA；
* 中间情况，就是 GQA。

所以这篇文章的本质就是一句话：

**GQA = 在 MHA 和 MQA 之间，通过“多个 Q 头共享较少数量的 KV 头”做结构折中；再配合 uptraining，把已有 MHA 模型低成本改造成推理更快的版本。** 

---

## 2. 为什么作者会盯上 KV head？

这篇文章的出发点不是“attention 算力不够”，而是 **decoder 推理阶段的 memory bandwidth 开销很大**。
在自回归解码时，每生成一个 token，都要反复读取：

1. 模型参数；
2. 历史 token 的 K cache；
3. 历史 token 的 V cache。

其中，K/V cache 会随着序列长度增长不断变大，所以当生成很长时，**读取 KV cache 的带宽成本** 会越来越显著。MQA 的关键收益正是来自这里：它不再为每个 query head 都保留单独的 K/V head，而是让所有 query head 共用一套 K/V，于是：

* KV cache 体积大幅减小；
* 每一步解码时需要搬运的数据减少；
* 推理速度上升。

这点你一定要真正吃透，因为它直接决定你写代码时哪些维度该变、哪些维度不该变。
**GQA/MQA 优化的不是 Q 的数量，而是 K/V 的数量。**

---

## 3. MHA、MQA、GQA 三者到底差在哪

### MHA

标准多头注意力里：

* 有 (H) 个 query heads
* 有 (H) 个 key heads
* 有 (H) 个 value heads

也就是每个 Q head 都有自己对应的一套 K/V。表达能力强，但 KV cache 最大。

### MQA

MQA 里：

* 仍然有很多个 Q heads
* 但只有 **1 个 K head** 和 **1 个 V head**

也就是所有 query heads 共用这一套 K/V。这样推理极快，但作者指出它可能导致：

* 质量下降；
* 训练 / 微调不稳定。

### GQA

GQA 里：

* Q heads 仍有 (H) 个；
* K/V heads 减少为 (G) 个，其中 (1 < G < H)；
* 每个 group 内若干个 Q heads 共享 1 套 K/V。

所以从实现角度看，最关键的映射关系就是：

[
\text{num_query_heads} = H,\quad \text{num_kv_heads} = G,\quad \text{group size} = H/G
]

如果你后面要写代码，这三个量会是核心配置。

---

## 4. 这篇文章最重要的方法：uptraining

作者不是从头训 GQA，而是从已有 MHA checkpoint 改出来。这个过程分两步。

### 第一步：checkpoint conversion

把原来 MHA 模型里的多个 K/V heads，合并成更少的 K/V heads。
如果目标是 MQA，那就是把所有 K head 平均起来，得到 1 个 K head；V head 也同理。
如果目标是 GQA，那么就把原本的 heads 分组，在每组内部做 mean pooling，得到该组共享的 K/V head。

注意这里作者特地比较了三种 conversion 方法：

1. **mean pooling**
2. 直接选某一个已有 head
3. 随机初始化新 head

结果是 **mean pooling 最好**。这很合理，因为它保留了更多原模型中的信息。文章在消融实验里也验证了这点。

### 第二步：继续预训练

conversion 之后，模型结构变了，但参数虽然是“合理初始化”，终究还没适应新结构，所以要再按原预训练方式跑一小段训练，让模型重新适应。作者把这个比例记为 (\alpha)，文中重点用了 (\alpha = 0.05)，也就是原始预训练步数的 5%。

这一步非常重要，因为它说明：
**GQA 不是只改个 forward 公式就完事，真正高质量的 GQA 模型通常需要让模型重新适应共享 KV 的结构。**

---

## 5. 论文里的一个关键直觉：为什么 GQA 会比 MQA 更稳、更好

作者的直觉大概是这样的。

MQA 把原来 (H) 套 K/V 压缩成 1 套，太狠了。
这样虽然带宽下降很多，但模型容量也一下子压得太厉害，所以容易损失质量。尤其模型越大、head 越多时，这种“一刀切到 1 个 KV head”的压缩更激进。

GQA 只把 K/V 压缩到 (G) 套，而不是 1 套。于是：

* KV cache 仍显著缩小；
* 但表达能力损失没那么剧烈；
* 因此在速度和质量之间能取得更好的平衡。

从你的实现角度，这意味着 GQA 的本质不是“某个新公式”，而是：
**用更少的 K/V heads 去服务更多的 Q heads，但又不极端到只有 1 套 K/V。**

---

## 6. 论文实验到底怎么做的

作者基于 **T5.1.1** 架构做实验，主要看了 T5 Large 和 T5 XXL。
GQA / MQA 主要加在：

* decoder self-attention
* decoder cross-attention

但**不用于 encoder self-attention**。
原因是 encoder 是并行算整段，不像 decoder 自回归那样强烈受 KV cache 带宽限制，所以收益没那么关键。

这个点也很值得你记住，因为后面你自己写代码时，通常也会先在 **decoder-only 自回归场景** 或 decoder 的 self-attn 部分实现 GQA，而不是不分场景到处改。

---

## 7. 主实验结果读懂就够了

论文最重要的一张结论表是：
**uptrained GQA 几乎保留了 MHA 的质量，但推理速度接近 MQA。** 

文中的结果大致是：

* **MHA-XXL** 质量最好，但慢；
* **MQA-XXL** 最快，但质量有些下降；
* **GQA-8-XXL** 在质量上接近 MHA-XXL，在速度上接近 MQA。

这正是整篇论文最想证明的东西。
所以你以后向别人解释 GQA 时，可以直接说：

**GQA 不是为了比 MQA 更快，而是为了在“几乎和 MQA 一样快”的前提下，把质量拉回去，尽量接近 MHA。**

---

## 8. 消融实验非常值得你注意

### 8.1 conversion 方式

作者比较了：

* mean pooling
* 选第一个 head
* 随机初始化

结果 mean pooling 最好。
这直接给了你未来“从 MHA 权重改成 GQA 权重”的实现答案：
**优先做分组均值池化。** 

### 8.2 uptraining 步数

作者比较不同 (\alpha)。结论是：

* GQA 在刚转换后就已经比 MQA 更像样；
* MQA 更依赖后续 uptraining；
* 5% 的继续训练很有效；
* 10% 还有收益，但边际递减。

这说明 GQA 本身结构就比 MQA 更“温和”，因此更容易继承原 MHA 模型的能力。

### 8.3 组数 G 的影响

组数越少，越接近 MQA，越快；
组数越多，越接近 MHA，越准，但也越慢。
作者实验发现从 1 组增加到 8 组，速度损失不算太大，但质量改善明显，所以选 **8 groups** 作为一个不错的折中点。

这个实验非常实用，因为它告诉你：
**GQA 不是一个固定结构，它是一个可调旋钮。**

---

## 9. 论文中的训练稳定性观察，也很关键

附录里作者专门提到，**MQA 会带来训练不稳定性**，尤其在长输入任务上更明显。
他们说从头训练的 MQA T5-Large 会出现频繁 loss spike，微调长输入任务时甚至会直接发散。
而 uptrained MQA 稍好一些，但仍有较高方差。
**GQA 则明显更稳定。** 

这个结论对你后面写代码很有帮助，因为它解释了为什么工业界里常见的是：

* 不是人人都直接上纯 MQA；
* 而是更偏向用 GQA，尤其在大模型中。

---

## 10. 这篇文章的局限，你也要知道

作者自己提了几个限制。

第一，他们主要关注的是 **长序列生成时 KV 带宽瓶颈**，而这个场景下质量评估本身就没那么完美，比如 summarization 里用 Rouge 有局限。

第二，他们没有系统比较“uptraining GQA”与“从头训练 GQA”的差异，所以并不能断言 uptraining 一定是最佳终态，只能说它是一个非常划算的办法。

第三，他们主要评估的是 **encoder-decoder 模型**。作者还特地说，考虑到现在 decoder-only 模型更流行，而 decoder-only 没有 encoder/cross-attn 这层区分，GQA 在这类模型里可能更有优势。

这也是为什么后来很多 LLM 架构里，你会更常看到 GQA。

---

## 11. 现在把全文压缩成“你真正要带走的 6 个结论”

第一，**GQA 是 MHA 和 MQA 的中间态**。
Q head 数量不变，只减少 K/V head 数量，让每组 Q 共享 K/V。

第二，**GQA 优化的是推理阶段 KV cache 的带宽与缓存开销**，不是单纯减少 attention 数学计算量。

第三，**从已有 MHA checkpoint 迁移到 GQA/MQA 是可行的**，做法是 mean pooling K/V heads，再进行少量 uptraining。

第四，**mean pooling 是最好的 checkpoint conversion 初始化方式**。

第五，**GQA 的质量通常明显优于 MQA，速度又比 MHA 快很多**，是一个很好的折中。

第六，**GQA 比 MQA 更稳定**，这点对真实训练和微调很重要。

---

## 12. 过渡到“写代码”前，你必须先建立的实现脑图

你后面自己写 GQA 时，核心不是重新发明 attention，而是改这三件事：

### 1）参数形状

MHA 通常是：

* (W_Q): 产出 (H) 个 query heads
* (W_K): 产出 (H) 个 key heads
* (W_V): 产出 (H) 个 value heads

GQA 则变成：

* (W_Q): 仍产出 (H) 个 query heads
* (W_K): 只产出 (G) 个 key heads
* (W_V): 只产出 (G) 个 value heads

### 2）forward 时的 head 对齐

因为 attention score 还是按每个 Q head 算，所以你需要让每个 Q head 找到自己所属组对应的 K/V head。
最常见实现方式是：

* 要么把 K/V 在 head 维上 `repeat_interleave` 到 (H) 个头，再用普通 attention 逻辑；
* 要么不真的复制，而是通过 reshape / broadcast 实现逻辑共享。

### 3）从 MHA checkpoint 转 GQA checkpoint

如果以后你要写“权重转换脚本”，就需要把原本 (H) 个 K/V heads 按组切分，然后组内做均值，得到 (G) 个 K/V heads。
这一步就是论文的 mean pooling conversion。

---

## 13. 你现在可以如何理解 GQA 与你之前学的 MQA 的关系

你之前已经在理解 MQA 了，所以现在可以把 GQA 看成一句特别简单的话：

**MQA 是 GQA 的特例。**

更准确地说：

* `num_kv_heads = 1` 时，GQA 就退化成 MQA；
* `num_kv_heads = num_query_heads` 时，GQA 就退化成 MHA。

所以你后面写代码，完全可以按一个统一版本写：

* 只要支持 `num_heads` 和 `num_kv_heads`
* 并要求 `num_heads % num_kv_heads == 0`

那么同一份代码就同时覆盖：

* MHA
* GQA
* MQA

这其实就是最自然、最工程化的写法。

---

## 14. 这篇文章读完后，你后面写代码时最容易犯的错

我提前帮你标出来。

第一，不要误以为 GQA 是“减少 Q heads”。不是。
**Q heads 数量通常保持不变，减少的是 K/V heads。**

第二，不要把 GQA 理解成“每组 query 先合并再做 attention”。不是。
每个 query head 仍然单独产生自己的 attention score，只是它们共享同一组 K/V。

第三，不要忘了 KV cache 的 shape 会变。
GQA 的缓存是按 `num_kv_heads` 存，不是按 `num_heads` 存。这个对自回归推理很关键。

第四，不要只改 self-attn 的公式，不改权重形状。
真正的 GQA 模块从投影层开始就和 MHA 不一样：`W_K/W_V` 的输出维度更小。

---

## 15. 我建议我们接下来的代码路线

既然你说之后要和我一起写 GQA 代码，我建议我们按下面这个顺序来，最稳：

先写一个**统一版 Scaled Dot-Product Attention 核心**，它只接受已经拆好 head 的 `q, k, v`。
然后写一个**统一版 MultiHeadAttention**，支持：

* `num_heads`
* `num_kv_heads`

这样：

* `num_kv_heads == num_heads` 是 MHA
* `1 < num_kv_heads < num_heads` 是 GQA
* `num_kv_heads == 1` 是 MQA

最后再补：

1. KV cache 版增量推理；
2. MHA checkpoint → GQA checkpoint 的 mean-pooling 转换函数；
3. 简单单元测试，验证输出 shape 和 head 映射没问题。

---

## 16. 最后一句，把整篇论文翻成“代码语言”

这篇论文如果翻译成代码层面的设计原则，其实就是：

> **保持 Query 的多头表达能力；压缩 Key/Value 的头数以减少 KV cache；用 grouped sharing 在质量与速度之间找平衡；若从已有 MHA 权重迁移，则对 K/V 头做分组均值池化并进行少量继续训练。** 

下一步我们就可以正式开写了：我建议先从 **统一版 GQA attention 模块的 PyTorch 接口设计** 开始，把类、张量 shape、forward 流程先搭出来。
