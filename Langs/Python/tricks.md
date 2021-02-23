# tricks

2021/2/23  

不定时更新一些python&torch的tricks...估计会很乱。  

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