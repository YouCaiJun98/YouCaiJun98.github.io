# Automated Log-Scale Quantization for Low-Cost Deep Neural Networks  

2021/8/28  

来源：CVPR2021
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/Quantization/Oh_Automated_Log-Scale_Quantization_for_Low-Cost_.pdf)的包括ipad标注的pdf版本。  
作者是韩国国立蔚山科学技术院的Sangyun Oh1, Hyeonuk Sim, Sugil Lee和Jongeun Lee。  

**Summary**：传统的对数量化方案在位宽比较宽裕的情况下相比均匀量化产生的量化误差更大，因此有了一种selective two-word logarithmic quantization(STLQ)的量化方案，大意是当对数量化的量化误差大于一个门槛的时候，对残差再进行一次对数量化。这种选择性两字对数量化对应的量化训练开发得还不是很充分，所以作者提出了一种**基于STLQ的训练方案**。具体而言，作者将参数分成了两组，一组是1word对数量化，另一组是2-word对数量化，两组参数分开训练，中间用两种tensor C和v进行了联系，其他的改进还有改变了分组粒度，从一般的按filter改成了按tile。虽然好像不是很难的东西，但是最后结果还挺不错的，在SID Dataset上用W3A6（只有W是STLQ，A是linear）上取得了27.78PSNR的性能(15% 2-word)。    

**Rating: 3.5/5.0**  
**Comprehension: 3.5/5.0**  

## 1 Introdution  
* 非均匀量化相比均匀量化的优点，在硬件实现上更简单，按照量化是对W还是对W/A都进行可以把乘法器改成移位器或者加法器（未深究）；  
* 当大幅值的参数对精度有显著影响时，在位宽相等的情况下，对数量化要比均匀量化效果差（讲道理这段写得真差）：  

```   
This can sometimes lead to a lower expected quantization error overall, but often disproportionately high error 
that happens at high-magnitude values can undermine the accuracy of a log-scale quantization scheme significantly, 
resulting in worse performance than linear quantization at the same bit-width
```  

* STLQ的硬件实现难度和对数量化一样，性能接近均匀量化。  

* 抨击了以前基于STLQ的训练方案（感觉大多不make sense）：  
    * 说2-word比例是个超参数，在同一层或同一通道固定，或者不好优化 —— （这不是粒度的问题吗，有必要这么讲吗？  
    * 之前的工作的优化目标是量化误差，而不是用潜变量显式地约束模型size和2-word比例，因此训练不是最优的 —— ？？你开心就好...这不该给个ablation吗？  
    * 不能在给定ratio下找到最佳参数 —— ...  

## 3 Preliminaries on Log-Scale Quantization  
对于对数量化和STLQ的描述还是有用的：  

### 3.1 Preliminaries on Log-Scale Quantization  
对于来自范围[-1, +1]的x，将其量化为一个N-bit的整数q，q的范围是[-M, M-1]，其中$$M=2^{N-1}$$，重建的$$\tilde{x}$$可以表示为：  

$$LogDequant : \tilde{x} = \begin{case} &0 \quad &if q = 0 \ &sign(q)2^{-|q|} \quad &otherwise.\end{case}$$


