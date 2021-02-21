# Decorators

{% include list.liquid all=true %}  


2021/2/6  

主要参考博文为[这篇](https://www.runoob.com/w3cnote/python-func-decorators.html)和[这篇](https://www.cnblogs.com/wolf-yasen/p/11240500.html)。  

修饰器（Decorators）：修饰器是一个函数，接受一个函数或方法作为其唯一的参数，并返回一个新函数或方法，其中整合了修饰后的函数或方法，并附带了一些额外的功能。  

## 首先是函数名类似指针（实际上就是指针）的用法
有点新鲜，例子引自第一篇博客  
* **将一个函数赋值给一个变量**  

```python  
def hi(name="yasoob"):
    return "hi " + name

greet = hi
print(greet())
# output: 'hi yasoob'

del hi
print(hi())
#outputs: NameError

#删除原来的函数名之后仍能通过新变量名访问该函数
print(greet())
#outputs: 'hi yasoob'
```  

* **函数（名）作为返回值**
函数的名字（实际上是指针？）可以作为返回值，区别于带`()`的执行返回：  

```python  
def hi(name="yasoob"):
    def greet():
        return "now you are in the greet() function"
 
    def welcome():
        return "now you are in the welcome() function"
 
    if name == "yasoob":
        return greet
    else:
        return welcome
 
a = hi()
print(a)
#outputs: <function greet at 0x7f2143c01500>

print(a())
#outputs: now you are in the greet() function
```  

还可以打印出`hi()()`，这会输出 `now you are in the greet() function`。  

* **将函数作为参数传给另一个函数**  
~~接着嫖例子~~  

```python  
def a_new_decorator(a_func):
 
    def wrapTheFunction():
        print("I am doing some boring work before executing a_func()")
        a_func()
        print("I am doing some boring work after executing a_func()")
     return wrapTheFunction
 
def a_function_requiring_decoration():
    print("I am the function which needs some decoration to remove my foul smell")
 
a_function_requiring_decoration()
#outputs: "I am the function which needs some decoration to remove my foul smell"
 
a_function_requiring_decoration = a_new_decorator(a_function_requiring_decoration)
#now a_function_requiring_decoration is wrapped by wrapTheFunction()
 
a_function_requiring_decoration()
#outputs:I am doing some boring work before executing a_func()
#        I am the function which needs some decoration to remove my foul smell
#        I am doing some boring work after executing a_func()
```  

## `@decorator`实际上是一种语法糖
刚才的例子可以用`@`改写为：  

```python  
@a_new_decorator
def a_function_requiring_decoration():
    print("I am the function which needs some decoration to \
          remove my foul smell")
 
a_function_requiring_decoration()
#outputs: I am doing some boring work before executing a_func()
#         I am the function which needs some decoration to remove my foul smell
#         I am doing some boring work after executing a_func()
 
#the @a_new_decorator is just a short way of saying:
#a_function_requiring_decoration = a_new_decorator(a_function_requiring_decoration)
```  

要注意的是，定义的装饰器**返回值一定是内部定义函数的名字**！  
但是包裹后的函数会丢失一些内省信息，比如：  

```python  
print(a_function_requiring_decoration.__name__)
# Output: wrapTheFunction
```  

上面函数名被warpTheFunction替代了，装饰器重写了函数的名字和注释文档(docstring)，解决问题可以用到`functools.wraps`函数。`@wraps`接受一个函数来进行装饰，并加入了复制函数名称、注释文档、参数列表等等的功能。这使得我们可以在装饰器里面访问在装饰之前的函数的属性：  

```python  
from functools import wraps
 
def a_new_decorator(a_func):
    @wraps(a_func)
    def wrapTheFunction():
        print("I am doing some boring work before executing a_func()")
        a_func()
        print("I am doing some boring work after executing a_func()")
    return wrapTheFunction
 
@a_new_decorator
def a_function_requiring_decoration():
    print("I am the function which needs some decoration to "
          "remove my foul smell")
 
print(a_function_requiring_decoration.__name__)
# Output: a_function_requiring_decoration
```  

## 装饰需要传入参数的函数&修饰有返回值的函数
当需要装饰的函数有若干需要传入的参数时，可以将装饰器拆成两层，第一层还是装饰器的外壳，第二层也仍为定义的内部函数，但是多了`*args, **kwargs`作为传入参数：  

```python  
def decorator(func):
    def print_note(*args, **kwargs):
        func(*args, **kwargs)
        print("This is from the decorator.")
    return print_note

@decorator
def func_with_paras(a):
    print("a = " + str(a))

func_with_paras(1)
```  

如果需要用到被修饰函数的返回值也是个问题（注意顺序，特别是在多层修饰中）：  
(摘自第二篇参考文献，显然作者忘记了)  

```python  
import time
def test(func):
    def wrapper():
        start = time.clock()
        print("this is a order test, if you need not it, delete it") # 用于测试执行顺序,可以跟着走一遍
        a = func()
        end = time.clock()
        print("start:", start, " end:", end)
        return a # 这种获得返回值的方法可能在多层修饰器的时候有矛盾,我先用!!!标记, 等理顺后再回来修改,如果我发布之后这里依然存在...说明我忘记了...
    return wrapper

@test
def foo():
    print("this is a test")
    return "this is a return value"

print(foo())
# 输出
# this is a test wrapper, if you need not it, delete it
# this is a test
# start: 4.44444839506524e-07  end: 1.8222238419767486e-05
# this is a return value
```  

## 含有参数的装饰器
下面的例子用到了含参装饰器、装饰需要传入参数的函数这两部分的知识：  

```python
from functools import wraps
 
def logit(logfile='out.log'):
    def logging_decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = func.__name__ + " was called"
            print(log_string)
            # 打开logfile，并写入内容
            with open(logfile, 'a') as opened_file:
                # 现在将日志打到指定的logfile
                opened_file.write(log_string + '\n')
            return func(*args, **kwargs)
        return wrapped_function
    return logging_decorator
 
@logit()
def myfunc1():
    pass
 
myfunc1()
# Output: myfunc1 was called
# 现在一个叫做 out.log 的文件出现了，里面的内容就是上面的字符串
 
@logit(logfile='func2.log')
def myfunc2():
    pass
 
myfunc2()
# Output: myfunc2 was called
# 现在一个叫做 func2.log 的文件出现了，里面的内容就是上面的字符串
```

## 装饰器类
类也可以用来构建装饰器，装饰的方法还是`@decorator`(本质原因应该是类中定义了`__call__`方法)：    

```python
from functools import wraps
 
class logit(object):
    def __init__(self, logfile='out.log'):
        self.logfile = logfile
 
    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = func.__name__ + " was called"
            print(log_string)
            # 打开logfile并写入
            with open(self.logfile, 'a') as opened_file:
                # 现在将日志打到指定的文件
                opened_file.write(log_string + '\n')
            # 现在，发送一个通知
            self.notify()
            return func(*args, **kwargs)
        return wrapped_function
 
    def notify(self):
        # logit只打日志，不做别的
        pass
```  

## 使用场景
包括但不限于：  
* 授权(Authorization)  
装饰器有助于检查某个人是否被授权去使用一个web应用的端点(endpoint)，被大量使用于Flask和Django web框架中：  

```python  
from functools import wraps
 
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            authenticate()
        return f(*args, **kwargs)
    return decorated
```  

* 日志(Logging)  
直接偷例子：  

```python  
from functools import wraps
 
def logit(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)
    return with_logging
 
@logit
def addition_func(x):
   """Do some math."""
   return x + x
 
 
result = addition_func(4)
# Output: addition_func was called
```  


