# Ubuntu Setup Instruction  

2021/4/12  

当我自己有新电脑可以装Ubuntu的时候这篇博客就有用了吧，大概。参考了[天辰的实现](http://a-suozhang.xyz/2020/01/08/UbuntuSetup/)。  

## Vim Config  
* 首先安装Vim。  

```bash  
sudo apt-get install vim git
mkdir -p ~/.vim/bundle 
git clone https://github.com/gmarik/Vundle.vim.git ~/.vim/bundle/Vundle.vim  # vim 插件管理器
```  

* 安装依赖项，以及源码编译安装Global。  

```bash  
sudo apt-get install silversearcher-ag ctags
sudo apt-get install gcc g++ cmake
sudo apt-get install libncurses5-dev # 插件需要的软件包
wget http://mirrors.ustc.edu.cn/gnu/global/global-6.4.tar.gz
tar xf global-6.4.tar.gz
cd global-6.4
./configure && make && sudo make install
```  

* 建立~/.vimrc，添加一些设置，.vimrc文件被我备份到了[github]()。  

```bash  
set nocompatible   " 必须, 关闭 vi 兼容模式
filetype off       " 必须
 
" 设置 Runtime Path，供 Vundle 初始化
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
 
" 让 Vundle 管理 Vundle，必须
Plugin 'gmarik/Vundle.vim'
Plugin 'rking/ag.vim'
Plugin 'kien/ctrlp.vim'
Plugin 'Yggdroot/indentLine'
Plugin 'scrooloose/syntastic'
Plugin 'scrooloose/nerdtree'
Plugin 'majutsushi/tagbar'
Plugin 'bling/vim-airline'
Plugin 'jrosiek/vim-mark'
Plugin 'bigeagle/molokai'
Plugin 'aceofall/gtags.vim'
Plugin 'hdima/python-syntax'
Plugin 'hynek/vim-python-pep8-indent'

Plugin 'scrooloose/nerdcommenter'
" Plugin 'suan/vim-instant-markdown'
 
call vundle#end()
 
colorscheme molokai " 使用 molokai 主题，请注意需要 256 色终端
set so=10     " 光标到倒数第10行开始滚屏   
syntax on     " 语法高亮
set number    " 显示行号
set autochdir " 打开文件时，自动 cd 到文件所在目录
set hlsearch 

" 文件类型支持
filetype on
filetype plugin on
filetype indent on
 
set list lcs=tab:\¦\   " 使用 ¦ 来显示 tab 缩进
 
" 缩进相关
set shiftwidth=4
set tabstop=4
set softtabstop=4
set smartindent
 
if has("autocmd")  " 打开时光标放在上次退出时的位置
    autocmd BufReadPost *
        \ if line("'\"") > 0 && line ("'\"") <= line("$") |
        \   exe "normal g'\"" |
        \ endif
endif
 
set completeopt=longest,menu " 自动补全菜单
 
" 鼠标支持
if has('mouse')
    set mouse=a
    set selectmode=mouse,key
    set nomousehide
endif
 
set modeline      " 底部的模式行
set cursorline    " 高亮光标所在行
" set cursorcolumn  " 高亮光标所在列
 
set showmatch     " 高亮括号匹配
set matchtime=0
set nobackup      " 关闭自动备份
 
set backspace=indent,eol,start
 
 
" 文件编码
set fenc=utf-8
set fencs=utf-8,gbk,gb18030,gb2312,cp936,usc-bom,euc-jp
set enc=utf-8
 
" 语法折叠
set foldmethod=syntax
set foldcolumn=0  " 设置折叠区域的宽度
set foldlevel=100
" 用空格键来开关折叠
nnoremap <space> @=((foldclosed(line('.')) < 0) ? 'zc' : 'zo')<CR>
 
 
set smartcase
set ignorecase  " 搜索时，智能大小写
set nohlsearch  " 关闭搜索高亮
set incsearch   " 实时显示搜索结果
 
 
" 让 j, k 可以在 自动wrap的行中上下移动
vmap j gj
vmap k gk
nmap j gj
nmap k gk
 
" Shift-T 开新 Tab
nmap T :tabnew<cr>
 
" 以下文件类型，敲 {<回车> 后，自动加入反括号 }
au FileType c,cpp,h,java,css,js,nginx,scala,go inoremap  <buffer>  {<CR> {<CR>}<Esc>O
 
" ------ python  ------------
let python_highlight_all = 1
au FileType python setlocal ts=4 sts=4 sw=4 smarttab expandtab
" ------ python end ---------
 
" ------- Tagbar ------------------
let g:tagbar_width = 30
nmap tb :TagbarToggle<cr>	" 使用 tb 开/关 Tagbar
 
" ------- Tagbar End --------------
 
" ------- Gtags -------------------
set cscopetag				 " 使用 cscope 作为 tags 命令
set cscopeprg='gtags-cscope' " 使用 gtags-cscope 代替 cscope
let GtagsCscope_Auto_Load = 1
let GtagsCscope_Quiet = 1
 
" ------- Gtags End ---------------
 
" ------- NerdTree -------------------
 
nmap nt :NERDTreeToggle<cr>
let NERDTreeShowBookmarks=0
let NERDTreeMouseMode=2
let g:nerdtree_tabs_focus_on_files=1
let g:nerdtree_tabs_open_on_gui_startup=0
 
let NERDTreeWinSize=25
let NERDTreeIgnore = ['\.pyc$']
let NERDTreeMinimalUI=0
let NERDTreeDirArrows=1
 
"let g:newrw_ftp_cmd = 'lftp'
" let g:netrw_altv          = 1
" let g:netrw_fastbrowse    = 2
" let g:netrw_keepdir       = 1
" let g:netrw_liststyle     = 3
" let g:netrw_retmap        = 1
" let g:netrw_silent        = 1
" let g:netrw_special_syntax= 1
" let g:netrw_browse_split = 3
" let g:netrw_banner = 0
" ------- NerdTree End ---------------
 
" ---- Airline 
" set laststatus=2
" let g:airline#extensions#tabline#enabled = 0
" let g:airline_powerline_fonts = 0
" let g:airline_theme = "powerlineish"
" ---- Airline
"
"
"  ---- NerdCommenter
" Create default mappings
let g:NERDCreateDefaultMappings = 1
" Add spaces after comment delimiters by default
let g:NERDSpaceDelims = 1 
" " Use compact syntax for prettified multi-line comments
let g:NERDCompactSexyComs = 1
" " Align line-wise comment delimiters flush left instead of following code
" indentation
let g:NERDDefaultAlign = 'left'
" " Set a language to use its alternate delimiters by default
let g:NERDAltDelims_java = 1
" " Add your own custom formats or override the defaults
let g:NERDCustomDelimiters = { 'c': { 'left': '/**','right': '*/' } }
" " Allow commenting and inverting empty lines (useful when commenting a
" region)
let g:NERDCommentEmptyLines = 1
" " Enable trimming of trailing whitespace when uncommenting
let g:NERDTrimTrailingWhitespace = 1
" " Enable NERDCommenterToggle to check all selected lines is commented or not 
let g:NERDToggleCheckAllLines = 1



" ------------------self-defined cfgs----------------------

inoremap <C-o> <Esc>o
inoremap <C-j> <Down>
inoremap <C-h> <Left>
inoremap <C-l> <Right>
inoremap <C-k> <Up>
inoremap <C-a> <Esc>0wi
inoremap <C-e> <Esc>A

" move cursor into the middle of ()
imap () ()<Left>
imap [] []<Left>
imap {} {}<Left>
imap "" ""<Left>

noremap <C-Left> :tabprevious<CR>
nnoremap <C-Right> :tabnext<CR>

cmap w!! w !sudo tee > /dev/null %
cmap W w
cmap Q q
cmap WQ wq

set hls

inoremap ipdb<Leader> import ipdb; ipdb.set_trace()

" au BufWritePre * :set binary | set noeol
" au BufWritePost * :set nobinary | set eol
"
set pastetoggle=<F12>

set list
set listchars=tab:>-

```  

* 打开这个文件（此时还会有报错），执行`: PluginInstall`，界面会分成左右两页进行安装。  
* 安装完毕，最后还剩下了这个错误：  

```log  
(awnas) shixiangsheng@ztc-eva7:~/utils/global-6.4$ vi ~/.vim/bundle/molokai/colors/molokai.vim
Error detected while processing /home/shixiangsheng/.vim/bundle/molokai/colors/molokai.vim:
line  132:
E254: Cannot allocate color none
E254: Cannot allocate color none
Press ENTER or type command to continue
```  

解决方法是`~/.vim/bundle/molokai/colors/molokai.vim:line 132:none -> NONE`  