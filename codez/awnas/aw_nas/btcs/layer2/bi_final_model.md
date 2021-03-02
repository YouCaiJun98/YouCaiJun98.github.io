# bi_final_model.py  

2021/3/2  

包括：  
* BinaryMacroStagewiseFinalModel  
* BinaryMacroSinkConnectFinalModel  
类。这个文件似乎主要是写查OP数量的hook的。  

## Class  
### BinaryMacroStagewiseFinalModel
继承自[final_model](https://youcaijun98.github.io/codez/awnas/aw_nas/btcs/layer2/final_model.html)中的`MacroStagewiseFinalModel`类。  
比父类多了`self.bi_flops`和`self._bi_flops_calculated`两个属性，前者指示BiOP的数量，后者指示BiOP有没有count过。  
方法:  
* **_hook_intermediate_feature(self, module, inputs, outputs)**  
根据module的类型（可为`nn.Conv2d`、`ops.BinaryConv2d`、`nn.Linear`）的数量增加bi_op/flop_op计数。  
* **forward(self, *args, **kwargs)**  
基本上沿用父类的`forward`方法，多的东西只有判断bi_op有没有数完，打印log。  

### BinaryMacroSinkConnectFinalModel  
继承自[final_model](https://youcaijun98.github.io/codez/awnas/aw_nas/btcs/layer2/final_model.html)中的`MacroSinkConnectFinalModel`类。  
比父类多了`self.bi_flops`和`self._bi_flops_calculated`两个属性，前者指示BiOP的数量，后者指示BiOP有没有count过。  
和上面类似，不赘述。  
