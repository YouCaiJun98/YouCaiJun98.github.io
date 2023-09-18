# DAQ: Channel-Wise Distribution-Aware Quantization for Deep Image Super-Resolution Networks  

2022/1/11    

来源：WACV22  

一句话总结：这篇文章出发点是激活值不同通道分布不均，且会随着输入图像发生变化（和我之前的想法非常接近，但是我是从不同图像对应不同聚类，进而对应不同scale想的，所以下午说得有点问题），所以他们做的是【per-channel的act量化】。具体而言，他们给每个act通道做了中心化（我理解就是手动BN）。一般act与w都per channel，算完conv乘，在kernel-wise加的时候就得把act的scale乘回来（变回FP），再channel-wise FP加，得到输出act的一层，再apply卷积核对应的scale。为了解决act per-channel之后FP操作爆炸的情况，他们进一步量化了统计参数（甚至出现了统计参数的统计参数的奇葩情况），改变了计算流，把FP操作堆到了Conv channel-wise加，尽可能保留了整形操作  