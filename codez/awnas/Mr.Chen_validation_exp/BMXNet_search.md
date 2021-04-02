# Comparation between BMXNet & AWNAS  

2021/4/2  

摸了好久，一直不敢去看这个代码，今天总算鼓起勇气去看了，就算自己害怕成长，差也要交不是。  

## Model Body  
首先看一下我们的XNOR Res18和BMXNet实现的Res18有什么不同。  
### Stem  
比较的开始就发现了不同，出现在Stem上：  
 
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104020001.png)  

BMXNet的Stem Conv层显然更大一些，**用了7x7的kernel**，具体的顺序是`BN-Conv-BN-ReLU-Maxpooling-BN`，这和原文描述的把一个Conv层拆成两个小Conv层的设置不一样啊。  
AWNAS中的Stem Conv是拆成两个3x3的小kernel，具体顺序是`Conv-BN-ReLU-Conv-BN`。  

### Normal Cell  
果然cell里也出现了非常明显的不一致，甚至感觉非常合理。  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104020002.png)  

~~AWNAS中的一个cell很大（而且有两个op？我需要好好看看ResNet18的结构了），相比之下BMXNet的cell就显得非常干瘪。~~ 原因找到了，借用一下一张[网图](https://www.baidu.com/link?url=pI-qz1Ametz0nfrcyNZlnQT7wIJyOzWDegELJlIzYbA6A7OVyPYOdyDEdTv14AOm&wd=&eqid=b11c89e4000642af000000066066cd1b)（准确性存疑），AWNAS是把skip connection连接的层layer合成了一个cell，BMXNet是裸着把Conv layer堆在一起：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104020003.jpg)  

使用`ipdb`打断点看[net variable]()以及检查[model.log]()发现了一些**异常**，需要看代码确认一下：  
* 



### Reduction Cell

