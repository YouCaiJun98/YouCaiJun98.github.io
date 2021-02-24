# bnn_ops.py  

2021/2/22  

包括：  
* BirealBinaryActivation(torch.autograd.Function)  
* StraightThroughBinaryActivation(torch.autograd.Function)  
* Binarize(torch.autograd.Function)  
* BinaryConv2d(nn.Module)  
* SkipConnectV2(nn.Module)  
* BinaryConvBNReLU(nn.Module)  
* ResNetDownSample(nn.Module)  
* BinaryResNetBlock(nn.Module)  
* BinaryVggBlock(nn.Module)  
* NIN(nn.Module)  
类。  

## New Methods
* [torch.ge,gt, etc.](https://youcaijun98.github.io/Langs/Python/Packets/Torch/torch_ge_gt_le.html)  



## Class  
### BirealBinaryActivation  
BiReal原文暂时没看，看完之后再考虑填坑。（似乎对应原文公式(3)？）  

### StraightThroughBinaryActivation  
继承自`torch.autograd.Function`类。  
含有方法：  
* `forward`：根据传入参数`method`选择对`inputs`的处理方法，`sign`或者`float`。  
* `backward`：需要传入梯度，然后原样返回。  

### Binarize
继承自`torch.autograd.Function`类。  
含有方法：  
* `forward`：传入参数包括`ctx, x, fp_weight, binarize_cfgs`。其中`x`表示activations，`fp_weight`表示全精度的weights，`binarize_cfgs`包括`bi_w_scale`（scaling factor related）和`bi_act_method`（activation量化方法）。Binarize activations。（有点问题，scale没改过来？）Binarize weights，包括不同的scale（scaling factor），`scale == -1`应该表示fp weights，通常不用，所以没写完？`scale ！= -1`的方式都需要对weights进行clamp（±1）截断，`scale == 0`应该就是正常BC的做法（没有scaling factor），`scale == 1`应该是XNOR-Net中的scaling factor，`scale == 2 or scale == 3`应该对应的是BiReal中的scaling factor计算方法。最后把`old_x, fp_weight, bi_weight, mean_val, scale`存到ctx里。  
* `backward`：传入参数包括`ctx, g_x, g_bi_weight`。这里似乎已经算出了`gradient of x(g_x)`，只对梯度进行一个clip？（逐元素比较，绝对值大于门槛的就clip成0）**奇怪的是gradient clip的门槛也要乘scaling factor？**  

### BinaryConv2d
继承自`torch.nn.Module`类。  
含有方法：  
* `__init__`：初始化，调用`BinaryConv2d`的父类的初始化方法，用`torch.zeros`开个全精度参数的数组，在(0,0.05)上`normal_`初始化，再初始化bias。  
* `forward`：写一个`binarize_cfgs`字典出来，binarize activations&weights，然后调用`torch.nn.functional.conv2d`用**binary weights**对**binary activations**做卷积。  

### SkipConnectV2
继承自`nn.Module`类。  
根据C_in、C_out、stride确定并执行操作，目的是对齐通道。  
含有方法：  
* `__init__`：~~`self.conv_ds`是什么的bool变量？似乎是支持任意channel的？C和C_out不用对齐？对输入的activations做group conv？~~ A：`conv_ds`表示对于downsample层，是用一个conv层来表示downsample，还是直接过一个avgpool2d然后在channel维度上复制一遍。**判断流程**：先判断stride是不是2：`if self.conv_ds`->op1=`nn.AvgPool2d(2)`，op2=`XNORGroupConv`；else判断C_in和C_out是不是相等或2倍关系，（这边写得感觉有点烂...）如果是的话就取average_pool（1个或2个，看expansion）；`stride == 1`就op=`Identity()`。  
* `forward`：**非静态方法**。按照上面反着来  
    * `self.stride == 1`则op=`Identity()`  
    * `self.stride == 2`  
        * `self.conv_ds`则op1=`nn.AvgPool2d(2)`，op2=`XNORGroupConv`  
        * `not self.conv_ds`
            * `self.expansion == 2`则op1=op2=`nn.AvgPool2d(2)`，结果concate  
            * `self.expansion == 1`则op=`nn.AvgPool2d(2)`  

### BinaryConvBNReLU  
基本的binary conv bn relu block。  

```python  
"""
xnor-conv-bn-relu should be the basic building block and contain all the possiible ops

It should contain the args:
    - ch disalignment arrangement
    - shortcut_op_type(simple parameter-free shorcut)
    - reduction_op_type(avgpool2d / factorized reduce)
    - layer-order
    - relu
    - group
    - dilation
    - binary_conv_cfgs
        - bi_w_scale
        - bi_act_method
        - bias(zero-mean)

"""
```  

含有方法：  
* `__init__`：正常初始化，要注意的是`shortcut`只有在特定的情况下（对应Line382-Line390）才能用。支持`"conv_bn_relu", "bn_conv_relu"`两种layer order。目前似乎只支持`self.shortcut_op_type == "simple"`。`self.bn`的初始化要考虑layer order（对应不同的channel数目）。根据`stride`初始化`self.convs`。根据`self.shortcut_op_type`初始化`self.shortcut`。  
* `forward`：在最开始或后面过BN，最后过relu（不重要）。`if self.stride == 2 and self.reduction_op_type == "factorized"`下面，~~`"factorized"`指什么？~~ A：当某一个operation是reduction的时候(stride=2)，原始的resnet提出了一种叫做factorzied reduce的结构。这个模块等价于一个stride=2,expansion=2的卷积； 它是用了两个stride=2的expansion=1的卷积，他们实际apply的时候，kernel在原图上移动的区域，相差了一个像素(看图里青色和紫色的部分)；然后把他们的结果concat起来，最后输出的还是2C。  
~~`x.size(2)`是什么？channel out？~~  
A：推测是w or h，这里应该假定了w==h。  
pad方式也不是很懂。  
A：其实这里已经规定了stride=2了，所以就算padding最多也只padding1...然后pad第二个传入参数是指定pad的位置（(1,0,1,0)表示在上方左方pad） **这里我认为padded x经过factorized reduction之后产生的activations w×h是一样的，虽然内心非常不安（主要是op后的尺寸能否对应）。** 两个conv后的activations能不能直接和同一个shortcut绑在一起的疑惑暂时消除了，因为与其担心这个**不如担心对pad后的x进行卷积产生的影响了。（无关紧要）**  
~~shortcut是直接加在一起？不是concate？~~  
A：shortcut的前后tensor shape是不变的，所以shortcut是tensor按元素相加。需要注意的是加shortcut的时候是让padded x过shortcut再concate，所以不会有w*h上对应的问题。  

### ResNetDownSample






## 问题集合  
~~1. `forward`和`backward`中出现的`ctx`是什么意思？~~  
A1：解决了，在[这里](https://youcaijun98.github.io/Langs/Python/Packets/Torch/ctxvesusself.html)给了详细的区分。  
~~2. 与Question1相关联，为什么在`StraightThroughBinaryActivation`里面需要在`forward`里把`inputs`和`method`存起来，`backward`里拿出来又不用？~~  
A2：可以用，没用到。但是不是存进去必须要取出来呢？  
~~3. `apply`的用法？是torch专门的方法吗？~~  
A3：确实是torch的方法。`apply`是`torch.nn.functional`的用法，因为我们写class的时候是继承了`torch.nn.functional`这个类的，我们相当于是重写了`forward`和`backward`函数；所以调用这个函数的时候应该用apply作为标准调用方式，只调用`xxx.forward`的话不确定会不会调用对应的`backward`  
~~4. Line120以下，对梯度clip的时候门槛也要乘scaling factor吗？~~  
A4: 按照正确定义应该是需要给threshold乘上scaling factor的。  
~~5. Line217为什么full precision weights初始化的时候不用`.cuda()`，bias的初始化用？~~  
A5：这个可能纯粹是写的时候没注意…后面会用`model.to(device)`把所有的module的attribute都搬到gpu上  
~~6. Line259`XNORGroupConv`在哪？请见其他`class SkipConnectV2`的问题。~~  
A6：没有改过来的历史遗留问题。`XNORGroupConv`貌似是之前的接口，可以看作和现在`BinaryConv2d`相对应。`class SkipConnectV2`中的问题已在之前回答过了。  
~~7. `BinaryConvBNReLU`的问题。~~  
A7：因为shortcut的前后tensor shape是不变的，所以**shortcut是tensor按元素相加**。  

## To-Do
* `nn.Module`是个重要的类...需要仔细研究。  
* `nn.Parameter`也很重要。。  
* `ModuleList`需要研究  


