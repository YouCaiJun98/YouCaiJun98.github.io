# tmux  

2021/2/21  

学着用tmux，主要的参考资料是[这个](http://www.ruanyifeng.com/blog/2019/10/tmux.html)和[这个](https://zhuanlan.zhihu.com/p/98384704)，快捷键配置参考了[这个](https://www.cnblogs.com/3wtoucan/p/tmux-usage.html)。  

## What's tmux  
### 1.1 会话与进程  
命令行的典型使用方式是，打开一个终端窗口（terminal window，以下简称"窗口"），在里面输入命令。用户与计算机的这种临时的交互，称为一次"会话"（session） 。  

会话的一个重要特点是，窗口与其中启动的进程是连在一起的。打开窗口，会话开始；关闭窗口，会话结束，会话内部的进程也会随之终止，不管有没有运行完。  

一个典型的例子就是，SSH 登录远程计算机，打开一个远程窗口执行命令。这时，网络突然断线，再次登录的时候，是找不回上一次执行的命令的。因为上一次 SSH 会话已经终止了，里面的进程也随之消失了。  

为了解决这个问题，会话与窗口可以"解绑"：窗口关闭时，会话并不终止，而是继续运行，等到以后需要的时候，再让会话"绑定"其他窗口。  

### 1.2 Tmux 的作用  
Tmux 就是会话与窗口的"解绑"工具，将它们彻底分离。

（1）它允许在单个窗口中，同时访问多个会话。这对于同时运行多个命令行程序很有用。

（2） 它可以让新窗口"接入"已经存在的会话。

（3）它允许每个会话有多个连接窗口，因此可以多人实时共享会话。

（4）它还支持窗口任意的垂直和水平拆分。

### 1.3 Tmux的安装  
服务器上似乎有现成的Tmux，但是也可以自己安装：  
方法一：  
```bash  
git clone https://github.com/tmux/tmux.git
cd tmux
sh autogen.sh
./configure && make
```  
方法二：  
```bash  
# Ubuntu 或 Debian
$ sudo apt-get install tmux

# CentOS 或 Fedora
$ sudo yum install tmux

# Mac
$ brew install tmux
```  

## Usage  
(我似乎弄混了窗口和session...不过不是大问题)  
* 启动和退出`tmux`:  

```bash  
# 启动tmux
$ tmux

# 退出
$ exit 或 Ctrl+D
```  

* 创建新的`tmux`窗口，注意不能在`tmux`里套`tmux`（似乎有强行套的可能）,下面的方法可以创建带名字的窗口：  

```bash  
# 启动命名tmux
$ tmux new -s <name>
```  

* 在`tmux`窗口里使用下面的命令可以**分离窗口**（从当前窗口弹出）:  

```bash  
# 分离会话
$ tmux detach
```  


* 使用`tmux ls`则可以查看当前所有的`tmux`窗口。  

* 通过`tmux detach`关闭`tmux`伪窗口后可以使用`tmux attach`**重新接回**原tmux会话：  

```bash  
# 重接会话 使用伪窗口编号
$ tmux attach -t 0

# 重接会话 使用伪窗口名称
$ tmux attach -t test01
```  


* **彻底关闭某个会话**可以通过：  

```bash  
# 使用会话编号
$ tmux kill-session -t 0

# 使用会话名称
$ tmux kill-session -t <name>
```  

* 在`tmux`会话间**切换**可以通过：  

```bash  
# 使用会话编号
$ tmux switch -t 0

# 使用会话名称
$ tmux switch -t <session-name>
```  

* 重命名会话：  

```bash  
$ tmux rename-session -t 0 <new-name>
```  

其他基础用法，包括列出所有快捷键、列出所有`Tmux`命令及其参数、列出当前所有`Tmux`会话的信息、重新加载当前的`Tmux`配置：  

```bash  
# 列出所有快捷键，及其对应的 Tmux 命令
$ tmux list-keys

# 列出所有 Tmux 命令及其参数
$ tmux list-commands

# 列出当前所有 Tmux 会话的信息
$ tmux info

# 重新加载当前的 Tmux 配置
$ tmux source-file ~/.tmux.conf
```  

## Advanced Usage  



## Keyboard shortcut modification  
通过`vi ~/.tmux.conf `打开`tmux`的`config`文件，这里直接嫖了tc的设置：  

```  
#prefix
set-option -g prefix C-q
unbind-key C-b
unbind-key C-x
bind-key C-q send-prefix

#水平垂直分pane
# unbind '"'
# bind 1 splitw -h
# unbind %
# bind 2 splitw -v

# resize pane
bind-key -n C-Up resize-pane -U
bind-key -n C-Down resize-pane -D
bind-key -n C-Left resize-pane -L
bind-key -n C-Right resize-pane -R

# prevent tmux from automatically rename window
setw -g allow-rename off
set -g default-terminal "screen-256color"
setw -g mouse on


set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
# reboot recovery
set -g @plugin 'tmux-plugins/tmux-resurrect'

run '~/.tmux/plugins/tpm/tpm'
```  

