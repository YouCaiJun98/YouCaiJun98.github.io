# defaultdict  

2021/3/3  

在读[layer2/final_model.py](https://youcaijun98.github.io/codez/awnas/aw_nas/btcs/layer2/final_model.html)的时候迎面来了个`defaultdict()`，非常困扰所以全篇借鉴了[这篇博客](https://www.cnblogs.com/herbert/archive/2013/01/09/2852843.html)来研究一下这个方法。  

在Python里面有一个模块collections，解释是数据类型容器模块。这里面有一个collections.defaultdict()经常被用到。主要说说这个东西。  

这里的`defaultdict`(function_factory)构建的是一个类似`dictionary`的对象，其中keys的值，自行确定赋值（*这里说的有点问题，意思大概是key的值自己定，value如果给了就是给定值，空的就是默认值*），但是values的类型，是`function_factory`的类实例（*不是`defaultdict`的实例！是后面比如`int()`的实例！*），而且具有默认值。比如`defaultdict(int)`则创建一个类似dictionary对象，里面任何的values都是int的实例，而且就算是一个不存在的key, `d[key]` 也有一个默认值，这个默认值是`int()`的默认值0。  

```  
defaultdict
dict subclass that calls a factory function to supply missing values。
```  

这是一个简短的解释。  

defaultdict属于**内建函数dict的一个子类**，调用工厂函数提供缺失的值。  
*意思挺明显了，就是一种特殊的dict，只不过对于没提供value的key用默认值填充。*  

比较晕，什么是工厂函数？来自python核心编程的解释：  
`Python 2.2`统一了类型和类， 所有的内建类型现在也都是类，在这基础之上，原来的所谓内建转换函数象`int()`, `type()`, `list()`等等，现在都成了工厂函数。也就是说虽然他们看上去有点像函数，实质上他们是类。当你调用它们时， 实际上是生成了该类型的一个实例， 就像工厂生产货物一样。  
下面这些大家熟悉的工厂函数在老版`Python`里被称为内建函数：  

```python  
int(), long(), float(), complex()
str(), unicode(), basestring()
list(), tuple()
type()
```  

以前没有工厂函数的其他类型，现在也都有了工厂函数。除此之外，那些支持新风格的类的全新的数据类型，也添加了相应的工厂函数。下面列出了这些工厂函数：  

```python  
dict()
bool()
set(), frozenset()
object()
classmethod()
staticmethod()
super()
property()
file()
```  

再看看它们的使用：  

```python  
import collections
s = [('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]

d = collections.defaultdict(list)
for k, v in s:
    d[k].append(v)
print(d)

d = list(d.items())
print(d)
```  

输出为：  

```python  
defaultdict(<class 'list'>, {'yellow': [1, 3], 'blue': [2, 4], 'red': [1]})
[('yellow', [1, 3]), ('blue', [2, 4]), ('red', [1])]
```  

(*上面对例子进行了改动，可以看到d是一个和dict非常像的实例，后面可以直接转换成dict。*)  

这里就开始有点明白了，原来`defaultdict`可以接受一个内建函数`list`作为参数。其实呢，`list()`本身是内建函数，但是再经过更新后，python里面所有东西都是对象，所以`list`改编成了类，引入`list`的时候产生一个类的实例。  

还是不太明白，再看`defaultdict`的help解释：  

```  
class collections.defaultdict([default_factory[, ...]])
Returns a new dictionary-like object. defaultdict is a subclass of the built-in dict class. It overrides one method and adds one writable instance variable. The remaining functionality is the same as for the dict class and is not documented here.
```  

首先说了，`collections.defaultdict`会返回一个类似`dictionary`的对象，注意是类似的对象，不是完全一样的对象。这个`defaultdict`和`dict`类，几乎是一样的，除了它重载了一个方法和增加了一个可写的实例变量。（可写的实例变量，我还是没明白）  

```  
The first argument provides the initial value for the default_factory attribute; it defaults to None. All remaining arguments are treated the same as if they were passed to the dict constructor, including keyword arguments.

defaultdict objects support the following method in addition to the standard dict operations:

__missing__(key)
If the default_factory attribute is None, this raises a KeyError exception with the key as argument.

If default_factory is not None, it is called without arguments to provide a default value for the given key, this value is inserted in the dictionary for the key, and returned.
```  

*然后那篇博客就开始犯晕了，这边其实很好李姐，上例子：*  

```python  
x = defaultdict(int)
y = defaultdict()
z = dict()
print(x['???'])
print(y['???'])
print(z['???'])
```  

*结果分别为：*  

```python  
0
KeyError: '???'
KeyError: '???'
```  

*所以，如果没有规定default_factory attribute(上例中y)，那么它的表现就像一般的`dict()`一样，对于一个不存在的key值raise KeyError，如果规定了就是对应default_factory的默认值。*  

*原文犯晕现场*：  
主要关注这句话，如果`default_factory`不是`None`, 这个`default_factory`将以一个无参数的形式被调用，提供一个默认值给`___missing__`方法的key。 这个默认值将作为key插入到数据字典里，然后返回。  

十分晕。又扯出了个`__missing__`方法，这个`__missing__`方法是`collections.defaultdict()`的内建方法：  

```  
If calling default_factory raises an exception this exception is propagated unchanged.

This method is called by the __getitem__() method of the dict class when the requested key is not found; whatever it returns or raises is then returned or raised by __getitem__().

Note that __missing__() is not called for any operations besides __getitem__(). This means that get() will, like normal dictionaries, return None as a default rather than using default_factory.

defaultdict objects support the following instance variable:

default_factory
This attribute is used by the __missing__() method; it is initialized from the first argument to the constructor, if present, or to None, if absent.
```  

看样子这个文档是难以看懂了。直接看示例：  

```python  
import collections
s = [('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]

# defaultdict
d = collections.defaultdict(list)
for k, v in s:
    d[k].append(v)

# Use dict and setdefault    
g = {}
for k, v in s:
    g.setdefault(k, []).append(v)
    
# Use dict
e = {}
for k, v in s:
    e[k] = v

##list(d.items())
##list(g.items())
##list(e.items())
```  

看看结果:  

```python  
list(d.items())
[('blue', [2, 4]), ('red', [1]), ('yellow', [1, 3])]
>>> list(g.items())
[('blue', [2, 4]), ('red', [1]), ('yellow', [1, 3])]
>>> list(e.items())
[('blue', 4), ('red', 1), ('yellow', 3)]
>>> d
defaultdict(<class 'list'>, {'blue': [2, 4], 'red': [1], 'yellow': [1, 3]})
>>> g
{'blue': [2, 4], 'red': [1], 'yellow': [1, 3]}
>>> e
{'blue': 4, 'red': 1, 'yellow': 3}
>>> d.items()
dict_items([('blue', [2, 4]), ('red', [1]), ('yellow', [1, 3])])
>>> d["blue"]
[2, 4]
>>> d.keys()
dict_keys(['blue', 'red', 'yellow'])
>>> d.default_factory
<class 'list'>
>>> d.values()
dict_values([[2, 4], [1], [1, 3]])
```  

可以看出，`collections.defaultdict(list)`使用起来效果和`dict.setdefault()`比较相似，python help上也这么说了：  

```  
When each key is encountered for the first time, it is not already in the mapping; so an entry is automatically created using the default_factory function which returns an empty list. The list.append() operation then attaches the value to the new list. When keys are encountered again, the look-up proceeds normally (returning the list for that key) and the list.append() operation adds another value to the list. This technique is simpler and faster than an equivalent technique using dict.setdefault():
```  

说这种方法会和`dict.setdefault()`等价，但是要更快，有必要看看`dict.setdefault()`：  

```  
setdefault(key[, default])
If key is in the dictionary, return its value. If not, insert key with a value of default and return default. default defaults to None.
```  

如果这个key已经在dictionary里面存着，返回value。如果key不存在，插入key和一个default value,返回Default。默认的defaults是None。  

但是这里要注意的是defaultdict是和`dict.setdefault`等价，和下面那个直接赋值是有区别的。从结果里面就可以看到，直接赋值会覆盖。  

从最后的`d.values`还有`d[“blue”]`来看，后面的使用其实是和dict的用法一样的，唯一不同的就是初始化的问题。defaultdict可以利用工厂函数，给初始key带来一个默认值。这个默认值也许是空的`list[]`(defaultdict(list)), 也许是0,(defaultdict(int))。  

再看看下面的这个例子。`defaultdict(int)` 这里的d其实是生成了一个默认为0的带key的数据字典。你可以想象成 `d[key] = int default` （int工厂函数的默认值为0）。所以`d[k]`可以直接读取 `d[“m”] += 1` 也就是`d[“m”]` 的默认值0+1 = 1，后面的道理就一样了：  

```python  
>>> s = 'mississippi'
>>> d = defaultdict(int)
>>> for k in s:
...     d[k] += 1
...
>>> list(d.items())
[('i', 4), ('p', 2), ('s', 4), ('m', 1)]
```  


