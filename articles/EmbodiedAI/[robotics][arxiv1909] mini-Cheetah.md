# Highly Dynamic Quadruped Locomotion via Whole-Body Impulse Control and Model Predictive Control

2026/7/7  

来源：arxiv1909  

这篇论文可以说是 MIT Cheetah 系列控制框架中的一个里程碑，它提出了后来影响很大的 **MPC + Whole-Body Control (WBC)** 双层控制架构。它最重要的贡献并不是发明了 MPC，也不是发明了 WBC，而是重新定义了两者之间的分工：**MPC负责规划未来一段时间的地面反作用力（Ground Reaction Force, GRF），而WBC负责尽可能忠实地执行这些力，而不是像传统方法一样去严格跟踪质心轨迹（CoM trajectory）**。这一思想后来成为MIT Mini-Cheetah、Deep-Tracking-Control、TAMOLS等许多工作的基础。

这篇工作的故事其实来源于四足机器人高速运动中的一个根本矛盾。在机器人缓慢行走时，我们可以认为机器人始终受到地面的约束，因此只要规划好身体（CoM）轨迹，再利用Whole-Body Controller去跟踪这条轨迹，就能够获得稳定运动。然而一旦机器人开始高速奔跑、Bounding、Pronking或者Jumping，它会大量经历飞行阶段（aerial phase），此时身体实际上是不受控制的，CoM根本不存在一条能够被严格跟踪的轨迹。如果控制器仍然坚持“跟踪质心轨迹”，那么机器人反而会因为试图控制一个不可控对象而产生较大的误差。这也是作者认为传统WBC难以直接扩展到高速动态运动的重要原因。

作者因此提出了一个新的观点：**真正应该规划和跟踪的不是CoM轨迹，而是地面对机器人的冲量（Impulse），也就是Ground Reaction Force。** 这种思想来源于他们之前MIT Cheetah 2关于Bounding的工作。因为机器人真正能够主动控制的是脚对地面的作用力，而不是飞行中的身体位置。因此，只要规划好了未来各条腿应该施加什么样的接触力，身体轨迹自然会按照动力学演化出来，而不需要人为去规定每一个时刻身体必须在哪里。整个控制框架正是在这一思想下建立起来的。

整个系统采用了一个非常经典、也是后来影响深远的双层架构。论文第一页和第二页的系统图很好地说明了整个数据流：用户输入期望速度、方向和步态（例如Trot、Bound、Gallop），首先进入MPC模块。MPC使用一个非常简单的质心动力学模型，仅优化未来一个步态周期内每条腿应该产生的接触力，同时输出身体参考姿态和摆腿参考位置。随后这些信息进入Whole-Body Impulse Control（WBIC），WBIC结合完整机器人动力学模型，以500 Hz频率计算最终关节力矩、关节位置和关节速度，再由底层40 kHz的关节PD执行。整个系统形成了"低频规划 + 高频执行"的控制闭环。

论文中的MPC部分其实相当简洁。作者没有采用完整机器人模型，而是采用一个Lumped Mass Model，把机器人近似为一个带惯性的刚体，只保留质心平移和机身旋转动力学。优化变量只有未来若干时刻每只脚的Ground Reaction Force。为了保证能够实时求解，他们进一步做了三项重要近似：假设Roll和Pitch较小；使用参考轨迹进行线性化；忽略惯量矩阵中的一些耦合项。经过这些处理之后，动力学可以写成线性离散系统，再进一步转化为一个标准二次规划（QP）。优化目标就是让未来状态尽量接近期望状态，同时让接触力不要过大，并满足摩擦锥约束。由于步态序列（哪些脚着地）是提前给定的，因此整个问题保持凸优化形式，可以稳定地实时运行。

除了MPC之外，论文还有两个非常经典的小模块。一个是Gait Scheduler，它实际上只需要给每条腿指定两个参数——相位偏移（phase offset）和支撑时间比例（stance duration），几乎所有常见步态（Trot、Pace、Bound、Gallop、Pronking）都可以表示出来。另一个是Footstep Planner，它采用Raibert提出的经典启发式落脚点规划。下一步落足点主要由三部分组成：身体当前位置附近的肩部位置、根据当前速度计算出的对称项（Raibert heuristic），以及高速转弯时用于补偿离心效应的一项。这一公式后来几乎成为传统四足机器人控制中的标准写法，也正是你之前分析Deep-Tracking-Control时看到的那套Footstep Planner来源。

真正让这篇论文具有影响力的是WBIC（Whole-Body Impulse Control）。传统Whole-Body Control通常会把身体姿态、足端位置等任务组成一个层级优化问题，希望机器人严格跟踪这些任务。而作者在这里加入了一个十分巧妙的修改：**允许Floating Base的加速度发生松弛（relaxation）**。也就是说，当机器人进入飞行阶段时，控制器并不会坚持认为身体一定要按照规划轨迹运动，而是允许身体自由演化，同时仍然要求接触力尽量跟踪MPC规划出来的Ground Reaction Force。这样，控制目标就从“必须跟踪轨迹”变成了“优先执行接触力，再尽可能稳定身体和摆腿”。作者把这种思想称为Whole-Body Impulse Control，而不是传统意义上的Whole-Body Control。

在实现上，WBIC仍然保留了Whole-Body Control的很多经典组成，包括任务优先级（Task Priority）、Null-space Projection以及基于QP的逆动力学求解。但QP的目标函数发生了变化：优化变量既包括Ground Reaction Force，也包括Floating Base加速度松弛量。优化时既希望最终接触力接近MPC规划值，又希望机器人整体动力学尽量满足任务要求。当发生冲突时，允许Floating Base轨迹偏离，而不是破坏Ground Reaction Force。这正是整篇论文最核心的创新点，也是后来Deep-Tracking-Control作者所说“similar to Mini-Cheetah”的真正含义。

实验部分主要验证了这一架构的能力。作者在Mini-Cheetah上实现了最高3.7 m/s的稳定奔跑速度，瞬时速度甚至达到4 m/s；机器人能够稳定完成Trot、Bounding、Gallop、Pacing、Pronking等多种步态，并且仅需要改变步态调度器即可切换，不需要重新设计控制器。同时系统能够在草地、碎石地等不同地形保持稳定运动。实验数据还展示了一个非常有意思的现象：虽然MPC输出的是恒定高度参考，但机器人实际高度会随着跳跃自然上下起伏，这是因为WBIC优先保证了Ground Reaction Force，而不是强行压制身体轨迹，因此整个运动更加符合真实动力学。

站在今天来看，这篇论文最大的意义并不是创造了某个复杂算法，而是提出了一种后来被广泛采用的控制思想：**MPC负责规划未来力的分布，WBC负责执行这些力；真正控制的是Ground Reaction Force，而不是CoM轨迹。** 这一思想后来被MIT Cheetah系列持续沿用，也影响了TAMOLS、Deep-Tracking-Control等大量基于传统优化的四足控制框架。你现在研究的Deep-Tracking-Control实际上正是在这一Mini-Cheetah框架基础上，把原来的Raibert落足规划替换成了更加智能的Foothold Planner，而底层MPC+WBIC思想基本保持一致，因此这篇论文可以看作理解整个MIT控制路线最重要的一篇基础文献。
