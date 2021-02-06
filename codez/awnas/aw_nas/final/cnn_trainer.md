# cnn_trainer.md

2021/2/6  

该文件包括`_warmup_update_lr`函数和`CNNFinalTrainer`类。  

## New Funcs  

## Function  
* `_warmup_update_lr(optimizer, epoch, init_lr, warmup_epochs)`：更新优化器的学习率  

## Class  
### CNNFinalTrainer
继承自`FinalTrainer`类。  
* `__init__`方法  
传入参数：  
    * `model`  
    * `dataset`  
    * `device`  
    * `gpus`  
    * `objective`：和性能相关，包括  
        * `get_perfs`  
        * `perf_names()`  
        * `get_loss`  
    * `multiprocess`  
    * `epochs`  
    * `batch_size`  
    * `optimizer_type`  
    * `optimizer_kwargs`  
    * `learning_rate`  
    * `momentum`  
    * `warmup_epochs`  
    * `optimizer_scheduler`  
    * `weight_decay`  
    * `no_bias_decay`  
    * `grad_clip`  
    * `auxiliary_head`  
    * `auxiliary_weight`  
    * `add_regularization`  
    * `save_as_state_dict`  
    * `workers_per_queue`  
    * `eval_no_grad`  
    * `eval_every`  
    * `calib_bn_setup`  
    * `schedule_cfg`  


## 问题集合


## TO-DO


