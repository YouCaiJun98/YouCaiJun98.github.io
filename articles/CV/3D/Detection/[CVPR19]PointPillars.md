# PointPillars: Fast Encoders for Object Detection from Point Clouds  

2023/9/18  

来源：CVPR19  
resource：[github上备份](https://github.com/YouCaiJun98/MyLibrary/blob/main/articles/CV/3D/Detection/%5BCVPR19%5DPointPillars.pdf)的包括ipad标注的pdf版本。  
作者是nuTonomy公司的Alex H. Lang, Sourabh Vora, Holger Caesar, Lubing Zhou, Jiong Yang, Oscar Beijbom。（这个公司是MIT的科技初创公司，13年就开始做DL了，16年被Delphi Automotive买了）

**Summary**：一篇很不错的经典文章，提了Lidar点云的一种编码方式（pillar）+ 一个backbone，实现了E2E且仅依赖于Conv2D的3D检测，并且取得了显著好的性能与效果：  

* 设计了一种Lidar点云的编码方式（pillar, point clouds organized in vertical columns）；  
* 设计了一种3D检测backbone，利用learning-based encoder可以实现端到端的检测，任务效果与推理性能都显著优于此前的工作。  

**Key words**:  
* 3D Detection  


**Rating**: 5.0/5.0 很不错，很经典的一篇3D检测的文章，内容很详实，主打一手开诚布公；无论是文章写作还是内容本身都非常优秀，今年以来读过最舒服的文章（其实是今年没怎么读文献！）。  
**Comprehension**: 3.0/5.0 第一次读3D相关的文章，一头雾水。。！不懂的东西太多了，还要再摸摸。  

来一张Teaser大图（虽然够呛用来总结全文）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230918222347.png)  


## 1. Introduction  
* 一些比较零碎的背景知识：  
    * Lidar是自动驾驶中最重要的传感器之一，用一个laser scanner来测距生成稀疏点云；  
    * 传统的robotic bottom-up pipeline是这么处理点云的，先做背景剪除，再做时空聚类（spatiotemporal clustering）和分类；  
    * 图片和Lidar是3D检测中的两种常见模态，它们的区别是：
        1. 点云是一种稀疏表示，而图片是一种dense表示；  
        2. 点云是3D的，图片是2D的；  
    * 传统的（19年及以前的）3D检测的思路是，用3D卷积（一个显著的劣势是**慢**）或者把点云映射到2D图像上；PointPillar同期的工作倾向于用Lidar点云的BEV视图（这个方法有两个好处，其一，BEV可以保持物体的尺度，scale；其次，BEV上作用的Conv2d可以保持"local range information"）；  
        * 但是，BEV的缺点是，这个视图也非常稀疏，计算效率不高 -> 一个workaround是，按照平面切分成若干格点，再做hand-craft encoding；（所以pillar+NN就是所谓的编码方案吗，区别于手工设计的某种计算规则？）    
      
* 给出了pillar编码方案的几个优点：  
    * pillar的编码是基于学习的（意思是后面跟着learnable encoder？），比手工设计的固定编码方案更能充分利用点云信息；  
    * 用pillar而不是voxel就不用手动调垂直方向的binning了；  
    * 处理得很快；  
    * 不需要手工调不同的点云配置（requires no hand-tuning to use different point cloud configurations such as multiple lidar scans or even radar point clouds）；  

* 一些RW相关内容：  
    * 2D CV中的检测可以分成2-stage和1-stage的；  
    * 3D CV中的检测：  
        * 早期的工作base on 3D Conv，这种卷积非常慢；  
        * PointPillar同期的工作往往将点云映射到ground plane（我理解就是BEV试图）或者image plane；  
            * 一个主流范式（voxelization）是，将点云组织成voxel，并将每个vertical column中的voxel编码成定长、手工设计的特征编码，来形成一个pseudo image，再用2D检测backbone处理；  

## 2. PointPillars Network  

PointPillar接受点云作为输入，输出**oriented 3D boxes**作为汽车、行人和骑自行车的检测结果，包括三个部分，（1）特征编码器（feature encoder），将点云编码成稀疏pseudo image；（2）2D卷积backbone，处理伪图生成高级表示；（3）解码器，检测并回归出3D boxes：

### 2.1 Pointcloud to Pseudo-Image  
**<font color='red'> PointPillar最关键的设计。 </font>** 计点云中的一个点为$l$，它有三个坐标$x$, $y$, $z$，  
* 第一步是在x-y平面均匀划分出grid，类似于voxel，区别是在z轴上的空间是无限的，也就不需要靠超参数控制z轴上的bin；Pillar的个数为$\mathcal{P}=B$；  
* 接着对每个Pillar中的点做增强（augmentation，这里也叫**decorate**），给每个点增加6个新的维度$r$, $x_c$, $y_c$, $z_c$, $x_p$, $y_p$：  
    * $r$是reflectance；  
    * $c$下标是到每个pillar的算术平均点的距离；  
    * $p$下标是指到pillar中心$x$, $y$的偏移量；  
* 这里是对Lidar点云点做的装饰，radar or RGB-D中的点也可做类似的处理；  
* 这么处理出的pillar绝大多数是稀疏的，一个典型的数字是97%的稀疏度（~~这里的稀疏度是指？相比最满的pillar，稀疏的pillar只有3%的点，还是97%的pillar是空的？~~ -> 看起来是指空pillar）；为此，可以限制每个样本中的非空pillar数（P）和每个pillar中的点数（N），来形成一个紧致的tensor (D, P, N)；  
    * 如果一个pillar里的点太多就sample，如果太少就填零；  
* 第四步，用一个简化的PointNet（说是Linear+BN+ReLU）**处理每一个点**，生成一个(C, P, N)维度的tensor（看起来就是D个维度的信息抽成C个通道），然后在N维度做个max操作，生成一个(C, P)维度的tensor（*给N干没了还行，每个pillar里的点这么不重要吗？还有，是在C维度上取最值吗，那每个通道的最值取完不是同一个点怎么办？*）；  
* 最后，把处理后的点填回原来的位置，形成一张(C, H, W)维度的pseudo image。  

### 2.2 Backbone  
采用了U-Net架构的backbone，读文章的时候要注意，**文中的$S$是指图像的“画幅”**（resolution的意思）。  

### 2.3 Detection Head  
用了SSD作为3D检测头。用2D IoU做priorbox和GT的匹配。  
* （*尚且不懂的细节*） Bounding box height and elevation were not used for matching; instead given a 2D match, the height and elevation become additional regression targets.  

## 3. Implementation Details  
**超级多的实现细节，令人叹为观止！**  
### 3.1. Network  
一些不是很重要的参数，直接就看代码就好；需要注意的是，PointPillar分成两个网络，一个负责car的检测，一个负责pedestrian/cyclist的检测，两者设置略有不同；  

### 3.2. Loss  
非常复杂，我的建议是我别手抄了，直接上图吧（看代码的时候好好对照下吧。。。）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230918235657.png)  

* 一些已经想明白的点：  
    * $\theta$是指box的角度（可能是角坐标系，有个朝向，那么flipped是指车头的朝向）；  
    * 那一坨&\delta&是做的放缩，应该是按照惯例，可能是直接回归想要的数比较困难吧，所以要做点编解码；  

## 4. Experimental setup  
连这里也有很多的细节！  

### 4.1. Dataset  

### 4.2. Settings  

### 4.3. Data Augmentation  


