# BNN in CVPRW21 0  

2021/7/9  

网页链接：https://www.youtube.com/watch?v=WDYhzWjNCYI  

分享者是Larq的作者，他们公司好像出了很多相关的产品，比如那个人物检测，有点厉害。  

分享的主旨是“Accuracy会掩盖NN中的一些问题，ImageNet等ML里常见的数据集可能不能反映真实世界的属性”：  

* ImageNet等常用数据集的validation set上取得较高的分数，可能并不能很好地泛化到真实应用中，举了例子：  
    * 现在的数据集可以看作flikr的子集（？），里面有很多随意采出来的图片，不一定适合训练；
    * 在ImageNet上比较好用的KD方法到了Tiny ML上并不适用，数据集之间不同method不一定能够迁移；  
    * 无论量化与否，架构对网络的性能/分类的标准影响很大，比如SpiderNet，由于有skip connect将前面的feature map引到后面，后面分类就用了很多底层语义信息，比如颜色（这显然是不好的），但是精度确有差别，这种差别掩盖了分类本来就不好的本质（这和网络的结构密切相关，比如SpiderNet就会有这样的问题，而QuickNet上的结果相对要好些）。  

* 提出的解决方案：  
    * 迭代式训练，不断敲定出问题的场景，补充数据继续训练；  
    * 关注架构。  

* Bias and Robustness
