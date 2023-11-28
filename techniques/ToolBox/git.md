# Usage of Git  

2021/4/1  

建新仓库才发现自己之前git的命令都快忘得差不多了，简单开个新page记录一下用法，[参考](https://www.bootcss.com/p/git-guide/)。  

## 在一个新服务器上关联账号，实现正常拉代码
2023/11/27 update  

**will encounter such circumstance from time to time.**  

---  
* 首先把自己的用户名和邮箱给关联上（这一步似乎无所谓）：  
    ```bash  
    git config --global user.name YouCaiJun98  
    git config --global user.email <my_email_address>  
    ```  
* 接下来生成SSH密钥对：  
    ```bash  
    ssh-keygen -t rsa -b 4096 -C <my_email_address>
    ```  
    * 一路回车；最熟悉的环节；仿佛回到家了一样；  
* 到`~/.ssh/id_rsa.pub`去把公钥给粘出来；  
* 到GitHub页面去创建新的ssh key，路径是点右上角头像 -> settings -> SSH and GPG keys -> New SSH key。  



## git设置代理  
2023/11/13 update  
**网络早晚出问题**
* 设置git的HTTP代理，可以用以下命令：
```bash  
git config --global http.proxy 127.0.0.1:7890
```  
* 设置git的HTTPS代理，可以用以下命令：
```bash  
git config --global https.proxy 127.0.0.1:7890
```  
* 查看已经配置好的配置，在`~/.gitconfig`文件里  


## 创建新仓库  
---
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

## 分支冲突解决  
---
https://www.cnblogs.com/shuimuzhushui/p/9022549.html  

鸽了。  

## 拉取远端已有分支  
2023/11/28 update  
鸽了一个月还是遇到这个事了。

---  
* 利用`git branch -a`查看本地与远程的所有分支：  
```bash  
> git branch -a
    * main  
    remotes/origin/HEAD -> origin/main  
    remotes/origin/branch_name_1
    remotes/origin/main
```  
* 利用以下命令从远端拉取某个分支，并在本地创建一个新分支：  
```bash
> git fetch origin <remote_branch_name>:<local_branch_name>  
    From github.com:<remote_repo_owner>/<remote_repo_name>  
     * [new branch]      <local_branch_name>        -> <remote_branch_name>  
```  
* 再checkout到本地刚拉取的这个分支即可。  


## 开一个新分支并推到远端   
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
    ```command  
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
    ```command  
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
    ```command  
    Branch 'new_branch' set up to track remote branch 'new_branch' from 'origin'.
    Everything up-to-date
    ```  


