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
*Line98(`if self.multiprocess:`)至Line112(`num_workers=workers_per_queue, shuffle=False, **test_kwargs)`)设置`multiprocess`，是否多线程只有`sampler`的设置区别。  
*Line122(`self.last_epoch = 0`)至Line127(`self._is_setup = False`)设置trainer的当前状态，看样子初始化后还需调用`setup`等方法。  

* `setup`方法：设置存储路径/文件/保存间隔等。  

* `save`方法：保存模型。  

* `load`方法：读model&optimzier&scheduler。  

* `train`方法：训练模型。流程：写log -> 过epoch，有个warm_up的判断，后面是调用下文的`train_epoch`与`infer_epoch`方法训练并eval模型，并写log，判断条件存模型。  

* `evaluate_split`方法：在训练集或者测试集上评估模型性能。  

* `_load_state_dict`方法：从state dict中读模型。  

* `_init_optimizer`方法：初始化optimizer。  

* `_init_scheduler`方法：初始化scheduler。  

* `train_epoch`方法：单步训练。回头好好看看？  

* `infer_epoch`方法：evaluate一个epoch，回头也看看。

* `on_epoch_start`&`on_epoch_end`方法：在epoch前后执行一些操作，奇怪的是`self.model`和`self.objective`有一些方法：  
    * `self.model.on_epoch_start` & `self.model.on_epoch_end`  
    * `self.objective.on_epoch_start` & `self.objective.on_epoch_end`  

* `def _forward_once_for_flops`方法：前传一步求flop数量。  



## 问题集合  
* ~~scheduler是什么干什么的？~~
A:和学习率调整相关。  

## TO-DO  
* `train_epoch`和`infer_epoch`方法应该需要看看，理解pytorch。  



