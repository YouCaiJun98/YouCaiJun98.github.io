# Deep Learning for Image Denoising: A Survey  

2021/7/13  

来源：不知名杂志？这玩意真能投中吗？不清楚。  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/CV/Denoising/Deep%20Learning%20for%20Image%20Denoising%EF%BC%9AA%20Survey.pdf)的包括ipad标注的pdf版本。  
作者是哈工大博士Chunwei Tian。  

**Summary**：很烂的一篇综述，看了简直浪费时间，junk level。  

**rating：0.1/5.0**  
**comprehension：4.8/5.0**  

文章的贡献有：  
* 没啥贡献，只有一点background knowledge。  

## 1 Introduction  
一点零碎的知识：  
* 图像处理领域的（典型）应用有：image segmentation, image classification, object detection, video tracking, image restoration, action recognition.  
* 传统的图像去噪方法有以下两个问题：  
    * 这些方法是非凸的，需要人工调整参数；  
    * 这些方法在测试阶段有一个复杂的优化过程(原文`these methods refer a complex optimization problem for the test stage`),有很高的计算代价。  

## 3 Image Denoising  
* 一些用了图像先验的传统方法：Markov random filed (MRF) method, BM3D, NCSR和NSS。  
* discriminative learning schemes：  
    * A trainable nonlinear reaction diffusion method was proposed and used to learn image prior(Shrinkage fields for effective image restoration, CVPR14)  
    * A cascade of shrinkage fields fuse the random field-based model and half-quadratic algorithm into a single architecture(Ffdnet: Toward a fast and flexible solution for cnn based image denoising, TIP18)  
    * 但是它们也有两个问题：  
        * 它们被限制在某种形式的先验上(specified forms of prior)  
        * 不能用一个model处理盲去噪问题  
* 可以看的经典文章：DnCNN、 FFDNet、 IRCNN。  
* 简单的梳理：  

```  
In addition, many other methods also obtain well performance for imagedenoising. For example, fusion of the 
dilated convolution and ResNet is used for image denoising. It is a good choice for combing disparate 
sources of experts for image denosing. Universal denoising networks for image denoising and deep CNN denoiser 
prior to eliminate multicative noise are also effective for image denoising. As shown in Table 1, deep 
learning methods are superior to the converntional methods. And the DnCNN method obtains excellent performance
for image denoising.
```  

## 4 5  
后面都是些废话或者过时的话了。  

