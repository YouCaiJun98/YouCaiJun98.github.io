# An Empirical study of Binary Neural Networks' Optimisation  

2021/3/20  

来源：ICLR2019  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/BNN/An%20Empirical%20study%20of%20Binary%20Neural%20Networks'%20Opt.pdf)的包括ipad标注的pdf版本。  
文章的作者是Oxford的Milad Alizadeh, Javier Fernandez-Marqu ´ es, Nicholas D. Lane & Yarin Gal，做这种empirical study是想进军BNN？但是为什么后面没声音了？~~讲道理我要是能发一篇ICLR就算成功，可以跑路了~~。  

**Summary**：文章还不错，挺有insight的，而且有一些比较想要的结果？~~可我为什么还是觉得做empirical study的工作很水~~。 **rating 3.5/5** 吧。文章挺散的，讲了很多点。大概说在end-to-end训练中Adam优化器挺好使的，gradient&weight clipping在训练早期太慢，可以先放一放（改用vanilla STE）然后在训练后期再用standard binary STE，或者将训练拆成2-stage，对pretrained model finetune。因为accuracy在训练中出现plateau的地方和最高的accuracy都一定距离，所以不要用早停。  

文章的贡献主要是提供了一些insight：  
* 
 
## 2 Background  
* （小insight）引用Hubara et al. 2017的文章，称将量化融到训练过程才能保持模型性能。  
* 似乎STE不是BNN独有的？原始的STE似乎是vanilla STE？BinaryConnect做了一些调整（使得STE后来成了BNN的paradim）：（1）gradient clipping，当weights的绝对值大于1的时候就用掩码把梯度置为0？后面半句不是很理解，放在下面：  

```  
Gradient clipping stops gradient flow if the weight’s magnitude is larger than 1.
This effectively means gradients are computed with respect to hard tanh function.
```  

（2）weight clipping，当weights由gradient更新之后将它们限制到一个范围里：  

```  
Weight clipping is applied to weights after gradients have been applied to keep them within a range.
```  

* （又是个小insight）kernels稀疏的时候有0会让硬件实现更有效（指的是ternary的情况）。  


## 3 A Systematic Study of Existing Methodologies in BNNs  
总结了下第三节的内容，挺有用的：  
* 说明optimizer的重要性  
* 评估了gradient&weights clipping和BN hyperparam对收敛速度和精度的影响  
* 测试了一些常用技巧的影响（真的有吗？我没看到？）  

### 3.1 Impact of Optimizer  
<font color='red'>非常有启发。</font>  
首先介绍了**4种不同的optimizer**，这是我所不了解的：  

```  
(1) history-free optimisers such as mini-batch SGD that do not take previous jumps or gradients into account, 
(2) momentum optimisers that maintain and use a running average of previous jumps such as Momentum
  and Nesterov (Sutskever et al., 2013), 
(3) Adaptive optimisers that adjust learning rate for each parameter separately such as AdaGrad 
(Duchi et al., 2011) and AdaDelta (Zeiler, 2012), and finally, 
(4) optimisers that combine elements from categories above such as ADAM which combines momentum with 
adaptive learning rate.
```  

第一种应该是最朴素的optimizer，是和过去历史无关的optimizer，和过去的`jumps`或者`gradient`没有关系，比如`mini-batch SGD`；第二种是包括了过去的`jumps`的`running average`的optimizer，比如`Momentum`和`Nesterov`；第三种是可以为param分别调LR的optimizer，比如`AdaGrad`和`AdaDelta`；第四种应该是集大成者，比如`ADAM`。  

下面的这些摘录很重要，非常insightful。  

```  
Our first observation is that vanilla SGD generally fails in optimising binary models using STE. We note that 
reducing SGD’s stochasticity (by increasing batch size) improves performance initially. However, it still fails 
to obtain the best possible accuracy. SGD momentum and Nesterov optimisers perform better than SGD when they are
carefully fine-tuned. However, they perform significantly slower compared to optimsing non-binary models and have 
to be used for many more epochs than normally used for CIFAR-10 and MNIST datasets. Similar to SGD, increasing 
momentum rate improves training speed significantly but results in worse final model accuracy.
```  

首先说vanilla SGD基本上不能优化使用STE的BNN，**通过增加batch size以降低SGD的随机性在开始时可以改善性能，但是后面就拉了**。`SGD momentum`和`Nesterov`相比`SGD`性能要好些，但是收敛速度要慢非常多。和`SGD`类似，增加momentum rate可以加快训练，但是会掉点。  

```  
A possible hypothesis is that early stages of training binary models require more averaging for the
optimiser to proceed in presence of binarisaton operation. On the other hand, in the late stages of the
training, we rely on noisier sources to increase exploration power of the optimiser. This is reinforced
by our observation that binary models are often trained long after the training or validation accuracy
stop showing improvements. Reducing the learning rate in these epochs does not improve things
either. Yet, the best validations are often found in these epochs. In other words, using early stopping
for training binary models would terminate the training early on and would result in suboptimal
accuracies.
```  

一个合理的假设是，**在训练早期需要更平均一些（比如batch size更大一些？），在训练的后期需要更加noisy来increase exploration**。一个观察：**BNN在停止涨点（出现plateau）之后还要再训训，而且在这时降低LR也不起作用（可是最好的模型会在这附近出现）**——>不能用早停。  

### 3.2 Impact of Gradient and Weight Clipping  
* Weight Clipping单独作用没什么效果，但是和Gradient Clipping搭配在一起会好些。  
* 上面这两种Clipping对`SGD`和`Momentum`的速度影响不大，但是ADAM对这种限制敏感。  

### 3.3 Impact of Batch Normalization  

```  
Reducing the momentum rate in BN can help to cancel the effect of long training. The effect is small 
but consistent.
```  

### 3.4 Impact of Pooling and LR  
* 改block内op的顺序中有一个是调Pooling的位置，合理，要趁vector是FP的时候做pooling，不然都是1了。  
* scaling LR有点说法，似乎还会牵扯到weights clipping的门槛：  

```  
In BinaryConnect Courbariaux et al. (2015) propose scaling
learning rates of each convolutional or fully connected layer by the inverse of Xavier initialisation’s
variance value. The same value is also used as the range in weight clipping after gradient update.
```  

## 4 Training BNNs Faster: Empirical Insights Put into Practice   
* 一种现象：BNN训得要比FP counterpart慢。  
* 对上述现象的一种解释：BNN不能用大LR训，所以训得慢。  
* 本文通过实验说明STE本身不会对训练速度产生太大影响。  
* 文章说训练慢是clipping引起的，但是不用clipping同时采用大LR会导致直接训不动。  
* 文章的**Core Insight**之：  

```  
While weight and gradient clipping help achieve better accuracy, our hypothesis is that they are only required 
in the later stages of training where the noise added by clipping weights and gradients increases the exploration 
of the optimiser.
```  

* 文章的**Core Insight**之“最后一公里问题”：  

```  
while we can quickly get to the point where training and validation accuracies stagnate, there is a small gap 
between the achieved accuracy and the best possible one. This gap can only be filled by continuing training for 
many epochs.
```  

同时argue“最后一公里”和STE capacity无关，倒和对param空间的随机探索有关：  

```  
last mile of model performance has little dependence on the STE’s capability and mostly relies on a 
stochastic exploration of the parameter space
```  

## Remained Questions
待补充。  