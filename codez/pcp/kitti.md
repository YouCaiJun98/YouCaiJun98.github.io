# Kitti for 3D Detection  

2023/9/19  

用来记录一下kitti dataset的学习情况！🧐🧐  

---  

来一点参考文献先：  
* [KITTI数据集](https://blog.csdn.net/weixin_36670529/article/details/103774700)    
* [【深度估计】KITTI数据集介绍与使用说明](https://zhuanlan.zhihu.com/p/364423582)  
* [自动驾驶开发者说 \| 数据集 \| 如何使用KITTI数据？](https://zhuanlan.zhihu.com/p/430490776?utm_id=0)  

## 目录结构与文件组织形式  
down下来的3D检测文件目录如下所示：  
```bash  

```


## Kitti数据加载  
* OpenPCDet中的kitti dataset setting是：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230919164224.png)  

* OpenPCDet中的Kitti Dataset实现： 
    * 有两个主要的类，基类`DatasetTemplate`和子类`KittiDataset`
        * 基类`DatasetTemplate` - `./OpenPCDet/pcdet/datasets/dataset.py`  
            * `__init__`初始化函数：  
                * 记录了dataset_cfg, training flag, class_name(car, pedestrain, cyclist), logger, path等一系列乱七八糟的属性；  
                * `point_cloud_range`是[0, -39.68, -3, 69.12, 39.68, 1],应该是数据集的属性，*但是各个维度的意义是什么呢？*  
                * `self.point_feature_encoder`是`PointFeatureEncoder`(`./OpenPCDet/pcdet/datasets/processor/point_feature_encoder.py`)，看描述应该是坐标转换；  
                * `self.data_augmentor`是`DataAugmentor`（`./OpenPCDet/pcdet/datasets/augmentor/data_augmentor.py`），字面意义能做data aug；根据config往aug queue里面填aug function：  
                    * `gt_sampling`  
                        * *TODO:这里又有个子类`database_sampler.DataBaseSampler`，没看*  
                    * `random_world_flip & rotation & scaling & translation`  
                    * `random_local_flip & rotation & scaling & translation`  
                    * ...  
                    * OpenPCDet中PointPillar的数据增强设置是，  
                    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230920102829.png)  
                    看起来只有`gt_sample`, `random_world_flip`, `random_world_rotation`, `random_world_scaling`这四个增强，*`box aug`怎么没有看到？*  
                * `self.data_processor`是`DataProcessor`（`./OpenPCDet/pcdet/datasets/processor/data_processor.py`），看描述应该是搞voxelization的（包括mask掉范围外的点、点采样之类的功能）；  
                    * OpenPCDet中PointPillar的数据处理设置是，  
                    ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230920112449.png)  
                    mask掉范围外的点，在训练时shuffle点，按照[0.16, 0.16, 4]的尺寸voxelization，每个voxel中有32个点，最大voxel数是16000（*和pointpillar不太一样哎？*）  
                        * *TODO:这里的shuffle_points又在干什么？*
                * `self.voxel_size`是[0.16, 0.16, 4]（*虽然4是啥不清楚，但是看起来还挺像pointpillar官方设置的*），`self.grid_size`是[432, 496, 1]（*TODO:这个是啥？*）
            * ..  
        * 子类`KittiDataset` - `./OpenPCDet/pcdet/datasets/kitti/kitti_dataset.py`  
            * `__init__`初始化函数：  
                * 最主要的初始化设置在基类`DatasetTemplate`中已经完成了，在这个类中的操作只是一些数据集位置记录等的操作。  
                * *TODO:有个`self.sample_id_list`，之前路径设置有问题，没用上这个，不知道会有什么影响...*  
            * ..  


## Kitti点云可视化  
参考链接列表：  
* [KITTI数据集可视化（一）：点云多种视图的可视化实现](https://blog.csdn.net/weixin_44751294/article/details/127345052)  
* [KITTI数据集可视化（二）：点云多种视图与标注展示的可视化代码解析](https://blog.csdn.net/weixin_44751294/article/details/128569985)  

---  













