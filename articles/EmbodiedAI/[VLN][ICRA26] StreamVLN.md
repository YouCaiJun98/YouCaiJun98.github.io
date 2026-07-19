# StreamVLN: Streaming Vision-and-Language Navigation via SlowFast Context Modeling

2026/7/14  

来源：ICRA26

**Takeaway message**

这篇 StreamVLN 的核心贡献并不是提出一个新的 VLN 模型结构，而是重新思考了 **Video-LLM 如何以“流式（streaming）”方式执行导航**。作者认为，真正限制 Video-LLM 在机器人导航中落地的不是理解能力，而是上下文越来越长导致的推理延迟和显存开销，因此提出了一套 SlowFast Context Modeling：快速更新近期上下文、缓慢维护长期记忆，再配合基于三维几何的 token pruning，使 Video-LLM 可以在长时间视频流中保持实时推理。

---

如果把最近一年的 VLN 工作串起来看，可以发现整个方向已经发生了一次明显的范式转变。早期的方法，例如 CMA、HMAT、ETPNav，更像是在做传统导航：建立地图、预测 waypoint，再由规划器完成控制。而 NaVid、NaVILA 等工作开始直接把 Video-LLM 微调成一个 Vision-Language-Action 模型，希望模型直接根据视频和语言输出动作。然而这些工作大多默认每一步导航都是一次独立推理：机器人拍一段视频，把视频和历史一起送进 LLM，重新计算全部上下文，再预测下一步动作。这样的设计虽然简单，但并不适合真实机器人，因为机器人的视频流是连续到来的，每走一步都重新计算全部历史，不仅延迟越来越高，KV Cache 和视觉 token 也会无限增长。作者认为，这才是真正阻碍 Video-LLM 用于真实 VLN 的关键问题。

因此，这篇工作的故事其实很简单：**把 VLN 看成一个持续不断的多轮对话，而不是一系列彼此独立的推理任务。**机器人不断看到新的图像，不断向模型询问“下一步应该怎么走”，模型则持续回复动作。于是整个导航过程自然就变成了一串 Observation → Action → Observation → Action 的交替序列，而不是每一步都重新组织输入。整个系统建立在 LLaVA-Video 上，只是把输入改造成 vision-language-action 交错排列，并充分利用 Transformer 的 KV Cache，实现真正意义上的 streaming inference。

## SlowFast Context Modeling

真正的创新来自作者提出的 **SlowFast Context Modeling**。作者认为，在机器人导航中，不同时间尺度的信息价值其实是不一样的。机器人最近几秒钟看到的内容，对于决定下一步动作最重要；而几十秒之前看到的内容，更多是帮助保持长期语义记忆，例如记住自己已经经过哪些房间。因此，他们把整个上下文拆成两个速度不同的记忆系统。

第一个就是 **Fast-streaming Dialogue Context**。它实际上就是一个固定大小的 sliding window。窗口内保存最近若干轮对话的 KV Cache，因此机器人连续几步移动时几乎不需要重新 prefill，只需要把当前新的 observation 编码进去即可，大部分历史计算全部复用。这一点非常符合 Transformer 推理的特点：prefill 是最昂贵的部分，而 decode 很便宜。因此窗口内几乎可以做到实时响应。与此同时，由于窗口大小固定，KV Cache 不再随着导航时间无限增长，而是始终保持一个稳定规模。

但是，仅靠滑动窗口又会带来新的问题：窗口之外的信息全部丢掉，机器人就失去了长期记忆。因此作者设计了第二层 **Slow-updating Memory Context**。窗口滑出之后，并不是直接删除，而是先压缩成 memory token，再供之后的新窗口继续访问。于是系统实际上形成了一个两级缓存：近期信息保存在完整 KV Cache 中，保证响应速度；远期信息保存在压缩后的 memory 中，保证长期推理能力。整个推理过程中，模型实际上同时利用当前窗口和历史 memory 完成动作生成，这也是论文标题中 SlowFast 的真正含义。

不过，作者进一步发现，仅仅做两级记忆仍然不够，因为 Video-LLM 的视觉 token 实在太多。即使进行了时间采样，一帧高分辨率图像仍然包含大量 patch token，而机器人连续移动时，相邻帧往往只是发生了很小的位移，大量 patch 实际对应的是同一个三维位置。作者认为，这部分冗余不是时间维度造成的，而是空间维度造成的。

## Voxel-based Spatial Pruning

因此，他们提出了全文另一个比较有意思的贡献：**Voxel-based Spatial Pruning**。它不是像很多 Video-LLM 那样根据 attention 或 feature similarity 去删 token，而是利用深度图把每个 patch 投影到三维空间，再划分 voxel。如果多个不同时间的 patch 落到同一个 voxel，就说明它们其实对应同一块三维区域，那么只保留最新那个 patch，其余全部删除。由于整个过程完全依赖几何关系，不需要训练，也不用计算巨大的 attention matrix，因此计算代价非常低，而且不会破坏预训练特征分布。对于机器人导航这种 RGB-D 输入来说，这种设计比通用 Video-LLM 的 token merge 更自然，也更符合机器人几何建模的特点。

## 训练

训练方面其实没有特别复杂。作者仍然采用两阶段训练：首先只利用 Oracle trajectory 学习基本导航，然后利用 DAgger 收集模型失败后的纠正轨迹继续训练。同时，为了避免模型因为只训练导航而丢失通用视觉能力，又加入了大量 VideoQA、ScanQA 以及 MMC4 等通用视觉语言数据进行联合训练。这一点和 NaVILA 等近期工作基本一致，都是希望导航能力和通用视觉理解共同保留，而不是变成一个专门的导航模型。整个数据配方中，大约三分之二来自 VLA 导航数据，三分之一来自通用多模态数据。

实验部分最值得关注的不是最终分数，而是几个设计是否真的有效。从导航结果来看，StreamVLN 在 R2R-CE 和 RxR-CE 上超过了此前的 RGB-only Video-LLM 方法，包括 NaVid、NaVILA 和 UniNaVid，在使用额外数据后达到新的 SOTA，而且没有依赖 waypoint predictor 或全景相机等额外模块。

更有意思的是几个消融实验。首先，Voxel Pruning 删除约 30% 左右的视觉 token 后，性能几乎没有下降，有些场景甚至还有提升，说明连续视频确实存在大量几何冗余。其次，Memory Context 的大小存在最佳点，并不是历史越长越好；过长的 memory 反而降低泛化能力，说明长期记忆也需要适当压缩。最后，KV Cache Reuse 带来的收益十分明显。如果完全复用 KV Cache，推理延迟几乎保持稳定；如果每一步重新计算历史（传统做法），延迟会随着对话轮数持续增长。这实际上证明了作者整篇论文最初提出的问题确实存在，而且 SlowFast 设计确实解决了它。

论文还进行了真实机器人实验，平台是 Unitree Go2 搭配 D455 RGB-D 相机，推理部署在 RTX4090 上。平均一次预测四个动作约需 0.27 秒，通信延迟室内约 0.2 秒，室外约 1 秒。在办公室、家庭、商场以及室外等多个真实场景中，能够完成长距离、多地标的语言导航任务，展示了该框架较好的真实部署能力。

## Summary

总体来看，我认为这篇论文最大的价值其实不在于提出了某一种新的导航模型，而是在 **Video-LLM 的系统架构** 上提出了一种更加符合真实机器人运行方式的设计思想。它把导航看成持续的视频流处理问题，因此重点优化的是 **上下文管理（context management）** 而不是模型能力本身。SlowFast Context、Sliding Window KV Cache、Memory Compression、3D Voxel Pruning 这几个模块其实都是围绕同一个目标展开：**让 Video-LLM 能够无限长时间地工作，同时保持实时推理。**

结合你之前一直关注的 NaVILA、UniNaVid，以及想在 Go2 上做 VLN 的方向，我觉得这篇文章尤其值得关注的有三点：第一，它提出了比 NaVILA 更合理的流式推理框架，你后续如果做在线导航，这种 Sliding Window + Memory 的组织方式很值得借鉴；第二，它利用 RGB-D 的三维几何进行 token pruning，这与你一直关注的深度相机、地图表示以及机器人几何信息高度契合；第三，它几乎所有优化都集中在推理系统层，而不是重新设计 VLA Backbone，因此这些思想未来也完全可以迁移到 Qwen2.5-VL、Pi 系列甚至其他具身模型上。

