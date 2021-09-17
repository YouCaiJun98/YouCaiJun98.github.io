# Learning Deep CNN Denoiser Prior for Image Restoration  

2021/9/17  

来源：CVPR17  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/CV/Denoising/IRCNN.pdf)的包括ipad标注的pdf版本。  
作者是HIT的Kai Zhang, Wangmeng Zuo, Shuhang Gu, Lei Zhang等人，这是ZK的早期作品，和传统方法离得还是很近的实际上是restoration相关的（更是multi-task，里面有denoise、SISR、deblur的实验），分在denoise类只是因为denoise有人引它。  

**Summary**：一篇比较经典的文献，提出将CNN denoiser作为prior替代MAP inference/model-based optimization中的prior。具体做法是训练一串噪声强度不等的CNN，根据变量分裂法（variable splitting techniques，文中用的HQS，将模型优化方法和判别学习方法合在一起，将fidelity项和正则项分开处理，且正则项可以描述为一个去噪子问题）作为prior插入迭代优化中，作为基于模型的优化方法中的一部分以实现**mult-task**/反演问题。但是里面用了很多optimization method的背景知识，理解起来很困难，只是勉强把握了个大概。      

**Key words**：  
* integration of model-based optimization methods and discriminative learning method.  
* CNN as prior    

**Rating: 3.5/5.0** 后面参考它的文献也不少，应该是有影响力的，但是结果可能不太好。  
**Comprehension: 2.5/5.0** 非常不理解。差了太多背景知识了，和model-based方法太相关了，读起来很困难。   

一张图总结模型结构（但是这篇文章远非模型而已！模型只是作为一种代替image prior的denoiser prior）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109170005.png)  

## 1 Introduction  
* 典中典之model-based optimization methods与discriminative learning method的优劣：  
    * 基于模型的优化方法可以灵活处理各种反演问题（multi-task, multi-level noise），但是很花时间而且依赖于复杂的prior  
    * 基于生成学习的方法推理速度快，但是受限与狭窄的应用范围  

* 将restoration问题建模成$$\mathbf{y}=\mathbf{Hx+v}$$，v是指加性高斯白噪声（我觉得这里不合理），$$\mathbf{H}$$可以根据不同任务有不同解释：  
    * 去噪任务中是相同矩阵(identity matrix)  
    * 去模糊任务中是blurring operator（具体我不清楚）  
    * 超分任务中是blurring + downsample  

* IR是一种不适定的反演问题，其先验(prior)也称为正则(regularization)用来约束解空间，从贝叶斯角度，解x_hat可以用MAP来表示（FFDNet中也有同样的东西）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109170006.png)  

上式可以改写成下式，该式的解通过最小化能量方程取得，能量方程第一项是fidelity项，保证解符合退化过程；第二项是正则项，使得输出满足需要的特性，对重建性能起到vital的作用。解上式的方法可以分为两大类，分别是基于模型的优化方法与基于生成学习的方法，前者直接通过迭代优化求解（2）式，后者学习先验的参数，拥有紧致的推理过程(compact inference,和基于模型的方法相对吧，我记得基于模型的方法两者可以拆开)：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109170007.png)  

由于这种推断由MAP估计指导，所以这类方法可以归类于MAP inference guided discriminative learning methods。将MAP推理替换成非线性函数$$\mathbf{\hat{x}}=f(\mathbf{y,H;\Theta})$$可以得到判别性学习方法的一般情形。  

根据上面公式（2），由于基于模型优化的方法可以灵活设定H所以对IR任务泛用性强；判别性学习方法则要不断训练模型。  

## 2. Background  
### 2.1. Image Restoration with Denoiser Prior  
* 已有将denoiser prior融合到model-based optimization问题以处理反演问题的思路，给了一段survey  
* 将fidelity项和regularization项拆开分别处理可以用许多已有的去噪方法处理不同的IR问题。  

### 2.2. Half Quadratic Splitting (HQS) Method  
有用！  
在HQS中，将regularization中的x替换成z可以将(2)改写成：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109170008.png)  

于是HQS尝试去解下面这个问题：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109170009.png)  

其中\mu是一个惩罚系数，在迭代中按照non-descending order变化(意思是不会减小？)，（5）可以进一步改写成下面这种迭代方案：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109170010.png)  

**这样f term和r term就成了两个独立的子问题。**特别地，f term和quadratic regularized
least-squares problem相关，可以很快地求出它关于不同H矩阵的解，比如：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109170011.png)  

(6b)可以改写成：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109170012.png)  

根据贝叶斯概率，（8）相当于用噪声level \sqrt{\lambda \\ \mu}的高斯去噪器去噪x_{k+1},这样，**任何的高斯去噪器都可以作为一个modular part解（2）式**，可以将(8)式改写成(9)式。  

根据(8)式和(9)式，图像先验(r term)可以隐式地用denoiser prior代替，有以下好处：  
* 可以用任意gray/color denoiser来解一系列反演问题；  
* `the explicit image prior Φ(·) can be unknown`我理解为不用再建模image prior了；  
* several complementary denoisers可以用来联合解同一个特定问题。  
这个特性可以在其他优化方法中使用(e.g., iterative shrinkage/thresholding algorithms ISTA and FISTA),只要那里有个去噪子问题。（有点不明确哎，不是很懂）  

## 3. Learning Deep CNN Denoiser Prior  
### 3.2. The Proposed CNN Denoiser  
网络结构见上图，没啥意思。  
* Using Dilated Filter to Enlarge Receptive Field  
* Using Batch Normalization and Residual Learning to Accelerate Training  
* Using Training Samples with Small Size to Help Avoid Boundary Artifacts  
    * zero padding  
    * (bullshit)将图片切成小块可以帮助CNN看到更多边界信息  
    * 如果训练patch比感受野小的话会有问题  
* Learning Specific Denoiser Model with Small Interval Noise Levels  
迭代优化框架需要很多噪声等级不同的去噪器(想想\sqrt{\lambda \\ \mu})，这问题是2-fold的：  
    * 许多研究表明如果子问题比较难优化，可以用不甚精确但是快的子问题来代替，从这个角度来讲不需要训练很多去噪器(interval不用太小)  
    * 这个问题里用到的高斯去噪器和传统情况下发挥着的作用不一样，最好能对按照当前的噪声水平来 -> interval要小些  
    * 总之是个tradeoff问题  
    * 用adjacent noise level的模型来初始化  
    * 这里说这里训练的去噪器的模型数量要比给不同的退化任务训练的模型数量少(bullshit，你这都25个了)  

## 4. Experiments  
### 4.1. Image Denoising  
* 用到的数据集包括BSD400, ImageNet, Waterloo  

### 4.2. Image Deblurring  
* 由于卷积是在circular boundary conditions进行的，公式(7)，即x_{k+1}的计算可以通过FFT快速求出来。  
* 这里暴露出了**IRCNN调超参是个问题**。对于某种退化过程，\lambda和\sigma ^2相关，在迭代中固定不动，从而\mu控制了去噪器的噪声水平，实际中是反过来进行的，即通过选去噪器来调整这一项。  
* 迭代30轮，噪声水平从49逐渐指数降低到[1, 15]，具体根据噪声水平定。  

### 4.3 Single Image Super-Resolution  
* 当时的SR大多是依赖于特定的降采样方式，盲SR效果很差；但是这种即插即用的方法可以避免重新训练。  
* SISR任务对应的(6a)为下式，在去噪前先重复5次：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109170013.png)  

## 5. Conclusion  
未来方向：  
* 减少CNN去噪器的数目以及迭代轮数  
* 解决其他反演问题  
* 使用互相补充的复数prior  
* （weak）指导CNN结构设计  