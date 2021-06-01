# 2021/6/3结果反馈与讨论记录  

2021/6/1  

## *stochastic rounding STE实验补充
实验条件：  
* 在三层32neuron-MLP上测试，预训练（如有）采用 bs = 16000 的 batch（数据i.i.d.采样自N(0, 1)）训练 500 step至 loss 收敛；  
* FP weight & Binary activation；  
* stochastic rounding STE修改成，在更新前后inference时采用普通的sign函数，在更新阶段的inference采用sr-STE（相当于为普通的STE引入一定随机性）  
* 后续STE/sr-STE梯度下降时 bs=1024 (在10个不同的batch上分别测试，以期消除部分随机性)，lr在从 1e-5 开始，以 1e-5 为间隔，至 0.5 的区间上扫描，取使得loss最小的值；  
* sr-STE grad的计算方式是，inference时对activation的量化采用stochastic rounding，计算出带有扰动的grad，将N次采样（1-10次采样）得到的grad累加起来取平均并normalize。  

### *Updated sr-STE on raw model  
log可参考[这个txt文件]()。  
下面的曲线都是更新前后的loss值，该值越小越好。  

* 情形一(sr-STE随采样次数增多效果逐渐变差)：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202106010001.png)  

上图是未预训练的、固定sr-STE（只在计算grad时取sr）、第一个batch上的结果，表现出了sr-STE updated loss随着采样数增加也逐渐增加的特性。  

* 情形二(sr-STE随采样次数增多效果振荡)：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202106010002.png)  

上图是未预训练的、固定sr-STE（只在计算grad时取sr）、第四个batch上的结果，采样次数增加

* 情形三：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202106010003.png)  

### *Updated sr-STE on pretrained model  