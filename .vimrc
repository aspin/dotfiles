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
NeoBundle 'altercation/vim-colors-solarized'

NeoBundle 'scrooloose/nerdtree'
NeoBundle 'vim-airline/vim-airline'
NeoBundle 'vim-airline/vim-airline-themes'
NeoBundle 'mutewinter/swap-parameters'
" NeoBundle 'Valloric/YouCompleteMe'
NeoBundle 'kien/ctrlp.vim'
NeoBundle 'scrooloose/nerdcommenter'
NeoBundle 'tpope/vim-sleuth'
NeoBundle 'ekalinin/dockerfile.vim'
NeoBundle 'google/vim-jsonnet'
NeoBundle 'jiangmiao/auto-pairs'
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
set background=dark
syntax on

colorscheme solarized

let g:airline_powerline_fonts = 1
let g:airline_theme='luna'
let g:ctrlp_map = '<c-p>'
let g:ctrlp_cmd = 'CtrlP'
let g:ycm_path_to_python_interpreter = '/usr/bin/python'
map <C-\> :NERDTreeToggle<CR>

