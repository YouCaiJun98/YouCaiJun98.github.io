# Deep Learning for Image Super-resolution: A Survey  

2021/9/6  

来源：TPAMI19  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/CV/SuperResolution/Deep%20Learning%20for%20Image%20Super-resolution_%20A%20Surve.pdf)的包括ipad标注的pdf版本。  
作者是SCUT/SMU的Zhihao Wang, Jian Chen, Steven C.H. Hoi等人，能在PAMI上发survey，绝了。      

**Summary**：一篇水平不错的survey，值得参考。将SR分成有监督、无监督、领域相关的SR，按照SR model的组件对模型进行了模块化并逐个survey，有点用。    

**Rating: 4.0/5.0**  
**Comprehension: 3.7/5.0**  

一张图总结文章：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109060001.png)  

## 1 Introduction  
* 传统的SR方法包括prediction-based, edge-based, statistical, patch-based, sparse
representation方法。  

## 2 Problem Setting and Terminology  
### 2.1 Problem Definitions  
通常来讲，LR图像是从高分辨率图像降采样得到的：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109060002.png)  

D是降采样映射函数，I_y是对应的HR图像，\delta是降采样过程的参数（比如scaling factor或者噪声），如果降采样过程不知道，那么就叫做盲SR(blind SR)。重建过程可以表示为：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109060003.png)  

如果不考虑降采样过程中的compression artifacts, anisotropic degradations, sensor noise and speckle noise等因素的话，降采样过程可以简单用降采样表述（SR问题一般都是用这种降采样描述，且常见的降采样方法是bicubic）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109060004.png)  

比较花哨的降采样过程可以用多个过程复合表示：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109060005.png)  

前面的卷积是blur kernel和HR图像卷积，后面的噪声是AWGN，这个描述更贴近于真实图片的情形。  

SR的**目标**（最常见的loss函数是pixel-wise mean squared error）是：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109060006.png)  

### 2.2 Datasets for Super-resolution  
抄表格就行了吧：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/2021090600007.png)  

### 2.3 Image Quality Assessment  
IQA可以分成三类(不是很关心，整理粗疏)：  
* **full-reference methods** performing assessment using reference images  
    * PSNR  
    * SSIM  
    * Mean Opinion Score  
    * Task-based Evaluation(虽然放在这里不是很合适)  
    * MS-SSIM  
* **reduced-reference methods** based on comparisons of extracted features  
比如学个CNN出来提取feature这样  
    * Learning-based Perceptual Quality  
* **no-reference methods(blind IQA)**  

### 2.4 Operating Channels  
RGB & YCrCb  

### 2.5 Super-resolution Challenges  
NTIRE Challenge & PIRM Challenge  

## 3 Supervised Super-Resolution  
这节主要讲监督学习的SR，分成四个组成部分：**model framework**(区分在哪upsample)、**upsampling methods**(插值还是学习的等等)、**network design**(residual或者recursive等局部设计)、**learning strategies**(分阶段学习等等)。  

### 3.1 Super-resolution Frameworks  
分成下面四种：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109060008.png)  

* **Pre-upsampling Super-resolution**  
这类结构在最前面把LR图像升采样到需要的尺寸，再用CNN重建高质量细节。  
    * 缺点是经常有副作用(e.g., noise amplification and blurring)，而且在大尺寸空间下操作，速度很慢；一个scale需要重训一个模型。  
* **Post-upsampling Super-resolution**  
    * 计算效率高。  
    * 缺点是，一步就升采样到需要的尺寸对large scale的情况比较困难，且每个scale需要重新训练一个模型；模型设计复杂，训练稳定性差，需要fancy的训练策略和模型指导。  
* **Progressive Upsampling Super-resolution**  
    * 有种individual heads的方法，可以有好几个输出接口？  
    * 有点分解的感觉（把一个large scale分解成多个小scale的串联），降低了训练难度，且对multi-scale SR友好，减少了时间空间开销。  
* **Iterative Up-and-down Sampling Super-resolution**  
    * 可以更好地捕捉LR-HR图片对之间的相互依赖关系。  
    * 又名back-projection，`iteratively apply back-projection refinement, i.e., computing the reconstruction error then fusing it back to tune the HR image intensity`  
    * 缺点是设计标准(design criteria)不清楚。  

### 3.2 Upsampling Methods  
* **Interpolation-based Upsampling**  
插值类的方法基于元素图像信号，不能带来额外信息，而且还有些副作用，比如计算复杂度、噪声放大、结果模糊。目前的趋势是用基于学习的方法取代差值方法。  
    * Nearest-neighbor Interpolation： fast  
    * Bilinear Interpolation：better than last one, relatively fast  
    * Bicubic Interpolation：smoother results with fewer artifacts but much lower speed, 抗锯齿(anti-aliasing)BCI是创建SR数据集的主流方法。  
* **Learning-based Upsampling**  
    * Transposed Convolution Layer  
    反卷积 - 插零再卷积。可能在各轴上造成uneven overlapping效应；可能造成checkerboard-like pattern。    
    * Sub-pixel Layer  
    扩大通道数再reshape。  
        * 感受野更大，可以提供更多contextual information。  
        * 感受野分布不均匀，`blocky regions actually share the same receptive field, it may result in some artifacts near the boundaries of different
        blocks`  
        * `independently predicting adjacent pixels in a blocky region may cause unsmooth outputs`  
    * Meta Upscale Module  
        * 过程过于抽象,描述见原文。大意是对于HR中的一个patch，将它投影到LR中对应的一个区域，并**predicts convolution weights according to the projection offsets and the scaling factor by dense layers and perform convolution**  
        * 性能和固定的factor一样甚至更高；  
        * 虽然需要预测weight，但是在inference的时候占用的时间其实很少；  
        * `this method predicts a large number of convolution weights for each target pixel based on several values independent of the image contents, so the prediction result may be unstable and less efficient when faced with larger magnifications`  

### 3.3 Network Design  
结构可以用下图来表示：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109060009.png)  

* **Residual Learning**  
    * Global Residual Learning：只学LR和HR之间的差距，只需要学出来一张residual map，里面包含upsampled LR与HR图像的区别，即高频细节，和我们对去噪任务的认知非常接近。  
    * Local Residual Learning：类似ResNet的结构。  
* **Recursive Learning**  
    * 可以减少参数的引入，就是不断复用某个计算块。但是不能避免高计算开销，且会带来梯度消失或者爆炸现象。    
    * 可以在不同地方用不同的循环模块。可以和residual learning和多监督方法配合使用。  
* **Multi-path Learning**  
使用不同的路径处理特征，再把它们合起来以改善模型的性能。下面的分类感觉就是整体上的不同路径和module内的不同路径。    
    * Global Multi-path Learning  
    * Local Multi-path Learning  
    * Scale-specific Multi-path Learning：特殊一点，复用一部分（比如特征提取），又分路一部分。  
* **Dense Connections**  
每个层将之前各层的输出作为输入，当前层的输出作为后面各层的输入。  
    * 缓解梯度消失，增强信号传播，鼓励特征重用以丰富信息，减小模型尺寸；  
* **Attention Mechanism**  
    * Channel Attention：关注通道间的交互，channel-wise scaling factors  
    * Non-local Attention： distant objects or textures  
* **Advanced Convolution**  
    * Dilated Convolution：large receptive field for better contextual information  
    * Group Convolution：减少参数数和运算数    
    * Depthwise Separable Convolution：减少参数数和运算数  
* **Region-recursive Learning**  
有点抽象，大概是循环捕捉pixel之间的依赖关系，比如“pixel-by-pixel generation”  
    * better performance, yet higher  computational cost and training difficulty
* **Pyramid Pooling**  
更好地利用全局和局部上下文信息。将h x w x c的特征图分成M x M个bin，进行max pooling变成M x M x c的输出，接着用1 x 1的conv把输出进一步压缩成单通道的输出，再用双线性插值上采样成原来的尺寸。通过使用不同的M来利用不同程度的上下文信息。    
* **Wavelet Transformation**  
可以减小模型体积和计算开销，但是保持性能。  
* **Desubpixel**  
subpixel的反过程，在通道数更多但是尺寸更小的特征图上进行操作，提高推理速度和性能。  
* **xUnit**  
又是奇怪的module，不关心好吧。combine spatial feature processing and nonlinear activations -> learning a spatial activation function   
虽然很难算，但是性能很好，所以trade off之后模型反而可以更小？  

### 3.4 Learning Strategies  
* **Loss Functions**  
早期常用L2 Loss，但是不能很好测量重建质量。  
    * Pixel Loss - L1 loss与L2 loss，经典：  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109070001.png)  

    一种特殊的Pixel Loss - Charbonnier loss，其实就是L1加一个数值稳定项：

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109070002.png)  

    pixel loss在像素值上限制了HR和LR图像接近，相比之下，L2 loss对大误差惩罚更大，但是对小误差较为容忍，通常会导致过度平滑的结果，实践中L1 loss的性能一般更好，且收敛更快。Pixel loss的总体问题在于不能描述图像质量，结果通常缺乏高频信息，质地过于平滑，感官接收质量不佳。  
    * Content Loss  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109070003.png)
    
    用一个预训练的图像（如ResNet、VGG）分类网络来区分不同图像之间的语义信息。鼓励SR图像与HR图像感官相似。  
    * Texture Loss - a.k.a. style reconstruction loss  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109070004.png)  

    考虑到SR图像应该和HR图像有相似的风格(e.g., colors, textures, contrast)，因此提出了这种loss。不同特征通道的相关性用G来衡量，定义为Gram矩阵（总之就是通过某种方法算出来对应通道的相似程度这种？~~但是感觉作用范围应该是patch才符合描述哎~~）  
    据说可以产生`much more realistic textures and produces visually more satisfactory results`，但是patch size的影响很大，太小会在textured region产生伪影，大的patch会在整个图像上产生伪影。  
    * Adversarial Loss  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109070005.png)  

    GAN对应的loss，下面的loss是对上式的改进，基于least square error可以稳定训练过程，改善质量。  
    另外还有GAN loss + Feature loss的例子。  
    判决器可以抽取出HR图像中难以学习的隐pattern并促使生成器学习。  
    虽然但是，GAN的训练仍然很困难，而且不稳定。  
    * Cycle Consistency Loss  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109070006.png)  

    要求LR-HR-LR'得到的LR'与LR一致。可以和分阶段训练结合在一起，额外要求HR图像一致。  
    * Total Variation Loss  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109070007.png)  
    要求邻居pixel接近，可以增强空间平滑性。  
    * Prior-Based Loss  
    引入外部先验知识，和domain-specific的SR关系紧密。  
* **Batch Normalization**  
BN虽然可以通过重塑数据的分布加速并稳定训练过程，但是BN会损失图像的尺度信息`scale info`，破坏网络的范围灵活性`gets rid of range flexibility from networks`  
* **Curriculum Learning**  
    * 本质上是**分阶段的训练**，要么是先训个2 x scale的再在后面挂载更高尺度的部分，要么是单独训三个submodel再把它们merge起来finetune。
    * 减少了训练难度，缩短了训练时长，尤其是对大factor而言。    
* **Multi-supervision**  
    * 在模型中插入多个监督（我理解是在2x、4x、8x的地方都输出图片要求对齐？）的loss term，增强梯度传播避免梯度消失或者爆炸。  
### 3.5 Other Improvements  
* **Context-wise Network Fusion**  
    * 本质上是ensemble  
* **Data Augmentation**  
    * 除了传统的cropping, flipping, scaling, rotation, color jittering，连`randomly shuffle RGB channels`也能起到增强数据，避免由于数据集色彩不均衡导致的color bias的作用。  
* **Multi-task Learning**  
    * 简单地说就是SR + high level task or SR + denoise  
* **Network Interpolation**  
    * PSNR-based net + GAN-based net这样，但是**令人困扰**的是怎么把这两个网络参数fuse到一起。  
* **Self-Ensemble**  
    * 看起来**很有道理**的方法，将原图旋转0/90/180/270度，再水平翻转，生成的8张图片一起输入模型，对输出结果求平均或中值，感觉很有道理。  

### 3.6 State-of-the-art Super-resolution Models  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109070008.png)  

## 4 Unsupervised SR  
前面介绍的SR都是监督学习的SR，通过HR-LR图像对来学，这很容易学成downsample的逆变换，对真实图像超分结果不好（而现实中很难采出来尺寸不一样的统一幅图），下面介绍了非监督或者弱监督的SR：  
### 4.1 Zero-shot Super-resolution  
* 又是很诡异的方法，在**测试**时训练一个image-specific的SR网络，具体而言是用nonparametric blind super-resolution的方法从单张图像中估计出来一个degradation kernel，并使用这个kernel对这张图像进行`degradation with different scaling factors and augmentation`构成一个数据集，用这个数据集训练一个小型CNN SR并最后预测。  
* 在接近真实SR的情况下性能会好，在理想条件SR下也还行，但是每次inference都要训一个模型，效率很低。  
### 4.2 Weakly-supervised Super-resolution  
弱监督也是为了尽可能接近真实世界SR，但是他们采用学习HR-LR变换并用它构建数据集的方法。~~讲道理，这样就不会学到反变换了？~~  
* Learned Degradation  
    * 这里描述不清楚（**疑似有误**），先说使用unpaired LR-HR图像训练，但是在训HR-LR过程的时候要求生成的LR和**真实的LR**图像接近且分布一样的degradation，哪里有真实LR图像？有真实的LR-HR pair还需要训练？而且不是说unpair吗？  
    * 大意就是训练HR-LR和LR-HR两个过程，可能还要求对齐生成的分布。  
* Cycle-in-cycle Super-resolution  
    * 将LR/HR图像视为两个域，变到对面的域要求分布一致，再变回来。  
    * 在harsh condition下性能还可以，但是训练困难、不稳定（GAN的锅）。  
### 4.3 Deep Image Prior  
（**没太看懂在干什么**）  
* DL+手工设计的先验（例如CNN结构，这里说CNN结构可以提取底层图像特征，于是就直接随机初始化一个小CNN出来？讲得很不清楚）or self-similarity  
## 5 Domain-specific Applications  
* Depth Map Super-resolution：深度地图  
* Face Image Super-resolution/face hallucination  
* Hyperspectral Image Super-resolution  
* Real-world Image Super-resolution  
* Video Super-resolution  

## 6 Conclusion and Future Directions  
不关心，有需要再回来看吧。  
