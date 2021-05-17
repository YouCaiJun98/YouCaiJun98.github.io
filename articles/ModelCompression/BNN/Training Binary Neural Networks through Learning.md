# Training Binary Neural Networks through Learning  

2021/5/17  

来源：ICML2020  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/BNN/Bayesian%20Optimized%201-Bit%20CNNs.pdf)的包括ipad标注的pdf版本。  
作者是Huawei Noah王云鹤组。  

**Summary**：文章感觉一般，提了一种Fine-tune的方法，具体是把weight的quantizer从简单的sign换成一个learnable function（在文章中是Neural Network/CNN），将输入的FP W通过该函数变成量化后的值（虽然我并不清楚为什么FP weight过一个CNN能变成quantized value吧...或许这个量化的值并不确定是±1？不对..又好像是..似乎没有scaling factor？）。对于每层的latent weight引入一个新的loss term，以（这个是监督谁的，CNN还是监督latent weights？）sign直接量化的weight作为noisy label进行含噪声的监督学习。所以这个方法只是调优+作用到W，至于A，管它呢。  

**Rating: 2.0/5.0**  
**Comprehension: 3.0/5.0**  

文章的贡献有：  
* 提出了一种Fine-tune的方法，在预训练的模型上再同时端到端训quantizer和latent weights，用训练的CNN将FP W作为输入产生binarized weight。  
同样用一张图来说明本文的工作：  

<center> ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202105170001.png)  </center>  
 

## 1 Introdution  
