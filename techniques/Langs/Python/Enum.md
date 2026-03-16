# Enum类  

2021/8/26  

直接抄自[这篇博客](https://www.cnblogs.com/skaarl/p/10279428.html)，有丶恶劣XD  
但是我又抄了[枚举的扩展](https://www.jianshu.com/p/f40fb915c783?utm_campaign=maleskine&utm_content=note&utm_medium=seo_notes&utm_source=recommendation)，所以还不算太恶劣！  


- [枚举的定义](#枚举的定义)
- [枚举取值](#枚举取值)
- [迭代器](#迭代器)
- [枚举比较](#枚举比较)
- [枚举扩展](#枚举扩展)


## 枚举的定义  
* 定义枚举要导入enum模块，枚举定义用class关键字，继承Enum类  

```python  
from enum import Enum

class Color(Enum):
    red = 1
    orange = 2
    yellow = 3
    green = 4
    blue = 5
    indigo = 6
    purple = 7
```  

* 代码分析：
    1. 上面的代码，我们定义了颜色的枚举Color。  
    2. 颜色枚举有7个成员，分别是Color.red、Color.orange、Color.yellow等。  
    3. 每一个成员都有它们各自名称和值，Color.red成员的名称是：red，值是：1。  
    4. 每个成员的数据类型就是它所属的枚举。【*注：用class定义的类，实际上就是一种类型】  

* 定义枚举时，成员名称不允许重复  

```python  
from enum import Enum

class Color(Enum):
    red = 1
    red = 2
```  

会报错：  

```  
TypeError: Attempted to reuse key: 'red'
```  

* 默认情况下，不同的成员值允许相同。但是两个相同值的成员，第二个成员的名称被视作第一个成员的别名  

```python  
from enum import Enum

class Color(Enum):
    red = 1
    red_alias = 1
```  

成员Color.red和Color.red_alias具有相同的值，那么成员Color.red_alias的名称red_alias就被视作成员Color.red名称red的别名。  

* 如果枚举中存在相同值的成员，在通过值获取枚举成员时，只能获取到第一个成员  

```python  
from enum import Enum

class Color(Enum):
    red = 1
    red_alias = 1

print(Color(1))
```  

输出结果是`Color.red`  

* 如果要限制定义枚举时不能定义相同值的成员，可以使用装饰器@unique【要导入unique模块】

```python  
from enum import Enum, unique

@unique
class Color(Enum):
    red = 1
    red_alias = 1

print(Color(1))
```  

输出结果是  

```  
ValueError: duplicate values found in <enum 'Color'>: red_alias -> red
```  

## 枚举取值  
* 通过成员的名称来获取成员  

```python  
Color['red']
```  

输出结果是`Color.red`。  

* 通过成员值来获取成员  

```python  
Color(2)
```  

输出结果也是`Color.red`。  

* 通过成员，来获取它的名称和值  

```python  
color_member = Color.red
color_member.name
color_member.value
```  

输出分别是`red`和`1`。  

## 迭代器  
* 枚举支持迭代器，可以遍历枚举成员  

```python  
for color in Color:
    print(color)
```  

输出结果是`color.red,...`，改成`color.value`会成为对应的值。  

* 如果枚举有值重复的成员，循环遍历枚举时只获取值重复成员的第一个成员  

```python  
from enum import Enum

class Color(Enum):
    red = 1
    orange = 2
    yellow = 3
    green = 4
    blue = 5
    indigo = 6
    purple = 7
    red_alias = 1

for color in Color:
    print(color)
```  

输出结果是`Color.red、Color.orange、Color.yellow、Color.green、Color.blue、Color.indigo、Color.purple`，但是`Color.red_alias`并没有出现。  

* 如果想把值重复的成员也遍历出来，要用枚举的一个特殊属性`__members__`  

```python  
from enum import Enum

class Color(Enum):
    red = 1
    blue = 2
    yellow = 3
    red_alias = 1

for color in Color.__members__:
    print(color)
```  

输出结果为`red blue yellow red_alias`，只有它们的`name`。  

或者`for color in Color.__members__.items():`，输出结果为`('red', <Color.red: 1>)('blue', <Color.blue: 2>)('yellow', <Color.yellow: 3>)('red_alias', <Color.red: 1>)`。  

## 枚举比较  
* 枚举成员可进行同一性比较  
`Color.red is Color.red` -> `True`  
`Color.red is not Color.blue` -> `False`  
* 枚举成员可进等值比较  
`Color.blue == Color.red` -> `False`  
`Color.blue != Color.red` -> `True`  
* 枚举成员不能进行大小比较
`Color.red < Color.blue` -> `ypeError: '>' not supported between instances of 'Color' and 'Color'`  
但是它们的值可以比较`Color.red.value > Color.blue.value` -> `False`  

## 枚举扩展  
* 枚举不能通过继承扩展：  

```python  
from enum import Enum

class Color(Enum):
    red = 1
    blue = 2
    yellow = 3
    red_alias = 1

class Colors(Color):
    white = 4
    black = 5

print(Colors.yellow)
```  

结果报错：`TypeError: Cannot extend enumerations`。  

* 但是可以通过[奇技淫巧](https://www.jianshu.com/p/f40fb915c783?utm_campaign=maleskine&utm_content=note&utm_medium=seo_notes&utm_source=recommendation)扩展：  

```python  
# noinspection PyProtectedMember
def extend_to_enum(enum, extend_dict):
    """
    扩展枚举类项目
    :params enum: Enum 枚举类型
    :params extend_dict: dict 追加的项目和值的字典
    :return: None
    """
    # 先做 key, value的唯一性校验
    if (
        extend_dict.keys() & enum._member_map_.keys() or
        extend_dict.values() & enum._value2member_map_.keys()
    ):
        raise ValueError('extend_dict:{} is invalid'.format(extend_dict))

    # 追加枚举项目
    for key, val in extend_dict.items():
        # 实例化枚举对象，enum.__new__ 是被重写过的，
        # 所以直接使用 object.__new__ 加赋值的方式实现
        v = object.__new__(enum)
        v.__objclass__ = enum
        v._name_ = key
        v._value_ = val

        # 将枚举对象加入枚举类型的映射表里
        enum._member_map_[key] = v  # 名字对应对象的字典
        enum._member_names_.append(key)  # 名字列表
        enum._value2member_map_[val] = v  # 值对应对象的字典
```  


