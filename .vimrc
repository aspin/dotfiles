if 0 | endif

if has('vim_starting')
  if &compatible
    set nocompatible
  endif

  set runtimepath+=~/.vim/bundle/neobundle.vim/
endif

call neobundle#begin(expand('~/.vim/bundle/'))
NeoBundleFetch 'Shougo/neobundle.vim'
NeoBundle 'tomasr/molokai'
NeoBundle 'scrooloose/nerdtree'
NeoBundle 'bling/vim-airline'
NeoBundle 'mutewinter/swap-parameters'
NeoBundle 'Valloric/YouCompleteMe'
NeoBundle 'kien/ctrlp.vim'
NeoBundle 'scrooloose/nerdcommenter'
NeoBundle 'tpope/vim-sleuth'
" NeoBundle 'majutsushi/tagbar' " needs ctags update
call neobundle#end()

filetype plugin indent on
NeoBundleCheck

set smartindent
set tabstop=2
set shiftwidth=2
set expandtab
set number
set encoding=utf-8
set laststatus=2
set noshowmode
set term=screen-256color
set nocompatible
set backspace=2
set foldmethod=indent
set nofoldenable
set foldlevel=20
set foldnestmax=10
syntax on

autocmd Filetype py setlocal tabstop=2

colors molokai

let g:airline_powerline_fonts = 1
let g:airline_theme='luna'
let g:ctrlp_map = '<c-p>'
let g:ctrlp_cmd = 'CtrlP'
let g:ycm_path_to_python_interpreter = '/usr/bin/python'
map <C-\> :NERDTreeToggle<CR>

