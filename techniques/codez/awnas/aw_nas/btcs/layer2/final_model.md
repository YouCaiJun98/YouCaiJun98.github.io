# final_model.py  

2021/2/28  

包括：  
* **MicroDenseCell**  
* **MacroStagewiseFinalModel**  
* **MacroSinkConnectFinalModel**  
类。  

## Class  
### MicroDenseCell  
继承自aw_nas\final\base.py中的`FinalModel`类。  
含有方法：  
* `__init__`  
还是把`__init__`的传入参数放一下：  

```python  
def __init__(
        self,
        search_space,
        arch,
        num_input_channels,
        num_out_channels,
        stride,
        postprocess=False,  # default use preprocess
        process_op_type="nor_conv_1x1",
        use_shortcut=True,
        shortcut_op_type="skip_connect",
        # applied on every cell at the end of the stage, before the reduction cell, to ensure x2 ch in reduction
        use_next_stage_width=None,  # applied on every cell at the end of the stage, before the reduction cell, to ensure x2 ch in reduction
        is_last_cell=False,
        is_first_cell=False,
        skip_cell=False,
        schedule_cfg=None,
    ):
```  

这里暂时需要注意的参数有`postprocess`、`use_shortcut`。  
`search_space`参数进一步包括`num_steps`、`_num_nodes`、`primitives`、`num_init_nodes`属性。  
Line79 - Line86：下面有个`use_next_stage_width`的判断，这一项apply到每个stage最后一个cell上（reduction cell前的那个），需要保证in_c == out_c，以保证align its width for the latter stage。  
Line95有段注释，是说stage的最后一个cell不会用cell-wise shortcut，因为难以handle ch disalignment：  

```  
no 'use-next-stage-width' is applied in to the cell-wise shortcut,
since the 'use-next-stage-width' only happens in last cell before reduction,
the shortcut is usually plain shortcut and could not handle ch disalignment
```  

Line93 - Line115：如果`self.use_shortcut`就根据`self.shortcut_op_type`选用对应的shortcut op，需要注意的是依据`self.postprocess`的不同channel的数量不一样（when using preprocess, the shortcut is of 4C width;when using postprocess, the shortcut is of C witdh）  

Line117 - Line150：根据设置写edge的op，**有点高端，但没有深究**。  

Line152 - Line177：根据`self.use_concat`和`self.postprocess`（影响`self.process_op`的C_in和C_out）注册`self.process_op`。  


* `forward`  






