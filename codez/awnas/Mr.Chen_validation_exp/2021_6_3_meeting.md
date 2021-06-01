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
log可参考[这个txt文件](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/codez/awnas/Mr.Chen_validation_exp/sr_ste_on_raw_toy_model.txt)。  
下面的曲线都是更新前后的loss值，该值越小越好。  

* 情形一(sr-STE随采样次数增多效果逐渐变差)：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202106010001.png)  

上图是未预训练的、固定sr-STE（只在计算grad时取sr）、第一个batch上的结果，表现出了sr-STE updated loss随着采样数增加也逐渐增加的特性。  

* 情形二(sr-STE随采样次数增多效果振荡)：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202106010002.png)  

上图是未预训练的、固定sr-STE（只在计算grad时取sr）、第四个batch上的结果，采样次数增加并不会一致地使loss改善，而是出现了振荡。  

* 情形三(sr-STE随采样次数增多效果逐渐变好)：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202106010003.png)  

上图是未预训练的、固定sr-STE（只在计算grad时取sr）、第二个batch上的结果，随着采样次数增多，loss逐渐下降。  

一些讨论：  
* 在训练初期使用Fixed sr-STE总可以使loss下降(相比原始loss)，而且在10个测试的batch上，Fixed sr-STE的更新结果总要优于vanilla STE（有点奇怪，这可能是初始化、样本随机性造成的，且不清楚在真实模型上是否有此表现）；  
* 增加采样数不会出现loss一致改善的情况，这应该是sr随机性造成的 -> 不同的采样应根据其效果有不同的重要性/加权系数，而不是均匀加权。  

### *Updated sr-STE on pretrained model  
log可参考[这个txt文件](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/codez/awnas/Mr.Chen_validation_exp/sr_ste_on_pretrained_toy_model.txt)。  
下面的曲线都是更新前后的loss值，该值越小越好。  

* 情形一（sr-STE的结果和vanilla STE接近）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202106010004.png)  

上图是预训练的、固定sr-STE（只在计算grad时取sr）、第一个batch上的结果，vanilla STE和sr-STE都能产生梯度下降，当MC sample上升的时候sr-STE的效果(0.2696472704410553)可以非常接近vanilla-STE(0.26964688301086426)。  

* 情形二（sr-STE的结果差于vanilla STE）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202106010005.png)  

上图是预训练的、固定sr-STE（只在计算grad时取sr）、第二个batch上的结果，sr-STE随着sample数目增多反而会恶化最后甚至不如原始loss的情形。  

* 情形三（sr-STE的结果优于vanilla STE）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202106010006.png)  

上图是预训练的、固定sr-STE（只在计算grad时取sr）、第三个batch上的结果，sr-STE随着sample数目增多效果渐好最后优于原始loss的情形。  

在10个batch上得到的一些统计数字：  
* 不同MC sample数下sr-STE更新优于vanilla STE（只要某一sample数下sr-STE优于vanilla STE即计入），频次8/10；  
* vanilla STE可以使loss下降(7/10)；  
* sr-STE更新后loss始终低于原始loss(8/10)；随sample数增多，sr-STE更新后loss由低于原始loss变为高于原始loss(1/10)；随sample数增多，sr-STE更新后loss由高于原始loss变为低于原始loss(1/10)。  

一些讨论：  
* 引入随机性的STE在训练末期有较高的概率仍能找到loss下降的方向，且在大部分时候表现要优于vanilla STE（指loss下降更多，但这可能是： ①batch数较少导致的随机性 ②模型过于简单，在真实模型上不适用 导致的）；  
* 在一个batch上可以产生更好的loss下降，是不是lr sweeping带来的增益？在一个batch上sr-STE优于STE（如是）在全局的更新上会有何种表现？真实模型上又会有怎样的表现？  
