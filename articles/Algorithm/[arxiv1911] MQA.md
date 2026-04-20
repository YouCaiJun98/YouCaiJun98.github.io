# Fast Transformer Decoding: One Write-Head is All You Need

2026/4/20

很好，这一步你问得很关键——MQA本质上就是**从工程瓶颈出发，对Transformer做的一个“最小侵入式改造”**。我帮你按“读论文的正确姿势”来导读这篇：

---

# 一、这篇论文到底在解决什么问题？

先说结论：

👉 **MQA不是为了提升效果，而是为了解决推理（inference）速度问题，尤其是自回归生成时的瓶颈。**

论文开头就点明了核心问题：

* Transformer **训练很快（并行）**
* 但 **推理很慢（必须逐token）**
* 瓶颈不是算力，而是 **memory bandwidth（显存带宽）**

> 关键句：
> “incremental inference is often slow, due to repeatedly loading large K/V tensors” 

---

# 二、先复习：你已经掌握的 Multi-Head Attention

论文第2节其实是在帮你复习：

## 标准 MHA 的结构（你已经写过）

每个 head：


$$Q_h = X W_q^h,\quad K_h = X W_k^h,\quad V_h = X W_v^h$$


然后：


$$\text{Attention}_h = \text{softmax}(Q_h K_h^T)V_h$$


最后 concat + projection。

👉 关键点：

* 每个 head 都有 **自己的 K、V**
* 所以 KV cache 的形状是：

```
[b, h, seq_len, d_k]
```

---

# 三、真正的问题：Incremental Inference（核心理解点）

论文第2.4节是**最重要的一节**，必须吃透。

## 推理时发生什么？

自回归生成：

```
step 1 → 生成 token1
step 2 → 生成 token2
step 3 → 生成 token3
...
```

每一步：

* 你只算一个新的 query
* 但要 **读取所有历史的 K、V**

也就是说：

👉 **每一步都要加载整个 KV cache**

---

## 复杂度分析（重点）

论文给出一个关键结论：

* 总计算量：
  
  $$\Theta(b n d^2)$$
  

* 但 memory access：

  
  $$\Theta(b n^2 d)$$
  

👉 所以问题是：

> **不是算不动，而是搬不动（memory-bound）**

---

# 四、MQA的核心思想（一句话版本）

终于到第3节：

> **所有 head 共享同一份 K 和 V，只保留多个 Q**

---

# 五、结构对比（必须搞清楚）

## 1️⃣ Multi-Head Attention（原版）

```
Q: [b, h, n, d_k]
K: [b, h, n, d_k]
V: [b, h, n, d_v]
```

---

## 2️⃣ Multi-Query Attention（MQA）

```
Q: [b, h, n, d_k]   ← 保留多头
K: [b, n, d_k]      ← 共享
V: [b, n, d_v]      ← 共享
```

👉 也就是：

* **Query 多头**
* **Key / Value 单头**

论文原话：

> “the different heads share a single set of keys and values” 

---

# 六、为什么这样能加速？

看关键公式：

原来：


$$\text{memory} \sim b \cdot h \cdot n \cdot d$$


现在：


$$\text{memory} \sim b \cdot n \cdot d$$


👉 **直接减少 h 倍**

---

## 推理瓶颈改善

论文给出：


$$\text{memory/computation} = \Theta\left(\frac{n}{d}\right)$$


MQA变成：


$$\Theta\left(\frac{n}{d h}\right)$$


👉 **瓶颈直接被 /h**

---

# 七、你最应该关心的工程意义

这篇论文真正重要的是：

## 1️⃣ KV cache 变小

* MHA：`h × seq_len × d`
* MQA：`seq_len × d`

👉 直接减少显存占用

---

## 2️⃣ 带宽压力下降

每一步 decode：

* 原来：要读 `h` 份 KV
* 现在：只读 1 份

---

## 3️⃣ latency 巨幅下降（论文实验）

论文给的数据：

* baseline decoder step：**47 µs**
* MQA：**3.8 µs**

👉 **≈ 12× 提速** 

---

# 八、效果有没有变差？

有，但很小：

* BLEU 略降（26.7 → 26.5）
* perplexity 略变差

👉 但远好于“减少 head 数”的方案

---

# 九、你现在可以建立的直觉

我帮你总结成一句你以后会一直用到的话：

> **MQA = 用“共享 KV”换“几乎不掉点的巨大推理加速”**

---

# 十、和你之前问题的连接（非常重要）

你之前问过：

> 多头是不是可以合成一个 linear？

现在你可以重新理解：

* 在 MHA：

  * head 的差异体现在 **Q/K/V**
* 在 MQA：

  * head 只体现在 **Q**
  * K/V 是“全局共享 memory”

👉 本质变化：

> **attention 的“检索方式”多样，但“存储内容”统一**

---

# 十一、接下来你可以深入的方向

我建议你下一步问我这些（按重要性排序）：

1. 👉 MQA 为什么效果不会明显下降？（很关键）
2. 👉 MQA vs GQA（Grouped Query Attention）
3. 👉 MQA 在 LLaMA / GPT 中怎么实现（代码级）
4. 👉 KV cache 在实际框架（vLLM）里怎么优化
5. 👉 为什么 MQA 特别适合长序列推理

---

如果你愿意，我们下一步可以直接做一件很有价值的事：

👉 **把你写的 Multi-Head Attention 改成 MQA（手写代码级）**

这一步你会彻底吃透它。
