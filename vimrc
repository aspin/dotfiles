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
Plug 'tpope/vim-rhubarb'
Plug 'junegunn/fzf.vim'
Plug 'tpope/vim-fugitive'
Plug 'scrooloose/syntastic'

" Editor mods
Plug 'scrooloose/nerdcommenter'
Plug 'honza/vim-snippets'
Plug 'mattn/webapi-vim'
Plug 'jiangmiao/auto-pairs'
Plug 'SirVer/ultisnips'

" Language/Syntax support
Plug 'Valloric/YouCompleteMe', { 'do': './install.py --rust-completer' }
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
Plug 'rust-lang/rust.vim' 
Plug 'tomlion/vim-solidity'

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
nnoremap <C-P> :call fzf#run(fzf#wrap({'source': 'ag -g ""'}))<CR>

" ycm
let g:ycm_rust_src_path = '/Users/kevin.chen/.rustup/toolchains/nightly-x86_64-apple-darwin/lib/rustlib/src/rust/src'
let g:ycm_add_preview_to_completeopt = 0
let g:ycm_autoclose_preview_window_after_completion = 1
let g:ycm_autoclose_preview_window_after_insertion = 0
let g:ycm_log_level = 'debug'

let g:ycm_key_list_select_completion = ['<TAB>', '<Down>', '<ENTER>']

nnoremap <leader>jd :YcmCompleter GoTo<CR>
nnoremap <leader>jr :YcmCompleter GoToReferences<CR>
nnoremap <leader>jb :YcmCompleter GoToImplementation<CR>


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

" rust
let g:rust_clip_command = 'pbcopy'

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

" ##########################################
" #               SYNTASTIC                #
" ##########################################
"
set statusline+=%#warningmsg#
set statusline+=%{SyntasticStatuslineFlag()}
set statusline+=%*

let g:syntastic_always_populate_loc_list = 1
let g:syntastic_auto_loc_list = 1
let g:syntastic_check_on_open = 0
let g:syntastic_check_on_wq = 0

let g:syntastic_python_checkers = ["mypy"]

noremap <C-w>e :SyntasticToggleMode<CR>

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
" set term=screen-256color
set nocompatible
set backspace=2
set foldmethod=indent
set nofoldenable
set foldlevel=20
set foldnestmax=10
set background=dark
set nowrap
set incsearch
set list
set listchars=tab:>-
syntax on

" ##########################################
" #                 PYTHON                 #
" ##########################################
"
au FileType python set tabstop=4
au FileType python set shiftwidth=4
au FileType python set expandtab
