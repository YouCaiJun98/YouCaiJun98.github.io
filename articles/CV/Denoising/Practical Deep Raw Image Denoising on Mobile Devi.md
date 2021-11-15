# Practical Deep Raw Image Denoising on Mobile Devices  

2021/10/27 - 11/15整理  

来源：ECCV20  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/CV/Denoising/Practical%20Deep%20Raw%20Image%20Denoising%20on%20Mobile%20Devi.pdf)的包括ipad标注的pdf版本。  
作者是Tsinghua University / Tsinghua University的Yuzhi Wang, Haibin Huang, Qin Xu, Jiaming Liu, Yiqun Liu, Jue Wang等人，yuzhi似乎是实验室的远古学长哎。  

**Summary**：一篇理论和实际结合得非常紧密的文章，简直非常可贵（u1s1一般LLCV理论强的都不怎么work吧，麻！）文章从噪声模型出发（虽然是经典的泊松-高斯 -> 异方差高斯的噪声模型，但是给了一个很详细的噪声引入过程，好评），给了一个针对特定sensor的噪声参数(分布中的k和$\sigma$, 这两个值后面会发现和ISO成线性/平方关系)的估计方法(很简洁，用一个linear regression + burst sample就能做到)，并提出一个**K-Sigma Transformation**, 在luminance space将不同ISO下采集的输入和输出同时映射到ISO-independent的空间，从而避免了**用过多ISO对应数据训练模型**的问题。文章在SID合成数据集上训练，并能很好地泛化到真实手机镜头采集的图片。文章还对U-Net结构进行了修改，让它变得更适合Mobile Device的应用场景。         

**Key words**：  
* Noise Model  
* Pre/Post-process（如果K-Sigma Transformation也能算在内的话）

**Rating: 3.7/5.0** 还不错，理论能用到实际上实在太难得了，简直感人。  
**Comprehension: 4.0/5.0** 基本上能懂在干什么事情。   

文章的贡献有：  
* 给出了估计sensor噪声模型参数的方法，用于生成合成数据训练模型，且能很好地泛化到真实模型上。  
* 提出K-Sigma变换，解决ISO对应不同噪声水平的问题。  

## 1 Introduction & 2 Related Work   
一些简单的insight / fact：  
* 移动设备拍出来的照片更容易被噪声污染，这是因为  
    * sensor和len的成本更低  
    * 特别是在低光环境下  
* 对于一个特定的sensor模型，其噪声特性是一致且可被充分估计的。  
* 当时对于mobile device的去噪方法主要是burst，局限性是  
    * 需要精确与快速的图像匹配  
    * 噪声水平高时不能有效去除噪声  

## 3 Method  
### 3.1 The Noise Model  
一张比较喜欢的噪声来源分析图：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150002.png)  

相机传感器将曝光时间内撞击pixel area的光子转换成数字化的luminance map，在没有噪声的情况下，这个过程（linear camera model, at each pixel, a linear amplification）可以建模成：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150003.png)  

式中$$u^*$$表示撞击像素区域的期望光子数，\alpha是"quantum efficiency factor"，g是模拟增益。上图Fig2中的完整过程（含噪声）可以表示成：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150004.png)  

其中u是实际的光子计数， 两个n都是高斯噪声，u满足一个关于$$u^*$$的泊松分布：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150005.png)  

将1式和3式合在一起有：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150006.png)  

做一下变量代换，就有：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150007.png)  

**式中的k和sigma都和ISO有关**。  

### 3.2 Parameter Estimation  
参数的估计可以用线性回归来做：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150008.png)  

具体做法可以用下面这张图来描述：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150009.png)  

### 3.3 The k-Sigma Transform  
下面有一个比较精彩的构造，它的目的在于让ISO-dependent的参数k和sigma转换到ISO-independent空间，这样就不必对各种ISO的图像分别训练或者混合训练了，可以视为k与sigma在ISO上的归一化：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150010.png)  

后面的描述我用截图来得更方便些：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150011.png)  

所以网络的处理流程是：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150012.png)  

## 4 Learning to Denoise  
网络的backbone基本上是U-Net，但是有许多细节修改，再细些就check原文吧：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150013.png)  

### 4.2 Training Dataset  
有点值得大书特书。这里的训练集是从SID从裁了一部分出来(10s / 30s曝光时长)，再去掉一些有明显噪声的图片生成的subset，在这些纯净图像上用噪声模型生成噪声加进去。测试的时候则是在自己采集的一个数据集上测，这样就体现出泛化性了。  

## 5 Experiments  
### 5.1 Noise Parameters Estimation  
估出来的噪声参数和实际测出来的非常接近，且和ISO呈一定关系：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202111150014.png)  

