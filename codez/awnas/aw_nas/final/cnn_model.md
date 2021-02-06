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
        * 似乎是一个tuple，里面包括  
            * `num_cell_groups`  
            * `num_init_nodes`  
            * `cell_layout`  
            * `reduce_cell_groups`  
            * `num_layers`  
            等元素  
    * `device`：训练设备？
    * `genotypes`：是evolution方法的？~~但是为什么这个类也叫genotype~~  
    * `num_classes`：应该指的是图像分类的类别数  
    * `init_channels`：初始通道数  
    * `layer_channels`：输入一个tuple，目测是每层的channel数？  
    * `stem_multiplier`  
    * `dropout_rate`：训练的dropout率  
    * `dropout_path_rate`：路径dropout率  
    * `auxiliary_head`  
    * `auxiliary_cfg`  
    * `use_stem`：默认参数为`"conv_bn_3x3"`，*可选的类型是`(list, tuple)`或者`bool`？ 
    * `stem_stride`  
    * `stem_affine`  
    * `no_fc`:似乎是决定最后输出是否进行分类的bool值。  
    * `cell_use_preprocess`  
    * `cell_pool_batchnorm`  
    * `cell_group_kwargs`：应该是自定义的cell布局（包括cell class和channel数？）  
    * `cell_independent_conn`  
    * `cell_use_shortcut`  
    * `cell_shortcut_op_type`  
    * `cell_preprocess_stride`  
    * `cell_preprocess_normal`  
    * `schedule_cfg`  

    *认为初始化中对`genotypes`的处理不是很重要，没看。  
    *Line134（`if not self.use_stem:`）至Line150（`init_strides = [1] * self._num_init`）似乎是根据`self.use_stem`进行“sub module”的初始化。  
    *Line161（`for i_layer, stride in enumerate(strides):`）至Line169(`num_out_channels = num_channels`)计算每层的输入输出channel数，至Line182(`kwargs = {}`)是用`cell_group_kwargs`中的设置获取channel数。  
    *Line185(`cell = CNNGenotypeCell(self.search_space,`)至Line205(`self.cells.append(cell)`)是根据config生成cell，并拼到一起。  
    *Line215(`self.global_pooling = nn.AdaptiveAvgPool2d(1)`)至Line225(`self.to(self.device)`)是设置global_pooling、drop_out、final_classification、device。  
  

  
* `set_hook`方法和`_hook_intermediate_feature`方法  

    *Line232(`def set_hook(self):`)至Line247(`pass`)注册hook用于计算参数数量。**hook的写法很重要，但是还没看。**  

* `forward`方法、`forward_one_step`方法和`forward_one_step_callback`方法  

    *应该是前向传播、单步前传、带回调的单步前传，**暂时不关心。**  



## 问题集合
* `stem`指的是什么？  
    * `forward`中也出现了  
* `prev_num_channel`是干嘛的？  
* `auxiliary_net`是什么？对应Line207(`if i_layer == (2 * self._num_layers) // 3 and self.auxiliary_head:`)至Line213(`prev_num_channels[-1], num_classes, **(auxiliary_cfg or {}))`)是做什么的？  

## TO-DO
* 中间出现的`CNNGenotypeCell`类没看  
* `ops.py`文件中的`ops.get_op`没有看  
* **pytorch里hook的写法**  
* 三个`forward`也没看  

  