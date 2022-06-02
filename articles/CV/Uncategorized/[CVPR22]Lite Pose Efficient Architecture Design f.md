# Lite Pose: Efficient Architecture Design for 2D Human Pose Estimation  

2022/5/31  

来源：CVPR22  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/CV/Uncategorized/%5BCVPR22%5DLite%20Pose%20Efficient%20Architecture%20Design%20f.pdf)的包括ipad标注的pdf版本。  
作者是韩松组的Yihan Wang, Muyang Li, Han Cai, Wei-Ming Chen, Song Han。  

**Summary**：做了个Efficient Pose Estimation架构设计，通过oracle实验（Gradual Shrinking，逐渐减去网络中的multi-branch支路，效果不减反增）证明经典Pose Estimation结构中high resolution支路存在冗余，设计了个Single Branch的Pose Estimation网络。方法设计上，①提出两种结构设计， fusion deconv head（deconv，但是输入concate不同支路的feature） 和large kernel conv （conv 7*7）弥补single branch的scale variation问题（同一张图里可能有不同大小的人需要估计姿势）；②训练方法上，利用超网（Weight Sharing） + NAS（搜width和输入patch size）训练。  


**Key words**：  
* pose estimation  
* efficient architecture design    

**Rating: 3.5/5.0** 一般，普通的设计，但是有很多的工程量。  
**Comprehension: 4.5/5.0** 挺好懂。   

* Inspirations：  
    - 图像的输入尺寸（patch size）也是可以优化的维度，可以考虑搜索，在适应网络结构 - 减少内存开销间trade-off （独立于网络结构的新维度）；  
    - Multi-scale设计是否有效可再考虑（点名LLCV+U-Net）；  
    - 推理延时不止受Flops影响，还和架构有关  


## Preliminary  
* Position Estimation  
    * 姿势估计，从图像中找出人的关键点（anatomical keypoints，比如elbow, wrist）或者部分（parts），belike：  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202206020010.jpg)  

    * 有**两种主流范式**，**top-down**与**bottom-up**。  
        * 前者先用检测网络把人框出来，再细化位置；（multi-stage）  
        * 后者直接检测关键点，再把人拼出来；（single-stage）  

    * **multi-branch**设计是目前的SOTA设计，用不同branch处理不同scale的图像以解决scale variation问题（同一张图里可能有不同大小的人），belike：  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202206020011.png)  

    * **评价方法**是OKS-based AP (Average Precision)：  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202206020012.jpg)  

## Methods  
* Oracle实验（Gradual Shrink）：**multi-branch设计里high-resolution对应的branch冗余性高**（calls for **single branch** design）  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202206020013.jpg)  

* Design1（结构）：Single Branch PE  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202206020014.jpg)  

    * 但是有问题，single branch不能解决scale variation问题，且难以分辨出离得近的keypoints，由此有  

* Design2.1（op）： Fusion Deconv Head  
    * 本质上是在普通deconv前concate了不同scale的feature  
    * 尽管不refine小scale的特征，但还是跳连地concate在一起  

    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202206020015.jpg)  

* Design2.2（op param）：large kernel  
  - 相比图像分类任务，大kernel卷积对PE影响更大（但是有个界限）  
  ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202206020016.jpg)  

- Design3（训练策略）：用超网（WS）+NAS搜width和input patch  

## Results  
- 大表格  
  
  ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202206020017.jpg)  

  - Input Size 可能有点歧义？  

- 曲线  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202206020018.jpg)  

## Limitations  
- 虽然将1 frame的计算量降低到了1GMACs，但还是放不进MCU（凡尔赛？）  
- **LitePose必须有TVM AutoScheduler这个backend的支持**  

