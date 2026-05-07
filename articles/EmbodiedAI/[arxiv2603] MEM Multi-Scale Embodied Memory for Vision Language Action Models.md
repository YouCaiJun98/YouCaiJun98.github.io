# MEM: Multi-Scale Embodied Memory for Vision Language Action Models

2026/5/7

来源：arxiv2603

下面给你做一个**结构化、尽量“论文级”的总结**，我会按“问题 → 方法 → 关键设计 → 实验 → 结论”的逻辑来讲，方便你后续复用到精读/项目里。

---

# 一、论文核心问题

这篇论文关注的是：

> **如何让机器人（VLA模型）具备“长时记忆能力”，从而完成真实世界的长时序任务？**

传统VLA（Vision-Language-Action）模型的问题是：

* 只能看**当前观测**（或很短历史）
* 或者把历史全塞进Transformer → **计算爆炸 / latency过高**
* 无法处理：

  * 长任务（10分钟+）
  * 部分可观测（被遮挡）
  * 多阶段任务（比如做饭、收拾）

论文指出一个关键洞察：

> 不同时间尺度的记忆，本质上需要**不同模态和不同抽象层级**

---

# 二、核心方法：MEM（Multi-Scale Embodied Memory）

论文提出一个核心框架：

> **MEM = 多尺度 + 多模态记忆系统**

它把记忆拆成两类：

| 记忆类型 | 表达方式               | 作用           |
| ---- | ------------------ | ------------ |
| 短期记忆 | 视频（image sequence） | 处理遮挡、动态、操作细节 |
| 长期记忆 | 语言（text summary）   | 记录语义事件、任务进度  |

📌 关键思想：

> 用**视觉处理“细节”**，用**语言压缩“语义”**



---

# 三、整体架构（非常关键）

论文把策略分成两层：

## 1️⃣ 高层策略（High-Level Policy）

负责：

* 生成子任务 instruction（比如“拿盘子”）
* 更新**语言记忆**

形式：

[
\pi_{HL}(l_{t+1}, m_{t+1} | o_t, m_t, g)
]

其中：

* ( m_t )：语言记忆（history summary）
* ( l_{t+1} )：下一步子任务

---

## 2️⃣ 低层策略（Low-Level Policy）

负责：

* 执行具体动作

形式：

[
\pi_{LL}(a_{t:t+H} | o_{t-K:t}, l_{t+1}, g)
]

特点：

* 只看**短期视频记忆**
* 不需要长历史

---

## 🔥 关键设计总结

> **用语言 memory 替代长序列 observation**

从：

```
长序列图像 → Transformer（不可扩展）
```

变成：

```
短视频 + 长文本总结
```

这一步是整篇论文最核心的贡献。

---

# 四、关键技术细节

## 4.1 长期记忆：Language Memory

### 做法

用一句话总结过去发生的事情：

例子（论文原文）：

* mt：

  > I placed a plate in the cabinet and moved to the counter.
* mt+1：

  > I placed a plate... and picked up a bowl.



---

### 训练方式（很关键）

不是人工标注，而是：

> 用 LLM 自动生成“记忆摘要”

输入：

* 子任务序列
* 成功/失败信息

输出：

* 当前应该记住的内容（压缩）

---

### 核心设计点

1. **主动压缩**

   * 不记细节（颜色/数量等）
   * 只保留“对未来有用的信息”

2. **避免分布偏移（非常重要）**

   * naive做法：拼接所有历史 → 会失败
   * MEM：只在成功时更新记忆

---

## 4.2 短期记忆：Video Encoder

问题：

> 多帧图像直接输入Transformer → 太慢

解决方案：

> 设计一个**高效视频编码器**

---

### 核心结构

基于 ViT，加入：

* 空间 attention（原本就有）
* 时间 attention（新增）

关键技巧：

* **分离时空 attention**
* **只保留当前帧 token（压缩历史）**

复杂度从：

[
O(n^2 K^2)
]

降到：

[
O(K n^2 + n K^2)
]



---

### 关键优点

* 不增加参数量
* 可以用预训练 ViT 初始化
* 支持实时推理（<300ms）

---

## 4.3 额外设计

* 状态（proprioception）→ 用 embedding，而不是文本
* 支持多相机输入
* 支持最长 **15分钟记忆**

---

# 五、实验结果（重点看结论）

## 5.1 长任务能力（最重要）

任务：

* 做饭（recipe setup）
* 清理厨房

结果：

* 无 memory：几乎失败
* MEM：显著提升成功率

结论：

> **必须同时有短期+长期记忆**



---

## 5.2 消融实验

| 模型           | 结果      |
| ------------ | ------- |
| 只有视频 memory  | 不会记任务进度 |
| 只有语言 memory  | 操作不稳定   |
| naive memory | 分布偏移严重  |
| MEM          | 最好      |

---

## 5.3 In-context adaptation（很亮点）

任务：

* 拿筷子（失败后调整抓取）
* 开冰箱（方向不确定）

结果：

* 无 memory：重复失败
* 有 memory：**会调整策略**

提升：

* +11%
* +62%

---

## 5.4 与其他 memory 方法对比

对比：

* Pool memory（平均池化）
* Proprio-only
* 无 memory

结论：

> MEM 是唯一在所有任务上都稳定的方案

---

## 5.5 不影响基础能力

重要结论：

> 加 memory **不会降低 manipulation 能力**

（很多 prior work 会 degrade）

---

# 六、核心贡献总结

你可以把这篇论文总结成三句话：

---

### ✅ 1. 提出多尺度记忆框架（核心贡献）

> 长期 → 语言
> 短期 → 视频

---

### ✅ 2. 解决长时序 + 实时推理矛盾

通过：

* 视频压缩
* 语言总结

实现：

> **分钟级 memory + 毫秒级推理**

---

### ✅ 3. 解锁新能力

* 长任务（15分钟）
* 部分可观测
* in-context adaptation

---

# 七、你可以怎么用这篇论文（结合你背景）

你现在在做：

* VLN / VLA
* memory system
* 多智能体协同

这篇论文对你非常关键的点是：

---

## 🔥 1. memory设计范式

你之前说：

> 想做层次化 memory + 时空记忆

这篇直接给了模板：

* semantic memory → language
* spatial/dynamic → video

---

## 🔥 2. 可以迁移到 VLN

VLN里：

* language memory → route history / decision history
* video memory → visual trajectory

---

## 🔥 3. multi-agent memory

你项目里的：

> 共享记忆 + 时空对齐

可以参考：

* language memory = shared global state
* video memory = local observation buffer

---

# 八、如果你要更深入

我可以帮你继续做：

* MEM vs Gato / RT-2 / Octo 的对比
* 如何把 MEM 改成 VLN memory
* 或直接帮你写“项目方案/论文思路”

你下一步想往**工程实现**还是**研究抽象**走？
