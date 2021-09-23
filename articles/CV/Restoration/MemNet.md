# MemNet: A Persistent Memory Network for Image Restoration  

2021/9/20  

来源：ICCV17  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/CV/Denoising/AINDNet.pdf)的包括ipad标注的pdf版本。  
作者是Nanjing University of Science and Technology的Ying Tai, Jian Yang, Xiaoming Liu, Chunyan Xu等人。  

**Summary**：一篇很一般的文章，能发真不是因为时间早吗...这篇文章的贡献纯粹是module design，设计了一种跳跃连接非常多的building block - memory block，认为之前的网络很难处理网络加深之后的长距离依赖问题，扯了很多生物学上的东西，然后又加了很多block wise的跳跃连接，每个block的最后有一个gate unit来逐层给长/短距离feature分配权重。说是“循环结构”都是抬举它，这根本就是块堆叠， 哪来的自信说是recursive...升级版本中用了一种multi-supervised方式，即网络的很多中间结果参与构建最后的图像，这个还是第一次见到，虽然一眼看不到作用（为什么没在摘要里提）。然后是经典的restoration multi-task，做了denoise、SISR、JPEG deblocking。  

**Key words**：  
* Module Design / Channel Attention  
* Residual Learning  
* Multi-supervised  

**Rating: 3.0/5.0** 一般，后面引的人还不算少。  
**Comprehension: 4.5/5.0** 挺好懂。   

三张图总结全文：
* Memory block    
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109200009.png)  

* 网络总体结构  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109200010.png)  

* Multi-supervised  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109200011.png)  

## 3. MemNet for Image Restoration  
3.1. Basic Network Architecture和3.2. Memory Block中有很多simple的描述...就是和想象中那样...  
* 比较有描述力的三个式子：  
    * $$B_m^{short}=[H_m^1,H_m^2,\ldots,H_m^R]$$  
    * $$B_m^{long}=[B_0,B_1,\ldots,B_{m-1}]$$  
    * $$B_m^{gate}=[B_m^{short}, B_m^{long}]$$  
* Gate unit就是个1*1 conv  
* 3.3. Multi-Supervised MemNet  
    * 每个block都会参与重建：$$\mathbf{y}_m=\hat{f}_{rec}(\mathbf{x},B_m)=\mathbf{x}+f_{rec}(B_m)$$，其中$$\{\mathbf{y}_m\}_{m=1}^M$$表示M个中间结果。  
    * 最后的结果通过这些中间结果重建：$$\mathbf{y}=\sum_{m=1}^Mw_m \cdot \mathbf{y}_m$$  
    * 多监督loss如下：  
    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109200012.png)  
* 3.4. Dense Connections for Image Restoration  
一些频谱分析，意在说明中高频信息在深度网络中丢失，而这种密集连接可以挽救，甚至画了很多吓人的图，但我倾向于不信。  
* 4. Discussion中有对Highway Network, DRCN, DenseNet的对比  

## 5. Experiments  
提到了RED一种**post-processing**：翻转，处理若干次后加起来求平均。  
关注的点还是ablation, 性能, model complexity, speed这些，无聊。倒是有一张画得不错的图：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109200013.png)  