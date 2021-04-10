# Understanding Straight-Through Estimator in Train  

2021/4/9  

来源：ICLR2019 / 陈老师安利    
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/BNN/ReCU%EF%BC%9A%20Reviving%20the%20Dead%20Weights%20in%20Binary%20Neural.pdf)的包括ipad标注的pdf版本。  
作者是第一次见到的Penghang Yin, Jiancheng Lyu, Shuai Zhang, Stanley Osher, Yingyong Qi, Jack Xin，感觉有点硬核，全文10页附录的推导有20页orz。  

**Summary**：讨论STE为什么能"正确"训练binary model的文章。提了一个非常关键，大家也非常关心的好问题，但是给的回答感觉非常草率且not general.文章给出了一些证明，证明对于一个两层的小网络（甚至还不算是Conv网络），ReLU STE、Clamp ReLU STE可以指向正确的梯度下降方法，identity STE则不能，会在local minima附近振荡，最后给了验证试验。虽然推导很多（但是看不懂也没看），但是他们就在toy model上做了实验，不知道能不能（大概率是不能）推广到更深/Conv的网络中，有种自娱自乐、自欺欺人的感觉。   

**rating：2.0/5.0**  
**comprehension：2.0/5.0**（对公式推导没有研究，不知道是不是对的，但肯定是没用的）  

文章的贡献有：  
* 提出使用ReCU对weights range进行clamp，从而降低量化误差（以及加快convergence）；  
* 提出weights的information entropy的角度（感觉非常牵强，甚至矛盾），解释BNN weights的standardization；  
* 提出减小量化误差和增加information entropy之间的矛盾，采用一种adaptive exponential scheduler来在训练中修改ReCU的clamp threshold。  

## Raised Question  
引起了一些思考：
* 为什么对weights的range进行clamp会减少量化误差？按说分布在tail的weights越多则量化误差越小（如果是按照文中给出的定义的话）？或许这点可以用文中的数学推导来解释？如果对于刚量化的weights来说，那确实是这样，但是gradient又该怎么算怎么传？更新完梯度（将多余的weights从quantile处推开之后，量化误差又怎么说呢？）等等，新想法：分布在quantile更两边的weights完全起到了减小量化误差的作用啊？？把它们堆到quantile完全会进一步增加QE啊？？还是说scaling factor也会影响这个过程？  
* 为什么增加information entropy就能提升performance？这个是共识吗？binary的entropy是离散的，而且从文中也可以看出来这个entropy是对连续的weights而言的，但是实际上weights都是要被量化的啊？所以information entropy高=分布在tail的weights多（分布在0附近的entropy低，总不可能聚集在中间吧？）+information entropy高了好=分布在tail的weights多就好，这不是矛盾了吗？因为p(x)是Laplace分布啊，不该是出现概率越低的weights信息量越大吗？又或者，通过clamp可以改变distribution，从而提升entropy呢？  
* 进一步地，提升information entropy能带来的是什么？是直接的性能提升还是性能上限的提升？  
* 因此，减少量化误差和提升weights的information entropy是矛盾的？（现在看好像又没有了，但是文章的做法让人感觉这两者是矛盾的）引出更本质的问题，减少量化误差，在多大程度上能带来性能的提升？binary网络一定越像FP的越好吗？可能存在一种更独特的形式吗？

## Core Argument  
latent weights分布中两头的weights对优化不利，应当去掉。  
<font color='Silver'>后面为什么突然又提information entropy意义不明，感觉文章的故事讲得不是很流畅。</font>  

## Abstract  
简述了文章的贡献：  
* 提出"dead weights"的概念，即在训练BNN中很少更新的weights（有点不达意，应该指的是幅值较大的那些latent weights，因为难以更新过0所以对应的binary weights很少变化）；  
* 提出"rectified clamp unit(ReCU)"作为weights的clamp函数，声称可以减少量化误差；  
* 作者提出考虑weights的information entropy，分析了BNN weights的standardization，并且指出了减小量化误差和增加information entropy之间的矛盾，采用一种adaptive exponential scheduler来在训练中修改ReCU的clamp threshold。  

## 1 Introdution  
* 指出BNN性能劣化的两大主要原因是前传中的量化误差和后传中的梯度不匹配，<font color='Silver'>这两者之间真的相对独立吗？有点不能接受。</font>  
* 作者说量化误差存在于weights中，**而不是weights和activations中**，这点存疑。  

## 3 Background  
* 这里给了量化误差的定义，有点新鲜：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104010001.png)  

* 也给出了量化误差L对w_r/a_r的定义，让我对STE/polynomial func的认识有点更新（见图中标注）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104010002.png)  

## 4 Methodology 
### 4.1 The Dead Weights in BNNs  
作者说latent weights distribution的tail中的小幅值的weight是限制BNN优化的因素，但是**这点非常不能理解，因为这一部分的参数数量非常之少**，而且硬要杠一下也不是不能杠，为什么peak附近的weights就一定好更新，就不是限制因素？这附近的weights更容易来回振荡，大的weights可能更新的幅度也更大怎么不说？原文：  

```  
Intuitively, the signs of the weights around the distribution peak are easily changed, while it is the opposite 
for the outliers in the tails, which greatly limits the representational ability of BNNs and thus causes slow 
convergence in training.
```  

找到个τ的下界0.82，但实际上并不能取到（因为information entropy）。  

### 4.3 Information Entropy of Weights  
```  
 Usually, the more diverse, the better the performance of a BNN.
```  

无法接受。完全和上文相悖。如果你觉得BNN的information entropy越大，表示能力越强，那么为什么还要clamp？clamp后的entropy一定会变小不是吗？就算这句话是对的，那么反而可以说明大的latent weight有用才对？那么不是又和核心观点矛盾了吗？而且突然提这个概念别提有多突兀了，也没个引入什么的。而且文章实验用了τ~s~和τ~e~并且τ~e~=0.99，约等于没有clamp不是吗？最根本的，为什么不把训练最后的distribution放出来？  

后面分析了weights的information entropy关于τ和b的变化，作出结论必须将b维持在较高水平才能让entropy比较高，又b实际上不知道，是最大似然估计出来的，所以需要对weights进行标准化。  

提出：  

```  
it is the standardization, but not the centralization, that contributes to the performance improvement.
```  

给的training procedures还挺有用的：首先standardize weights（此时还是FP的），再用ReCU revive "dead weights"，接着计算scaling factor α，接着binarize inputs & processed weights，最后计算BConv；反传的时候就正常来。  

### 5.2.1 Effect of τ for ReCU  
* exponential scheduler：  

```  
Our motivation lies in that τ should start with a value falling within [0.85, 0.94] to pursue a good accuracy, and then gradually 
go to the interval [0.96, 1.00] to stabilize the variance of performance.
```  