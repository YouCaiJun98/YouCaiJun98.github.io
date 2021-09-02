# MQBench: Towards Reproducible and Deployable Model Quantization Benchmark  

2021/9/2  

来源：NIPS2021  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/Quantization/MQBench%EF%BC%9A%20Towards%20Reproducible%20and%20Deployable.pdf)的包括ipad标注的pdf版本。  
作者是商汤的工具链团队，包括Yuhang Li, Mingzhu Shen, Jian Ma, Yan Ren, Mingxin Zhao, Qi Zhang, Ruihao Gong, Fengwei Yu, Junjie Yan等人。  

**Summary**：传统的对数量化方案在位宽比较宽裕的情况下相比均匀量化产生的量化误差更大，因此有了一种selective two-word logarithmic quantization(STLQ)的量化方案，大意是当对数量化的量化误差大于一个门槛的时候，对残差再进行一次对数量化。这种选择性两字对数量化对应的量化训练开发得还不是很充分，所以作者提出了一种**基于STLQ的训练方案**。具体而言，作者将参数分成了两组，一组是1word对数量化，另一组是2-word对数量化，两组参数分开训练，中间用两种tensor C和v进行了联系，其他的改进还有改变了分组粒度，从一般的按filter改成了按tile。虽然好像不是很难的东西，但是最后结果还挺不错的，在SID Dataset上用W3A6（只有W是STLQ，A是linear）上取得了27.78PSNR的性能(15% 2-word)。    

**Rating: 3.5/5.0**  
**Comprehension: 3.5/5.0**  
