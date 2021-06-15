# nics_fix_pytorch rEADING Record  

2021/6/14  

### python中的cls  
转载自[这篇博客](https://www.cnblogs.com/wayne-tou/p/11896706.html).  
* cls含义  
python中cls代表的是类的本身，相对应的self则是类的一个实例对象。  
* cls用法  
cls可以在静态方法中使用，并通过cls()方法来实例化一个对象。  

[这篇参考资料](https://www.zhihu.com/question/49660420/answer/335991541)里有对`@staticmethod`和`@classmethod`更详细的解释。  



### 目前想到的问题：  
1. 这个是对initialized model进行定点的框架吗？似乎也可以读pretrained model进行定点/能只用于inference吗？这里支不支持pretrained model定点后调优？  
2. 因为是按module操作的，所以可以实现mixed-precision：更细粒度？grouped channels？(在quant.py里有个group)  
3. 
