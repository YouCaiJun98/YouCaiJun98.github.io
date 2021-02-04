# Python的杂货知识——Class相关 
2021/2/3  
好久不看不写Python和NN，乍一看代码就是头大，而且基本的东西都忘光了，实在丢人。  
所以重新捡一捡一些基本的python知识。  
本篇中的基本内容包括：  
 
<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Python的杂货知识——Class相关](#python的杂货知识class相关)
  - [__init__方法](#__init__方法)
    - [self](#self)
    - [*args与**kwargs](#args与kwargs)
  - [继承](#继承)
  - [五种下划线](#五种下划线)

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
需要注意的是：  
* `__init__`方法的第一参数永远是`self`，表示创建的类实例本身，因此，在`__init__`方法内部，就可以把各种属性绑定到`self`，因为`self`就指向创建的实例本身。  
* 有了`__init__`方法，在创建实例的时候就不能传入空的参数了，必须传入与`__init__`方法匹配的参数，但`self`不需要传，Python解释器会自己把实例变量传进去。  
在这里顺便说一下经常见到的`self`、`*args`和`**kwargs`。  

主要的参考文章是[这个](https://blog.csdn.net/CLHugh/article/details/75000104)还有[这个](https://www.cnblogs.com/yunguoxiaoqiao/p/7626992.html)。  
### self  
* `self`代表类的**实例**，而非类。  
  * 但是，`self.__class__`则指向实例对应的类。  
  * 注意，把`self`换成`this`，结果也一样，但最好使用Python中常用的`self`。  
* `self`在定义时不可以省略，但是定义类方法时（定义和后续调用时均不传类实例）可以不写。
  * 类方法里如果不写的话会有解释器会产生警告，有点奇妙（大概是某种危险操作）

~~还有两条莫名其妙的性质，大概还用不到，需要的时候去查第一篇参考文章。~~  

### *args与**kwargs
* `*args`是将参数打包成tuple给函数体调用
  * 例一：  
  ```
  def function(x, y, *args):
    print(x, y, args)
    print(x, y, *args)

  function(1, 2, 3, 4, 5) 
  ```
  运行结果：  
  ```
  1 2 (3, 4, 5)
  1 2 3 4 5
  ```
  看起来在调用的时候`args`是后续传入参数打包后的tuple，`*args`则是解耦的原始参数。  
  * 例二：  
  ```
  class base_model:
    def __init__(self, a, b):
        self.a = a
        self.b = b

  class second_model(base_model):
      def __init__(self, *args, **kwargs):
          super(second_model, self).__init__(*args, **kwargs)
          self.c = 30
          self.d = 40

      def print(self):
          print(self.a)
          print(self.b)
          print(self.c)
          print(self.d)

  instance = second_model(10, 20)
  instance.print()
  ```
  运行结果显然是：  
  ```
  10
  20
  30
  40
  ```

* `**kwargs` 将关键字参数打包成`dict`给函数体调用。 
  * 例如：  
  ```
  def function1(**kwargs):
    print(kwargs)

  def function2(**kwargs):
      print(**kwargs)

  function1(a=1, b=2, c=3)
  function2(a=1, b=2, c=3)
  ```
  输出结果为：  
  ```
  Traceback (most recent call last):
  File "F:/codes_learning/AWNAS/aw_nas_private/aw_nas/final/test.py", line 101, in <module>
    function2(a=1, b=2, c=3)
  File "F:/codes_learning/AWNAS/aw_nas_private/aw_nas/final/test.py", line 98, in function2
    print(**kwargs)
  TypeError: 'a' is an invalid keyword argument for print()
  {'a': 1, 'b': 2, 'c': 3}
  ```
  显然字典就没有“拆包”一说了（~~合理~~）  

* 参数arg、*args、\**kwargs三个参数的位置必须是一定的。必须是(arg,*args,\**kwargs)这个顺序，否则程序会报错。  

## 继承

这里有篇很有趣的[博文](https://www.cnblogs.com/KbMan/p/11247473.html)，讲的是继承。  
**定义：继承是一种创建新的类的方式，新创建的叫子类，继承的叫父类、超类、基类。子类可以使用父类的属性。**  
**作用：减少代码冗余、提高重用性。**  
继承的要点包括：  
* **单继承**  
  * 类在定义的时候执行**类体代码**，执行顺序是从上到下，例如  

  ```   
  class base_class:
    #def __init__(self):
      print("This is from base class.")

  class second_class(base_class):
    #def __init__(self):
      print("This is from the second class.")

  class third_class(second_class):
    #def __init__(self):
      print("This is from the third class.")

  instant = third_class()
  ```   

  * 输出的结果是：  

  ```   
  This is from base class.
  This is from the second class.
  This is from the third class.
  ```   

  (实际上会在初始化的时候使用`super`调用父类的初始化函数吧，所以执行顺序其实是可变的)  

* **多继承**  
  * 继承自多个类，比如`class succeeded_class(base_class1, base_class2)`  

* **新式类与经典类**  
  * 继承了object的类以及该类的子类，都是新式类。在Python3中如果一个类没有继承任何类，则默认继承object类，因此，Python3中都是新式类。  
  * 没有继承object的类以及该类的子类，都是经典类。在Python2中如果一个类没有继承任何类，不会继承object类，因此，只有Python2中有经典类。  

* **抽象类**：通过抽象可以得到类，抽象是一种分析的过程。（从具体的对象中，分析抽象出一个类），**没有仔细看**。  

* **派生类**：派生，就是在子类继承父类的属性的基础上，派生出自己的属性。子类有不同于父类的属性，这个子类叫做派生类。通常情况下，子类和派生类是同一个概念，因为子类都是有不同于父类的属性，如果子类和父类属性相同，就没必要创建子类了。  

* **组合**：组合指的是，在一个类A中，使用另一个类B的**对象**作为类A的数据属性（特征）（变量），成为类的组合。  
  * 继承建立了派生类和基类的关系，是一种'是'的关系，比如白马是马，人是动物。  
  * 组合建立了两个类之间'有'的关系，比如人有手机，然后人可以使用手机打电话。  
  * 有点类似于C中的结构体...但是两个类之间的组合通过**实例**进行的。  

* **属性查找顺序**：对象自己的 -> 所在类中 -> 找父类 ->父类的父类 -> ... -> Object  

* **覆盖（override）**：子类出现了与父类名称完全一致的属性或是方法。  

* **super函数与__base__方法**  
  * 使用`__bases__`方法可以获取子类继承的类  
  * 使用`super`函数在子类中访问父类的内容，方式如下：  
  ```
  方式1:
  super(当前类名称,self).你要调的父类的属性或方法
  方式2:
  super().你要调的父类的属性或方法
  方式3:
  类名称.你要调的父类的属性或方法(self)
  ```
  当你继承一个现有的类，并且你覆盖了父类的init方法时，必须在初始化方法的第一行调用父类的初始化方法，并传入父类所需的参数。  

## 五种下划线


