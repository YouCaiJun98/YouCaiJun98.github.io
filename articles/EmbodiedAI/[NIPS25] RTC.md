# Real-Time Execution of Action Chunking Flow Policies  

2026/10/20  

来源：NIPS25

# 论文导读：Real-Time Execution of Action Chunking Flow Policies

中文标题：基于 Flow Policy 的动作分块实时执行方法

作者： Kevin Black、Manuel Y. Galliker、Sergey Levine（Physical Intelligence、UC Berkeley）

发表： NeurIPS 2025

论文： [arXiv:2506.07339](https://arxiv.org/abs/2506.07339?utm_source=chatgpt.com)

## 一、研究背景与现状

近年来，以 π0、π0.5 为代表的 Vision-Language-Action（VLA）模型逐渐具备了复杂机器人操作能力。然而，这些模型通常包含数十亿参数，推理耗时明显高于机器人底层控制周期，难以直接满足实时控制要求。

为此，现有 VLA 普遍采用 Action Chunking：模型根据当前观测，一次预测未来多个时间步的动作，机器人连续执行其中一部分，再重新获取观测、生成下一段动作。这种方法既减少了模型调用次数，又能够在一定程度上保持动作的时间一致性。

但 Action Chunking 并没有真正解决推理延迟问题。现有执行策略主要存在两种不足。

第一种是同步执行（Synchronous Execution）：机器人执行完当前 Action Chunk 后，暂停等待下一次模型推理完成。这会导致运动间歇性停顿，不仅降低执行效率，还可能改变机器人与环境交互的动力学过程。例如，在划火柴等需要连续运动的操作中，短暂的停顿也可能导致任务失败。

第二种是朴素异步执行（Naive Asynchronous Execution）：在执行当前 Chunk 的同时，提前启动下一次推理，待新 Chunk 生成后直接切换。虽然避免了停顿，但新旧 Chunk 是分别生成的，可能选择不同的运动策略。例如，旧 Chunk 计划从障碍物左侧绕过，而新 Chunk 计划从右侧绕过，两段动作直接拼接就可能产生剧烈的位置或速度变化。

已有的 Temporal Ensembling 可以通过平均多个预测来缓解动作突变，但对于具有多模态分布的动作，两个合理动作的平均值未必仍然合理。因此，简单的轨迹平滑无法从根本上解决这个问题。

## 二、核心问题与研究动机

本文关注的核心问题是：

如何在 VLA 推理耗时超过机器人控制周期的情况下，实现不中断的实时动作执行，同时保持不同 Action Chunk 之间的连续性，并保留对新观测的响应能力？

作者认为，解决问题的关键不只是让推理和执行并行，还需要考虑新旧 Chunk 之间的关系。

当模型开始生成下一段动作时，机器人仍在执行上一段动作。假设新 Chunk 需要经过 \\(d\\) 个控制周期才能生成完毕，那么在这段时间内，机器人必然继续执行旧 Chunk 的 \\(d\\) 个动作。

也就是说，在新 Chunk 开始生成时，它的前 \\(d\\) 个时间步实际上已经被旧 Chunk 的动作决定了。

因此，生成新 Chunk 不应该被视为一次完全独立的动作预测，而应该考虑那些已经确定的动作，并在此基础上规划后续运动。

这一观察构成了 RTC 的核心设计动机：将跨 Chunk 的连续性问题转化为一个带有已知前缀约束的动作生成问题。

## 三、研究目标与主要贡献

论文提出 Real-Time Chunking（RTC），一种面向 Diffusion / Flow-based Policy 的实时异步动作执行方法。

RTC 的目标是在不重新训练基础 VLA 的前提下，让机器人持续执行动作，并使新生成的 Action Chunk 与上一段动作保持协调。

其主要贡献有三个方面。

首先，作者提出将动作衔接建模为 Inpainting（补全） 问题。传统 Inpainting 根据图像中已知的部分生成缺失区域，而 RTC 根据已经确定的动作前缀，生成与其兼容的后续动作。

其次，作者设计了 Soft Masking（软掩码） 机制。RTC 不仅约束推理期间必然执行的动作，还对新旧 Chunk 中尚未执行的重叠部分施加逐渐减弱的约束，从而兼顾动作连续性与重新规划能力。

最后，作者建立了一个包含 12 个动态任务的 Kinetix 仿真评测基准，并在使用 π0.5 的 6 个真实双臂操作任务上验证了 RTC 的有效性。

需要强调的是，RTC 的创新不在于提出新的 VLA 架构或 Flow Matching 训练方法，而在于将已有生成式动作模型的推理过程与机器人实时执行机制结合起来。

## 四、方法概览

RTC 主要由异步动作执行、Inference-Time Inpainting 和 Soft Masking 三部分组成。

[Real-Time Execution of Action Chunking Flow Policies (RTC)](https://images.openai.com/static-rsc-4/MV6rQYVYI5ECwPzwpjILSVGISgvIj7cQwhxOXY7NUmtE9jacITt_hevjjaSA48Om7bhk2jWCkY61LaJc9Tk_00HD33ggUUyg5fZ3OCdV5r2HAdsz9QxvOlSiBmiFw4qG1JxTaqFVnzHMR8qmW6t_49z46kLs_CfmQK0wgm4Fk0E?purpose=inline)

论文 Figure 3 展示了 RTC 对新旧 Action Chunk 重叠区域施加不同约束的设计。

1\. 异步执行：让机器人边执行、边推理。

RTC 将机器人控制与 VLA 推理分开运行。机器人按照固定控制频率持续读取并执行当前 Chunk 的动作，而 VLA 在后台提前生成下一段 Chunk。新动作一旦完成生成，系统便切换到新 Chunk，从而避免同步推理造成的停顿。

2\. Inpainting：让新 Chunk 继承已确定的动作。

RTC 利用 Flow Matching 本身具有的迭代生成能力，在生成过程中加入对已有动作的约束。

具体而言，它利用当前的 Flow 状态估计最终动作序列，检查其中已确定的动作是否与旧 Chunk 一致，再通过梯度引导修正生成方向。

这样，新 Chunk 并不是先独立生成、再与旧动作拼接，而是在生成过程中就考虑了旧动作提供的约束。

这与 Temporal Ensembling 存在本质区别：后者在动作生成之后进行平均，RTC 则在生成过程中引导动作分布，使新 Chunk 更可能延续旧 Chunk 已经选择的运动策略。

3\. Soft Masking：让历史约束随预测时间逐渐减弱。

仅约束推理期间必然执行的前 \\(d\\) 个动作，并不一定能够避免策略突变。因为即使前几个动作一致，新 Chunk 仍可能很快改变运动方向。

因此，RTC 将新 Chunk 划分为三个区域：

- Frozen Region：推理期间必然执行的动作，施加强约束。
- Intermediate Region：新旧 Chunk 中尚未执行的重叠动作，施加逐渐减弱的约束。
- New Region：超出旧 Chunk 预测范围的动作，不施加历史约束，由模型自由生成。

这种设计使模型在近期尽量延续已确定的运动，在较远的未来逐渐获得根据新观测调整行为的自由度。

需要注意，RTC 的 Frozen Region 在实现上使用的是梯度引导，并非数学上严格的硬约束，因此不能保证生成结果与旧动作完全相等。

总体而言，RTC 实际上是在动作连续性与闭环响应能力之间建立一种时间相关的权衡机制。

## 五、实验设计与结果

论文分别从动态仿真任务和真实机器人操作两个方面验证 RTC。

在仿真实验中，作者基于 Kinetix 构建了 12 个涉及抛掷、接取、平衡与运动控制的动态任务。这些任务比常见的准静态操作更依赖持续反馈，因此更适合考察推理延迟对机器人性能的影响。

对比方法包括 Naive Async、Temporal Ensembling 和 Bidirectional Decoding（BID）。

实验表明，RTC 在不同推理延迟下整体表现最好，尤其随着延迟增大，相对于其他方法的优势更加明显。同时，Soft Masking 相比只约束前缀的 Hard Masking 能进一步改善性能。RTC 还能够更有效地利用较短的 Execution Horizon，提高闭环控制的响应能力。

在真实机器人实验中，作者使用 π0.5，测试了点燃蜡烛、插入网线、整理床铺、折叠衣物等 6 个双臂操作任务。

[NeurIPS Poster Real-Time Execution of Action Chunking Flow Policies](https://images.openai.com/static-rsc-4/QGm7-GoTLZnEfot3EHoQt0cApJjhvLPLKcXsOmD4iK8ph5jnxzn5oKucQR3lwXlzxKhXpbRW3wMVRdRFXKscRuUGau6jZLzw6UGxk2i0GB-fWCHJKb2FSKKAvUrPriDmjHTO-91EtPcUurECHksJhR3t-zhR4UIEMn__OSB9rJE?purpose=inline)

论文中的点火柴任务对动作连续性要求较高，是 RTC 的代表性真实机器人测试。

真实实验采用 50 Hz 控制频率，每次生成 50 步动作，并人为增加 100 ms、200 ms 的推理延迟，以测试不同方法的鲁棒性。

结果显示：

首先，RTC 在所有测试延迟下均取得最高的平均任务吞吐率。即使增加 200 ms 的额外延迟，其表现也没有明显下降，而同步执行方法的效率会随着推理延迟增大而降低。

其次，Temporal Ensembling 在较大延迟下出现明显的动作振荡，甚至触发机器人的保护性停机，说明简单地平均多个动作预测并不能保证安全、连续的执行。

最后，RTC 的收益并不只是消除了推理等待。即使将同步执行中的等待时间从比较中排除，RTC 仍然能够在多项任务中更快完成操作步骤。这说明跨 Chunk 连续性的改善，也有助于减少操作失误和反复尝试。

论文中的点火柴任务尤其体现了这一点：由于任务精度要求高且难以通过重试恢复，RTC 在最终任务得分上具有明显优势。

RTC 也存在计算代价。在作者的 π0.5 实验设置中，普通推理耗时约 76 ms，加入 RTC 后增加到约 97 ms。这主要来自 Inpainting 所需的梯度计算。不过，得益于异步执行机制，增加的模型计算耗时并没有直接转化为机器人执行过程中的等待。

## 六、局限性与思考

论文的主要局限是 RTC 需要在 Flow Matching 的生成过程中计算额外的梯度，因此会增加模型推理开销。此外，它主要适用于 Diffusion / Flow-based Policy，不能直接推广到所有类型的动作生成模型。

真实机器人实验主要集中于双臂操作，尚未验证复杂的真实腿式运动场景。在四足机器人或人形机器人中，动作连续性还涉及步态相位、接触状态和动力学稳定性，因此 RTC 能否直接取得类似收益，仍需要进一步研究。

从方法设计上看，我认为 RTC 还有一个值得关注的问题：它主要根据历史动作约束新 Chunk，而不是直接根据机器人在推理完成时的真实状态进行规划。当执行存在误差、环境突然变化或发生意外接触时，已承诺的动作不一定能准确反映实际状态。因此，RTC 改善了异步生成和动作衔接，但并没有完整解决延迟带来的状态预测问题。

对于你的 Foothold-VLN 研究，这篇论文的启发在于：如果 Action Expert 负责生成未来一段落足点计划，那么可以考虑让它在执行上一段计划时异步生成新计划，并利用已确定的落足目标作为条件。不过，相比双臂动作，落足点是否可以修改还取决于摆动相位和接触状态，因此可能需要进一步设计 Contact-Aware 的条件机制。这属于基于论文思想的延伸，并非 RTC 原文已经验证的方案。

## 七、总结

RTC 研究的是大模型机器人控制中的一个重要实际问题：当动作生成速度慢于机器人控制频率时，如何既保持实时执行，又避免不同 Action Chunk 之间的动作突变。 作者提出将动作衔接转化为 Inpainting 问题，通过推理时梯度引导和 Soft Masking，使新 Chunk 在遵守已有动作约束的同时，仍能根据新观测规划未来运动。仿真和真实机器人实验表明，这种方法能够改善动作连续性、提高任务执行效率，并增强系统对推理延迟的鲁棒性。其价值在于无需重新训练 VLA，便能改善已有 Flow-based Policy 的实时执行能力，为大模型机器人策略的实际部署提供了一种通用思路。