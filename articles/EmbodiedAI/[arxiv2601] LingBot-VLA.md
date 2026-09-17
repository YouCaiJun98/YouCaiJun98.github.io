# A Pragmatic VLA Foundation Model  

2026/9/15  

来源：arxiv2601  

Takeaway Message：LingBot-VLA 的核心不是提出一个全新的 VLA 架构，而是系统验证了一件更重要的事：**真实机器人数据继续扩大，VLA 的性能是否还能持续提升。** 作者用约 2 万小时、9 种双臂机器人数据进行预训练，并在大规模真实机器人评测中发现，随着预训练数据从 3000 小时扩展到 2 万小时，模型性能仍持续上升，没有明显饱和。

这篇文章的背景是，近年的 VLA 已经逐渐形成了比较明确的路线：用大规模、多任务、多本体数据预训练一个通用 policy，再用少量下游数据适配到具体机器人和任务。但相比语言模型，机器人领域一直缺少一个足够有说服力的回答：**VLA 是否也存在类似的 data scaling behavior？** 原因很简单，真实机器人数据非常昂贵，过去很多工作的数据规模还不足以观察长期趋势。LingBot-VLA 因此把问题直接放在“真实机器人数据规模”上，想验证继续扩数据是不是仍然值得。

为此，作者构建了一个约 2 万小时的真实世界预训练数据集，覆盖 9 种不同双臂机器人，包括 AgiBot、AgileX、Galaxea、Realman、KUAVO、Qinglong、ARX、Bimanual Franka 等。数据主要来自遥操作，不同平台的机械臂自由度、相机配置和 action space 都不完全一致，因此预训练目标本身就是跨 embodiment 的。语言标注方面，作者先把长视频按 atomic action 切分，再利用 Qwen3-VL 给完整任务和子任务生成 instruction。 

模型结构本身可以把它理解为一个 **π0 风格的 flow-based VLA**。它使用 Qwen2.5-VL 作为视觉语言 backbone，再接一个 action expert 来生成连续动作。视觉、语言和动作并不是完全独立的，而是通过 Mixture-of-Transformers 形式进行层间交互；动作生成采用 Flow Matching，并一次预测一段 action chunk，而不是单步 action。

LingBot-VLA 相比普通 VLA 还有一个比较重要的设计：作者认为 VLM 擅长语义理解，但对机器人操作需要的精细几何和深度感知并不够强，因此额外引入了 **depth representation distillation**。具体来说，它让 VLM 中的视觉表示去对齐 LingBot-Depth 提供的 depth token，希望把空间几何信息蒸馏进 VLA，而不是单纯依赖 RGB 语义特征。

除了模型本身，这篇工作还很强调训练系统。因为 2 万小时机器人数据意味着很高的训练吞吐要求，作者对分布式训练、attention 和算子进行了系统优化，包括 FSDP、针对 action expert 的 shard group、FlexAttention 和 `torch.compile`。这部分的意义不是提出新的学习算法，而是让这种大规模 VLA 训练真正可行。

实验上，作者做了一个规模较大的真实机器人 benchmark。基于 GM-100 的 100 个 manipulation task，在多个真实机器人平台上统一收集和筛选 post-training 数据，并在相同训练配置下比较 π0.5、GR00T N1.6、WALL-OSS 和 LingBot-VLA。总体上，LingBot-VLA 的 SR 和 Progress Score 都优于这些 baseline；加入 depth 后，平均表现进一步提升。

不过这篇文章最重要的实验其实是 scaling study。作者把预训练数据从 3000 小时逐步增加到 2 万小时，发现 Success Rate 和 Progress Score 的整体趋势持续上升，而且到 2 万小时还没有看到明显饱和。这个结果支持了作者的核心判断：**当前阶段的 VLA 很可能仍然处于“继续扩大真实机器人数据就能持续获益”的区间。** 

另一个有价值的结论是 data efficiency。作者发现，在部分下游任务上，LingBot-VLA 使用更少的 post-training demonstrations，就能超过 π0.5 使用更多数据的结果。也就是说，大规模预训练不仅提高最终性能，也让模型更容易被适配到新任务。

所以，这篇论文真正值得记住的不是某一个局部结构，而是它给 VLA 发展路线提供了一个比较强的经验判断：**真实机器人预训练数据目前还远没有“堆到没用”，规模和多样性仍然是提升通用机器人 policy 的核心变量。** 模型层面，它基本延续 π0 一类 VLM + action expert + Flow Matching 的路线，再通过 depth distillation 补空间能力；系统层面，则说明未来 VLA foundation model 的竞争，很可能不仅是网络结构，还包括数据工程和大规模训练基础设施。
