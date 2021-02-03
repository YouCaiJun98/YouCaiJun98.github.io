# 创建MarkDown目录

2021/2/3  

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [创建MarkDown目录](#创建markdown目录)
  - [测试标题一](#测试标题一)
  - [测试标题三](#测试标题三)

<!-- /code_chunk_output -->

New Trick！  
在写博客的时候发现自己手敲一个目录出来太麻烦，[TOC]在github又不能用...所以就找到了使用**VSCode + MarkDown_Previewed_Enhanced**的解决方案！  
首先需要在VSCode中安装`MarkDown Previewed Enhanced`插件，打开需要生成目录的md文件，按下`ctrl + shift + P`并搜索`Markdown Preview Enhanced: Create Toc`来创建[TOC],效果如下：  
![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202102030006.png)  
接下来我们创建三个测试用标题：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202102030007.png)  

保存后生成目录：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202102030008.png)  
注意到使用在标题后添加`{ignore=true}`可以避免在目录中生成此标题：  

![](https://raw.githubusercontent.com/YouCaiJun98/MyPicBed/main/imgs/202102030009.png)  

下面是摘自[官方文档](https://shd101wyy.github.io/markdown-preview-enhanced/#/zh-cn/toc)的内容:  
设置选项  
* orderedList 是否使用有序列表  
* depthFrom, depthTo设置目录深度  
* ignoreLink 如果设置为`true`，那么`TOC`将不会被超链接  

发现下面的标题中出现了`{ignore=true}`，这在本地是没有的（预览自动将这个mark屏蔽了），解决的方法也很简单，关掉VSCode中的预览页面，再对标题进行修改，保存即可。

## 测试标题一
无内容。  

## 测试标题二 
内鬼。  

## 测试标题三
无内鬼。  




