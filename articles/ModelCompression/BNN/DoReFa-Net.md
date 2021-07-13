# DoReFa-Net: Training Low Bitwidth Convolutional Neural Networks with Low Bitwidth Gradients  

2021/7/13  

来源：arxiv16(最后是不投了吗，1.2k被引感觉好强！不愧是BNN经典作！)  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/BNN/DoReFa-net.pdf)的包括ipad标注的pdf版本。  
作者是旷视的Shuchang Zhou, Yuxin Wu, Zekun Ni, Xinyu Zhou, He Wen和Yuheng Zou，这篇文章也是BNN领域的开创性&代表性作品，但是很奇怪，这个组后面是金盆洗手了吗，怎么不见发其他BNN相关的文章了？  

**Summary**：BNN领域非常具有代表性的作品，提出将模型的参数、激活值、梯度都进行量化（位数不定，根据需要调整），给出了敏感度梯度>激活值>参数的排名（因此需要的位数也是如此排序），因此加速在CPU, FPGA, ASIC和GPU等设备上的推理速度和训练速度（没想清楚，在FPGA上训练是怎么回事...真会有这样的需求吗？）。但是DoReFa给出的方案非常简单粗暴，所以影响也比较深？  

**rating：3.8/5.0**  
**comprehension：4.0/5.0**  

文章的贡献有：  
* 提出了同时量化模型权重、激活值和梯度的方法，指出参数、激活值、梯度的敏感程度依次上升，因此依次需要更多的位数；指出参数和激活值的量化是确定的，但是梯度的量化是随机量化。    

## 2 DoReFa-Net  
这里指出参数和激活值的量化是确定量化，梯度的量化是随机量化。  

### 2.1 Using Bit Convolution Kernels in Low Bitwidth Neural Network  
这节讲的是低比特乘法？对于两个定点数$$\Bbb{x}= \sum_{m=0}^{M-1}c_m(\Bbb{x})2^m$$和$$\Bbb{y}= \sum_{k=0}^{K-1}c_k(\Bbb{y})2^k$$，那么$$\Bbb{x}$$和$$\Bbb{y}$$之间的点乘积可以用下式计算：$$\Bbb{x} \cdot \Bbb{y} = \sum_{m=0}^{M-1}\sum_{k=0}^{K-1}2^{m+k}bitcount[and(c_m(\Bbb{x}), c_k(\Bbb{y}))]$$，计算的时间和$$\Bbb{x}$$与$$\Bbb{y}$$的位宽相关。  

### 2.2 Straight Through Estimator  
这里的forward形式（low-bit quantization）有点没见过：  

<center>![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202107130001.png)<\center>  

量化之后的比特串就按照上面的式子计算，再按情况scaling。  


