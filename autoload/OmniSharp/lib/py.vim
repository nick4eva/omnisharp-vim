if !(has('python') || has('python3'))
  finish
endif

let s:pycmd = has('python3') ? 'python3' : 'python'
let s:pyfile = has('python3') ? 'py3file' : 'pyfile'
let s:module_path_added = 0
let g:omnisharp_python_path = join([expand('<sfile>:p:h:h:h:h'), 'python', 'omnisharp'], '/')

let s:save_cpo = &cpo
set cpo&vim

if exists('*py3eval')
  let s:pyeval = function('py3eval')
elseif exists('*pyeval')
  let s:pyeval = function('pyeval')
else
  exec s:pycmd 'import json, vim'
  function! s:pyeval(e)
    exec s:pycmd 'vim.command("return " + json.dumps(eval(vim.eval("a:e"))))'
  endfunction
endif

function! OmniSharp#lib#py#load(filename)
  if s:module_path_added == 0
    exec s:pycmd "sys.path.append(r'" . g:omnisharp_python_path . "')"
    let s:module_path_added = 1
  endif
  exec s:pyfile fnameescape(g:omnisharp_python_path . a:filename)
endfunction

function! OmniSharp#lib#py#eval(tmp, ...)
  return s:pyeval(printf(tmp, a:000))
endfunction

function! OmniSharp#lib#py#exists()
  return has('python') || has('python3')
endfunction

let &cpo = s:save_cpo
unlet s:save_cpo
