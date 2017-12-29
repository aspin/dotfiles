" ##########################################
" #                SETTINGS                #
" ##########################################
"
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

" ##########################################
" #                PLUGINS                 #
" ##########################################

call plug#begin('~/.vim/plugged')

Plug 'tomasr/molokai'
Plug 'altercation/vim-colors-solarized'

Plug 'scrooloose/nerdtree'
Plug 'Xuyuanp/nerdtree-git-plugin'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'mutewinter/swap-parameters'
Plug 'Valloric/YouCompleteMe', { 'do': './install.py' }
Plug 'kien/ctrlp.vim'
Plug 'scrooloose/nerdcommenter'
Plug 'tpope/vim-sleuth'
Plug 'ekalinin/dockerfile.vim'
Plug 'google/vim-jsonnet'
" Plug 'jiangmiao/auto-pairs'
Plug 'SirVer/ultisnips'
Plug 'honza/vim-snippets'
Plug 'majutsushi/tagbar'
Plug 'marijnh/tern_for_vim'
Plug 'udalov/kotlin-vim'
Plug 'pangloss/vim-javascript'
Plug 'mxw/vim-jsx'
Plug 'elixir-lang/vim-elixir'

call plug#end()

" ##########################################
" #             PLUGIN CONFIG              #
" ##########################################
"
colorscheme solarized

let g:jsx_ext_required = 0
let g:javascript_plugin_flow = 1


let g:airline_powerline_fonts = 1
let g:airline_theme='luna'

let g:ctrlp_map = '<c-p>'
let g:ctrlp_cmd = 'CtrlP'
let g:ctrlp_custom_ignore = 'node_modules\|DS_Store\|git'

let g:ycm_path_to_python_interpreter = '/usr/bin/python'
let g:ycm_key_list_select_completion = ['<Down>']

let g:UltiSnipsJumpForwardTrigger="<c-b>"
let g:UltiSnipsJumpBackwardTrigger="<c-z>"
let g:UltiSnipsExpandTrigger="<tab>"

let g:tagbar_type_javascript = {
  \ 'ctagstype': 'js',
  \ 'kinds': [
    \ 'n:constant:0:0',
    \ 'o:object',
    \ 'c:class',
    \ 'f:function',
    \ 'm:method'
  \ ],
  \ 'sro': '.',
  \ 'kind2scope': {
    \ 'o': 'object',
    \ 'c': 'class',
  \ }
\}

" ##########################################
" #               NERD TREE                #
" ##########################################
"

map <C-\> :NERDTreeToggle<CR>
nmap <F8> :TagbarToggle<CR>

autocmd vimenter * NERDTree
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

function! NERDTreeHighlightFile(extension, fg, bg, guifg, guibg)
  exec 'autocmd filetype nerdtree highlight ' . a:extension .' ctermbg='. a:bg .' ctermfg='. a:fg .' guibg='. a:guibg .' guifg='. a:guifg
  exec 'autocmd filetype nerdtree syn match ' . a:extension .' #^\s\+.*'. a:extension .'$#'
endfunction

call NERDTreeHighlightFile('jade', 'green', 'none', 'green', '#151515')
call NERDTreeHighlightFile('ini', 'yellow', 'none', 'yellow', '#151515')
call NERDTreeHighlightFile('md', 'blue', 'none', '#3366FF', '#151515')
call NERDTreeHighlightFile('yml', 'yellow', 'none', 'yellow', '#151515')
call NERDTreeHighlightFile('config', 'yellow', 'none', 'yellow', '#151515')
call NERDTreeHighlightFile('conf', 'yellow', 'none', 'yellow', '#151515')
call NERDTreeHighlightFile('json', 'yellow', 'none', 'yellow', '#151515')
call NERDTreeHighlightFile('html', 'yellow', 'none', 'yellow', '#151515')
call NERDTreeHighlightFile('styl', 'cyan', 'none', 'cyan', '#151515')
call NERDTreeHighlightFile('css', 'cyan', 'none', 'cyan', '#151515')
call NERDTreeHighlightFile('coffee', 'Red', 'none', 'red', '#151515')
call NERDTreeHighlightFile('js', 'Red', 'none', '#ffa500', '#151515')
call NERDTreeHighlightFile('php', 'Magenta', 'none', '#ff00ff', '#151515')
