# Training Binary Neural Networks with Real-to-Binary Convlutions  

2021/3/19  

来源：ICLR2020  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/BNN/binaryduo_reducing_gradient_mismatch_in_binary_ac.pdf)的包括ipad标注的pdf版本。  
作者是Korea的Kim ** Kim ** Kim ** Kim **~~好家伙有四个金某某~~。来自于POSTECH, Department of Creative IT Engineering，看这名字有点像个国家机构。  

**Summary**：文章一般？感觉 **rating 3.5/5** 的样子。这里面把BNN性能不好的锅主要甩给了梯度的mismatch（这确实是个问题，但是远远不是本质原因吧？不是很清楚）然后文章给了一种梯度估计的方法CDG以取代cumulative difference，以此想说明的问题是，不同的sophisticated STE其实在梯度方面都不太行，主要的问题来自于activations的量化精度。后面作者给了一种training scheme（main contribution），第一步是训一个ternary activation的model，后面把activation function替换成两个binary activation function，把连接的weights拆成两个（base model有处理，会变得更小一点），作为初始化，再finetune，这应该就是文章的主要贡献了。2020年的文章，**结果还挺惨的**，60.x，被BATS（河外方法）暴打。  

文章的贡献有：  
* 提出了一种gradient mismatch estimation的方法，并且用这种方法和coarse STE作cosine similarity，想说明之前forward换sigh函数，backward提approximation的思路都不本质（~~activation precision matters!~~）；  
* 提出了一种training scheme，把训练分成**2-stage**，第一步先用ternary activation function，后面decouple了作为初始化finetune这样子。  
 
## Abstract  
本文核心论点：**对activation用更高的precision比整花里胡哨的STE（modify forward阶段的sigh函数以及backward阶段的approximation）来得更有效。**  

## Introdution  
有趣的观察——activation从high-bit量化到low-bit的accu drop不如2bit-1bit来得剧烈，偷个表格：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202103180001.png)  

再顺便偷张图：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202103180002.png)  

### 3.2 Gradient Mismatch And Sophisticated STEs  
作者在这里攻击现在衡量gradient mismatch的方法（就是用面积的方法，是个积分）indirect。

## 4 Estimation the Gradient Mismatch  
这里说实话**没看明白**，但是主要的目的清楚了。  
作者提出的mismatch估计方法是CDG，还指了一种evolutionary strategy，在appendix里给了形式。  

## 5 BinaryDuo: The Proposed Method
用几张图说明会简单很多：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202103180003.png)  

这张图说明的问题是怎么把ternary activation func拆成两个binary activation funcs，要注意的是这里weights **double**了。  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202103180005.png)  

所以解决方法是上来就把pretrained model尺寸限制住，这样decouple之后weights相比baseline就不会多。  

### Appendix  
<font color='Silver'>晦涩难懂的CDG图示和计算方法。</font>  
这边似乎因为CDG/cosine similarity有点难算所以搭了个简单的模型做的实验？  
对更高精度的拆分/BinaryDuo-Q进行了分析，因为这两种方法对应初始的模型参数被砍了若干倍，所以最后的结果不好（可以理解，因为相当于初始化弱了很多），作者给的解释非常晦涩：  

```  
We suspect that the cause of this phenomenon is that the local minimum value 
that was found by the pretrained model becomes less useful when the model is 
more deformed through decoupling.
```  

最后不忘boost一下CDG/踩一下ESG：相同计算资源下CDG和真实mismatch更接近一些（需要深入研究~~真有人会跟这个flow吗~~）  

## Remained Questions
CDG/cosine similarity没有深究