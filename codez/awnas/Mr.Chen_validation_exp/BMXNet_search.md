# Comparation between BMXNet & AWNAS  

2021/4/2  

摸了好久，一直不敢去看这个代码，今天总算鼓起勇气去看了，就算自己害怕成长，差也要交不是。  

## Model Body  
首先看一下我们的XNOR Res18和BMXNet实现的Res18有什么不同。  
### Stem  
比较的开始就发现了不同，出现在Stem上：  
 
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104020001.png)  

BMXNet的Stem Conv层显然更大一些，**用了7x7的kernel**，具体的顺序是`BN-Conv-BN-ReLU-Maxpooling-BN`，这和原文描述的把一个Conv层拆成两个小Conv层的设置不一样啊。  
AWNAS中的Stem Conv是拆成两个3x3的小kernel，具体顺序是`Conv-BN-ReLU-Conv-BN`。  

### Normal Cell  
果然cell里也出现了非常明显的不一致，甚至感觉非常合理。  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104020002.png)  

~~AWNAS中的一个cell很大（而且有两个op？我需要好好看看ResNet18的结构了），相比之下BMXNet的cell就显得非常干瘪。~~ 原因找到了，借用一下一张[网图](https://www.baidu.com/link?url=pI-qz1Ametz0nfrcyNZlnQT7wIJyOzWDegELJlIzYbA6A7OVyPYOdyDEdTv14AOm&wd=&eqid=b11c89e4000642af000000066066cd1b)（准确性存疑），AWNAS是把skip connection连接的层layer合成了一个cell，BMXNet是裸着把Conv layer堆在一起：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104020003.jpg)  

使用`ipdb`打断点看[net variable](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/codez/awnas/Mr.Chen_validation_exp/BMXNet_net_variable.txt)以及检查[model.log](https://github.com/YouCaiJun98/YouCaiJun98.github.io/blob/master/codez/awnas/Mr.Chen_validation_exp/model.log)发现了一些**异常**，需要看代码确认一下：  
* 看不到preprocess的地方。按说我们这里每个cell前应该有1x1的preprocess，BMXNet每两层layer前应该也有？但是`net`中看不到，需要进一步确认。  
* ~~Block/layer中的顺序和原文不对~~，不知道是`net`的问题还是写的代码就是如此，原文中是`BN-ReLU-Conv-Pool`，~~但是`net`中显示的是`BN-QActivation-Conv-BN`~~。问题解决了，原来串起来看是一样的，但是AWNAS和BMXNet都没有用`Pool`？而且AWNAS里Stem后面的`BN`能不能和第一个Block开始的`BN`合并到一起？最后一个layer的顺序就有问题了，AWNAS依然是`BN-ReLU-Conv`最后跟一个global pooling，BMXNet最后是`qact-qconv-BN-ReLU`最后接global pooling。  
* AWNAS中的layer-wise `shortcut`感觉有点奇怪，需要再看看到底有没有起作用。  
* 在BMXNet中都没有看到cell-wise shortcut的描述，需要看看（AWNAS中的skip connect应该是和op1/2并列的那个，也可以再确认下）。  

### Reduction Cell  
还是很有点奇怪。  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104020004.png)  

* 首先依然是没有看到preprocess的影子，这个可能写在了basic block里了，需要注意一下继承里面。  
* AWNAS中的`downsaple`不是一个(64,128)的`Conv`，是两个(64,64)的`Conv`并列？？之后又分别接了两个`AvePool`。这里连接64/128的skip op是FP的。BMXNet的情况就很有些奇怪，他已经有个`qconv`是64 -> 128的操作了，后面又来了个downsample layer？而且还是64 -> 128，同时使用`FP Conv`？这边暂时**猜测它是描述的cell-wise skip op**，但是出现的位置还是感觉很奇怪（在必经之路上？）。  

## Noticeable Codez Difference  

## Notes for Codez  
* 字典里定义的ResNet18是：  

```python  
resnet_spec = {18: ([2, 2, 2, 2], [64, 64, 128, 256, 512]),
               34: ([3, 4, 6, 3], [64, 64, 128, 256, 512]),
               50: ([3, 4, 6, 3], [64, 256, 512, 1024, 2048]),
               101: ([3, 4, 23, 3], [64, 256, 512, 1024, 2048]),
               152: ([3, 8, 36, 3], [64, 256, 512, 1024, 2048])}
```  

第一个list是"layers"，第二个list是"channels"，观察上面的大网图，layers（的每一个element）应该是里面不同颜色的块（对应AWNAS里的cell），channels指的大概是算上stem各个layer中的channel。  

### Memoir for Model Construction  
* Model Construction的入口是在`BMXNet-v2/example/bmxnet-examples/image_classification.py(86)get_model()`。原文是：  

```python  
    with gluon.nn.set_binary_layer_config(bits=opt.bits, bits_a=opt.bits_a,approximation=opt.approximation,
                                          grad_cancel=opt.clip_threshold,activation=opt.activation_method,
                                          weight_quantization=optweight_quantization):
        net = binary_models.get_model(opt.model, **kwargs)
```  

`binary_models.get_model(opt.model, **kwargs)`的方法写在了`/BMXNet-v2/example/bmxnet-examples/binary_models/__init__.py`里，里面写了个dict，根据name索引对应的class，返回class的构造方法。用法和下一节中的 *New perspective of Python Class* 描述一致。（不是很一致，见下）  
通过字典索引了方法`resnet18_e1`，方法里进一步套了一个方法`get_resnet_e`，在这个方法里才用到了下节说的字典存类名，即`net = resnet_class(block_class, layers, channels, **kwargs)`。  
* `self.features`是在`ResNetE`类的`__init__()`方法里添加的。  
* initial layer（也就是stem层）的添加是通过`add_initial_layers`方法完成的，它在`BMXNet-v2/example/bmxnet-examples/binary_models/common_layers.py`里。  



## While Reading Codez
### New perspective of Python Class  
在单步看BMXNet的时候发现了奇怪的现象：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104060001.png)  

上面用`resnet_class`作为function，**但是上下文并没有这个方法或者类**。将断点打到这句的上面：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104060002.png)  

发现这个**变量是一个Class**，来源是这里：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202104060003.png)  

这里写了一个装有两个元组的List作为索引，**元组中的第一个元素就是上文出现的类**，后面把这个类赋给了变量`resnet_class`（应该是作为func用了？用到了它的`__init__`），就在这里神不知鬼不觉地把model给建起来了。  

**收获：原来类名可以当值传来传去啊，也合理，像个指针一样？**  

2021/4/7补充：原来`binary_models/__init__.py`的字典也是这种用法！通过name索引~~类名~~，返回的时候是通过类名使用类的构造方法！  
有点不一样，这里是用字典索引方法名！  








