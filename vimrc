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
set nowrap
syntax on

" ##########################################
" #                PLUGINS                 #
" ##########################################

call plug#begin('~/.vim/plugged')

" Themes
Plug 'tomasr/molokai'
Plug 'altercation/vim-colors-solarized'
Plug 'jnurmine/zenburn'
Plug 'vim-airline/vim-airline-themes'

" UI mods
Plug 'scrooloose/nerdtree'
Plug 'Xuyuanp/nerdtree-git-plugin'
Plug 'vim-airline/vim-airline'
Plug 'majutsushi/tagbar'
Plug 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --all' }
Plug 'tpope/vim-fugitive'
Plug 'tpope/vim-rhubarb'

" Editor mods
" Plug 'mutewinter/swap-parameters'
Plug 'scrooloose/nerdcommenter'
Plug 'tpope/vim-sleuth'
Plug 'honza/vim-snippets'
" Plug 'jiangmiao/auto-pairs'
" Plug 'SirVer/ultisnips'

" Language/Syntax support
Plug 'Valloric/YouCompleteMe', { 'do': './install.py' }
Plug 'ekalinin/dockerfile.vim'
Plug 'google/vim-jsonnet'
Plug 'udalov/kotlin-vim'
Plug 'elixir-lang/vim-elixir'
Plug 'Vimjas/vim-python-pep8-indent'
Plug 'marijnh/tern_for_vim'
Plug 'pangloss/vim-javascript'
Plug 'jelera/vim-javascript-syntax'
Plug 'flowtype/vim-flow'
Plug 'mxw/vim-jsx'

call plug#end()

" ##########################################
" #             PLUGIN CONFIG              #
" ##########################################

colors zenburn

" js plugin
let g:jsx_ext_required = 0
let g:javascript_plugin_flow = 1

" airline config
let g:airline_powerline_fonts = 1
let g:airline_theme = 'zenburn'

" fzf
map <C-P> :call fzf#run(fzf#wrap({'source': 'ag -g ""'}))<CR>

" ycm
let g:ycm_path_to_python_interpreter = '/usr/bin/python'
let g:ycm_key_list_select_completion = ['<Down>']


" custom ctags for js
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

" jsonnet
let g:jsonnet_fmt_on_save = 0

" NERDCommenter
let g:NERDSpaceDelims = 1
let g:NERDCompactSexyComs = 1
let g:NERDDefaultAlign = 'left'
let g:NERDTrimTrailingWhitespace = 1

" ##########################################
" #               NERD TREE                #
" ##########################################
"

map <C-\> :NERDTreeToggle<CR>
nmap <F8> :TagbarToggle<CR>

autocmd vimenter * if (&filetype !=# 'gitcommit') | NERDTree | endif
autocmd vimenter * wincmd w
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

" let NERDTreeShowHidden=1

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
