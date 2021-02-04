# CNN_model.py

包括：  
* `AuxiliaryHead(nn.Module)`  
* `AuxiliaryHeadImageNet(nn.Module)`  
* `CNNGenotypeModel(FinalModel)`  
* `CNNGenotypeCell(nn.Module)`  
 这几个类。其中bnn_model.py中的`BNNGenotypeModel`直接继承自`CNNGenotypeModel`，所以目前只看了`CNNGenotypeModel`。  


## New Funcs


## Class
### CNNGenotypeModel(FinalModel)
由`NAME = "cnn_final_model"`**推测**为最终训练的CNN模型的基类。  
* `__init__`方法  
出现的属性有（不含父类中的属性）：  
    * `search_space`：搜索空间  
    * `device`：训练设备？
    * `genotypes`  
    * `num_classes`：应该指的是图像分类的类别数  
    * `init_channels`：初始通道数  
    * `layer_channels`：输入一个tuple，目测是每层的channel数？  
    * `stem_multiplier`  
    * `dropout_rate`：训练的dropout率  
    * `dropout_path_rate`：路径dropout率  
    * `auxiliary_head`  
    * `auxiliary_cfg`  
    * `use_stem`：默认参数为`"conv_bn_3x3"` 
    * `stem_stride`  
    * `stem_affine`  
    * `no_fc`  
    * `cell_use_preprocess`  
    * `cell_pool_batchnorm`  
    * `cell_group_kwargs`  
    * `cell_independent_conn`  
    * `cell_use_shortcut`  
    * `cell_shortcut_op_type`  
    * `cell_preprocess_stride`  
    * `cell_preprocess_normal`  
    * `schedule_cfg`  

*认为初始化中对`genotypes`的处理不是很重要，没看。



## 问题集合

## TO-DO
* 中间出现的`CNNGenotypeCell`类没看