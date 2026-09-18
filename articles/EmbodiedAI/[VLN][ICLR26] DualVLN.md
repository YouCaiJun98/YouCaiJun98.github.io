# Ground Slow, Move Fast: A Dual-System Foundation Model for Generalizable Vision-and-Language Navigation

2026/9/18  

来源：ICLR26  

**Takeaway Message**

DualVLN 想解决的不是“怎样让 VLM 再多预测几个动作”，而是一个更基础的系统设计问题：VLN 中的语义推理和局部运动控制，本来就处在完全不同的时间尺度，却被现有 VLM/VLA 方法塞进了同一个高延迟模型里。作者因此把导航拆成两个异步系统：慢速的 System 2 用大 VLM 做高层语义推理、决定“下一阶段该往哪里去”；快速的 System 1 用轻量 diffusion policy 根据这个目标和最新视觉，持续生成连续局部轨迹。真正连接两者的关键，不只是一个显式的 pixel goal，而是“pixel goal + latent goal”这一对显式/隐式中间表示。

DualVLN 的出发点其实很好理解。近几年 VLN 从传统离散导航逐渐走向 continuous navigation，又开始引入 VLM，希望利用大模型的视觉语言先验提升未见环境和复杂指令上的泛化能力。但很多所谓 continuous VLN 方法，决策层仍然是“VLM 看图和指令，然后预测一个很短的动作”，比如前进 25 cm、左转 15°。这就产生了一个结构性的矛盾：大 VLM 很擅长理解“出门以后在楼梯口右转，再进入左手边的浴室”这种长时程语义关系，却并不适合以几十 Hz 的频率处理“现在前面突然来了个人，我应该往左绕 20 cm”这种局部控制问题。每一步都重新调一次大模型，不仅慢，而且得到的运动往往是碎片化的。作者认为，现有方法的问题并不只是模型不够大，而是把 high-level reasoning、global planning 和 local control 耦合得太紧。

所以 DualVLN 的核心 insight 是：**不要让 VLM 直接承担高频控制，而是让它只解决它最擅长的那部分问题。**

整套系统因此被分成两个时间尺度。System 2 是一个 Qwen2.5-VL-7B，低频运行，负责理解自然语言指令、历史视觉和当前环境，并产生一个中期导航目标；System 1 则是一个很小的 diffusion-based trajectory policy，高频运行，根据这个中期目标和最新 RGB 不断修正机器人接下来要走的局部轨迹。论文 Figure 1 给出的典型频率是 System 2 约 2 Hz、System 1 约 30 Hz，最底层 controller 再以约 200 Hz 执行，因此高层“想去哪”和低层“怎么走”可以异步进行。

这里第一个关键设计是：System 2 不再输出 short-horizon action，而是输出 **pixel goal**。

具体地说，给定历史 RGB、当前 RGB 和语言指令，QwenVL 要在当前图像中指出“下一阶段最应该走向哪个位置”，也就是预测一个二维像素坐标 \((u,v)\)。作者把这个任务称为 *Farthest Pixel Goal Grounding*。训练时，他们拿原本的 3D ground-truth navigation trajectory，将其中的未来轨迹点投影到当前相机图像上，再利用 depth 判断哪些点真正可见：如果某个轨迹点虽然投影进了图像，但实际位于当前表面之后，就认为它被遮挡而丢弃。最后，从当前所有可见的未来轨迹点中取最远的一个作为监督目标。

为什么要取“最远可见点”而不是下一步？因为作者希望 System 2 给的是一个真正的中期 subgoal，而不是把原来的“前进 25 cm”换成另一种表达形式。如果当前视野能看到沿正确路径更远的位置，VLM 就应该一次告诉低层策略“朝那边走”，之后由 System 1 自己完成这一小段运动。

但 pixel grounding 很快又遇到一个现实问题：正确的 waypoint 不一定在当前视野里。例如机器人应该在下一个路口右转，但此刻相机还正朝前；或者相机姿态较高，真正应走的地面位置并不容易看清。因此 System 2 还被赋予了 *Self-Directed View Adjustment* 能力。它可以暂时不输出 pixel goal，而是先输出 Turn Left/Right 15°、Look Up/Down 15° 这样的视觉调整动作，让自己先获得更合适的观察视角，再做 grounding。

所以更准确地说，System 2 学的是三个能力：需要时主动调整视角、看到正确方向后给出 pixel goal，以及判断任务已经完成并输出 STOP。附录中的训练形式也是围绕这三类输出构造的。

如果论文到这里结束，那么 DualVLN 其实只是一个很传统的层级系统：

$$
VLM \rightarrow \text{2D goal} \rightarrow \text{local planner}.
$$

作者自己也意识到了这个问题。一个 \((u,v)\) 坐标虽然明确、可解释，但信息压缩得太厉害了。VLM 在决定这个 pixel goal 的过程中，本来已经综合了“指令进行到哪一步”“当前处于什么场景”“历史上经过了什么地标”“为什么应该走这个方向”等大量语义信息；如果最后只传两个数字给 System 1，那么这些 reasoning information 全部丢失，slow system 和 fast system 之间就只剩下一个非常浅的接口。论文明确把这一点作为为什么必须引入第二种 goal representation 的理由。

于是就有了 DualVLN 最有意思的第二个设计：**latent goal**。

System 2 预测完 pixel goal 之后，整个 QwenVL 上下文中已经包含语言、历史图像、当前图像、view adjustment 以及 pixel-goal text。作者在这个 sequence 的最后再插入 4 个 learnable latent query token。QwenVL 本身此时被冻结，但这 4 个 query 是可训练的；它们经过 VLM 的 self-attention 后，可以从整个 multimodal context 中抽取对后续 trajectory generation 最有用的信息。最后取这 4 个 token 在最后一层对应的 hidden states，作为 latent goal 传给 System 1。

因此 DualVLN 实际上给 System 1 保留了两种互补的信息：

$$
\text{explicit pixel goal}
$$

负责告诉系统“空间上往哪里去”，具有很强的可解释性和 grounding 约束；

而

$$
\text{implicit latent goal}
$$

负责保留“为什么去那里、当前任务上下文是什么、哪些信息可能对局部规划有用”这类很难用一个二维坐标表达的隐式信息。

这个 explicit + implicit 的设计，是我认为这篇论文比单纯 slow-fast hierarchy 更值得注意的地方。

接下来就是 System 1。它的角色不再是理解长指令，而是一个纯粹得多的问题：**给定高层目标和当前视觉，生成接下来一段可执行的连续轨迹。**

System 1 使用 lightweight Diffusion Transformer，一次生成 32 个 dense trajectory waypoints。它的 condition 有两部分：一部分是刚才 System 2 传过来的 latent goal，另一部分则是高频 RGB visual feature。

高频 RGB 为什么仍然必不可少？因为两个系统是异步的。假设 System 2 在时刻 \(t\) 判断“沿走廊朝门走”，然后下一次 VLM 推理要几百毫秒以后才完成。在这期间机器人已经移动了，而且前方可能突然出现一个人。System 1 显然不能机械执行几百毫秒前规划好的轨迹，所以它同时看 System 2 当时所看到的 RGB 和当前时刻 \(t+k\) 的最新 RGB，先用 ViT 编码，再通过 self-attention 融合两个时刻的信息，之后用 Q-Former 压缩成 32 个 visual tokens。这套高频视觉条件使得 System 1 可以在保持高层目标不变的情况下，根据局部变化重新生成 trajectory。

这也解释了 DualVLN 所谓“dynamic obstacle avoidance”的来源。它不是让 7B VLM 以 30 Hz 重新判断“这个人应该怎么绕”，而是把高层目标保持为“继续朝那扇门前进”，同时让快速视觉 policy 自己根据最新观测改变局部轨迹。

因此从功能分工上看：

$$
\text{System 2} \approx \text{semantic navigation / subgoal planning}
$$

而

$$
\text{System 1} \approx \text{goal-conditioned reactive local planning}.
$$

System 1 用 flow matching 形式训练，但在首遍理解这篇文章时，公式本身不是重点。重要的是它不是做单点 regression，也不是输出 forward/left/right，而是在条件信息下生成一整段平滑 trajectory；这也是为什么作者认为它比短动作 VLM 更适合真实机器人连续运动。

训练上，作者刻意没有把整个系统从头到尾 joint training。第一阶段先完整 finetune QwenVL，让 System 2 学会 view adjustment、pixel goal grounding 和 STOP；第二阶段冻结 System 2，只训练 latent query 和 System 1。 

这个选择对应论文的另一个核心观点：**high-level reasoning 和 low-level control 不仅推理时应该解耦，训练时也应该适当解耦。**

原因是两者的数据需求和学习目标不同。System 2 需要大量、多样的 VLN 数据去学泛化和语义推理，而 System 1 的任务相对简单，就是学“给定 goal 怎么走过去”。作者后面的 data-scaling 实验也很有意思：System 1 只使用 System 2 轨迹数据的一小部分就已经表现不错，到大约 10% 数据时性能就接近饱和，而继续增加数据收益很小。

这实际上是在支持他们整个架构背后的假设：VLN 中真正 data-hungry、需要 foundation model 能力的是“理解环境与指令、决定目标”；而局部 navigation policy 并不需要同样规模的模型和数据。

实验最关键的不是某个单独数字，而是几个核心 claim 基本都得到了验证。

首先，在标准 VLN-CE 上，DualVLN 相比 NaVILA、StreamVLN 等 RGB-based VLM 方法取得了明显提升，例如 R2R Val-Unseen 的 SR 从 StreamVLN 的 56.9 提升到 64.3。

更重要的是，在考虑机器人动力学和 locomotion controller 的 VLN-PE 中，DualVLN 即使没有针对 VLN-PE trajectory 做额外 finetune，也明显优于很多原有方法。这个结果支持作者关于“连续 trajectory generation 比 VLM 输出碎片化短动作更适合真实执行”的主张。

论文还专门构造了 Social-VLN，把动态 humanoid 放到原本的 VLN 路径附近，测试机器人能不能绕开人以后继续完成语言任务。DualVLN 在这个 setting 中仍然优于 StreamVLN，但性能同样出现了很大的下降，说明 slow-fast architecture 对动态环境确实有效，但 social navigation 并没有因此被解决。

几个消融尤其能帮助理解作者真正想证明什么。

如果不先训练 System 2 的显式 pixel grounding，而是直接把两个系统 joint training，性能明显下降，而且作者观察到 System 2 的泛化也受到破坏。这支持“先把高层语义规划学好，再接低层控制”的两阶段设计。

如果保留 System 2，但生成 latent goal 时不给 query 看到 pixel-goal text，性能也会下降，说明显式 grounding 并不是一个纯可视化接口，而是能真正帮助下游 trajectory generation。

反过来，如果不要 learnable latent goal，只把 pixel-goal token 自己的 VLM hidden state 传给 System 1，性能同样下降。这说明作者设计 latent query 的目的不是简单“多拿几个 feature”，而是让 downstream trajectory objective 去学习“应该从 frozen VLM context 中提取哪些信息”。

还有一个很有说明力的实验：作者用传统 point-goal navigation policy 替换 System 1，甚至额外提供 depth，把 2D pixel goal 转成 3D point goal，效果仍然不如原始 System 1。作者认为原因之一是 System 1 并不是机械追踪一个坐标；它通过视觉学到了一定的局部 navigation prior，因此如果 pixel goal 有小幅误差、甚至恰好落在障碍附近，只要整体方向正确，它仍有可能自己绕开障碍。

这点其实很好地解释了 DualVLN 为什么不只是“VLM + 传统 local planner”。

它想做的是：

$$
\text{semantic reasoning}
\rightarrow
\text{learned semantic-spatial goal}
\rightarrow
\text{learned reactive trajectory policy}.
$$

所以整篇文章最重要的贡献，我认为不是“用了 diffusion”本身，而是提出了一种更合理的 VLN 系统分工：

大模型不再负责每一步怎么动，而只负责低频、长时程、强语义的目标选择；小模型则根据这个目标和高频视觉做连续、实时的局部执行。Pixel goal 保证两个系统之间存在一个显式、可监督、可解释的空间接口，而 latent goal 又避免把整个高层 reasoning 压缩成一个二维点。

如果只保留一张 mental model，可以把 DualVLN 记成：

$$
\text{Instruction + RGB History}
$$

$$
\downarrow
$$

$$
\boxed{\text{Slow VLM: Where should I go?}}
$$

$$
\downarrow
$$

$$
\text{Pixel Goal + Latent Goal}
$$

$$
\downarrow
$$

$$
\boxed{\text{Fast Visual Policy: How should I get there now?}}
$$

$$
\downarrow
$$

$$
\text{Continuous Trajectory}.
$$

这就是 DualVLN 的主线。它真正想改变的是 VLN 的架构范式，而不只是把某个 benchmark 再往上刷几个点。
