# ipdb

2021/2/22  

还没有用到，但是总之先记录下来。[参考资料](https://xmfbit.github.io/2017/08/21/debugging-with-ipdb/)。  

IPDB(Ipython Debugger)是一款集成了IPython的Python代码命令行调试工具。有两种~~食用方式~~：  

## 写在codez里  

```python
import ipdb
# some code
x = 10
ipdb.set_trace()
y = 20
# other code
```  

程序会在执行完`x = 10`这条语句之后停止，展开IPython环境，就可以自由地调试了。（**注意要把`ipdb.set_trace()`放在想停止的地方之前！**）  

## 命令式  

需要按步执行，边运行边跟踪代码流并进行调试时，使用交互式的命令式调试方法更加有效。启动IPDB调试环境的方法如下：  

```bash  
python -m ipdb your_code.py
```  

IPDB环境中的指令包括  
* 帮助：使用`h`即可调出IPDB的帮助。可以使用`help command`的方法查询特定命令的具体用法。  
* 下一条语句：使用`n(next)`执行下一条语句。注意一个函数调用也是一个语句。（意即不会自动step into）  
* 进入函数内部：使用`s(step into)`进入函数调用的内部  
* 打断点：使用`b line_number(break)`的方式给指定的行号位置加上断点。使用`b file_name:line_number`的方法给指定的文件（还没执行到的代码可能在外部文件中）中指定行号位置打上断点。另外，打断点还支持指定条件下进入，可以查询[帮助文档](https://wangchuan.github.io/coding/2017/07/12/ipdb-cheat-sheet.html)。  
* 一直执行直到遇到下一个断点：使用`c(continue)`执行代码直到遇到某个断点或程序执行完毕。  
* 一直执行直到返回：使用`r(return)`执行代码直到当前所在的这个函数返回。  
* 跳过某段代码：使用`j line_number`(jump)可以跳过某段代码，直接执行指定行号所在的代码。  
* 更多上下文：在IPDB调试环境中，默认只显示当前执行的代码行，以及其上下各一行的代码。如果想要看到更多的上下文代码，可以使用`l first[, second]`(list)命令。其中first指示向上最多显示的行号，second指示向下最多显示的行号（可以省略）。当second小于first时，second指的是从first开始的向下的行数（相对值vs绝对值）  
* 我在哪里：调试兴起，可能你会忘了自己目前所在的行号。例如在打印了若干变量值后，屏幕完全被这些值占据。使用`w`或者`where`可以打印出目前所在的行号位置以及上下文信息  
* 这是啥：我们可以使用`whatis variable_name`的方法，查看变量的类别（感觉有点鸡肋，用`type`也可以办到）  
* 列出当前函数的全部参数：当你身处一个函数内部的时候，可以使用`a(argument)`打印出传入函数的所有参数的值。  
* 打印：使用`p(print)`和`pp(pretty print)`可以打印表达式的值。  
* 清除断点：使用`cl`或者`clear file:line_number`清除断点。如果没有参数，则清除所有断点。  
* 再来一次：使用`restart`重新启动调试器，断点等信息都会保留。`restart`实际是`run`的别名，使用`run args`的方式传入参数。  
* 退出：使用`q`退出调试，并清除所有信息。  



