# From Foundation to Application: Improving VLA Models in Practice  

2026/9/21  

来源：arxiv2607  

## Takeaway Message

LingBot-VLA 2.0 不是对 V1 的架构推倒重来，而是在保留“VLM + Action Expert + Flow Matching”主干的基础上，进一步解决 V1 在真实应用中的三个不足：**数据和本体覆盖还不够广、动作空间仍偏双臂操作、模型缺少对未来状态变化的显式建模能力**。因此 V2 的核心升级可以概括为：更大且更异质的数据、更统一的 whole-body action space、MoE Action Expert，以及从“当前深度蒸馏”扩展到“当前/未来双 Query 的时空蒸馏”。

LingBot-VLA 1.0 的核心问题其实很明确：**真实机器人数据继续扩大，VLA 能否持续获得收益？** 所以 V1 的重点是用约 2 万小时、9 种机器人数据证明 real-world robot data scaling 仍然有效。模型本身则比较接近 π0 的路线：VLM 处理图像与语言，Action Expert 用 Flow Matching 生成 action chunk，再额外通过 LingBot-Depth 的视觉蒸馏给 VLM 注入空间几何能力。换句话说，V1 更像是在建立一个“足够强的 manipulation foundation model”。 

V2 的出发点已经从“foundation model 是否能 scale”转向“**这样的 foundation model 离真正的机器人应用还差什么**”。作者认为，实验室里的双臂桌面操作并不能覆盖真实机器人部署：实际机器人可能需要控制头、腰、移动底盘和灵巧手；不同本体的 action space 差异更大；同时长程任务也不能只根据当前画面做反应式控制，而需要理解当前动作会把环境带向什么未来状态。

因此第一项变化还是数据，但这次重点不只是“更多”，而是“更杂、更接近实际”。V2 将预训练数据扩展到约 **6 万小时**：其中约 5 万小时是真实机器人轨迹，覆盖 20 种机器人 configuration，另外加入约 1 万小时 egocentric human video。机器人从 V1 主要的双臂平台扩展到单臂、双臂、half-humanoid、humanoid、移动平台、gripper 和 dexterous hand。 

人类第一视角视频在这里也不是单纯拿来增强视觉理解。作者会通过 SLAM 和手部姿态估计恢复人手 trajectory，再统一转换到训练时使用的坐标系，从而尽可能把 human video 也变成和机器人 action learning 兼容的 supervision。这说明 V2 已经开始尝试把“机器人数据”和“人类具身数据”放进同一个预训练体系里，而不是只做视觉共训练。

为了让这些完全不同的机器人可以放到同一个 policy 里训练，V2 定义了统一的 **55 维 canonical state/action representation**，把 arm joint、EEF pose、gripper、dexterous hand、waist、head 和 mobility signal 分别占据固定槽位；某个机器人没有对应自由度时，就把这些位置 padding。这里相较 V1 是一个很重要的变化：V1 主要解决多种双臂机器人之间的迁移，而 V2 已经在明确解决 whole-body heterogeneous embodiment 的 action-space 统一问题。

模型主体并没有脱离 V1 的路线，仍然可以理解为 **VLM + Action Expert**。最明显的新变化是 Action Expert 内部引入了 sparse MoE。V1 的 Transformer FFN 是 dense 的，而 V2 把 Action Expert 中的 FFN 替换成多个 expert：每个 token 都经过一个 shared expert，同时 Router 再选择少量 routed experts。这样做的动机是，面对 20 种机器人、whole-body control 和大量不同任务时，不再强迫一套 FFN 同时吸收所有控制模式，而是让部分容量形成自动 specialization，同时保留一个 shared expert 学通用控制规律。

这里的 expert 并没有被人工规定成“某个 expert 控制手、某个 expert 控制底盘”，而是 token-level routing，自行学习如何分工。作者还采用类似 DeepSeek-V3 的 auxiliary-loss-free load balancing：用 routing bias 调整 expert 的被选频率，但不额外把 load-balancing loss 加进 action learning objective。这样希望在扩大模型总容量的同时，尽量不干扰原本的动作学习。

不过 V2 相对 V1 在思想上最值得关注的变化，其实是 **Dual-Query Distillation**。V1 只有当前时刻的 spatial query \(Q_t\)，目标是让它去匹配 LingBot-Depth 的当前几何表示；V2 则额外加入一个未来 query \(Q_{t+T}\)。其中 \(T\) 对应一个 action chunk 的时间范围，因此模型不但要理解“现在场景是什么样”，还要学习“执行完这段动作以后，场景应该是什么样”。

同时 teacher 也从一个扩展成两个。LingBot-Depth 继续负责空间几何监督，让 \(Q_t\) 和 \(Q_{t+T}\) 分别预测当前和未来的 depth representation；新加入的 DINO-Video 则负责时序语义监督，它使用 causal temporal modeling，提供当前和未来 frame 的 motion-aware visual representation。于是 V2 的 query 同时学习两件事：**空间上环境长什么样，以及时间上环境会怎么变化。** 

因此 V1 和 V2 的区别可以很直观地理解成：V1 的 depth distillation 主要是在教模型“**看懂当前空间**”；V2 的 dual-query distillation 则进一步教模型“**预测动作之后的未来空间和视觉状态**”。这并不是一个完整的显式 world model——它不会真的生成未来视频——而更像是把 predictive dynamics 作为一个 auxiliary/proxy task，让 Action Expert 在决策时获得更有未来一致性的内部表示。

实验也基本围绕这几个 claim 展开。V2 在 GM-100 的 generalist mixed-task setting 下整体优于 V1 和 π0.5，说明扩大数据、本体覆盖和模型容量确实提高了跨任务共享能力；但不同任务和不同本体上的增益并不完全一致，说明 kinematics、camera viewpoint 和 action-space alignment 仍然是实际跨本体迁移中的难点。

相比 V1，更有代表性的新增结果是 long-horizon mobile manipulation。V2 可以同时控制移动底盘和机械臂，完成例如“移动到冰箱、收集物体、打开冰箱、放入物品、关门”这种需要 navigation 和 manipulation 串联的任务，并在 ID 和 OOD 条件下都优于 π0.5。这个实验真正体现了 V2 想表达的“from foundation to application”：它不再只证明桌面双臂 manipulation 的平均分更高，而是开始验证 unified whole-body policy 是否能够完成更长、更复杂的真实任务。

从整篇论文来看，LingBot-VLA 2.0 的价值不在于发明一个全新的 VLA 范式，而在于把 V1 的路线向前推了一步：**V1 证明大规模真实机器人数据值得继续扩；V2 则尝试回答，数据继续扩以后，怎样容纳更多本体、更复杂动作空间，并让模型具备一定的未来状态预测能力。**

它的局限也比较明显。首先，所谓 predictive dynamics 仍然是 latent feature distillation，而不是能够长期 rollout 的 world model；其次，统一 55 维 action representation 解决了接口统一，却没有从根本上消除不同本体之间的动力学差异；最后，虽然数据扩大到 20 种机器人和 6 万小时，但实机 generalist evaluation 的规模仍远小于预训练数据规模，因此它更像是在展示“这条路线可行”，而不是已经证明 whole-body cross-embodiment VLA 的问题被解决。

如果把 V1→V2 用一句话概括，就是：

**LingBot-VLA 1.0 解决的是“VLA 能不能靠真实机器人数据 scale”，而 LingBot-VLA 2.0 进一步解决“scale 起来之后，怎样把它变成一个能覆盖 whole-body、多本体和长程任务的实际机器人 policy”。**
