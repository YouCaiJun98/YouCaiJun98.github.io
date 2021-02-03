# Python的杂货知识——Class相关 
2021/2/3  
好久不看不写Python和NN，乍一看代码就是头大，而且基本的东西都忘光了，实在丢人。  
所以重新捡一捡一些基本的python知识。  
本篇中的基本内容包括：  
 
<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Python的杂货知识——Class相关](#python的杂货知识class相关)
  - [__init__方法](#__init__方法)
  - [继承](#继承)
  - [super函数的用法](#super函数的用法)
  - [*args, **kwargs的含义](#args-kwargs的含义)
  - [五种下划线](#五种下划线)
  - [待续](#待续)

<!-- /code_chunk_output -->

 
## __init__方法
__init__方法的主要参考资料是一篇[知乎的回答](https://www.zhihu.com/question/46973549)。   
**作用：定义类的时候，如果添加__init__方法，实例化时产生的实例会自动调用这个方法，一般用来对实例的属性进行初使化。**  
举例：  
```
class base_test:
    def __init__(self, prop_a):
        print("This is from base_test class.")
        self.prop_a = prop_a
        self.prop_b = 20

class succeeded_class(base_test):
    def __init__(self, prop_a, prop_c, prop_d):
        super(succeeded_class, self).__init__(prop_a)
        self.prop_c = prop_c
        self.prop_d = prop_d
        print("This is from succeeded class.")

test = succeeded_class(10, 30, 40)
print(test.prop_a)
print(test.prop_b)
print(test.prop_c)
print(test.prop_d)
```
运行结果显然是：  
```
This is from base_test class.
This is from succeeded class.
10
20
30
40
```
上面这个例子中用到了**继承**，后面也得复习一下，总之是定义了两个类`base_test`和`succeeded_class`，分别称之为“基类”和“继承类”，基类中的`__init__`方法给这个类的两个属性`self.prop_a`与`self.prop_b`赋初值，实例化的时候需要传入参数prop_a；继承类在实例化的时候需要传入三个参数`prop_a`、`prop_c`、`prop_d`，其中参数`prop_a`是基类所需要的，调用了`super`函数（后面也得复习一下）来访问继承类的父类（也就是基类）中的方法或属性，这里是调用了父类中的初始化方法。  
上面输出的结果"This is ..."是为了说明在实例化的时候就调用这两个`__init__`方法，输出的顺序和子类中的定义顺序一致。  

## 继承
我真的吐了，怎么回事

## super函数的用法



## *args, **kwargs的含义



## 五种下划线


## 待续