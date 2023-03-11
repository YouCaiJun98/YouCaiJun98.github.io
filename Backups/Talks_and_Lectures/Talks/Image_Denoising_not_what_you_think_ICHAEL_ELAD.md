# Image Denoising - Not What You Think  

2023/2/18  

by Prof. Michael Elad  

分成以下部分：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218224123.png)  

* NN the Saver:  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218225149.png)  

* 喷了现有的NN for LLCV架构设计，要么是挪用已有的架构加微调，要么是堆参数量：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218225844.png)  

* classic + NN可以改善模型的可解释性：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218230039.png)  

* denoiser的新应用：  
    * 解非适定问题  
    * 做图像生成  
    * IQA？  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218230142.png)  

1. 解非适定问题：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218230335.png)  
* 可以将denoiser作为regularizer，反复用来求解非适定问题：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218230736.png)  

* 非适定问题的求解可以解释成反复利用denoiser优化：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218231036.png)  

* plug-and-play flow的改进：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218231631.png)  

2. 做图像生成：  
*不太懂，直接记录：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218232346.png)  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218232438.png)  

3. 做高视觉还原：  
* 解释了为什么生成的图像很模糊 -> MMSE准则下会把含噪图像拉到图像流形的均值位置：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218232803.png)  

* 在视觉效果（sharp, crisp）和最小"distortion"之间有个trade-off：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230218233839.png)  

