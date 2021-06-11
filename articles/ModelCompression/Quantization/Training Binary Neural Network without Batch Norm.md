# Training Binary Neural Network without Batch Normalization for Image Super-Resolution  

2021/6/11  

来源：AAAI2021  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/BNN/BATS%20Binary%20ArchitecTure%20Search.pdf)的包括ipad标注的pdf版本。  

作者还是ECCV2020上做BSR的西电的组，有Xinrui Jiang, Nannan Wang, Jingwei Xin, Keyu Li, Xi Yang, Xinbo Gao（或许可以去看下他们的主页）。  

**Summary**：感觉文章**挺虚的**，~~这就是做应用的吗~~。文章的出发点还挺好的，觉得除了前后两个FP Conv之外中间的BN层也会引入大量的FP OP，所以想解决掉这个BN层（但是解决的方式有点南辕北辙了，你加个PReLU和BN其实区别不大吧，都是zero point/distribution shifting，而且这还是引入FP op啊）。文章提出了一种Binary Training Scheme（但是对BNN的训练没有启发，这里说是“训练方案”实际上只是一些BNN里常见设置的堆砌，没有什么参考价值），利用BNN里的一些fancy方法构建了个强baseline（同样没什么参考价值），最后提了一种BSR architecture(一种building block，里面的一种dilated conv concate的操作好像还有点参考价值)。此外这篇文章中BSR的训练还用了multi-step KD，同样是直接挪用了现在BNN工作的一些思路。 

**Rating: 3.0/5.0**  
**Comprehension: 3.5/5.0**  

**motivation**：（不错的出发点，可是落脚点不太对劲？）BSR网络中的BN层虽然可以重中心化输入的分布从而减轻量化的影响提点，但是引入了很多FP op，对低精度硬件非常不友好，因此想移除这种层。  

文章的贡献有：  
* Binary Training Scheme（取代BN的方案，但本质上是BNN工作中的常用设置）；  
* 一种BSR building block（这种东西一般没什么很强的创新性可言吧）+ KD的使用。  

## 1 Introduction  
* 学到了一个新词：ill-posed problem（不适定问题），描述SR中的这种one-to-many mapping。  
* SR研究的方向之  
    * 增加层数打点；  
    * 减少参数和资源消耗（比如recursive learning、parameters sharing、squeeze operation、 group convolution、 wavelet domain）。  

## 2 Related Work  
关于SR更详细的报菜名，或许还有点用。  









