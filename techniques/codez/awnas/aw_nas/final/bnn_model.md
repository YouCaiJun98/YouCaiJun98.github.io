# bnn_model.py

## 出现的未知函数
* `isinstance()`  
`isinstance() `函数来判断一个对象是否是一个已知的类型，类似 `type()`，但是不同之处在于：  
    * type() 不会认为子类是一种父类类型，不考虑继承关系。  
    * isinstance() 会认为子类是一种父类类型，考虑继承关系。  

更多请参考这篇[博客](https://www.runoob.com/python/python-func-isinstance.html)。  

## 出现的类
* `BNNGenotypeModel`  
继承自`CNNGenotypeModel`，里面就override了`__init__`、`_hook_intermediate_feature`、`forward`。  
    * `_hook_intermediate_feature`  
    用来计算里面的flops与biops数目。其中对于flops的计算如下：  

    ```  
    if isinstance(module, nn.Conv2d):
        self.total_flops += 2* inputs[0].size(1) * outputs.size(1) * \
                        module.kernel_size[0] * module.kernel_size[1] * \
                        outputs.size(2) * outputs.size(3) / module.groups
    elif isinstance(module, nn.Linear):
        self.total_flops += 2 * inputs[0].size(1) * outputs.size(1)
    ```  

    对于biops的计算如下：  

    ```  
    elif isinstance(module, ops.BinaryConv2d):
        # 1-bit conv
        self.bi_flops += 2* inputs[0].size(1) * outputs.size(1) * \
                            module.kernel_size * module.kernel_size * \
                            outputs.size(2) * outputs.size(3) / (module.groups)
    ```  

    * `forward`  
    就是前向传播？里面增加了在log里输出biops的环节。

## 问题集合
* 不知道`module.group`是啥，好像是`in_channels`和`out_channels`的乘积？  
* 不知道`inputs[0].size(1)`等等的具体含义。  
* model文件有什么作用...是整个模型的基类吗？那和module有什么关系？
