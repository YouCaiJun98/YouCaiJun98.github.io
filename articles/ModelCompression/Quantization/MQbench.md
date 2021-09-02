# MQBench: Towards Reproducible and Deployable Model Quantization Benchmark  

2021/9/2  

来源：NIPS2021  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/Quantization/MQBench%EF%BC%9A%20Towards%20Reproducible%20and%20Deployable.pdf)的包括ipad标注的pdf版本。  
作者是商汤的工具链团队，包括Yuhang Li, Mingzhu Shen, Jian Ma, Yan Ren, Mingxin Zhao, Qi Zhang, Ruihao Gong, Fengwei Yu, Junjie Yan等人。  

**Summary**：尽管现在有很多的量化算法，但是学术上提出的新方法因为训练pipeline没有统一，且忽视了硬件部署的要求（意思大概是硬件库不支持？），他们的结果通常无法复现，或者无法部署。所以他们做了这个Model Quantization Benchmark工作来评估模型量化算法的复现与部署能力。结果发现不同的学术量化算法**性能非常接近，且没有明显的优劣关系**(有些性能提升主要是通过改进训练达到的，这里点了DSQ的名，好狠，连自己主管的工作都diss)。      

**Rating: 3.5/5.0**  
**Comprehension: 3.5/5.0**  

## 1 Introduction  
* 据说在W3A3的情况下就能达到FP accuracy了，哈人( Learned step size quantization)  
* 文章提了两个在量化算法研究中长期被忽略的点：  
    * 超参数设置对量化网络的性能影响很大，比如lr、wd和预训练，所以他们对齐了训练管道  
    * 大多数学术研究没有在硬件设备上部署算法，比如没有fuse BN、有些算法只量化了输入和参数(而没量化element-wise add和concate)，同时还有鲁棒性的问题（比如算法是per-tensor设计的，但是用到per-channel情形），因此学术研究和真实部署之间有较大的gap。  

## 2 MQBench: Towards Reproducible Quantization  
* 在复现性方面的评估包括给定硬件支持的推理库、量化算法、网络结构和比特位宽。  
* Hardware-aware Quantizer：  
    * 本文只关注均匀量化，非均匀量化需要特殊的硬件设计。  
    * 均匀量化的quantization op和dequantization op可以用下式表示，其中s和z分别是scale(实数)和零点偏移(整数)：  
    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109020001.png)  
    * 这些量化方案可以进一步分为：  
        * 对称与非对称量化  
        * per-tensor与per-channel量化(前者是对整个layer，后者是更细粒度的量化)  
        * FP32 scale与power of two scale，前者几乎连续(nearly continuous)，后者更难些，但是可能会进一步加速。  
* Hardware Library报菜名：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109020002.png)  
* 细节设置：  
    * Bitwidth里说他们对算法的仿真是**fake quantizaiton**，因为在通用硬件上不能部署所以没实验3-bit的情形，在硬件设置下2-bit不收敛。  
    * 实验用相同的pre-trained model初始化。  

## 3 MQBench: Towards Deployable Quantization  
这部分总体还挺有用的。  
### 3.1 Fake and Real Quantization  
仿真中的Fake Quantize与部署中的Real Quantization：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109020003.png)  
在GPU上做QAT的时候实际上是用FP32仿真量化过程（也就是Fake Quantize），在部署的时候则是使用只有整数运算的Real Quantize。这个过程可以用公式表示为：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109020004.jpg)  
下面对requantize的定义则解释了上图右侧的疑问：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109020005.png)  
在实际部署中，两个int8的数的计算结果是个int32的数，进一步经过激活成为$$x^{l+1}$$，还是个int32的数，通过scale恢复FP32的数，再量化回8bit的数，进行下面的运算。上式（2）里real quantization括号里的最后两项可以离线计算，因为参数和$$z_w$$与$$z_x$$在量化前就已经能确定了（**但是$$z_w$$和$$z_x$$是啥啊**）  
因为仿真和实际部署的计算图里有些细微的差距（**在哪？**）所以最终结果也有一些区别。  

### 3.2 Folding Batch Normalization  
* BN的作用包括`reduce internal covariate shift and also smooth the loss surface for fast convergence`  
* BN可以和Conv中的参数merge起来：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109020006.png)  
* 有五种常见的BN folding策略(式中$$\gamma$$和$$\beta$$分别表示仿射变换的参数和偏移，$$\mu$$,$$\sigma^2$$分别表示running mean和variance，$$\epsilon$$是数值稳定引入的工具变量，$$\tilde{\mu}$$, $$\tilde{\sigma}^2$$表示当前batch上的均值与方差)：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109020007.png)  

### 3.3 Block Graph  

## 4 MQBench Implementation  

## 5 MQBench Evaluation  

## 6 Discussion  

## Attachment  