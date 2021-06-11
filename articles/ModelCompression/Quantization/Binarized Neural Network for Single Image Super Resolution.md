# Binarized Neural Network for Single Image Super Resolution  

2021/6/10  

来源：ECCV2020
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/Quantization/Binarized%20Neural%20Network%20for%20Single%20Image%20Super%20Resolution.pdf)的包括ipad标注的pdf版本。  
作者是西电的Jingwei Xin, Nannan Wang, Xinrui Jiang, Jie Li, Heng Huang, Xinbo Gao等人，不认识呢。      

**Summary**：第一篇把BNN的概念引入SR的文章（灌水？），具体不好判断怎么样。文章提出了一种BAM(bit-accumulation mechanism)算法，将不同层的weights和activations分别加权加在一起，通过BN再取sign作为量化的weights和activations（见鬼了，这能work？也没解释这么做的动机啊？）。这种BAM方法似乎可以直接去改SR的一些baseline。这篇文章还提出了一种SR model building block，这种block搭出来的网络比直接BAM一些baseline效果更好些。总之读起来是一篇抢坑的水文（~~更别说文中还有"ass"这种拼写错误了，怎么回事~~）    

**Rating: 3.0/5.0**  
**Comprehension: 4.0/5.0**  

## 1 Introdution  
有一些关于Super Resolution的知识：  
* SR中已经采用了Residual Learning、Recursive Learning、Skip Connection、Channel Attention等学习策略和模型结构。  
* SR文章报菜名：SRCNN、Sparse Coding Network (SCN)、VDSR、SRDenseNet、EDSR、RDN、RCAN。  
* 为了用更少的参数取得更好的效果，使用残差块，相关工作有：DRCN、DRRN、MemNet；还有减少推断时间的设计：FSRCNN、ESPCN、CARN、ODE。  

## 3 Proposed Approach  
### 3.1 Motivation  
现有的基于深度神经网络的SISR方法的处理过程可以分成三个阶段：特征提取（feature extraction）、非线性映射（nonlinear mapping）和图像重建（image reconstruction）。用公示表示成：  

<center>$$y=\mathcal{R}(\mathcal{M}(\mathcal{E}(x)))$$</center>  

其中$$\mathcal{R}$$、$$\mathcal{M}$$和$$\mathcal{E}$$分别表示上文所述的图像重建（通常是一层Conv）、非线性映射（通常是级联的Conv）和特征提取（一层Conv），x和y分别是输入的低分辨率图像和输出的高精度图像。  



