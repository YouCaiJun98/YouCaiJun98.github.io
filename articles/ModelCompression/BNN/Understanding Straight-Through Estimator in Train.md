# Understanding Straight-Through Estimator in Training Activation Quantized Neural Nets  

2021/4/9  

来源：ICLR2019 / 陈老师安利    
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/BNN/Understanding%20Straight-Through%20Estimator%20in%20Train.pdf)的包括ipad标注的pdf版本。  
作者是第一次见到的Penghang Yin, Jiancheng Lyu, Shuai Zhang, Stanley Osher, Yingyong Qi, Jack Xin，感觉有点硬核，全文10页附录的推导有20页orz。  

**Summary**：讨论STE为什么能"正确"训练binary model的文章。提了一个非常关键，大家也非常关心的好问题，但是给的回答感觉非常草率且not general.文章给出了一些证明，证明对于一个两层的小网络（甚至还不算是Conv网络），ReLU STE、Clamp ReLU STE可以指向正确的梯度下降方向，identity STE则不能，会在local minima附近振荡，最后给了验证试验。虽然推导很多（但是看不懂也没看），但是他们就在toy model上做了实验，不知道能不能（大概率是不能）推广到更深/Conv的网络中，有种自娱自乐、自欺欺人的感觉。   

**rating：2.0/5.0**  
**comprehension：1.0/5.0**（对公式推导没有研究，不知道是不是对的，但肯定是没用的）  

文章的贡献有：  
* 用大量的数学推导证明了在一个非常受限的情况下（数据分布、network都严格受限）不同的STE确实能指向population loss下降的方向，在该特殊情况下，identity STE表现不如另外两者。  
* 1.2有句看不懂的话：  

```  
This is an implication that poor STEs generate coarse gradients incompatible with the energy landscape, which is consistent with 
our theoretical finding about the identity STE.
```  



## Abstract  
好问题，问得人心潮澎湃：  

```  
 Since this unusual “gradient” is certainly not the gradient of loss function, the following question arises: why searching in its 
 negative direction minimizes the training loss?
```  

**但是你最后答得算什么？**  

推导基础和测试基础：本文的toy model是训练`two-linear-layer network`，它的weight是**full-precision**的（陈老师赞许这点了诶？先固定weight是full-precision的再单研究binary activation的影响），activation是**binarized ReLU activation**的，输入满足高斯分布。  

本文结论：  

```  
We prove that if the STE is properly chosen, the expected coarse gradient correlates positively with the population gradient 
(not available for the training), and its negation is a descent direction for minimizing the population loss.
```  

“我们证明了，如果STE选取得当，那么expected coarse gradient(根据proxy计算出来的梯度的期望？**注意全文的gradient都指的是关于weight的！**)和真正的gradient正相关，它的反方向就是减少population loss的方向。”  

```  
We further show the associated coarse gradient descent algorithm converges to a critical point of the population loss minimization 
problem. Moreover, we show that a poor choice of STE leads to instability of the training algorithm near certain local minima.
```  

"我们进一步揭示了coarse gradient下降算法最后收敛到population loss minimization的关键点，不合适的STE会在特定local minima附近震荡。"  

## 1 Introdution  
表了一些related works（大概率也不会看就是了）：  

```  
This proxy derivative used in the backward pass only is referred as the straight-through estimator (STE) (Bengio et al., 2013). 
In the same paper, Bengio et al. (2013) proposed an alternative approach based on stochastic neurons. In addition, Friesen & 
Domingos (2017) proposed the feasible target propagation algorithm for learning hard-threshold (or binary activated) networks 
(Lee et al., 2015) via convex combinatorial optimization.
```  

## 3 Main Results  
### Remark 1  

```  
The convergence guarantee for the coarse gradient descent is established under the assumption that there are infinite training 
samples. When there are only a few data, in a coarse scale, the empirical loss roughly descends along the direction of negative 
coarse gradient. As the sample size increases, the empirical loss gains monotonicity and smoothness.
```  

收敛的保证条件是梯度下降建立在无限样本的基础上，只有少数样本的时候下降的方向大体是coarse gradient的负方向，当样本数目增多时empirical loss单调性和平滑性会更强。  

后面的证明大概就是说明the coarse partial gradient using clipped ReLU/ReLU和the true partial gradient of the population loss正相关，最后能不能收敛到local minima这样（identity STE则是在这种local minima梯度不能消失，因此振荡）。  

后面的实验设置没怎么看，可能是隐患吧。  
