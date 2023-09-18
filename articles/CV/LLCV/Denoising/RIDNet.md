# Real Image Denoising with Feature Attention  

2021/9/13  

来源：ICCV19 Oral  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/CV/Denoising/RIDNet.pdf)的包括ipad标注的pdf版本。  
作者是The Australian National University的Saeed Anwar和Nick Barnes，写作水平只能说是灾难级，瞎起什么破名——但是人家ICCV Oral。  

**Summary**：一篇还可以的图像去噪文章。指出现在的基于CNN的图像去噪器对真实噪声表现不行，且需要多个阶段（噪声估计-噪声去除），所以提出了一个**单阶段**、**真实图像**、**盲去噪**模型，感觉主要贡献还是**modular design**(很一般)和首次引入**feature attention**（这个用处还很多，后面很多工作都整个这种channel-scale module）。        

**Key words**：   
* module design：EAM（一般）  
* feature attention：本质上也是module design，用处很多  

**Rating: 3.5/5.0**  
**Comprehension: 4.5/5.0**  

两张图总结模型结构：  
* 总体结构与EAM：  
    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109130009.png)  
* Feature Attention/Channel Attention：  
    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109130010.png)  

## 1 Introduction  
感觉介绍都在哪里看过哎，为什么捏（字句几乎都一样，离谱）  

### 1.1 Contributions  
自述贡献：  
* 和一般的真实噪声去噪不同，这个是单阶段的（10% off？）  
* feature attention（这确实是后面用的很多的东西）  
* modular network，可以解决网络变深梯度消失的问题（这完全是residual的贡献吧）  

## 2. Related Works  
包括但不关心：传统方法/CSF/DnCNN与IrCNN/TRND与NLNet/真实图像盲去噪/CBDNet  
* 再次强调事实：一般的真实图像去噪由两个阶段构成：噪声估计和非盲噪声去除  

## 3. CNN Denoiser  
### 3.1 Network Architecture  
* 大框架包括三个部分：  
    * feature extraction, i.e. 第一层Conv，离谱  
    * feature learning residual on the residual module, i.e. EAM（enhancement attention modules）堆叠部分  
    * reconstruction, i.e. 最后一层Conv，离谱  
* 报告了些常用的loss：  
    * l2  
    * perceptual loss  
    * total variation loss  
    * asymmetric loss  
    * 本文的l1 loss  

### 3.2 Feature learning Residual on the Residual  
详解EAM罢了。  
* Residual on the Residual structure(我怀疑指的就是EAM)由local skip和short skip connections组成，之所以叫“residual on residual”可能就是大shortcut套小shortcut吧。  
* EAM又包括三部分：  
    * 第一部分是分叉那一块，用的两路dilated conv接普通conv  
    * 第二部分learning on the features，就是两层卷积  
    * 第三部分features compression，那三层卷积（enhanced residual block (ERB)，喜欢起名是吧），最后一层卷积核1x1    
    * 最后和feature attention module连一块  
    * 一般的conv都是3x3除了ERB最后一层，通道数都是64  
* 接着又介绍了图上部分的两个LSC，分别是内层和外层，用简单的公式表示了下。  

#### 3.2.1 Feature Attention  
**文章出发点**之不同的通道被同等对待，这不合适。  
用feature attention发掘不同通道之间的关系。  
* 图像有低频部分（feature attention）和高频部分（lines edges and texture）  
* 因为Conv只能发掘局部信息而不能用global contextual information，所以先用个global average pooling来表示整张图像的统计特征  
* 用self-gating mechanism来表示通道间的依赖关系，具体是通过soft-shrinkage和sigmoid functions实现的，分别是下面的\delta和\alpha，H_u和H_D分别表示通道缩减和通道上采样：  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202109130011.png)  

## 4. Experiments  
* 训练数据（分成两个track，而不是混在一起）：  
    * 合成数据
        * BSD500  
        * DIV2K  
        * MIT-Adobe FiveK  
    * 真实噪声图片：  
        * SSID  
        * Poly  
        * RENOIR  
* 测试数据  
    * 真实
        * RNI15  
        * DND  
        * Nam  
        * SSID   
    * 合成  
        * classic 12  
        * BSD68(gray/color)  
* 关心的实验：  
    * grayscale noisy images（AWGN）  
    * Color noisy images(AWGN，合成)  
    * Real-World noisy images  
        * 真实图像盲去噪的三个难点：unknown level of noise（没事，你不是盲去噪吗）；various noise sources；噪声spatially variant&signal dependent  
    * 对速度不怎么关心了，只一句话带过。  











