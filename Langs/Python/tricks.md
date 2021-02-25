# tricks

2021/2/23  

不定时更新一些python&torch的tricks...估计会很乱。  

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [tricks](#tricks)
  - [tuple初始化](#tuple初始化)
  - [用dict填默认设置](#用dict填默认设置)

<!-- /code_chunk_output -->

## tuple初始化
读bnn_ops.py的时候看到了这种初始化的方法，觉得很快（可以少敲很多等号）：  

```python  
        (
            self.in_channels,
            self.out_channels,
            self.kernel_size,
            self.stride,
            self.padding,
            self.dilation,
            self.groups,
            self.dropout_ratio,
            self.bi_w_scale,
            self.bi_act_method,
            self.use_bias,
        ) = (
            in_channels,
            out_channels,
            kernel_size,
            stride,
            padding,
            dilation,
            groups,
            dropout_ratio,
            bi_w_scale,
            bi_act_method,
            bias,
        )
```  

做了一点简单的实验：  

```python  
class Test_4_tuple_ini():
    def __init__(self):
        (
            self.first_prop,
            self.second_prop,
            self.third_prop
        ) = (
            1,
            2,
            3
        )

instance = Test_4_tuple_ini()
print(instance.first_prop)
print(instance.second_prop)
print(instance.third_prop)
```  

输出的结果是：  

```python  
1
2
3
```  

## 用dict填默认设置  
起因是在看[bnn_ops.py](https://youcaijun98.github.io/codez/awnas/aw_nas/ops/bnn_ops.html)的时候看到了这种操作（~~虽然最后发现其实cfgs是下面注册需要用到的~~）：
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202102250002.png)  
所以大胆猜想这样就可以把下面的dict里面的设置作为默认设置填到上面的调用里，**毕竟实在太像`**kwargs`了**。  
做了个简单的实验：  

```python  
class This_is_a_test_class():
    def __init__(self,
                 prop1=1,
                 prop2=2,
                 prop3=3,
                 prop4=4):
        self.prop1 = prop1
        self.prop2 = prop2
        self.prop3 = prop3
        self.prop4 = prop4

    def validate(self):
        print("prop1 is {}".format(self.prop1))
        print("prop2 is {}".format(self.prop2))
        print("prop3 is {}".format(self.prop3))
        print("prop4 is {}".format(self.prop4))

default_para = {
    "prop1": "one",
    "prop2": True,
    "prop3": ["person", "woman", "man", "camera", "TV"],
    "prop4": {
        "prop5": 1,
        "prop6": (2, 3)
    },
}
test_instance = This_is_a_test_class(**default_para)
test_instance.validate()
```  

输出的结果为：  

```python  
prop1 is one
prop2 is True
prop3 is ['person', 'woman', 'man', 'camera', 'TV']
prop4 is {'prop5': 1, 'prop6': (2, 3)}
```  

好耶！  



