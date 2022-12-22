# BATS: Binary ArchitecTure Search

2021/3/11  

这篇文章看了足足四天。。每天看一点，所以最近都在干啥...  

来源：ECCV2020  

resource：自己[收录](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/ModelCompression/BNN/BATS%20Binary%20ArchitecTure%20Search.pdf)了一下。  

作者是Adrian Bulat、Brais Martinez和Georgios Tzimiropoulos，~~第二个人的名字和XNOR-Net的作者（Rastegari）好像~~。  

总结一下，感觉全文**挺柴**的，**没什么特别insightful的地方**，有点BNN+NAS**手速文**的感觉。  

文章贡献（if any），将NAS应用到BNN中需要：  
* 设计Binary搜索空间（改op）。  
* 在Darts的gumbel里加个temperature来稳定搜索的topology（避免skip坍缩）。  
* 二值化策略，在搜索的时候二值化activations（因为更困难），在训练的时候同时二值化activations和weights。  

## Pieces of Insight
### 4.1 Binary Neural Architecture Search Space  
* real-valued的op不一定适用于binary空间，i.e. depth-wise conv, 1 × 1 conv, bottleneck block.  

### 4.2 Search Regularization and Stabilisation  
在Gumbel里加temperature以变得更加discriminative.  

### 4.3 Binary Search Strategy  
在search阶段用FP weights和binary activations，在evaluation阶段用both binary activations和weights.  

### 6.1 Architecture search  
```  
Furthermore, since the down-sampling operation compresses the information
across the spatial dimension, to compensate for this, the reduction cell tends
to be wider (i.e. more information can flow through) as opposed to the normal
cell which generally is deeper.
```  

normal cell通常更深，而down sample层会压缩流入的信息，所以通常更宽。common sense.  

