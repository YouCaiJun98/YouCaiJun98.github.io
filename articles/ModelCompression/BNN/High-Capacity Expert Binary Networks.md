# High-Capacity Expert Binary Networks  

2021/3/17  

来源：ICLR2021  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/BNN/BATS%20Binary%20ArchitecTure%20Search.pdf)的包括ipad标注的pdf版本。  

作者又是Adrian Bulat、Brais Martinez和Georgios Tzimiropoulos，这仨哥们还真能水文章啊（呜呜，还能中顶会，数据还好看~~就是不知道数据保不保真~~）。  

**Summary**：文章挺有用的，感觉 **rating 4/5** 的样子？主要的思路是一种类似ensemble的*expert*/conditional conv，用input通过gate func选一个expert出来，然后扩大width，通过group conv抵消掉增大的op num，还有就是*半自动*地设计了binary network的结构？但是**没有看实现细节**（我也不实现是吧）。  

文章的贡献有：  
* 增加 model capacity ，提出Expert Binary Convolution，实际上是一种**Conditional Computing**的方法（又非常像ensemble，但总之非常有道理）；  
* 增加 representation capacity，增加width（accu ++）的同时，引入group conv（accu -）来平衡地提点；  
* Network design，似乎是做了很多对比实验，~~没见到有什么启发~~。  

### 2.2 Conditional Computations  
有点打开新世界的窗户的感觉，这种方法总体很有道理，背景review的时候说了四种（后两种有点意义不明）现有的工作，1）skip-connect: bypass some part of a model 2)split dataset & seperately train different part.  

## 3 Background & 4 Method
训练的时候也是**2-Stage**进行的。每个expert也是通过正交的数据训练的。训练的时候先训一个expert，再用这个expert作为初始化。在**4.2**里讲了group conv，这里是用width expansion涨点，然后用group conv把op num拉回来，**非常聪明**。  

### 4.3 Designing binary networks  
讲得有点意义不明的感觉...就是很多东西堆砌在一起？小标题有`Effect of block arrangement`(就是N~0~N~1~N~2~N~3~保持complexity不变，具体分布排列组合测点数据，就这？)、`Depth vs Width`(preference, known)、`Effect of aggregation over groups`(说在grouped conv layer后接 1x1 conv layer without group可以涨点)、`Effect of groups`(用group conv会降点)。  

## 5 Comparsion with SOTA  
说用4x experts只占了2x storage。  

## Appendix  
#### A.2.1 Real-valued Downsample decomposition  
说width ↑ 也会影响downsample里的op num（合理），解决方法是把一个strided conv拆成两个小conv（似乎没说在哪层里用stride?）  

#### A.2.3 Data augmentation  
more aggressive augmentation leads to consistently better results.  

### A.5 Improved training scheme with stronger teacher  
对狙，说老师↑学生跟着↑。  



