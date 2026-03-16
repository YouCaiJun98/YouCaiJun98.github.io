# torch.ge、torch.gt、torch.le、torch.lt、torch.eq、torch.equal.

2021/2/23  

读[bnn_ops.py](https://youcaijun98.github.io/codez/awnas/aw_nas/ops/bnn_ops.html)的时候遇到的torch相关属性。[参考资料](https://www.cnblogs.com/lqchen/p/12346748.html)。  

## torch.ge  
torch.ge(input, other, out=None) → Tensor  
逐元素比较`input`和`other`，即是否 input>=otherinput>=other。(ge=greater+equal？)  
如果两个张量有相同的形状和元素值，则返回True ，否则 False。 第二个参数可以为一个数或与第一个参数相同形状和类型的张量。  
* 参数包括:  
    * `input (Tensor)` – 待对比的张量  
    * `other (Tensor or float)` – 对比的张量或float值  
    * `out (Tensor, optional)` – 输出张量。必须为ByteTensor或者与第一个参数tensor相同类型。  

* 返回值： 
一个`torch.ByteTensor`张量，包含了每个位置的比较结果(是否 input >= other )。返回类型： `Tensor`  
* 参考用法：  

```python  
>>> torch.ge(torch.Tensor([[1, 2], [3, 4]]), torch.Tensor([[1, 1], [4, 4]]))
 1  1
 0  1
[torch.ByteTensor of size 2x2]
```  

注意到还可以作为tensor的属性调用，例如：  

```python  
>>>x=torch.tensor([[1,2],[3,4]])
>>>x
tensor([[1, 2],
        [3, 4]])

>>>x.ge(torch.tensor([[2,1],[4,3]]))
tensor([[False,  True],
        [False,  True]])

#还可以将返回的列表作为索引
>>>x[x.ge(torch.tensor([[2,1],[4,3]]))] = 0
>>>x
tensor([[1, 0],
        [3, 0]])
```  

## torch.gt  
同理，torch.gt(input, other, out=None) → Tensor  
逐元素比较`input`和`other` ， 即是否input>otherinput>other（gt=greater than）  
如果两个张量有相同的形状和元素值，则返回True ，否则 False。 第二个参数可以为一个数或与第一个参数相同形状和类型的张量。  
* 输入参数：  
    * `input (Tensor)` – 要对比的张量  
    * `other (Tensor or float)` – 要对比的张量或float值  
    * `out (Tensor, optional)` – 输出张量。必须为ByteTensor或者与第一个参数tensor相同类型。  

* 返回值： 一个 `torch.ByteTensor` 张量，包含了每个位置的比较结果(是否 input > other )。返回类型： `Tensor`  

* 参考用法：  

```python  
>>> torch.gt(torch.Tensor([[1, 2], [3, 4]]), torch.Tensor([[1, 1], [4, 4]]))
 0  1
 0  0
[torch.ByteTensor of size 2x2]
```  

## torch.le  
剩下的就直接复制粘贴了。。没什么用啦。  
torch.le(input, other, out=None) → Tensor  
逐元素比较`input`和`other` ， 即是否input<=otherinput<=other (le=less equal)  
第二个参数可以为一个数或与第一个参数相同形状和类型的张量。  

* 输入参数：  
    * `input (Tensor)` – 要对比的张量  
    * `other (Tensor or float)` – 要对比的张量或float值  
    * `out (Tensor, optional)` – 输出张量。必须为ByteTensor或者与第一个参数tensor相同类型。  

* 返回值： 一个 `torch.ByteTensor` 张量，包含了每个位置的比较结果(是否 input <= other )。返回类型： `Tensor`  

* 参考用法：  

```python  
>>> torch.le(torch.Tensor([[1, 2], [3, 4]]), torch.Tensor([[1, 1], [4, 4]]))
 1  0
 1  1
[torch.ByteTensor of size 2x2]
```  

## torch.lt  
torch.lt(input, other, out=None) → Tensor  
逐元素比较`input`和`other` ， 即是否input<otherinput<other (lt=less than)  
第二个参数可以为一个数或与第一个参数相同形状和类型的张量。  

* 输入参数：  
    * `input (Tensor)` – 要对比的张量  
    * `other (Tensor or float)` – 要对比的张量或float值  
    * `out (Tensor, optional)` – 输出张量。必须为ByteTensor或者与第一个参数tensor相同类型。  

* 返回值： 一个 `torch.ByteTensor` 张量，包含了每个位置的比较结果(是否 input < other )。返回类型： `Tensor`  

* 参考用法：  

```python  
>>> torch.lt(torch.Tensor([[1, 2], [3, 4]]), torch.Tensor([[1, 1], [4, 4]]))
 0  0
 1  0
[torch.ByteTensor of size 2x2]
```  

## torch.equal&torch.eq  
a,b是两个列表  
a.equal(b)要求整个列表完全相同才是True(单个bool值)  
a.eq(b) 相同位置值相同则返回对应的True,返回的是一个列表  
用属性的方式给出参考用例：  

```python  
>>> x=torch.tensor([[1,2],[3,4]])
>>> y=x.equal(torch.tensor([[1,2],[3,4]]))
>>> y2=x.eq(torch.tensor([[1,2],[3,4]]))
>>> y
True
>>> y2
tensor([[True, True],
        [True, True]])
```  

