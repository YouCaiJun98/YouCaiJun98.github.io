# Learning to See in the Dark  

2021/7/14  

来源：CVPR18  
Resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/BNN/ABC-net.pdf)的包括ipad标注的pdf版本。  
作者是UIUC的Chen Chen和Intel的Qifeng Chen, Jia Xu, Vladlen Koltun。  

**Summary**：这篇文章给出了低光照条件下快速摄像的SID数据集，分成Sony和Fuji两个subset，由一串曝光时间不等的照片和长曝光时间的ground truth构成，并且文章提出的U-Net variation作为取代传统pipeline的原始数据处理管道就已经取得了非常接近现在Sota的性能。        

**rating：4.3/5.0**  
**comprehension：3.8/5.0**  

文章的贡献有：  
* 提出了一个低光环境下的数据集SID，由两款相机采集得到，分为Sony和Fuji两个Subset，由一串曝光时间不等的照片和长曝光时间的ground truth构成；  
* 文中给出的U-Net结构已经非常接近Sota性能，PSNR报告为28.88（SOTA ~ 29.6）。   

## Abstract  
* 低光照短曝光时间的图片有噪声，长曝光时间的图片则blur且impractical。  

## 1 Introduction  
一些豆知识：  
* 高ISO会提升亮度(brightness)，但是也会放大噪声；  
* 后处理(postprocessing)不能解决低信噪比的问题，由于“低光子计数”（low photon counts）；  
* 物理方法来提升SNR（比如增大光圈，眼长曝光时间）也有自己的问题。  

## 2 Related Works  
* 以往工作的一些问题：  
    * 在某种等级的噪声下训练的模型，也就只能针对该等级噪声；  
    * 采用的数据都是合成数据，在图片上施加人工噪声；  
* multiple-image denoising： a burst of images  
* 低光增强的传统方法（但是这些方法都假定了原始低光图像能充分反映场景信息）：  
    * 直方图均衡(histogram equalization)：平衡整张图像的直方图；  
    * 伽马校正(gamma correction)：增强暗区域的亮度，压缩暗的像素；  
    * the inverse dark channel prior  
    * the wavelet transform  
    * illumination map estimation  
* 噪声图片数据集：  
    * RENOIR：成对的图片有空间上的misalignment；  
    * Bursts of images：缺少GT；  
    * Google HDR+：没有低光图片；  
    * Darmstadt Noise Dataset (DND)：也没有低光图片。  

## 3 See-in-the-Dark Dataset  
可以看眼介绍。  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202107140005.png)  

## 4 Method  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202107140006.png)  

pipeline对比：  
* 传统pipeline包括white balance, demosaicing, denoising, sharpening, color space conversion, gamma correction, and others  
* L3(local, linear, and learned) pipeline用来近似复杂的非线性pipeline  
* burst imaging pipeline可以处理系列图片，但是比较复杂，因为有用lucky imaging所以难以处理视频。  

输入数据为Bayer Raw Pattern，处理之前先把图像pack起来，这样分辨率就成了原来的1/2，减去原来的black level（这里不清楚，我理解为减去某个均值之类的？），再乘以放大系数，这里的放大系数是短曝光时间和长曝光时间的倍数，再通过U-Net，处理之后的图像成为了RGB图像（也就是取名pipeline的原因）。  
* residual block在这里不太好使，因为输入数据和输出图像的域不一样。  
* 放大系数需要外部输入（在训练和测试时都需要，~~我记得在哪看到过测试时不需要来着？~~那个说的是盲去噪，但还是需要输入放大系数？所以我对盲去噪的理解可能有点问题...这不是告诉了noise level了？），这是个drawback。  
* crop成512*512的patch再进行数据增强。  
* L1 Loss。  

## 5 Experiments  
### 5.2 Controlled experiments  
这个对比感觉还有点用的：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202107140007.png)  

* U-Net结构挺好；  
* 在Raw域开始处理很重要；  
* L1 Loss也挺好；  
* 直接pack就行；  
* 学不会histogram stretching。  

## 6 Discussion  
作者提出这篇文章的一些问题：  
* 没有解决HDR tone mapping问题（过曝？）  
* 放大系数必须要外部选择；  
* 计算时间较长；  
* 低光图像去噪网络的泛化性（不同CFA）；  
* 数据集不含运动物体和人。
