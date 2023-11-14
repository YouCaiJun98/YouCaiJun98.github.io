# LLM Quantizaiton 101  

2023/11/7  
一代人有一代人的量化要看（大嘘）  

---  

* gen_act_stat.py  
    * 这里的trainloader是一个长度为nsamples(1024)的list，其中每个元素是一个长度为2的tuple，每个tuple元素都是个长度为(1, 2048)的tensor；  
    [ ] 在写hook的时候只对Linear层的权重和output挂了hook，意思是只量化了linear层？  
    * （和pytorch hook可能有关的性质）在forward hook的scope下，有m, x, y三个传入参数，分别是当前的module，当前module的输入，当前module的输出：
        * 例如，可以写一个hook函数：  
        ```python  
        def stat_input_hook(m, x, y, name):  
            if isinstance(x, tuple):
                x = x[0]
            stat_tensor(name, x)
            stat_weight(name, m.weight)
        ```  
        入参里的m, x, y似乎是固定的；在推理前注册这个hook：  
        ```python    
        for name, m in model.named_modules():
            if isinstance(m, nn.Linear):
                hooks.append(
                    m.register_forward_hook(
                        functools.partial(stat_input_hook, name=name))
                )
        ```   
        在推理结束后再删除这个hook：
        ```python    
        for h in hooks:
            h.remove()
        ```   
        在hook里打断点观察，发现y就是m(x)。  

    * 这里是统计一个module **输入tensor**和权重的最大最小值，并更新到一个dict里存下来。
        * 一个很蠢但还是犯了的错误：在统计输入tensor的最大最小值的时候，是按照(-1, hidden_dim)展开后在dim=0处记录的最大最小值以及std（一个例子是，如果一个(bs, token, hidden_dim)是(16, 4, 8)的dummy输入，统计结果的尺寸是(1, 8)），看起来统计出来的结果是per-channel的，进一步加工可以得到per-tensor的；
            [ ] 一个没想清楚的问题是，在不动态量化的前提下per-token量化其实就是per-tensor吧，统计各个channel上历史最大最小值，还不是等于在整个tensor上去算最值？  
            * 出于上述原因，weight的统计方式和tensor的一样，都是在dim=0处统计，所得结果就是(1, w_out_dim)尺寸的，后面可以很自然地做成per-channel或者per-tensor量化；
* ./config/opt-1.3b_w4a4.yaml  
    * qkvfc_cluster是啥意思？（cluster？意思是分组大小吗？）  
    * a_q_method和w_q_method里的'mix'又是啥意思？  
    * a_q_mode的's_woz'是什么意思？  
    * 

* main_opt_w4a4.py  
    * 算了一个std的kmeans（完全不懂这么分有什么意义）  
        * ./group_methods/kmeans.py  
            * max_std_kmeans  
                * 输入是一个(576, 2048)的tensor（576=(3+3)*96, 2048是hidden_dim）；  
                * 输出是一个(8, 576)的centroid和(1, 2048)的label，看起来是在每个2048的维度做了8个聚类中心的聚类，看描述可能只有里面的std有意义；（但是为什么要这么聚类呢？）    
    * 做了一个smooth_lm：  
        * ~~预计是把scale吸收到LN里~~；  
            * 订正，是smoothquant的w/a smooth；    
        * ./quantize/smooth.py  
            [ ] smooth的scale的具体计算方式没有记住，需要再ck；  
            * 一个细节：在LN中做scale的系数中的weight部分是根据Q/K/V权重的最大值来确定的，这个目前还没想清楚（straight-forward来想好像也有点道理）  
            * 另一个细节，这个scale是在output_channel维度乘上去的；  
            * 还有一个没想清楚但是似乎很简单的问题，为什么output_scale是作用在fc1上而不是fc2上的？似乎和输入输出通道有关，回头再想吧。  
            * 还有还有一个没想清楚但是又似乎很简单的问题，为什么在LN和weight上做完scale后没有去修改act_stat和weight_stat？  
    * 

### TODO
[ ] 没看dataset里具体是怎么load数据的，看起来是直接采样了几个东西  
[ ] 为什么在初始化tokenizer和model后要再搞个lm_model？这个是干什么的？  
