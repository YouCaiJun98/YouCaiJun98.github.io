# Learning Channel-wise Interactions for Binary Convolutional Neural Networks  

2021/3/30  

来源：CVPR2019  
resource：[github上备份](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/articles/BNN/Wang_Learning_Channel-Wise_Interactions_for_Binar.pdf)的包括ipad标注的pdf版本。  

**Summary**：  
* **Rating：1.0/5.0**
* **Comprehension：2.0/5.0**  
没怎么看懂，但是感觉也不用怎么看懂，这篇文章认为binarized feature maps和real-valued feature maps之间符号的inconsistency是导致accuracy gap的重要原因，因此文章致力于减少这种inconsistency（首先我就不喜欢这个flow）。但是这里有一个需要思考的问题，也就是binary网络和FP网络的表现相差很多，真的可以用full precision的角度来衡量binary model吗？FP的训练方式能否直接作用于binary model？binary model是否一定要对齐FP model？作者为了纠正量化中出现并累积的符号错误提出了一种channel-wise interaction，用同一layer中不同channel作为teacher/student，对bitcount之后的feature map进行修正，并且采用RL的方法进行训练。因为我觉得这个思路本来就有问题（符号一致是否直接意味着性能好？那为什么不直接对FP model进行sign？这不是完全一样了吗？是我理解出了偏差吗？），而且采用的RL方法我不可能去follow，所以简单看看拉倒。  

## To Do  
什么时候有兴趣了/有时间了再来研究一下里面的RL设置吧。  