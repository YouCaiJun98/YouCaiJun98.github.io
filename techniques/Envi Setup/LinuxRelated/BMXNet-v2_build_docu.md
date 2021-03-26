# BMXNet-V2 building record  

2021/3/26  

部署别人的项目是真难，配环境配到头秃。~~以后我有了成果一定也整点难配的环境，一报还一报~~  

* 用bash命令`pwd`可以查看当前路径。  

* 使用[`find`命令](https://www.runoob.com/linux/linux-comm-find.html)来查找文件。这里有个[很NB的博客](https://blog.csdn.net/l_liangkk/article/details/81294260)详解了用法。  

* linux下压缩tar.gz格式的命令是`tar -zcvf 目录文件名.tar.gz 目录文件名`，解压命令是`tar -zxvf 目录文件名.tar.gz`，里面`-zxvf`是什么含义没有追究。  


总算进行到了`cmake .. -G Ninja`的一步了！

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202103260003.png)  

首先出现的问题是MKLML下不下来：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202103260004.png)  

这个问题尝试解决了很多次，包括在本地ssh config添加`RemoteForward`词条，但是添加了之后服务器也不走我的梯子，梯子流量一直没有变化。非常痛苦。上午（那时候注释掉了`RemoteForward`）用学校的网还可以下（虽然很慢），为什么下午删掉build文件夹重新`cmake`就下不下来了呢？更不用说一直没有卵用的梯子（为什么设置一样但是我不能通过梯子翻墙呢？甚至连搜索关键词都不知道，找到的都是远不相关的东西）。  

可是下载完MKLML之后很快就出现了一个新的错误，找不到doxygen（本blog写于第一次`ninja`失败，删除build文件夹后重新`cmake`时，第一次`cmake`的时候确实也出现了这个错误，但是当时感觉生成了build文件就没有关系了，所以这可能是最后`ninja`失败的诱因（之一？？））：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202103260005.png)  

解决方法：  

```bash  
sudo apt-get install doxygen
```  

讲道理，这东西没用过的人怎么知道要提前装啊，tutorial写得实在不详细..（是我菜了）  
将这次`cmake`的log存到了[这里]()。  






### Make CUDA great again  
在`sxs-eva8`上部署BMX-Net，但是到了下面的`ninja`这一步时：  

```bash  
# build the project
mkdir build && cd build
cmake .. -G Ninja
ninja
```  

出现了错误。具体来看，从200+开始的build项目就开始打印不祥的log了，主要还是一些warning，在stackoverflow里查了下，说这种warning **potentially produce wrong code**而且debug起来会**非常痛苦**。但是事情到这里还算**可以接受**，因为从第570个build term开始出现了**hard error**，直接把build过程给**崩掉了**（大段的log被顶掉了，现在reproduce error只能出现这些最hard的问题了）：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202103260001.png)  

因为上面说找不到`/usr/bin/ld:`目录下的`-lcuda`，看到`**cuda`关键字就想会不会是CUDA出了问题。这个container开通以来一直没有跑过训练，极有可能环境配置有问题，而且`/usr/bin/ld`本身又是个二进制文件，这谁懂啊：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202103260002.png)  

所以先解决最简单的问题，看看CUDA是不是健在。  
尝试bash`nvcc -V`，果然出现了command not find的问题了。所以要设置环境变量，bash`sudo vim /etc/profile`（这里**sudo权限**很重要，不然profile只是个可读文件），在末尾添加：  

```bash  

export PATH=/opt/cuda-10.0/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/opt/cuda-10.0/lib64\
                                ${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```  

然后`source /etc/profile`或者重新登一下eva就可以了。  
重新测试`nvcc -V`，能正确输出log了：  

```bash  
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2018 NVIDIA Corporation
Built on Sat_Aug_25_21:08:01_CDT_2018
Cuda compilation tools, release 10.0, V10.0.130
```  

