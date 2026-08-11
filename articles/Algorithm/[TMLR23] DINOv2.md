# DINOv2: Learning Robust Visual Features without Supervision

2026/8/11  

来源：TMLR23  

它关注的是一个非常基础但也非常重要的问题：能不能像 NLP 中的大语言模型一样，在视觉领域训练出一种真正“通用”的基础表征，使得模型在面对新的图像分布和新的下游任务时，不需要重新微调整个 backbone，仅仅使用冻结的视觉特征就能够取得很好的效果。作者认为，当时视觉基础模型主要有两条路线：一条是以 CLIP 为代表的 image-text 预训练，通过文本监督获得很强的高层语义能力；另一条是 DINO、iBOT、MAE 等纯图像自监督方法。DINOv2选择第二条路线，它希望证明：如果数据足够大、足够多样且经过合理筛选，同时把已有的自监督训练方法扩展到足够大的模型规模，那么即使完全没有文本和人工标签，也能够学习到非常通用的视觉特征。论文最终训练了最大的 ViT-g/14，参数量约 1.1B，并进一步将其蒸馏成 ViT-L/B/S 等较小模型。作者在大量 image-level 和 pixel-level benchmark 上证明，这些冻结的视觉特征显著超过此前的自监督模型，并且在很多任务上已经能够接近甚至超过 CLIP、OpenCLIP 等弱监督视觉模型。

理解 DINOv2 时，首先要抓住作者对“好的视觉特征”的定义。作者并不只希望模型知道“一张图里是什么”，还希望 feature 本身保留足够丰富的局部结构。例如，对于分类任务，模型需要从整张图得到一个 global representation；但对于语义分割、单目深度估计等任务，模型还必须知道不同 patch 分别对应什么物体、物体之间有什么空间关系。作者在引言中认为，text-guided pretraining 存在一个潜在限制：caption 只是图像信息的一种不完整描述，复杂的 pixel-level 信息未必会出现在文本监督中，因此纯图像自监督学习反而可能更适合保留丰富的局部视觉结构。过去的问题在于，这类 SSL 方法基本都在 ImageNet-1k 这样的有限数据集上发展；直接把它们扩大到互联网级的未整理数据上，又经常因为数据质量和分布失衡而导致 feature 质量下降。因此 DINOv2 的核心并不是重新发明一种全新的 SSL 目标，而是重新回答“已有的 discriminative SSL 方法在大模型、大数据条件下到底应该怎样训练”。

论文的第一项主要工作因此是数据，而不是模型。作者构造了一个 1.42 亿张图片的预训练数据集 LVD-142M。它不是直接随机抓取 142M 张互联网图片，而是先准备一批质量较高、分布较明确的 curated datasets，包括 ImageNet-22k、Google Landmarks，以及覆盖 fine-grained classification、segmentation、depth estimation、retrieval 等不同视觉任务的数据集；另一方面，从公开网页抓取数据中得到十亿级的 uncurated image pool。作者随后对这些互联网图片做安全过滤、NSFW 过滤、人脸模糊以及近重复图片去除，然后利用一个自监督 ViT-H/16 把图片转换成 visual embedding，以 cosine similarity 衡量图像相似度，再以 curated datasets 中的图片作为“锚点”，从庞大的互联网数据中检索视觉上相似的样本。对于较大的参考数据集，他们通常为每个 query image 检索几个 nearest neighbors；对于较小的数据集，则先对未整理数据进行 k-means clustering，再从 query 所属的 cluster 中采样。也就是说，curated datasets 并不是直接给模型提供标签，而是用来定义“什么样的互联网图像值得纳入预训练集”，从而使最终的 LVD-142M 同时具有较大的规模、较高的多样性和更受控的数据分布。论文 Figure 3 展示的就是 `embedding → deduplication → retrieval → augmented curated data` 这一过程。 

这套数据筛选流程对于理解 DINOv2 非常重要，因为作者后面的消融实验表明，“数据多”本身并不够。使用同样规模的 142M 张未经整理的互联网图片训练，ImageNet-A、Oxford retrieval、iNaturalist 等跨域任务都明显差于经过筛选的 LVD-142M。相反，LVD-142M 在 ImageNet-1k 本身与 ImageNet-22k 预训练基本持平，但在大量 ImageNet 之外的任务上更好。这说明 DINOv2 所谓 scaling 并不是简单地把数据量堆大，而是强调 model scale、data scale、data quality 和 data diversity 必须同时扩大。随着模型从 ViT-L 增大到 ViT-H、ViT-g，使用 LVD-142M 相比 ImageNet-22k 的收益也越来越明显。 

在模型本身上，DINOv2仍然使用标准的 Vision Transformer，因此如果已经熟悉 ViT，它的 backbone 并不复杂。最大的 ViT-g/14 使用 patch size 14、embedding dimension 1536、24 个 attention heads 和 40 个 Transformer blocks，参数量大约 1.1B；ViT-L/14 是 1024 维、16 heads、24 blocks，而 ViT-B/14 和 ViT-S/14 则进一步缩小。真正需要重点理解的是它怎样在没有标签的情况下训练这些 ViT。作者把训练方法概括为 DINO 和 iBOT 两类目标的组合，同时加入来自 SwAV 的 centering 方法、KoLeo regularizer 和最后的高分辨率 adaptation。

整个训练框架仍然是 DINO 系列经典的 student-teacher self-distillation。Student 和 Teacher 结构相同，Student 通过正常的反向传播更新，而 Teacher 不参与梯度下降，而是 Student 历史参数的 exponential moving average，Teacher momentum 从 0.994 逐渐增加到 1。 对同一张原始图片产生不同 crop，然后分别输入 Student 和 Teacher。这里的核心思想不是让模型预测人工类别，而是要求同一张图片在不同 view 下形成一致的内部表征，因此 Teacher 相当于不断为 Student 提供一个相对平滑、稳定的自监督训练目标。

DINOv2首先保留了原始 DINO 的 image-level objective。对于同一图片的不同 crop，Student 和 Teacher 都从 ViT 的 class token 中取得全局图像特征，再分别通过一个 DINO projection head。这个 head 是一个 MLP，输出一组作者称为 prototype scores 的值；经过 softmax 和相应 normalization 后，Student 得到 (p_s)，Teacher 得到 (p_t)，训练目标就是两者之间的 cross entropy：

$$
L_{\mathrm{DINO}}
=
-\sum p_t \log p_s .
$$

这些 prototype 并不是带有“dog”“car”之类人工标签的类别，而是网络自己形成的表征空间。这里真正监督的是 class token，所以 DINO objective 更主要地负责学习图像整体层面的 representation：不同 crop 即使只观察同一物体的不同部分，最终也应该保持一致的 global semantics。

但仅仅训练 class token 还不足以解释 DINOv2为什么在 segmentation 和 depth 这样的 dense prediction 上那么强，因此第二个关键目标是来自 iBOT 的 patch-level objective。训练时，Student 输入中的一部分 image patches 会随机被 mask，而 Teacher 仍然观察完整图片。随后 Student 在这些被遮挡位置输出 mask token 的特征，Teacher 则输出完整图片中对应位置的真实 patch feature；二者分别经过 iBOT projection head 和 normalization，再只在这些 masked patch 上计算 cross entropy。 从作用上看，这和 masked language modeling 有一点相似：Student 必须依靠周围未遮挡 patch 和全局上下文，推断被遮挡区域在 Teacher 表征空间中应该是什么。不过它预测的不是原始像素，也不是离散的人工视觉词，而是 Teacher 自己产生的 patch-level representation。

因此可以把 DINOv2最核心的两个训练信号理解为：

$$
\text{DINO: CLS token}\rightarrow
\text{image-level representation}
$$

$$
\text{iBOT: patch token}\rightarrow
\text{local/dense representation}.
$$

这也是论文结构上非常重要的一点：DINOv2不是单纯希望一个 `[CLS]` token 在分类任务上很好，而是显式训练了 patch token。论文的消融实验也支持这一点：移除 iBOT 的 masked image modeling objective 后，ImageNet 分类变化不大，但 ADE20K segmentation 从 47.1 mIoU 降低到 44.2，说明这一目标特别有利于 dense prediction。

在这两个主体 objective 之外，DINOv2还加入了几个解决 feature distribution 和训练稳定性的问题。首先是 Sinkhorn-Knopp centering。DINO 这种没有人工标签的 self-distillation 方法需要防止 representation collapse，也就是网络把大量不同图像映射成极其相似的输出。DINOv2按照相关工作的建议，把 Teacher 原来的 softmax-centering 替换成来自 SwAV 的 Sinkhorn-Knopp normalization，并运行三次 Sinkhorn-Knopp iteration，而 Student 仍使用 softmax。 这里可以把它理解为约束 Teacher 对 prototype 的分配不要过度集中在少数 prototype 上，从而维持有信息量的 representation。

另一个比较重要的新成分是 KoLeo regularizer。设一个 batch 中有 (n) 个经过 L2 normalization 的 feature (x_i)，作者计算每一个 feature 与 batch 内其他 feature 的最近邻距离

$$
d_{n,i}=\min_{j\neq i}|x_i-x_j|,
$$

并采用

$$
L_{\mathrm{KoLeo}}
=
-\frac{1}{n}\sum_i\log d_{n,i}.
$$

由于优化这个目标倾向于增大相邻 feature 之间的距离，因此它会鼓励整个 batch 的 representation 更均匀地铺在 feature space 中，而不是大量堆在少数位置。 这一项对于 nearest-neighbor 类型的任务特别有效：论文中 Oxford-M retrieval 从 55.6 提升到 63.9，而其他指标基本没有受损。因此 KoLeo 解决的是 representation space 本身的分布问题，而 iBOT 和 DINO 则分别负责提供局部和全局学习信号。

另外一个看似简单但对 dense task 很有实际价值的设计，是训练末期才提高输入分辨率。分割和检测等任务天然需要更精细的 patch representation，但 ViT 在高分辨率下的 self-attention 代价很高。作者因此没有从头到尾都使用高分辨率，而是先完成主要的低分辨率预训练，在最后一小段训练中把分辨率提高到 (518\times518)。 论文的分辨率消融进一步证明这种做法很划算：全程在 416 分辨率训练大约需要 224 分辨率的三倍计算量，而先在 224 训练、最后只进行 10k iterations 的 416 adaptation，性能已经非常接近全程高分辨率训练。

到这里可以看到，DINOv2的方法本身其实没有依靠一个单独的“新算法”取得突破。论文真正花费很多篇幅讨论的是怎样让这样一套 SSL recipe 扩展到十亿参数模型和亿级数据。作者采用了 memory-efficient attention、sequence packing、efficient stochastic depth、FSDP 和 mixed precision 等工程优化。例如 DINO 训练中会同时存在较大的 global crops 和较小的 local crops，它们形成不同长度的 token sequences，通常不能简单作为一个普通 batch 一起计算。DINOv2借用了 NLP 中 sequence packing 的思想，把这些不同序列拼接成一个长序列，再在 self-attention 中使用 block-diagonal mask，确保不同 crop 之间完全无法相互 attention。这样数学结果仍然等价于分别 forward，却能明显提高 GPU 的计算利用率。 最终作者声称，在相同硬件条件下，他们的实现相比 iBOT 约快两倍，同时只使用大约三分之一的显存。

模型规模化之后，作者采用了一种很有意思的训练策略：真正从头大规模训练的核心模型是 ViT-g/14，而更小的 ViT-S/B/L 则主要通过知识蒸馏获得。由于 DINO 本身已经是 teacher-student 的训练形式，蒸馏时只需要把原来的 EMA Teacher 换成一个冻结的大模型 ViT-g，再让小 Student 拟合 Teacher 的输出即可。论文比较了从头训练的 ViT-L/14 与从 ViT-g/14 蒸馏得到的 ViT-L/14，结果后者在所测试的 12 个 benchmark 中全部更好，有些任务甚至接近或超过用于蒸馏的 ViT-g。 因而作者的实际 scaling strategy 可以概括成：先把训练资源集中到一个非常强的大视觉模型上，然后再把它的能力转移给不同尺寸的模型，而不是把每一种模型都独立从头训练。

论文后半部分的实验，主要在回答“这种 self-supervised feature 到底有多通用”。作者覆盖了 ImageNet 分类、fine-grained classification、domain generalization、instance retrieval、视频动作识别、语义分割和单目深度估计等任务，而且大量实验故意冻结 DINOv2 backbone，只训练 linear probe 或非常简单的 downstream head。这样做的目的不是追求某个 benchmark 的绝对 SOTA，而是检验：下游任务所需的信息是否已经存在 pretrained feature 中。整体趋势非常明显——随着 DINOv2从 ViT-S 增大到 ViT-B、L 和 g，几乎所有任务都持续提高；最大的 DINOv2-g 已经在相当多任务上达到或超过当时最强的公开 weakly-supervised representation。Figure 2 将这种 scaling trend 汇总在分类、分割、深度、retrieval、robustness 和 video understanding 等八类任务中。

其中 domain generalization 的结果尤其能体现这套 feature 的鲁棒性。例如相比 iBOT，DINOv2-g 在 ImageNet-A 上由 41.5 提升到 75.9，在 ImageNet-R 上由 51.0 提升到 78.8，在 ImageNet-Sketch 上由 38.5 提升到 62.5。作者认为这说明 DINOv2并不是单纯在训练分布内部学到了更好的 ImageNet 分类 feature，而是在跨域情况下也拥有更强的 transferable representation。

更值得注意的是 dense prediction。对于 semantic segmentation，作者甚至可以直接从冻结 DINOv2 的 patch tokens 上训练一个线性分类层，得到低分辨率 segmentation logits，然后再上采样成完整 segmentation map。在 ADE20K 上，DINOv2-g 的简单 linear setup 达到 49.0 mIoU；把最后四层 patch tokens 拼起来、使用更高输入分辨率和 multi-scale test augmentation 后达到 53.0。如果保持 DINOv2 backbone 冻结，只在它上面增加 ViT-Adapter 和 Mask2Former head，则 ADE20K 可以达到 60.2 mIoU。 对论文来说，真正重要的并不是 60.2 这个数字本身，而是大量 segmentation information 已经可以被非常简单的 predictor 从冻结 patch feature 中线性地“读出来”。

单目深度的实验传达的也是类似信息。DINOv2预训练过程中从来没有使用过 depth label，但冻结 feature 后，仅训练简单的 depth prediction module 就能得到很好的结果，而且还能从 NYUv2 等训练域迁移到不同图像域。论文中的 qualitative comparison 表明，DINOv2相对于 OpenCLIP 能得到更加平滑、artifact 更少的 depth map；一些在 OpenCLIP representation 中几乎被忽略的物体，在 DINOv2 feature 上仍能恢复出正确的位置。 这说明自监督 image representation 中不只是存在类别语义，还自发形成了一定程度的 scene geometry。

论文 Figure 1 和后面的 PCA 分析把这种性质展示得更加直观。作者直接对不同图片的 patch feature 做 PCA，发现第一主成分很容易把主要前景物体和背景分离开；去掉背景后，再对几个同类图片的 patch feature 做 PCA，不同主成分会对应到相似的 object parts，而且即使对象姿态、风格甚至具体实例发生明显改变，对应的身体部位仍表现出相似的 feature。这些结构没有任何 object-part annotation 或 segmentation supervision，是模型在大规模自监督学习过程中自动产生的 emergent property。 这其实也是 DINOv2后来被大量用于 correspondence、tracking、3D perception 和机器人视觉的重要原因：它提供的不只是一个全局图片 embedding，而是一张带有丰富局部结构的 patch feature map。

从整篇论文的论证逻辑来看，DINOv2最重要的结论因此并不是“我们设计了一个比 DINO 更好的 loss”，而是证明了一套更宏观的观点：纯视觉 SSL 可以像语言模型一样依赖 scale 获得越来越通用的 representation，但它的 scaling 不能只是把模型和互联网数据机械放大，而需要同时解决高质量数据筛选、global/local 自监督信号、feature collapse 与分布、训练稳定性、计算效率以及大模型向小模型的能力迁移。作者在最后的讨论中自己把性能来源归纳为四点：更好的 training recipe 与 regularization、更大的模型、更大的数据集，以及利用 ViT-g 蒸馏小模型；同时作者认为 object parts 和 scene geometry 等能力已经在这种大规模 SSL 中自然出现，并预期随着模型与数据继续扩大，还可能产生更多 emergent properties。

如果把这篇文章与你之前看的 CLIP 放在同一条脉络下，二者实际上代表两种不同的视觉基础模型思路。CLIP通过 image-text alignment 让视觉 feature 主动靠近语言语义空间，因此非常适合 zero-shot recognition 和视觉语言任务；DINOv2则刻意完全去掉文本，只要求模型从图像自身学习稳定而丰富的 representation，因此尤其强调 patch-level structure、object parts 和 geometry。DINOv2并不能因为自身的训练方式直接理解自然语言，但它证明了一件对后来的 VLM 很重要的事情：视觉 encoder 本身可以在进入语言模型之前，就已经提供质量非常高、包含局部结构和几何信息的 visual tokens。事实上作者在文章最后也明确提出，未来希望构建能够“像处理 word tokens 一样处理这些 visual features”的 language-enabled AI system。

所以，如果把整篇 DINOv2 压缩成一条最核心的逻辑，它就是：

$$
\boxed{
\text{高质量大规模纯图像数据}
+
\text{DINO 的 global SSL}
+
\text{iBOT 的 patch-level SSL}
+
\text{稳定与高效的规模化训练}
\rightarrow
\text{通用视觉 foundation features}
}
$$

这篇论文真正重要的地方，也正是在“feature”二字。它不是为了直接输出分类、分割或者深度，而是希望训练出一个可以被冻结、然后被各种不同下游模型直接读取的通用视觉表征。对于后续阅读 VLM、VLN 或机器人视觉来说，尤其值得记住的是 DINOv2 的 patch token：为什么它在没有 segmentation、depth、part annotation 的情况下仍然包含如此丰富的空间结构，以及 DINO 的 global objective 和 iBOT 的 local objective 是怎样共同促成这种性质的。这两个问题基本就是理解 DINOv2方法层面的主线。
