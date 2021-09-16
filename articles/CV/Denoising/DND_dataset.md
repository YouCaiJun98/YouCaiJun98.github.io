# Benchmarking Denoising Algorithms with Real Photographs  

2021/9/15  

来源：CVPR17  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/CV/Denoising/DND_dataset.pdf)的包括ipad标注的pdf版本。  
作者是TU Darmstadt的Tobias Plotz和Stefan Roth，挺有价值，但是难懂。  

**Summary**：知识密度很高的一篇文献，从里面接触了图像噪声的一些信息。本篇文献提供了一个新的Raw Real Image数据集（方法是将低ISO长曝光时间的图片当做准纯净图像，对应高ISO短曝光时间的图片当做噪声图像，保证二者乘积相同），并且认为之前的数据集获取纯净图像的方式有问题，提出了制作纯净图像的pipeline，包括Linear intensity changes（对齐感光度、曝光时间误差）、Lucas-Kanade Approach（Spatial misalignment）、Low-frequency residual correction（避免光照随时间变化）。后面有对pipeline有效性的证明实验，但是没有相关背景知识，没看懂，暂时也不需要懂。        

**Key words**：   
* 噪声原理  
* 真实图像(raw)去噪benchmark  

**Rating: 4.0/5.0** 还是比较有价值的，感觉对理解噪声很有帮助。  
**Comprehension: 2.0/5.0** 但是后面方案有效性的证明缺少太多preliminary所以没有看懂（目前对我而言不重要）。  

## Abstract   
* 将不同ISO/Exposure Time（两者乘积相同）的图像对作为纯净-含噪图片对。  
* 进一步引入了处理“纯净图像”的pipeline，用一种线性强度变换（linear intensity transform校正了因为相机震动等因素产生的图像像素不匹配、exposure param不准确的问题，并去除了光照强度变化变化的影响（附原文：  

```  
We capture pairs of images with different ISO values and appropriately adjusted exposure times, where the nearly noise-free low-ISO image serves as reference. To derive the ground truth, careful post-processing is needed. We correct spatial misalignment, cope with inaccuracies in the exposure parameters through a linear intensity transform based on a novel heteroscedastic Tobit regression model, and remove residual low-frequency bias that stems, e.g., from minor illumination changes.
```  

