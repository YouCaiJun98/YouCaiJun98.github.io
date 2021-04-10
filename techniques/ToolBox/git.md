# Usage of Git  

2021/4/1  

建新仓库才发现自己之前git的命令都快忘得差不多了，简单开个新page记录一下用法，[参考](https://www.bootcss.com/p/git-guide/)。  


## 创建新仓库  
在当前文件夹下使用`git init`应该就能生成对应的文件了？后续参考[这篇博客](https://blog.csdn.net/zamamiro/article/details/70172900)。但是直接在Web上创建repo然后再clone到本地不是更简单吗233.  

### 实例：从EVA8上将awnas项目迁移到EVA7上  
2021/4/10 update  
* 首先将logs等不必要的大文件搬出，删除原有的`.git`文件夹（以解除和原来项目的关联，没找其他方法）  
* 在项目根目录下用`git init`重建git项目  
* （因为把这个项目依附于我fork的awnas项目的一个分支，所以）建立本地分支bnn：`git branch bnn`并切换到这个本地分支：`git checkout bnn`  
* 将本地项目与远程项目建立联系：`git remote add 仓库名 仓库地址`，并将本地分支上传到远程分支：`git push --set-upstream bnn bnn`  
* 将远程分支clone到EVA7上，注意我只要bnn这个分支，不要默认的master：`git clone -b bnn 仓库地址`  

鸽了。  
