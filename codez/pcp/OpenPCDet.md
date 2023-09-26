 # OpenPCDet  

## Overall Framework  
* OpenPCDet官网上给了个整体的模型框架，非常清楚：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230926154257.png)  
* 其中，一些典型模型的组成如下所示：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230926154423.png)  

## Dataset  
* Kitti的数据集加载与预处理见[这个页面](https://youcaijun98.github.io/codez/pcp/kitti.html)。  


## PointPillar实例  
### 模型初始化  
* 模型`PointPillar`在OpenPCDet中是个`detector`，似乎有对应的`backbone`（实际的网络定义）  
* `detector`的基类是`Detector3DTemplate`，主要靠里面的`build_networks`方法来实现模型定义。模型中包括的模块有：  
    * `VFE`(short for Voxel Feature Encoder):  
        * 甚至找到了个专门介绍`VFE`模块的[博客](https://blog.csdn.net/weixin_45080292/article/details/129880756)。看起来是负责做由point cloud到pillar的encoding过程；    
        * 定义在`./pcdet/models/backbones_3d/vfe/pillar_vfe.py`；  
        * VFE的一些参数设置：  
        ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230926154657.png)  
        * VFE的功能主要是靠`PFNLayer`实现的，定义也在同一个文件中；  
            * `PointPillar`的PFNLayer就是一个Linear(10, 64) + 一个BN1d：  
            ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230926155630.png)  
            * 初始化函数里除了定义`PFNLayer`就是算几个offset；  
    * `backbone_3d`：  
        * 这个是空的（*of course...*）      
    * `map_to_bev_module`:  
        * 定义在`./pcdet/models/backbones_2d/map_to_bev/pointpillar_scatter.py`；具体是`PointPillarScatter`；  
        * 看起来是生成pseudo image的模块；  
        * grid size(432, 496, 1)分别对应于`self.nx`, `self.ny`, `self.nz`.    
    * `pef`:  
        * None  
    * `backbone_2d`：  
        * 定义在`./pcdet/models/backbones_2d/base_bev_backbone.py`；具体是`BaseBEVBackbone`；  
        * 正经的模型定义；具体参数如下所示：  
        ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230926163440.png)  
        * 分成3个阶段（enc-dec对称的，一共6个block），每个stage有1（含有stride的） + num_layer[idx]个层（更具体的是，ZeroPad-Conv-BN-ReLU + num_layer[idx] * (Conv2d-BN-ReLU)）；  
        * in case I don't remember:  
        ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230926165305.png)  
        * deblocks则相对更thin一些，只有一个deconv； 
        * self.blocks & self.deblocks的全景图（nmd真的有必要放吗？）：  
        ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230926170321.png)  
        ![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/20230926170354.png)  
        * `forward`函数：  
            ```python
                def forward(self, data_dict):
                    """
                    Args:
                        data_dict:
                            spatial_features
                    Returns:
                    """
                    spatial_features = data_dict['spatial_features']
                    ups = []
                    ret_dict = {}
                    x = spatial_features
                    for i in range(len(self.blocks)):
                        x = self.blocks[i](x)

                        stride = int(spatial_features.shape[2] / x.shape[2])
                        ret_dict['spatial_features_%dx' % stride] = x
                        if len(self.deblocks) > 0:
                            ups.append(self.deblocks[i](x))
                        else:
                            ups.append(x)

                    if len(ups) > 1:
                        x = torch.cat(ups, dim=1)
                    elif len(ups) == 1:
                        x = ups[0]

                    if len(self.deblocks) > len(self.blocks):
                        x = self.deblocks[-1](x)

                    data_dict['spatial_features_2d'] = x

                    return data_dict
            ``` 
    * `dense_head`:  
        * 定义在`./pcdet/models/dense_heads/anchor_head_single.py`，具体是`AnchorHeadSingle`；    
        
    * ..  
    * ..  

