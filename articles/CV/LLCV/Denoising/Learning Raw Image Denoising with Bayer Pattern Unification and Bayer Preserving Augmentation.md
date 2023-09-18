# Learning Raw Image Denoising with Bayer Pattern Unification and Bayer Preserving Augmentation  

2021/7/14  

来源：NTIRE19 & CVPRW19  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/CV/Denoising/Learning%20Raw%20Image%20Denoising%20with%20Bayer%20Pattern%20U.pdf)的包括ipad标注的pdf版本。  
作者是旷视的Jiaming Liu, Chi-Hao Wu, Yuzhi Wang, Qin Xu, Yuqian Zhou, Haibin Huang,
Chuan Wang, Shaofan Cai, Yifan Ding, Haoqiang Fan 和 Jue Wang，这篇文章是NTIRE19 Real Image Denoising Challenge （某个track）的champion，当时达到了SIDD上的sota性能。  

**Summary**：提出了统一四种不同Bayer Pattern的方法与相应的数据增强方法，分别是对Bayer Pattern进行crop，和翻转之后进行crop，以实现扩充数据集（同时也不必每个Bayer Pattern训练一个model）。文章使用的网络架构还是普通修改过的U-Net，所以主要的贡献就在于Bayer Pattern Unification和Bayer Preserving Augmentation。  

**rating：3.5/5.0**  
**comprehension：3.5/5.0**  

文章的贡献有：  
* 提出了Bayer Pattern Unification和Bayer Preserving Augmentation的方法，扩充数据集。  

## 1 Introduction    
**出发点**：Pack-Reorder-Unpack 统一模式和Naive Augmentation对性能有害：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202107140004.png)  


Raw Image的相关知识：Raw images是从sensor里直接读出来的数据，这些数据按照camera filter arrays安排成不同的模式，比如Bayer Pattern。这些数字信号进一步经过pipeline后处理，进行镜头阴影校正、白平衡、去马赛克、伽马校正等处理获得RGB图像。  

**一个论点**：原始数据中的噪声在经过pipeline的时候会被扭曲，后续就更难处理了，所以**最好直接在原始数据域上处理数据**。  

## 3 Proposed Method  
### 3.1 Bayer Pattern Unification (BayerUnify)  
为了用单个CNN对不同Bayer Pattern的model进行去噪，需要注意以下两点：  
* 统一通道的顺序（align the order of the channels）  
* 要维持不同通道中邻接像素之间的结构信息（the structural information laid in adjacent pixels from different channels has to be maintained）  

在训练阶段的统一方法是crop：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202107140001.png)  

~~但是是不是需要注意切完之后的raw image需要保持一定的尺寸？比如要求能pack起来~~  
↑这是显然的吧，如果不能pack那就不算成为另一种Bayer Pattern了吧。  

测试阶段由于需要保证输入输出图像尺寸一致，所以在crop前需要对raw image进行填充，通过边缘对称镜像填充保证每个像素来自正确的通道：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202107140002.png)  

### 3.2 Bayer Preserving Augmentation (BayerAug)  
增强方法也是crop：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202107140003.png)  

* 由于转置(transposition)会让$$C_1C_2C_3C_4$$变成$$C_1C_3C_2C_4$$，这对RGGB和BGGR影响不大（认为Gr和Gb区别不大），所以可以直接对这两类Bayer Pattern进行转置，但是不能直接转GRBG和GBRG（没说该怎么处理）。  

* 在crop成不同大小的patch时需要注意保持crop前后的Bayer Pattern一致，因此切的时候按偶数切。  

## 4 Experiment  
一些细节：  
* 输出是4通道feature map，再unpack回raw image。  
* L1 Loss  
* 用了model ensemble，对每个category训一个模型出来，根据metadata选择对应的model。  


