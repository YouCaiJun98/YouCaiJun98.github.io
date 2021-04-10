# 2021/4/9 会议记录  

2021/4/9  

Mr.Chen's 只言片语:  
* BinaryDuo： 1.数值梯度  无穷多时间/样本要比STE好。  
              2.appendix H & 4.1  

    weight空间是离散的（所以需要平滑）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104100001.png)  

    看一下这个问题是否存在（做一遍binaryduo的实验验证一下）-> 类NES方法search ->  

* NES  
    e_i是方向，相减是下降的大小：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104100002.png)  


* 验证benchmark  estimator （可行的方向）  
* 低维的toy，看看STE为什么不行  

妃哥：
* clean code base（摘出来） / NonAWNAS
* 实现一下gradient functions /工程上完善
* 为什么要smoothed loss？需要问一下陈老师

天辰：  
* 数值梯度方法的库？（自己搭一下）  
* reference 4 code base:https://github.com/A-suozhang/meanteacher-pytorch/blob/master/utils.py  

## To-Do  
- [ ] 1. 对齐配置跑一下BMXNet XNOR实现（早期epoch对齐，eva7）  
- [ ] 2. 搭toy model（类BinaryDuo，两三层CONV，FP weights & Binary activation, priority ++）  
- [ ] 3. 搭code base  
- [ ] 4. 扩大width看一下accuracy。  
- [ ] 5. 看一下陈老师给的NES的文章，和他新给的另一篇文章。  




## Questions  
Q1:为什么要做smooth -> gradient 方向更丰富（而不是0/1）？
Q2：BMXNet的weight initialization？（我们似乎是norm，忘记BMXNet的initialization方法了。   

