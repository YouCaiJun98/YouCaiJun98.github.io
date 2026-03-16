# nn.avgpool2d

2021/2/25  

看到了好多`nn.avgpool2d`，但是似乎用法不像我想的那么简单，就对着[官方文档](https://pytorch.org/docs/stable/generated/torch.nn.AvgPool2d.html#torch.nn.AvgPool2d)简单看了看（抄了抄）。  

## nn.avgpool2d

```python  
torch.nn.AvgPool2d(
    kernel_size: Union[T, Tuple[T, T]], 
    stride: Optional[Union[T, Tuple[T, T]]] = None, 
    padding: Union[T, Tuple[T, T]] = 0, 
    ceil_mode: bool = False, 
    count_include_pad: bool = True, 
    divisor_override: bool = None
    )
```  

作用是对由多个输入平面（input planes）组成的输入信号应用2维池化。  
最简单的情况，输入尺寸为$$(N, C, H, W)$$，输出尺寸为$$(N, C, H_{out}, W_{out})$$，`kernel_size`为$$(kH, kW)$$的输出可以表示为：  
$$out(N_i, C_j, h, w) = \frac{1}{kH * kW} \sum_{m=0}^{kH-1} \sum_{n=0}^{kW-1} input(N_i, C_j, stride[0] * h + m, stride[1] * w + n)$$  

如果`padding`不是0，那么输入会自动在每一边都非显式地（implicitly）零填充`padding`个点。  

对应的输入输出维度为：  
* 输入维度：$$(N, C, H_{in}, W_{in})$$  
* 输出维度：$$(N, C, H_{out}, W_{out})$$，其中：  
$$H_{out} = \lfloor \frac{H_{in} + 2 × padding[0] - kernel\_size[0]}{stride[0]} + 1\rfloor$$  
$$W_{out} = \lfloor \frac{W_{in} + 2 × padding[1] - kernel\_size[1]}{stride[1]} + 1\rfloor$$  


## Parameters
* **kernel_size** – 池化窗（window）的大小。  
* **stride** – 池化窗的步长。默认值是`kernel_size`。  
* **padding** – 在每边用0非显式地（implicit）pad。  
* **ceil_mode** – 如果值为True则用ceil而不是floor计算输出的shape。  
* **count_include_pad** – 如果值为真则在平均计算（averaging calculation）时加入零填充（zero-padding）。  
* **divisor_override** – 如果指定的话用`divisor`，没有指定用`kernel_size`。  

`kernel_size`, `stride`, `padding`可以是：  
* 一个`int`，这种情况下该值同时作用于高和宽。  
* 两个整数组成的`tuple`，这种情况下第一个整数对应高维度，第二个整数对应宽维度。  

## Examples  

首先是**并没有什么卵用**的官方例子：  

```python  
    # pool of square window of size=3, stride=2
>>> m = nn.AvgPool2d(3, stride=2)
    # pool of non-square window
>>> m = nn.AvgPool2d((3, 2), stride=(2, 1))
>>> input = torch.randn(20, 16, 50, 32)
>>> output = m(input)
```  

完全没法看结果好吧，最多只能看个输出的size。  

然后简单做个实验：  

```python  
>>> input = torch.arange(1, 26).reshape(1, 1, 5, 5)
>>> input
tensor([[[[ 1,  2,  3,  4,  5],
          [ 6,  7,  8,  9, 10],
          [11, 12, 13, 14, 15],
          [16, 17, 18, 19, 20],
          [21, 22, 23, 24, 25]]]])
>>> m = nn.AvgPool2d(3, stride=2)
>>> output = m(input)
>>> output
tensor([[[[ 7,  9],
          [17, 19]]]])
```  

看起来是起点按照**左上角对齐的，类似于conv的**池化方法。  
又比如[bnn_ops](https://youcaijun98.github.io/codez/awnas/aw_nas/ops/bnn_ops.html)里面`class ResNetDownSample`的池化方法：  

```python  
self.avg = nn.AvgPool2d(kernel_size=1, stride=2)
```  
它其实就是隔一个点取一个值的简单池化。  




