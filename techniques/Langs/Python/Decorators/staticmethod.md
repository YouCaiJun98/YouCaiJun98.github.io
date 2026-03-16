# staticmethod

2021/2/21  

[参考资料](https://www.runoob.com/python/python-func-staticmethod.html)  

该方法不强制要求传递参数，如下声明一个静态方法：  

```python  
class C(object):
    @staticmethod
    def f(arg1, arg2, ...):
        ...
```  

以上实例声明了静态方法`f`，从而可以实现实例化使用`C().f()`，当然也可以不实例化调用该方法`C.f()`  

例如：  

```python  
class Test_Class():
    @staticmethod
    def Amethod():
        print("This is a nice try, huh?")
    def Bmethod(self):
        print("Bad Try, haha!")

Test_Class.Amethod()  # 静态方法无需实例化
Test_instant = Test_Class()
Test_instant.Amethod()  # 也可以实例化后调用
Test_instant.Bmethod()  
Test_Class.Bmethod()  # 需要注意的是该装饰器和定义时的self互斥
```  

输出结果为：  

```python
This is a nice try, huh?
This is a nice try, huh?
Bad Try, haha!
Traceback (most recent call last):
  File "F:/codes_learning/AWNAS/aw_nas_private/aw_nas/final/test.py", line 177, in <module>
    Test_Class.Bmethod()
TypeError: Bmethod() missing 1 required positional argument: 'self'

Process finished with exit code 1
```  

互斥指的是如果有了装饰器`@staticmethod`那么定义方法时就不能加入`self`变量（合理，因为该装饰器的作用就是让类方法可以静态调用，`self`指向的实例就有些不伦不类 => ~~就不能在编译的时候初始化一个空的实例吗~~）。  
