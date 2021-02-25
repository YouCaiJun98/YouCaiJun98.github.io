# torch.cat

2021/2/25  

所幸这个和我印象中的用法非常一样:sob:  
而且这次[官方文档](https://pytorch.org/docs/stable/generated/torch.cat.html?highlight=cat#torch.cat) 写得更像个人了:EVEN BETTER（worse，为什么难的函数不写这么明白）

## torch.cat
```python  
torch.cat(
    tensors, 
    dim=0, 
    *, 
    out=None
    ) → Tensor
```  
* **作用**：在给定维度上Concatenate输入的tensor序列。所有的tensor应该有相同的shape（除了需要concatenate的维度）或为空。  
* `torch.cat()`可以被看作是`torch.split()`和`torch.chunk()`的反操作。  

## Parameters
* **tensors** (sequence of Tensors) – 任何相同类型（type）的python tensor序列。非空的tensor要在非concatenate维度有相同的形状。  
* **dim** (int, optional) – 要concate的维度。

## Keyword Arguments
* **out** (Tensor, optional) – 输出的tensor。  

## Examples
官方例子：  

```python  
>>> x = torch.randn(2, 3)
>>> x
tensor([[ 0.6580, -1.0969, -0.4614],
        [-0.1034, -0.5790,  0.1497]])
>>> torch.cat((x, x, x), 0)
tensor([[ 0.6580, -1.0969, -0.4614],
        [-0.1034, -0.5790,  0.1497],
        [ 0.6580, -1.0969, -0.4614],
        [-0.1034, -0.5790,  0.1497],
        [ 0.6580, -1.0969, -0.4614],
        [-0.1034, -0.5790,  0.1497]])
>>> torch.cat((x, x, x), 1)
tensor([[ 0.6580, -1.0969, -0.4614,  0.6580, -1.0969, -0.4614,  0.6580,
         -1.0969, -0.4614],
        [-0.1034, -0.5790,  0.1497, -0.1034, -0.5790,  0.1497, -0.1034,
         -0.5790,  0.1497]])
```  

但是我至今**对高维tensor的concatenate缺乏想象力**...还是尝试写了个例子：  

```python  
>>> x =torch.ones(2, 2, 2, 2)
>>> x
tensor([[[[1., 1.],
          [1., 1.]],
         [[1., 1.],
          [1., 1.]]],
        [[[1., 1.],
          [1., 1.]],
         [[1., 1.],
          [1., 1.]]]])
>>> y = torch.ones(2, 2, 3, 2).mul(2)
>>> torch.cat((x, y) ,2)
tensor([[[[1., 1.],
          [1., 1.],
          [2., 2.],
          [2., 2.],
          [2., 2.]],
         [[1., 1.],
          [1., 1.],
          [2., 2.],
          [2., 2.],
          [2., 2.]]],
        [[[1., 1.],
          [1., 1.],
          [2., 2.],
          [2., 2.],
          [2., 2.]],
         [[1., 1.],
          [1., 1.],
          [2., 2.],
          [2., 2.],
          [2., 2.]]]])

```  




