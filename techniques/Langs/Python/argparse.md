# Argparse  

2021/4/13  

从命令行获取参数的设置，请看[官方文档](https://docs.python.org/zh-cn/3/library/argparse.html)。  

更新一些使用细节：  

## argparse.add_argument  
* `action`为`store_true`的使用说明：  
[参考文献](https://blog.csdn.net/zkq_1986/article/details/85287896)在此。`action`设置为`store_true`会让出现此参数时（如果不传bool值）的值默认为`True`（和一般的default setting还不一样），见参考代码：  

```python  
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--t', help=' ', action='store_true', default=False)

config = parser.parse_args()

print(config.t)
```  

直接运行`python a.py`，输出结果`False`;  

运行`python a.py --t`，输出结果`True`;  

也就是说，`action='store_true'`，只要运行时该变量有传参就将该变量设为`True`。  




