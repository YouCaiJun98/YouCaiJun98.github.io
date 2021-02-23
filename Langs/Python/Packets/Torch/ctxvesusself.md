# ctx vs self

2021/2/23  

需要补充的pytorch知识好多orz  

[参考资料](https://stackoverflow.com/questions/49516188/difference-between-ctx-and-self-in-python)  

`ctx`可能是`context`的缩写，它出现在静态方法(static method，由`@staticmethod`修饰)里。这种静态方法和类外定义的方法一致（而且不会用到类里的属性），只是放在类内更合适一些（分类意义？）。使用这种静态方法时，直接用类名调用方法，例如：  

```python  
LinearFunction.backward(x, y)
```  

因为没有实例化类，所以也就没有`self`可用，这里`ctx`就是个调用函数需要传入的常规参数。  

引一下doc背书，`ctx`实际上是**implicit argument**：  


    A static method does not receive an implicit first argument. When function 
    decorated with @staticmethod is called, we don’t pass an instance of the 
    class to it (as we normally do with methods). This means we can put a 
    function inside a class but we can’t access the instance of that class (this 
    is useful when your method does not use the instance).

(update)这里有篇[更好的blog](https://blog.csdn.net/littlehaes/article/details/103828130)...非常有条理：  
1. `ctx`是context的缩写, 翻译成"上下文; 环境"  
2. `ctx`专门用在静态方法中  
3. `self`指的是实例对象; 而`ctx`用在静态方法中, 调用的时候不需要实例化对象, 直接通过类名就可以调用, 所以`self`在静态方法中没有意义  
4. 自定义的`forward()`方法和`backward()`方法的第一个参数必须是`ctx`; `ctx`可以保存`forward()`中的变量,以便在`backward()`中继续使用, 下一条是具体的示例  
5. `ctx.save_for_backward(a, b)`能够保存`forward()`静态方法中的张量, 从而可以在`backward()`静态方法中调用, 具体地, 下面地代码通过`a, b = ctx.saved_tensors`重新得到a和b  
6. `ctx.needs_input_grad`是一个元组, 元素是`True`或者`False`, 表示`forward()`中对应的输入是否需要求导, 比如`ctx.needs_input_grad[0]`指的是下面`forward()`代码中`indices`是否需要求导  

代码也嫖过来...  

```python  
class SpecialSpmmFunction(torch.autograd.Function):
    """
    Special function for only sparse region backpropataion layer.
    """
    # 自定义前向传播过程
    @staticmethod
    def forward(ctx, indices, values, shape, b):
        assert indices.requires_grad == False
        a = torch.sparse_coo_tensor(indices, values, shape)
        ctx.save_for_backward(a, b)
        ctx.N = shape[0]
        return torch.matmul(a, b)
    # 自定义反向传播过程
    @staticmethod
    def backward(ctx, grad_output):
        a, b = ctx.saved_tensors
        grad_values = grad_b = None
        if ctx.needs_input_grad[1]:
            grad_a_dense = grad_output.matmul(b.t())
            edge_idx = a._indices()[0, :] * ctx.N + a._indices()[1, :]
            grad_values = grad_a_dense.view(-1)[edge_idx]

        if ctx.needs_input_grad[3]:
            grad_b = a.t().matmul(grad_output)
        return None, grad_values, None, grad_b
```  

这个[知乎问题](https://www.zhihu.com/question/366882609/answer/982196400)进一步讨论了`ctx.save_for_backward`和直接`ctx.input = input`的区别，但是并没有很懂。  