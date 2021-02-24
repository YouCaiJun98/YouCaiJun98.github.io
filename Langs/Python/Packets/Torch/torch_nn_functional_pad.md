# torch.nn.functional.pad

2021/2/24  

因为有[官方文档](https://pytorch.org/docs/stable/nn.functional.html#torch.nn.functional.pad)，所以这种东西都写得简单些。（不会真有人查自己的blog而不是查官方doc吧，不会吧不会吧不会吧）  

## torch.nn.functional.pad(input, pad, mode='constant', value=0)  
### Parameters  
* **input** (Tensor) – N维 tensor
* **pad** (tuple，数组) – m个元素的数组, 其中$$ \frac{m}{2} \leq input dim $$ ，m是偶数。
* **mode** – 'constant', 'reflect', 'replicate' or 'circular'. 默认值: 'constant'。
* **value** – 'constant'模式下的填充值。默认值: 0  

* **NOTE**:当使用CUDA时，上述操作可能会在反向计算的过程中带来不确定的影响，并且这种影响是不易停止的。  

## padding size  
用于填充输入（input）的不同维度的填充尺寸（padding size）是从最后一个维度依次向前描述的。输入（input）的$$\lfloor \frac{len(pad)}{2} \rfloor$$维将会被填充。举个栗子，如果仅填充输入张量（tensor）的最后一个维度，填充的形式为`(padding_left,padding_right)`;如果输入张量的最后两个维度，使用`(padding_left,padding_right,padding_top,padding_bottom)`;如果输入张量的最后三个维度，使用`(padding_left,padding_right,padding_top,padding_bottom,padding_front,padding_back)`。  
来个实际的例子。对于二维tensor x：  

```python  
x = torch.ones([5,5])
```  

对它的左边和右边填充0，那么应该：  
```python  
x = torch.nn.functional.pad(x,(1, 1, 0, 0), "constant", 0)
```  

最后的结果是：  

```python  
tensor([[0., 1., 1., 1., 1., 1., 0.],
        [0., 1., 1., 1., 1., 1., 0.],
        [0., 1., 1., 1., 1., 1., 0.],
        [0., 1., 1., 1., 1., 1., 0.],
        [0., 1., 1., 1., 1., 1., 0.]])
```  


## Examples  
下面放一点官方的例子。看到确实pad是**成对**出现的，从**最后一个维度**开始向前pad（高维情况无法想象...）。  

```python  
>>> t4d = torch.empty(3, 3, 4, 2)
>>> p1d = (1, 1) # pad last dim by 1 on each side
>>> out = F.pad(t4d, p1d, "constant", 0)  # effectively zero padding
>>> print(out.data.size())
torch.Size([3, 3, 4, 4])
>>> p2d = (1, 1, 2, 2) # pad last dim by (1, 1) and 2nd to last by (2, 2)
>>> out = F.pad(t4d, p2d, "constant", 0)
>>> print(out.data.size())
torch.Size([3, 3, 8, 4])
>>> t4d = torch.empty(3, 3, 4, 2)
>>> p3d = (0, 1, 2, 1, 3, 3) # pad by (0, 1), (2, 1), and (3, 3)
>>> out = F.pad(t4d, p3d, "constant", 0)
>>> print(out.data.size())
torch.Size([3, 9, 7, 3])
```  

## padding modes  
三个mode：Constant、Replicate和Reflect。Constant模式用于任意维度的填充；Replicate模式用于5D输入张量最后三维或4D输入张量最后两维或3D输入张量最后一维的填充；Reflect模式用于4D输入张量最后两维或3D输入张量的最后一维的填充。再把三种pad的subclass的例子搬上来：  
1. **class torch.nn.ConstantPad2d(padding,value)**  
* 作用：用常值填充输入张量的边界。  
* 对于N维的填充，使用`torch.nn.functional.pad()`  
* 参数：padding (python:int, tuple) – 填充的尺寸。如果是int型的，对所有的边界使用相同的填充方式。 如果是4维的数组，使用(padding_left,padding_right,padding_top,padding_bottom)。  
形式：  
    * 输入：$$\left ( N,C,H_{in},W_{in}\right )$$
    * 输出：$$\left ( N,C,H_{out},W_{out}\right )$$ ，其中 $$\left (H_{out}=H_{in}+padding\: top+padding\: bottom\right )$$ , $$\left (W_{out}=W_{in}+padding\: left+padding\: right\right )$$   
* 例子：  

```python  
>>> m = nn.ConstantPad2d(2, 3.5)
>>> input = torch.randn(1, 2, 2)
>>> input
tensor([[[ 1.6585,  0.4320],
         [-0.8701, -0.4649]]])
>>> m(input)
tensor([[[ 3.5000,  3.5000,  3.5000,  3.5000,  3.5000,  3.5000],
         [ 3.5000,  3.5000,  3.5000,  3.5000,  3.5000,  3.5000],
         [ 3.5000,  3.5000,  1.6585,  0.4320,  3.5000,  3.5000],
         [ 3.5000,  3.5000, -0.8701, -0.4649,  3.5000,  3.5000],
         [ 3.5000,  3.5000,  3.5000,  3.5000,  3.5000,  3.5000],
         [ 3.5000,  3.5000,  3.5000,  3.5000,  3.5000,  3.5000]]])
>>> # using different paddings for different sides
>>> m = nn.ConstantPad2d((3, 0, 2, 1), 3.5)
>>> m(input)
tensor([[[ 3.5000,  3.5000,  3.5000,  3.5000,  3.5000],
         [ 3.5000,  3.5000,  3.5000,  3.5000,  3.5000],
         [ 3.5000,  3.5000,  3.5000,  1.6585,  0.4320],
         [ 3.5000,  3.5000,  3.5000, -0.8701, -0.4649],
         [ 3.5000,  3.5000,  3.5000,  3.5000,  3.5000]]])
```  

2. **class torch.nn.ReflectionPad2d(padding)**  
* 作用：用输入的边界做映射（镜像）来进行填充。  
* 对于N维的填充，使用`torch.nn.functional.pad()`  
* 参数：padding (python:int, tuple) – 填充的尺寸。如果是int型的，对所有的边界使用相同的填充方式。 如果是4维的数组，使用(padding_left,padding_right,padding_top,padding_bottom)。  
形式：  
    * 输入：$$\left ( N,C,H_{in},W_{in}\right )$$
    * 输出：$$\left ( N,C,H_{out},W_{out}\right )$$ ，其中 $$\left (H_{out}=H_{in}+padding\: top+padding\: bottom\right )$$ , $$\left (W_{out}=W_{in}+padding\: left+padding\: right\right )$$   
* 例子：  

```python  
>>> m = nn.ReflectionPad2d(2)
>>> input = torch.arange(9, dtype=torch.float).reshape(1, 1, 3, 3)
>>> input
tensor([[[[0., 1., 2.],
          [3., 4., 5.],
          [6., 7., 8.]]]])
>>> m(input)
tensor([[[[8., 7., 6., 7., 8., 7., 6.],
          [5., 4., 3., 4., 5., 4., 3.],
          [2., 1., 0., 1., 2., 1., 0.],
          [5., 4., 3., 4., 5., 4., 3.],
          [8., 7., 6., 7., 8., 7., 6.],
          [5., 4., 3., 4., 5., 4., 3.],
          [2., 1., 0., 1., 2., 1., 0.]]]])
>>> # using different paddings for different sides
>>> m = nn.ReflectionPad2d((1, 1, 2, 0))
>>> m(input)
tensor([[[[7., 6., 7., 8., 7.],
          [4., 3., 4., 5., 4.],
          [1., 0., 1., 2., 1.],
          [4., 3., 4., 5., 4.],
          [7., 6., 7., 8., 7.]]]])
```  
~~上面的例子有点阴间。不会真有人这么填吧？~~  
看法是从被填充的边界镜像来看。  

3. **class torch.nn.ReplicationPad2d(padding)**  
* 作用：用输入边界的复制来进行填充。  
* 对于N维的填充，使用`torch.nn.functional.pad()`  
* 参数：padding (python:int, tuple) – 填充的尺寸。如果是int型的，对所有的边界使用相同的填充方式。 如果是4维的数组，使用(padding_left,padding_right,padding_top,padding_bottom)。  
形式：  
    * 输入：$$\left ( N,C,H_{in},W_{in}\right )$$
    * 输出：$$\left ( N,C,H_{out},W_{out}\right )$$ ，其中 $$\left (H_{out}=H_{in}+padding\: top+padding\: bottom\right )$$ , $$\left (W_{out}=W_{in}+padding\: left+padding\: right\right )$$   
* 例子：  

```python  
>>> m = nn.ReplicationPad2d(2)
>>> input = torch.arange(9, dtype=torch.float).reshape(1, 1, 3, 3)
>>> input
tensor([[[[0., 1., 2.],
          [3., 4., 5.],
          [6., 7., 8.]]]])
>>> m(input)
tensor([[[[0., 0., 0., 1., 2., 2., 2.],
          [0., 0., 0., 1., 2., 2., 2.],
          [0., 0., 0., 1., 2., 2., 2.],
          [3., 3., 3., 4., 5., 5., 5.],
          [6., 6., 6., 7., 8., 8., 8.],
          [6., 6., 6., 7., 8., 8., 8.],
          [6., 6., 6., 7., 8., 8., 8.]]]])
>>> # using different paddings for different sides
>>> m = nn.ReplicationPad2d((1, 1, 2, 0))
>>> m(input)
tensor([[[[0., 0., 1., 2., 2.],
          [0., 0., 1., 2., 2.],
          [0., 0., 1., 2., 2.],
          [3., 3., 4., 5., 5.],
          [6., 6., 7., 8., 8.]]]])
```  




