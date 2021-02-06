# Decorators  

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

## `@修饰器名称`实际上是一种语法糖
刚才的例子可以用`@`改写为：  

```python  
@a_new_decorator
def a_function_requiring_decoration():
    print("I am the function which needs some decoration to \
          "remove my foul smell")
 
a_function_requiring_decoration()
#outputs: I am doing some boring work before executing a_func()
#         I am the function which needs some decoration to remove my foul smell
#         I am doing some boring work after executing a_func()
 
#the @a_new_decorator is just a short way of saying:
#a_function_requiring_decoration = a_new_decorator(a_function_requiring_decoration)
```  


