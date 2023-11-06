# Usage of Git  

2021/4/1  

建新仓库才发现自己之前git的命令都快忘得差不多了，简单开个新page记录一下用法，[参考](https://www.bootcss.com/p/git-guide/)。  


## 创建新仓库  
在当前文件夹下使用`git init`应该就能生成对应的文件了？后续参考[这篇博客](https://blog.csdn.net/zamamiro/article/details/70172900)。但是直接在Web上创建repo然后再clone到本地不是更简单吗233.  

### 实例：从EVA8上将awnas项目迁移到EVA7上  
2021/4/10 update  
* 在操作之前确定`~/.gitconfig`文件中正确配置了邮箱和用户名  
* 首先将logs等不必要的大文件搬出，删除原有的`.git`文件夹（以解除和原来项目的关联，没找其他方法）  
* 在项目根目录下用`git init`重建git项目  
* （因为把这个项目依附于我fork的awnas项目的一个分支，所以）建立本地分支bnn：`git branch bnn`并切换到这个本地分支：`git checkout bnn`  
* 同步内容（将本地分支内容加到git缓冲区）：`git add .` & `git commit -m ".."`  
* 将本地项目与远程项目建立联系：`git remote add 仓库名 仓库地址`，并将本地分支上传到远程分支：`git push --set-upstream bnn bnn`  
* 将远程分支clone到EVA7上，注意我只要bnn这个分支，不要默认的master：`git clone -b bnn 仓库地址`  

### 分支冲突解决  
https://www.cnblogs.com/shuimuzhushui/p/9022549.html  

鸽了。  


### 开一个新分支并推到远端   
2023/11/6 update
**Do Not ask me why I update such basic concept so late.**  
参考了[这篇博客](https://blog.csdn.net/wangfei0225_/article/details/130734732)。  
* 首先在本地创建一个分支并切换过去：
```bash
git checkout -b <branch_name>
```
* 接着关联远程仓库  
    * 需要注意的是这个关联可能已经做好了，比如把一个repo给clone到本地之后；可以先用下面的命令check是否已经关联了远程仓库：  
    ```bash
    git remote -v
    ```  
    一个已经关联了的情况是：
    ```bash
    origin  git@github.com:YouCaiJun98/Test4GitUsage.git (fetch)
    origin  git@github.com:YouCaiJun98/Test4GitUsage.git (push)
    ```  
    * 否则就手动关联一下：  
    ```bash  
    git remote add origin <remote_repo_address>
    ```  
* 将本地分支推送到远程仓库（相当于在远程仓库创建一个新分支）  
    ```bash  
    git push origin <local_branch_name>:<remote_new_branch_name>  
    ``` 

    * 一个参考运行结果是：  
    ```bash  
    Total 0 (delta 0), reused 0 (delta 0)
    remote:
    remote: Create a pull request for 'new_branch' on GitHub by visiting:
    remote:      https://github.com/YouCaiJun98/Test4GitUsage/pull/new/new_branch
    remote:
    To github.com:YouCaiJun98/Test4GitUsage.git
    * [new branch]      new_branch -> new_branch
    ```  
* 上一步只是创建一个新的branch，但是还没**关联**起来，所以还需要一步：  
    ```bash  
    git push --set-upstream origin <local_branch_name>:<remote_new_branch_name>  
    ```  

    * 一个参考运行结果：  
    ```bash  
    Branch 'new_branch' set up to track remote branch 'new_branch' from 'origin'.
    Everything up-to-date
    ```  

