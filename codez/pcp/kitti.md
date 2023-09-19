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
                * `self.data_augmentor`是`DataAugmentor`（`./OpenPCDet/pcdet/datasets/augmentor/data_augmentor.py`），字面意义能做data aug：  
                    * `gt_sampling`  
                    * `random_world_flip & rotation & scaling & translation`  
                    * `random_local_flip & rotation & scaling & translation`  
                    * ...  
                * 
            * ..
        * 子类`KittiDataset` - `./OpenPCDet/pcdet/datasets/kitti/kitti_dataset.py`  
            * 


## Kitti点云可视化  
参考链接列表：  
* [KITTI数据集可视化（一）：点云多种视图的可视化实现](https://blog.csdn.net/weixin_44751294/article/details/127345052)  
* [KITTI数据集可视化（二）：点云多种视图与标注展示的可视化代码解析](https://blog.csdn.net/weixin_44751294/article/details/128569985)  

---  













