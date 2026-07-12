# TAMOLS: Terrain-Aware Motion Optimization for Legged Systems  

2026/7/7

来源：TOR22  

**Takeaway Message**

TAMOLS（Terrain-Aware Motion Optimization for Legged Systems）可以看作是ETH Zurich在传统模型优化路线上的代表性工作，也是后来Deep-Tracking-Control明确提到借鉴的方法之一。它的核心思想不是在已有落足点附近进行修正（foothold adaptation），而是**将机器人机身轨迹（base trajectory）和所有未来落足点（footholds）放进同一个Trajectory Optimization（TO）中联合优化**，并直接利用机器人实时感知得到的高度图（heightmap）进行规划。为了使这样一个高度非凸的问题能够实时求解，作者提出了一系列围绕“优化可解性”的设计，包括新的稳定性约束GIAC、Graduated Optimization初始化策略以及专门针对高度图设计的地图处理流程。

如果说上一篇Mini-Cheetah（2019）的故事是在回答“高速动态控制应该如何做”，那么TAMOLS回答的问题则完全不同：**机器人已经能够动态运动了，如何让它真正利用环境感知，在复杂地形上自主决定脚应该踩在哪里？** 作者指出，现实中的地形具有四个特点：高度图高度非光滑、非凸、局部遮挡严重，而且传感器噪声很大。传统的平地控制器或者blind locomotion根本没有利用这些信息，而已有的感知式规划器往往又计算太慢，无法满足动态运动需要。因此，他们希望建立一个能够**100 Hz以上实时重规划**、真正结合视觉感知的运动优化框架。

文章首先花了很大的篇幅梳理已有工作的技术路线，并把整个领域分成了两大类。第一类叫MMO（Modular Motion Optimization），即模块化规划。它通常先规划身体，再规划落足点，或者先得到一个nominal foothold，再在附近做局部修正（foothold adaptation）。这种方法速度快，也是后来大量工业控制器采用的方法，例如ANYmal早期的terrain-aware locomotion、Raibert heuristic以及学习型foothold adaptation都属于这一类。但由于身体和落足点分别规划，它们之间缺乏运动学一致性，很容易出现腿伸得太长、身体不可达等问题。第二类叫CMO（Combined Motion Optimization），即把Base和Foothold放到同一个优化问题中。这样能够保证运动学一致，但优化规模大、计算慢。TAMOLS的目标就是希望保留CMO的优点，同时把计算速度做到接近MMO。

为了达到这一目标，作者首先重新思考了动力学模型应该选到什么复杂程度。文章第三页给出了一张非常经典的图，把整个机器人动力学模型按照复杂程度排列：Whole-Body Dynamics、Centroidal Dynamics、Single Rigid Body Dynamics（SRBD）、Contact Wrench、GIAC、最后一直简化到ZMP。作者认为，如果采用Whole-body模型，优化变量太多；如果采用ZMP，又只能处理平地。因此，他们选择了介于两者之间的SRBD，并进一步提出一种新的GIAC（Gravito-Inertia Acceleration Cone）稳定性模型，把接触力变量完全消除，只保留机器人机身状态和落足点位置。这样一来，优化变量数量明显减少，而且所有约束都保持对落足点可微，非常适合梯度优化。可以说，GIAC是整篇论文最重要的理论贡献。

GIAC的核心思想其实非常直观。传统动力学约束需要显式优化每只脚的Ground Reaction Force，而GIAC通过一系列合理假设，例如腿质量可以忽略、地面摩擦满足库仑模型、机器人机身始终位于支撑腿上方等，把这些接触力全部消掉，最终得到一组只依赖于机身加速度、角动量变化和落足点几何关系的稳定性约束。作者证明，这些约束实际上定义了一个几何上的“重力—惯性加速度锥”（GIAC），只要机器人未来的运动始终保持在这个锥体内部，就一定能够找到满足摩擦约束的真实接触力。这一点与Mini-Cheetah工作形成了鲜明对比：Mini-Cheetah直接优化Ground Reaction Force，而TAMOLS则完全不再把接触力作为优化变量。

有了动力学模型之后，作者开始构建整个控制系统。系统架构可以分成四个模块：最底层是机器人和状态估计；其上是地图构建模块，由机载LiDAR实时生成高度图；然后进入TAMOLS优化器，同时输出未来Base Trajectory和Footholds；最后由Whole-Body Controller负责执行。与Mini-Cheetah几乎相同的是，TAMOLS仍然采用WBC作为底层控制器，不同的是高层规划器已经从MPC变成了Terrain-aware Motion Optimization。整个优化器工作在约100 Hz，而WBC保持400 Hz执行。

作者在感知部分也做了很多针对高度图的工程设计。LiDAR首先生成原始高度图，然后经过一整套滤波流水线，包括空洞填充（in-painting）、异常值去除（median filtering）以及不同程度的高斯平滑，最终生成三层不同用途的地图：h保存真实几何结构，用于落足点优化；hs1稍微平滑一些，用于计算梯度和边缘信息；hs2则被处理成一个“虚拟地板”，主要用于Base轨迹规划。这样设计的原因在于，机器人应该准确踩到真实台阶上，但机身轨迹没有必要跟随每一个小起伏，而应该更加平滑。这也是后来很多Terrain-aware Planner都会采用多层Heightmap的原因。

真正进入Trajectory Optimization之后，整篇论文开始围绕“联合优化”展开。作者把整个未来一个预测窗口内的所有变量一次性放进优化器，包括所有Spline参数、当前支撑脚位置、未来落足点以及松弛变量。优化变量不仅决定机器人未来机身轨迹，也决定未来每一步踩在哪里。整个优化目标可以理解为多个代价函数的加权和，包括：保证脚踩在地面上、避免两条腿发生碰撞、保持合理腿部姿态、使机身沿着地形自然运动、远离台阶边缘、保持和上一帧解连续，以及跟踪期望速度等。这些目标共同决定了最终的落足位置，而不是像传统Foothold Planner一样先打分再选最大值。

其中有几个目标尤其值得注意。第一，作者没有使用传统的Foothold Score Map，而是直接把Heightmap梯度作为优化目标，让脚自动远离边缘。第二，机身姿态不是拟合支撑脚平面，而是拟合经过特殊平滑后的hs2，因此机器人会主动沿着“虚拟地板”前进，而不会随着每一个石块上下起伏。第三，为了避免连续两帧优化得到完全不同的落足点，他们专门增加了一项“保持与上一帧解接近”的代价，使规划结果更加连续稳定。这些设计后来都可以在Deep-Tracking-Control中看到明显影子。

不过，真正让TAMOLS区别于此前Trajectory Optimization工作的，是它提出的Graduated Optimization。作者指出，高度图导致整个优化问题高度非凸，如果直接优化真实地形，很容易陷入局部最优，例如机器人一直停留在当前台阶，而不知道应该迈到下一层。为了解决这个问题，他们提出三级优化策略：首先使用经过强平滑处理的虚拟地板hs2求解一个几乎凸的问题；然后利用一个简化版Batch Search对落足点进一步修正；最后再以此作为初始化，在真实高度图上进行最终优化。也就是说，他们不是直接解决困难问题，而是逐步把简单问题“演化”成真实问题。这种Graduated Optimization原本主要用于计算机视觉，而作者首次把它系统引入四足机器人Trajectory Optimization中，也是论文的另一项重要贡献。

最后，实验验证了整个框架能够真正做到在线感知运动。ANYmal不仅能够上下楼梯，还能够稳定跨越Stepping Stones、Gap等复杂障碍，并支持多种动态步态。更重要的是，整个Trajectory Optimization能够在约10 ms内完成一次求解，从而达到100 Hz以上的在线重规划频率，这是此前联合优化方法很难达到的水平。

从今天来看，TAMOLS最大的价值并不是GIAC本身，而是它建立了一套完整的Terrain-aware Motion Optimization范式：**利用高度图作为优化变量的一部分，同时联合优化Base和Footholds，并通过Graduated Optimization保证实时性和收敛性。** 后来你分析的Deep-Tracking-Control明确说明“adapt a method similar to TAMOLS and Mini-Cheetah”，其中“TAMOLS”主要借鉴的是**联合优化落足点、利用Heightmap作为优化对象以及整体优化框架**；而“Mini-Cheetah”借鉴的则是**底层MPC/WBC控制思想**。两篇论文实际上分别代表了MIT控制路线和ETH感知规划路线，而Deep-Tracking-Control正是将这两条路线融合到了一起。
