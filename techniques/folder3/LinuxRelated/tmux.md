# tmux  

2021/2/21  

学着用tmux，主要的参考资料是[这个](http://www.ruanyifeng.com/blog/2019/10/tmux.html)和[这个](https://zhuanlan.zhihu.com/p/98384704)，快捷键配置参考了[这个](https://www.cnblogs.com/3wtoucan/p/tmux-usage.html)。  

## What's tmux  
### 1.1会话与进程  
命令行的典型使用方式是，打开一个终端窗口（terminal window，以下简称"窗口"），在里面输入命令。用户与计算机的这种临时的交互，称为一次"会话"（session） 。  

会话的一个重要特点是，窗口与其中启动的进程是连在一起的。打开窗口，会话开始；关闭窗口，会话结束，会话内部的进程也会随之终止，不管有没有运行完。  

一个典型的例子就是，SSH 登录远程计算机，打开一个远程窗口执行命令。这时，网络突然断线，再次登录的时候，是找不回上一次执行的命令的。因为上一次 SSH 会话已经终止了，里面的进程也随之消失了。  

为了解决这个问题，会话与窗口可以"解绑"：窗口关闭时，会话并不终止，而是继续运行，等到以后需要的时候，再让会话"绑定"其他窗口。  

### 1.2Tmux 的作用  
Tmux 就是会话与窗口的"解绑"工具，将它们彻底分离。

（1）它允许在单个窗口中，同时访问多个会话。这对于同时运行多个命令行程序很有用。

（2） 它可以让新窗口"接入"已经存在的会话。

（3）它允许每个会话有多个连接窗口，因此可以多人实时共享会话。

（4）它还支持窗口任意的垂直和水平拆分。

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
```  

