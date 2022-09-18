# 2022/8/27 LLCV talk总结  

2022/8/27  

## Summary  
1. Talk分成五个议题，分别是：  
    * Transformer是LLCV未来发展的趋势吗？  
    * 实验室技术在实际生产中效果并不好，该怎么解决？  
        * 进一步的，这个问题主要是讨论合成数据和真实case不匹配的情形  
    * 如何看待LLCV研究目前进入定式化状态，还有什么高价值的研究内容？  
        * 就是指LLCV发展陷入刷榜打点的陷阱  
    * LLCV有什么区别于其他任务的特点、难点？  
    * LLCV发文技巧；趣事分享。  

2. 议题讨论与结论  
    1. （**与我们的研究兴趣无关**）Transformer议题请到了LLCV第一个A+B文章SwinIR的作者，除了他以外的嘉宾都暗示transformer只是一个新的A+B方式，难堪大用（除了一些minor的改进，似乎不能支撑领域进一步发展）；细节可看讨论记录。  
    2. （**与我们的研究方向无关**）实验室结果和实际结果不能匹配的原因来自①合成数据和真实数据特性背离严重；②模型overfitting到特定数据集；
        * 有三条解决思路（**完全含于我们目前的认知**）：  
            * 做unsupervision；（效果不好，前两年火过现已式微，或者改做semi-supervision）  
            * 采集paired数据（成本太高；工业界最主流的做法）；  
            * 真实degradation过程建模 + 合成数据（sxs：困难，目前已有很多尝试，似可继续做）；  
        * 工业界最主流的LLCV解决方案还是暴力采数据；数据相比模型是LLCV领域更核心的要素；  
    3. LLCV领域**确实饱和了**（所以会有很多定式化的工作）；
        * 可做基于数学物理prior + DL研究的工作，寻找LLCV领域的first principle（sxs：一直有人在做，但是不温不火；和传统方法的结合确实是继续发展的方向）；  
        * DL-LLCV领域的进步基本靠搬运high-level的工作，应该从LLCV任务特性出发；（sxs：正确但无用）
        * 近期发文密码是diffusion；  
    4. **最重要的议题，因为时间跳过了，进入发文经验分享环节了** 
    5. 分享了一些AI领域发文共性问题。  

3. 结论：没有收获；讨论的预设问题与我们的关心的不重合，比如高效性问题没有纳入讨论，弹幕里多次申请互动未果；感觉LLCV领域taste可能不怎么好；嘉宾似乎有所保留；

一、LLCV里transformer是未来发展的趋势吗
* jinyun liang：  
    * transformer是一种新的backbone；动态感受野（感受野大，LLCV里感受野大对性能好）；  
    * transformer理论计算量小，但是测试/训练速度慢；（因为实现的问题？小op和投影等）；  
    * Conv的进展停滞很久了；18年的RCNN已经很好了；transformer比RCNN明显要好；  
    * transformer可以提供一个数据集上的upperbound（我反对）；
    * 需要进一步研究怎么变小、部署；  
    * transformer可以提供可解释性的窗口（不同意）；  

* jinjin liang：  
    * 不同意transformer是未来方向；  

* ruicheng feng：  
    * local-attention 和 transformer的区别是什么？是设计成熟（传统non-local）吗？还是有本质区别？  

* jinyun liang：  
    * transformer的思想和non-local很像（算patch和周围background的相似度等），可能只是实现上有些区别；  

* jinjin liang：  
    * SwinIR里每个token是像素，在LLCV里很成熟，在high-level task里不行；  
    * 像素token计算量大，但是更准（不丢失信息）；  
    * denoise和deblur可以用U-Net类的架构降采样降低计算量（但是SR不行） -> 一个新知识；

* yihao liu：  
    * （LLCV里CNN+Transformer很重要，没法剔除CNN）LLCV里在transformer前后都要插入Conv（似乎和提取处理输入输出有关），没有这种Conv层性能下降很严重；  
    * transformer对不同任务有倾向性；dehaze上效果不行；transformer的结构设计对任务也有倾向性（不就是说不同结构效果不一样吗。。）；  
    * LLCV transformer的pretrain可以研究（目前已经有文章了）；  

* jinjin liang：  
    * transformer废卡，提高门槛；  

* yihao liu：  
    * 要加速，去除冗余；  

* jinyun liang：  
    * （一个有效信息）小模型有效那么大模型也会更强；  
    * 可用小模型做surrogate；  
    * yihao liu：
        * 有一些case不行；模型增大后小模型上有效的module大模型上可能就不好了（。。。）；

* ruicheng feng：
    * 讲了mobile的故事（transformer的高效性）；  

* jinjin liang：  
    * 大的CNN都不容易在mobile上跑，更不必说transformer； 
    * 高通6系soc上没优化的CNN跑LLCV任务跑个几十秒没问题（LLCV模型高效性很差）；

二、实验室技术在真实场景下效果并不好，怎么能解决落地问题？  
问题细化：仿真数据上性能好的方法可迁移性不好。  

* jinyun liang：  
    * unsupervised；
        * jinjin gu：
            * unsupervised最近研究变少了；效果也不行；    
        * ruicheng feng：  
            * degradation -> restoration的循环，artifacts多，不符合LLCV的要求，但是可以做style transfer；  
    * 收集配对LR-HR图像（和相机有关，也很不好对齐）；  
        * jinjin gu：  
            * huawei 计算光学；建模模组（每个元件的畸变都不一样，且每个个体都不一样），开销很大； -> 工业界喜欢暴力出奇迹？  
            * 数据采集的方法很boring，流水线；各个公司比性能还都是在比数据收集；数据才是核心，壁垒；    
            * 过于依赖数据反而说明学术界不行（同意，做了个寂寞）；  
    * 真实退化模型（从头到尾的噪声建模）；  

* yihao liu：  
    * 原因：domain迁移特征不匹配；overfitting；  
    * 成本问题（为各个组件建模等）；  
        * 解决方法1：合成数据需要了解退化特征（精确噪声建模）；  
            * 问题：没法精准建模，因素太多；  
        * 解决方法2：采集paired数据集；  
            * 问题：采集代价也很大，时间成本也很高；老电影复原等任务没法采用这种方法（特殊任务下label不好收集）  
    * unsupervised：  
        * （类似半监督）可与采集的方法结合，扩展数据；减少收集成本；  

* ruicheng feng：  
    * 有些问题没法用数学建模；（iphone上的鬼影 -> flare？）多次折射等（随机性、入射角度等）； -> 只能数据驱动；  


三、如何看待底层视觉研究进入定式化状态，还有什么高研究价值的问题？  
问题分析：现在的工作都是在任务上打点，很无聊。  

* jingyun liang：  
    * 有好有坏，很无聊，但是比较起来规范。  

* yihao liu：  
    * LLCV里一般都是把high-level的东西拿过来用；-> 数学方法建模+DL；
    * 目前饱和了。  

* ruihao liu：  
    * 下一波论文密码是diffusion。  

* haitao mao：  
    * 找物理中的first principle，做DL+physical modeling。  

四、LLCV独特于其他领域的难点是什么？
时间不够了，跳到第五个问题了。
？？？这么关键的问题能跳过的？直接跳到发文章是吧？  


五、怎么发LLCV论文？  
* yihao liu：  
    * 换着benchmark刷点（A不行了去刷B）；  
    * 做LLCV可解释性；  
    * 做IQA；  

* jinjin gu：
    * 论文不能露怯；  
    * 拒稿常用理由：  
        * novelty；  
        * 多来点数学包装（不能太简单，也不能太复杂）；  

* ruicheng feng：  
    * 多编些故事，来点knowledge。  

