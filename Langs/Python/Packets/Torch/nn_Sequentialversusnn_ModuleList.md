# nn.Sequential vs nn.ModuleList

2021/2/24  

看代码的时候遇到了`nn.ModuleList`，作用不是很清楚，参考这篇[知乎帖子](https://zhuanlan.zhihu.com/p/75206669)试图弄明白。  

太长不看心得版：`nn.ModuleList`就有点像module的注册机制，把paras绑定到网络里，然后是个layers组成的dict，不必按顺序（也没有顺序）执行module。`nn.Sequential`就是个贯序模型。  

## Official Docu
首先**简单**介绍了几个常用的容器(Containers)中的class。  

### torch.nn.Module  
Base class for all neural network modules.  

Your models should also subclass this class.  
下面的例子是简单的定义，`forward`写得有点好看。  

```python  
import torch.nn as nn
import torch.nn.functional as F

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, 5)
        self.conv2 = nn.Conv2d(20, 20, 5)

    def forward(self, x):
        x = F.relu(conv1(x))
        return F.relu(conv2(x))
```  


### torch.nn.Sequential(*args)  
A sequential container.  

Modules will be added to it **in the order** they are passed in the constructor. Alternatively, an ordered dict of modules can also be passed in.  

例子里面给了用`OrderedDict`传入modules的方法，好处是可以起名。  

```python  
# Example of using Sequential
model = nn.Sequential(
    nn.Conv2d(1, 20, 5),
    nn.ReLU(),
    nn.Conv2d(20, 64, 5),
    nn.ReLU()
    )
# Example of using Sequential with OrderedDict
model = nn.Sequential(OrderedDict([
    ('conv1', nn.Conv2d(1, 20, 5)),
    ('ReLU1', nn.ReLU()),
    ('conv2', nn.Conv2d(20, 64, 5)),
    ('ReLU2', nn.ReLU())
    ]))
```  

### torch.nn.ModuleList(modules=None)  
Holds submodules in a list.  

ModuleList can be indexed like a regular Python list, but modules it contains are properly registered, and will be visible by all Module methods.  

`ModuleList`里面可以用循环定义，`forward`时也可以用`enumerate`套娃。  

```python  
class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.linears = nn.ModuleList([nn.linear for i in range(10)])

    # ModuleList can act as an iterable, or be indexed using ints
    def forward(self, x):
        for i, l in enumerate(self.linears):
            x = self.linears[i // 2](x) + l(x)
        return x
```  

## nn.Sequential与nn.ModuleList简介  
### nn.Sequential  
`nn.Sequential`里面的模块按照顺序进行排列的，所以必须确保前一个模块的输出大小和下一个模块的输入大小是一致的。下面的例子：  

```python  
import torch.nn as nn
class net_seq(nn.Module):
    def __init__(self):
        super(net_seq, self).__init__()
        self.seq = nn.Sequential(
                        nn.Conv2d(1,20,5),
                        nn.ReLU(),
                        nn.Conv2d(20,64,5),
                        nn.ReLU()
                       )
    def forward(self, x):
        return self.seq(x)
net_seq = net_seq()
print(net_seq)
```  

输出的结果是：  

```python  
net_seq(
  (seq): Sequential(
    (0): Conv2d(1, 20, kernel_size=(5, 5), stride=(1, 1))
    (1): ReLU()
    (2): Conv2d(20, 64, kernel_size=(5, 5), stride=(1, 1))
    (3): ReLU()
  )
)
```  

这里还是序号。  
`nn.Sequential`中可以使用`OrderedDict`来指定每个module的名字，而不是采用默认的命名方式(按序号 0,1,2,3...)，例子：  

```python  
from collections import OrderedDict

class net_seq(nn.Module):
    def __init__(self):
        super(net_seq, self).__init__()
        self.seq = nn.Sequential(OrderedDict([
                        ('conv1', nn.Conv2d(1,20,5)),
                        ('relu1', nn.ReLU()),
                        ('conv2', nn.Conv2d(20,64,5)),
                        ('relu2', nn.ReLU())
                       ]))
    def forward(self, x):
        return self.seq(x)
net_seq = net_seq()
print(net_seq)
```  

结果为：  

```python  
net_seq(
  (seq): Sequential(
    (conv1): Conv2d(1, 20, kernel_size=(5, 5), stride=(1, 1))
    (relu1): ReLU()
    (conv2): Conv2d(20, 64, kernel_size=(5, 5), stride=(1, 1))
    (relu2): ReLU()
  )
)
```  

这里已经显示名字而不是序号了。  

### nn.ModuleList  
`nn.ModuleList`，它是一个储存不同 module，并自动将每个 module 的 parameters 添加到网络之中的容器。你可以把任意 `nn.Module` 的子类 (比如 `nn.Conv2d`, `nn.Linear` 之类的) 加到这个 list 里面，方法和 Python 自带的 list 一样，无非是 `extend`，`append` 等操作。但不同于一般的 list，加入到 `nn.ModuleList` 里面的 module 是会自动注册到整个网络上的，同时 module 的 parameters 也会自动添加到整个网络中。若使用python的list，则会出问题。下面看一个例子：  

```python  
class net_modlist(nn.Module):
    def __init__(self):
        super(net_modlist, self).__init__()
        self.modlist = nn.ModuleList([
                       nn.Conv2d(1, 20, 5),
                       nn.ReLU(),
                       nn.Conv2d(20, 64, 5),
                       nn.ReLU()
                        ])

    def forward(self, x):
        for m in self.modlist:
            x = m(x)
        return x

net_modlist = net_modlist()
print(net_modlist)
```  

运行结果是：  

```python  
net_modlist(
  (modlist): ModuleList(
    (0): Conv2d(1, 20, kernel_size=(5, 5), stride=(1, 1))
    (1): ReLU()
    (2): Conv2d(20, 64, kernel_size=(5, 5), stride=(1, 1))
    (3): ReLU()
  )
)
```  

再来看看这个网络的权重 (weithgs) 和偏置 (bias)：  

```python  
for param in net_modlist.parameters():
    print(type(param.data), param.size())
```  

这些para都被注册了：  

```python  
<class 'torch.Tensor'> torch.Size([20, 1, 5, 5])
<class 'torch.Tensor'> torch.Size([20])
<class 'torch.Tensor'> torch.Size([64, 20, 5, 5])
<class 'torch.Tensor'> torch.Size([64])
```  

但是用Python 自带的 list就会有问题：  

```python  
class net_modlist(nn.Module):
    def __init__(self):
        super(net_modlist, self).__init__()
        self.modlist = [
                        nn.Conv2d(1, 20, 5),
                        nn.ReLU(),
                        nn.Conv2d(20, 64, 5),
                        nn.ReLU()
                        ]

    def forward(self, x):
        for m in self.modlist:
            x = m(x)
        return x

net_modlist = net_modlist()
print(net_modlist)
for param in net_modlist.parameters():
    print(type(param.data), param.size())
```  

输出的结果是：  

```python  
net_modlist()
```  

显然这里面的参数都没有被注册进网络。当然，我们还是可以使用 forward 来计算输出结果。但是如果用其实例化的网络进行训练的时候，因为这些层的parameters不在整个网络之中，所以其网络参数也不会被更新，也就是无法训练。  

## nn.Sequential与nn.ModuleList的区别  
### 1.nn.Sequential内部实现了forward函数，因此可以不用写forward函数。而nn.ModuleList则没有实现内部forward函数。  

继续剽窃例子：  

```python  
seq = nn.Sequential(
          nn.Conv2d(1,20,5),
          nn.ReLU(),
          nn.Conv2d(20,64,5),
          nn.ReLU()
        )
input = torch.randn(16, 1, 20, 20)
print(seq(input).size())
```  

输出为：  

```python  
torch.Size([16, 64, 12, 12])
```  

可行。  
继承`nn.Module`类的话，就要写出`forward`函数：  

```python  
class net1(nn.Module):
    def __init__(self):
        super(net1, self).__init__()
        self.seq = nn.Sequential(
                        nn.Conv2d(1,20,5),
                        nn.ReLU(),
                        nn.Conv2d(20,64,5),
                        nn.ReLU()
                       )
    def forward(self, x):
        return self.seq(x)

input = torch.randn(16, 1, 20, 20)
net1 = net1()
print(net1(input).shape)
```  

输出结果为：  

```python  
torch.Size([16, 64, 12, 12])
```  

否则则会报出`NotImplementedError`错误。  

当然对于贯序模型，也可用循环的方式定义`forward`函数：  

```python 
def forward(self, x):
    for s in self.seq:
        x = s(x)
    return x
```

而对于`nn.ModuleList`，不写`forward`方法就会出现`NotImplementedError`错误：  

```python  
modlist = nn.ModuleList([
         nn.Conv2d(1, 20, 5),
         nn.ReLU(),
         nn.Conv2d(20, 64, 5),
         nn.ReLU()
         ])

input = torch.randn(16, 1, 20, 20)
print(modlist(input))
```  

所以要定义`forward`函数：  

```python  
class net2(nn.Module):
    def __init__(self):
        super(net2, self).__init__()
        self.modlist = nn.ModuleList([
                       nn.Conv2d(1, 20, 5),
                       nn.ReLU(),
                       nn.Conv2d(20, 64, 5),
                       nn.ReLU()
                        ])
    def forward(self, x):
        for m in self.modlist:
            x = m(x)
        return x
input = torch.randn(16, 1, 20, 20)
net2 = net2()
print(net2(input).shape)
```  

注意**只能按照下面利用for循环的方式**，不能用下面这种方式，否则还是会出`NotImplementedError`错误：  

```python  
def forward(self, x):
    return self.modlist(x)
```  

如果完全直接用`nn.Sequential`，确实是可以的，但这么做的代价就是失去了部分灵活性，不能自己去定制 `forward` 函数里面的内容了。  

一般情况下 `nn.Sequential` 的用法是来组成卷积块 (block)，然后像拼积木一样把不同的 block 拼成整个网络，让代码更简洁，更加结构化。  

### 2. nn.Sequential可以使用OrderedDict对每层进行命名  

### 3. nn.Sequential按顺序执行，需要对齐module之间的输入输出，nn.ModuleList则没有定义网络  
`nn.Sequential`里面的模块按照顺序进行排列的，所以必须确保前一个模块的输出大小和下一个模块的输入大小是一致的。而`nn.ModuleList` 并没有定义一个网络，它只是将不同的模块储存在一起，这些模块之间并没有什么先后顺序可言。例子如下：  

```python  
class net3(nn.Module):
    def __init__(self):
        super(net3, self).__init__()
        self.linears = nn.ModuleList([nn.Linear(10,20), nn.Linear(20,30), nn.Linear(5,10)])
    def forward(self, x):
        x = self.linears[2](x)
        x = self.linears[0](x)
        x = self.linears[1](x)

        return x

net3 = net3()
print(net3)
input = torch.randn(32, 5)
print(net3(input).shape)
```  

输出的结果为：  

```python  
net3(
  (linears): ModuleList(
    (0): Linear(in_features=10, out_features=20, bias=True)
    (1): Linear(in_features=20, out_features=30, bias=True)
    (2): Linear(in_features=5, out_features=10, bias=True)
  )
)
torch.Size([32, 30])
```  

可以看到，`print(net3)`中的结果是按照`self.linears`中的module存放顺序来的，实际上和网络的执行顺序（拓扑）不一样，否则就会报输入输出不匹配的错误。  

### 4.ModuleList可以通过for循环创建层
用 for 循环来创建网络中相似或者重复的层，需要用到`ModuleList`：  
```python  
class net4(nn.Module):
    def __init__(self):
        super(net4, self).__init__()
        layers = [nn.Linear(10, 10) for i in range(5)]
        self.linears = nn.ModuleList(layers)

    def forward(self, x):
        for layer in self.linears:
            x = layer(x)
        return x

net = net4()
print(net)
```  

输出的结果为：  

```python  
net4(
  (linears): ModuleList(
    (0): Linear(in_features=10, out_features=10, bias=True)
    (1): Linear(in_features=10, out_features=10, bias=True)
    (2): Linear(in_features=10, out_features=10, bias=True)
    (3): Linear(in_features=10, out_features=10, bias=True)
    (4): Linear(in_features=10, out_features=10, bias=True)
  )
)
```  

