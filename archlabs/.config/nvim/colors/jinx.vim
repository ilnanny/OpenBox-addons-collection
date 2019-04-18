"    ------------------- jinx ----------------------     "
"       Written by Nathaniel Maia, December 2017         "
"    -----------------------------------------------     "
" vim:fdm=marker

" ---------- Setup and Checks ----------- " {{{1

if exists('syntax_on')
    highlight clear
    syntax reset
endif

" Colors {{{1

" start with an empty color dictionary
let s:jinx = {}

" NOTE: For those looking to edit the theme
"
" Color definition is done for both true color
" and 256 color. The format is in ['HEX', 256color, 16color]
"
" let s:jinx.black = ['#000000', 0, 0]

let g:terminal_ansi_colors = [
            \ '#4D545E', '#D9534F', '#80B080', '#FFEB56', '#6699CC', '#CC99CC', '#5DD5FF', '#E1E1E1',
            \ '#4D545E', '#D9534F', '#80B080', '#FFEB56', '#6699CC', '#CC99CC', '#5DD5FF', '#E1E1E1'
            \ ]
let s:i = 0
for s:color in g:terminal_ansi_colors
    let g:terminal_color_{s:i} = s:color
    let s:i += 1
endfor

let s:jinx.red    = ['#EE5555', 210,  1]
let s:jinx.green  = ['#88BB88', 108,  2]
let s:jinx.yellow = ['#FFCC66', 220,  3]
let s:jinx.blue   = ['#4488CC',  32,  4]
let s:jinx.purple = ['#AA88CC', 140,  5]
let s:jinx.cyan   = ['#44CCEE',  81,  6]
let s:jinx.orange = ['#FF8844', 172,  9]

if exists('g:jinx_theme') && g:jinx_theme =~? 'day'
    set background=light
    let s:jinx.fgr    = ['#494949', 238,  0]
    let s:jinx.bgr    = ['#E1E1E1', 254,  7]
    let s:jinx.line   = ['#D0D0D0', 252, 15]
    let s:jinx.select = ['#D0D0D0', 252,  1]
    let s:jinx.folded = ['#B2B2B2', 249, 15]
    let s:jinx.commnt = ['#808080', 244, 15]
    let s:jinx.yellow = ['#EE9911', 178,  3]
    let s:jinx.cyan   = ['#3388AA',  37,  6]
elseif exists('g:jinx_theme') && g:jinx_theme =~? 'midnight'
    set background=dark
    let s:jinx.fgr    = ['#CCCCCC', 251, 15]
    let s:jinx.bgr    = ['#111111', 234,  0]
    let s:jinx.line   = ['#2A2A2F', 237,  8]
    let s:jinx.select = ['#2A2A2F', 237,  1]
    let s:jinx.folded = ['#2A2A2F', 237,  8]
    let s:jinx.commnt = ['#777777', 243,  7]
else " night
    set background=dark
    let s:jinx.fgr    = ['#E1E1E1', 254, 15]
    let s:jinx.bgr    = ['#4D545E', 237,  0]
    let s:jinx.line   = ['#5F6772', 243,  8]
    let s:jinx.select = ['#5F6772', 243,  8]
    let s:jinx.folded = ['#5F6772', 243,  8]
    let s:jinx.commnt = ['#B9B9B9', 250,  7]
endif

function! <SID>HighLight(GRP, FG, BG, ATT) abort  " {{{1
    if a:FG !=# ''
        let l:fg_col  = get(s:jinx, a:FG)
        let l:fg_true = l:fg_col[0]
        if $TERM =~? 'linux' || &t_Co < 256
            let l:fg_term = l:fg_col[2]
        else
            let l:fg_term = l:fg_col[1]
        endif
        exec 'highlight! '.a:GRP.' guifg='.l:fg_true.' ctermfg='.l:fg_term
    endif
    if a:BG !=# ''
        let l:bg_col  = get(s:jinx, a:BG)
        let l:bg_true = l:bg_col[0]
        if $TERM =~? 'linux' ||  &t_Co < 256
            let l:bg_term = l:bg_col[2]
        else
            let l:bg_term = l:bg_col[1]
        endif
        exec 'highlight! '.a:GRP.' guibg='.l:bg_true.' ctermbg='.l:bg_term
    endif
    if a:ATT !=# '' && &t_Co >= 256
        exec 'highlight! '.a:GRP.' gui='.a:ATT.' cterm='.a:ATT
    endif
endfunction


" ---------- Highlight Groups ------------ " {{{1

" Editor {{{2

call <SID>HighLight('Title',        'commnt',   'bgr',  'bold')
call <SID>HighLight('Visual',       '',         'select',   '')
call <SID>HighLight('SignColumn',   '',         'line',     '')
call <SID>HighLight('CursorLine',   '',         'line',     '')
call <SID>HighLight('CursorColumn', '',         'line',     '')
call <SID>HighLight('CursorLineNr', 'cyan',     'line',     '')
call <SID>HighLight('LineNr',       'commnt',   'line',     '')
call <SID>HighLight('ColorColumn',  'fgr',      'red',      '')
call <SID>HighLight('Error',        'red',      'bgr',      '')
call <SID>HighLight('ErrorMsg',     'red',      'bgr',      '')
call <SID>HighLight('WarningMsg',   'red',      'bgr',      '')
call <SID>HighLight('MatchParen',   'yellow',   'bgr',      '')
call <SID>HighLight('ModeMsg',      'cyan',     'bgr',      '')
call <SID>HighLight('MoreMsg',      'cyan',     'bgr',      '')
call <SID>HighLight('Directory',    'blue',     'bgr',      '')
call <SID>HighLight('Question',     'green',    'bgr',      '')
call <SID>HighLight('NonText',      'commnt',   'bgr',      '')
call <SID>HighLight('SpecialKey',   'commnt',   'bgr',      '')
call <SID>HighLight('Folded',       'commnt',   'folded',   '')
call <SID>HighLight('Search',       'bgr',      'blue',     '')
call <SID>HighLight('HLNext',       'bgr',      'red',      '')
call <SID>HighLight('Normal',       'fgr',      'bgr',      '')
call <SID>HighLight('VertSplit',    'line',     'commnt',   '')

" Tabline {{{2

call <SID>HighLight('TabLine',      'fgr',     'line',   '')
call <SID>HighLight('TabLineFill',  'line',    'line',   '')
call <SID>HighLight('TabLineSel',   'line',    'green',  '')
call <SID>HighLight('WildMenu',     'bgr',     'fgr',    '')
call <SID>HighLight('Pmenu',        'bgr',     'commnt', '')
call <SID>HighLight('PmenuSel',     'fgr',     'bgr',    '')
call <SID>HighLight('PmenuSbar',    'commnt',  'line',   '')
call <SID>HighLight('PmenuThumb',   'commnt',  'line',   '')
call <SID>HighLight('StatusLine',   'line',    'fgr',    '')
call <SID>HighLight('StatusLineNC', 'fgr',     'line',   '')

" Spelling {{{2
call <SID>HighLight('SpellBad',   '', '', 'underline')
call <SID>HighLight('SpellLocal', '', '', 'underline')
call <SID>HighLight('SpellRare',  '', '', 'underline')


" ALE linter {{{2

call <SID>HighLight('ALEErrorSign',    'red',    'line',       '')
call <SID>HighLight('ALEWarningSign',  'orange', 'line',       '')
call <SID>HighLight('ALEError',        'red',    '',  'underline')
call <SID>HighLight('ALEWarning',      'red',    '',  'underline')
call <SID>HighLight('ALEStyleError',   'orange', '',  'underline')
call <SID>HighLight('ALEStyleWarning', 'orange', '',  'underline')

" Generic {{{2

call <SID>HighLight('Comment',      'commnt', '',     '')
call <SID>HighLight('Todo',         'red',    '',     '')
call <SID>HighLight('Exception',    'red',    '',     '')
call <SID>HighLight('Float',        'cyan',   '',     '')
call <SID>HighLight('Number',       'cyan',   '',     '')
call <SID>HighLight('Include',      'cyan',   '',     '')
call <SID>HighLight('Character',    'blue',   '',     '')
call <SID>HighLight('Operator',     'blue',   '',     '')
call <SID>HighLight('String',       'blue',   '',     '')
call <SID>HighLight('Label',        'green',  '',     '')
call <SID>HighLight('Repeat',       'purple', '',     '')
call <SID>HighLight('Statement',    'green',  '',     '')
call <SID>HighLight('Conditional',  'green',  '',     '')
call <SID>HighLight('Boolean',      'green',  '',     '')
call <SID>HighLight('Keyword',      'green',  '',     '')
call <SID>HighLight('Macro',        'purple', '',     '')
call <SID>HighLight('Define',       'purple', '',     '')
call <SID>HighLight('Special',      'purple', '',     '')
call <SID>HighLight('Tag',          'purple', '',     '')
call <SID>HighLight('Type',         'purple', '',     '')
call <SID>HighLight('TypeDef',      'purple', '',     '')
call <SID>HighLight('Structure',    'purple', '',     '')
call <SID>HighLight('StorageClass', 'purple', '',     '')
call <SID>HighLight('PreProc',      'yellow', '',     '')
call <SID>HighLight('Constant',     'yellow', '',     '')
call <SID>HighLight('Identifier',   'yellow', '',     '')
call <SID>HighLight('PreCondit',    'yellow', '',     '')
call <SID>HighLight('Conceal',      'orange', '',     '')
call <SID>HighLight('Function',     'orange', '',     '')

" Vim {{{2

call <SID>HighLight('vimCommand',     'green',  '', '')
call <SID>HighLight('vimVar',         'yellow', '', '')
call <SID>HighLight('vimGroup',       'yellow', '', '')
call <SID>HighLight('vimGroupName',   'yellow', '', '')
call <SID>HighLight('VimFunction',    'orange', '', '')
call <SID>HighLight('VimFunctionKey', 'orange', '', '')
call <SID>HighLight('vimMapModKey',   'purple', '', '')
call <SID>HighLight('vimBracket',     'purple', '', '')
call <SID>HighLight('vimOption',      'purple', '', '')
call <SID>HighLight('vimMapMod',      'purple', '', '')
call <SID>HighLight('vimNotation',    'purple', '', '')

" Shell {{{2

call <SID>HighLight('shSet',          'green',  '', '')
call <SID>HighLight('shLoop',         'green',  '', '')
call <SID>HighLight('shFor',          'yellow', '', '')
call <SID>HighLight('shTestOpr',      'blue',   '', '')
call <SID>HighLight('shConstant',     'yellow', '', '')
call <SID>HighLight('shFunctionKey',  'orange', '', '')
call <SID>HighLight('shStatement',    'green',  '', '')
call <SID>HighLight('shKeyword',      'purple', '', '')
call <SID>HighLight('zshStatement',   'green',  '', '')
call <SID>HighLight('zshOption',      'purple', '', '')
call <SID>HighLight('zshParentheses', 'purple', '', '')
call <SID>HighLight('zshBrackets',    'purple', '', '')
call <SID>HighLight('zshRepeat',      'green',  '', '')
call <SID>HighLight('zshRedir',       'fgr',    '', '')
call <SID>HighLight('zshFunction',    'orange', '', '')
call <SID>HighLight('zshVariableDef', 'yellow', '', '')
call <SID>HighLight('zshVariable',    'yellow', '', '')
call <SID>HighLight('zshOperator',    'blue',   '', '')
call <SID>HighLight('zshPreProc',     'commnt', '', '')

" C {{{2

call <SID>HighLight('cConditional',  'green',  '', '')
call <SID>HighLight('cRepeat',       'purple', '', '')
call <SID>HighLight('cStorageClass', 'purple', '', '')
call <SID>HighLight('cType',         'yellow', '', '')

" PHP {{{2

call <SID>HighLight('phpMemberSelector', 'blue',   '', '')
call <SID>HighLight('phpVarSelector',    'red',    '', '')
call <SID>HighLight('phpConditional',    'green',  '', '')
call <SID>HighLight('phpStatement',      'green',  '', '')
call <SID>HighLight('phpKeyword',        'purple', '', '')
call <SID>HighLight('phpRepeat',         'purple', '', '')

" Ruby {{{2

call <SID>HighLight('rubyInclude',                'blue',   '', '')
call <SID>HighLight('rubyAttribute',              'blue',   '', '')
call <SID>HighLight('rubySymbol',                 'green',  '', '')
call <SID>HighLight('rubyStringDelimiter',        'green',  '', '')
call <SID>HighLight('rubyRepeat',                 'purple', '', '')
call <SID>HighLight('rubyControl',                'purple', '', '')
call <SID>HighLight('rubyConditional',            'purple', '', '')
call <SID>HighLight('rubyException',              'purple', '', '')
call <SID>HighLight('rubyCurlyBlock',             'orange', '', '')
call <SID>HighLight('rubyLocalVariableOrMethod',  'orange', '', '')
call <SID>HighLight('rubyInterpolationDelimiter', 'orange', '', '')
call <SID>HighLight('rubyAccess',                 'yellow', '', '')
call <SID>HighLight('rubyConstant',               'yellow', '', '')

" Python {{{2

call <SID>HighLight('pythonRun',             'red',    '', '')
call <SID>HighLight('pythonOperator',        'blue',   '', '')
call <SID>HighLight('pythonClass',           'blue',   '', '')
call <SID>HighLight('pythonClassParameters', 'purple', '', '')
call <SID>HighLight('pythonParam',           'purple', '', '')
call <SID>HighLight('pythonDecorator',       'blue',   '', '')
call <SID>HighLight('pythonExClass',         'blue',   '', '')
call <SID>HighLight('pythonException',       'blue',   '', '')
call <SID>HighLight('pythonExceptions',      'blue',   '', '')
call <SID>HighLight('pythonBrackets',        'blue',   '', '')
call <SID>HighLight('pythonEscape',          'blue',   '', '')
call <SID>HighLight('pythonImport',          'green',  '', '')
call <SID>HighLight('pythonRepeat',          'green',  '', '')
call <SID>HighLight('pythonCoding',          'green',  '', '')
call <SID>HighLight('pythonInclude',         'green',  '', '')
call <SID>HighLight('pythonPreCondit',       'green',  '', '')
call <SID>HighLight('pythonStatement',       'green',  '', '')
call <SID>HighLight('pythonConditional',     'green',  '', '')
call <SID>HighLight('pythonDef',             'yellow', '', '')
call <SID>HighLight('pythonSelf',            'blue',   '', '')
call <SID>HighLight('pythonBuiltinType',     'purple', '', '')
call <SID>HighLight('pythonBuiltin',         'purple', '', '')
call <SID>HighLight('pythonBuiltinObj',      'purple', '', '')
call <SID>HighLight('pythonBuiltinFunc',     'orange', '', '')
call <SID>HighLight('pythonDot',             'orange', '', '')
call <SID>HighLight('pythonLambda',          'orange', '', '')
call <SID>HighLight('pythonLambdaExpr',      'orange', '', '')
call <SID>HighLight('pythonFunction',        'orange', '', '')
call <SID>HighLight('pythonDottedName',      'orange', '', '')
call <SID>HighLight('pythonBuiltinObjs',     'orange', '', '')

" LaTeX {{{2

call <SID>HighLight('texZone',        'red',    '', 'none')
call <SID>HighLight('texStatement',   'blue',   '', 'none')
call <SID>HighLight('texRefLabel',    'blue',   '', 'none')
call <SID>HighLight('texRefZone',     'green',  '', 'none')
call <SID>HighLight('texMath',        'orange', '', 'none')
call <SID>HighLight('texMathZoneX',   'orange', '', 'none')
call <SID>HighLight('texMathZoneA',   'orange', '', 'none')
call <SID>HighLight('texMathZoneB',   'orange', '', 'none')
call <SID>HighLight('texMathZoneC',   'orange', '', 'none')
call <SID>HighLight('texMathZoneD',   'orange', '', 'none')
call <SID>HighLight('texMathZoneE',   'orange', '', 'none')
call <SID>HighLight('texMathMatcher', 'orange', '', 'none')
call <SID>HighLight('texDelimiter',   'purple', '', 'none')
call <SID>HighLight('texComment',     'commnt', '', 'none')

" JavaScript {{{2

call <SID>HighLight('javaScriptNumber',      'cyan',   '', '')
call <SID>HighLight('javascriptNull',        'red',    '', '')
call <SID>HighLight('javascriptStatement',   'green',  '', '')
call <SID>HighLight('javaScriptConditional', 'green',  '', '')
call <SID>HighLight('javaScriptRepeat',      'purple', '', '')
call <SID>HighLight('javaScriptBraces',      'purple', '', '')
call <SID>HighLight('javascriptGlobal',      'yellow', '', '')
call <SID>HighLight('javaScriptFunction',    'orange', '', '')
call <SID>HighLight('javaScriptMember',      'orange', '', '')

" HTML {{{2

call <SID>HighLight('htmlTag',       'red',    '', '')
call <SID>HighLight('htmlTagName',   'red',    '', '')
call <SID>HighLight('htmlLink',      'blue',   '', '')
call <SID>HighLight('htmlArg',       'green',  '', '')
call <SID>HighLight('htmlScriptTag', 'purple', '', '')
call <SID>HighLight('htmlTitle',     'blue',   '', '')
call <SID>HighLight('htmlH1',        'blue',   '', '')
call <SID>HighLight('htmlH2',        'cyan',   '', '')
call <SID>HighLight('htmlH3',        'cyan',   '', '')
call <SID>HighLight('htmlH4',        'green',  '', '')
call <SID>HighLight('htmlH5',        'green',  '', '')

" YAML {{{2

call <SID>HighLight('yamlKey',            'red',   '', '')
call <SID>HighLight('yamlAnchor',         'red',   '', '')
call <SID>HighLight('yamlAlias',          'blue',  '', '')
call <SID>HighLight('yamlDocumentHeader', 'green', '', '')

" Markdown {{{2

call <SID>HighLight('markdownHeadingRule',       'red',    '', '')
call <SID>HighLight('markdownHeadingDelimiter',  'red',    '', '')
call <SID>HighLight('markdownListMarker',        'blue',   '', '')
call <SID>HighLight('markdownOrderedListMarker', 'blue',   '', '')
call <SID>HighLight('markdownCode',              'purple', '', '')
call <SID>HighLight('markdownCodeBlock',         'purple', '', '')
call <SID>HighLight('markdownCodeDelimiter',     'purple', '', '')
call <SID>HighLight('markdownH1',                'blue',   '', '')
call <SID>HighLight('markdownH2',                'blue',   '', '')
call <SID>HighLight('markdownH3',                'cyan',   '', '')
call <SID>HighLight('markdownH4',                'cyan',   '', '')
call <SID>HighLight('markdownH5',                'green',  '', '')

" ShowMarks {{{2

call <SID>HighLight('ShowMarksHLm', 'cyan',   '', '')
call <SID>HighLight('ShowMarksHLl', 'orange', '', '')
call <SID>HighLight('ShowMarksHLo', 'purple', '', '')
call <SID>HighLight('ShowMarksHLu', 'yellow', '', '')

" Lua {{{2

call <SID>HighLight('luaRepeat',     'purple', '', '')
call <SID>HighLight('luaStatement',  'purple', '', '')
call <SID>HighLight('luaCond',       'green',  '', '')
call <SID>HighLight('luaCondEnd',    'green',  '', '')
call <SID>HighLight('luaCondStart',  'green',  '', '')
call <SID>HighLight('luaCondElseif', 'green',  '', '')

" Go {{{2

call <SID>HighLight('goDeclType',    'blue',   '', '')
call <SID>HighLight('goLabel',       'purple', '', '')
call <SID>HighLight('goRepeat',      'purple', '', '')
call <SID>HighLight('goBuiltins',    'purple', '', '')
call <SID>HighLight('goStatement',   'purple', '', '')
call <SID>HighLight('goDirective',   'purple', '', '')
call <SID>HighLight('goDeclaration', 'purple', '', '')
call <SID>HighLight('goConditional', 'purple', '', '')
call <SID>HighLight('goTodo',        'yellow', '', '')
call <SID>HighLight('goConstants',   'orange', '', '')

" Clojure {{{2

call <SID>HighLight('clojureException', 'red',    '', '')
call <SID>HighLight('clojureParen',     'cyan',   '', '')
call <SID>HighLight('clojureCond',      'blue',   '', '')
call <SID>HighLight('clojureFunc',      'blue',   '', '')
call <SID>HighLight('clojureMeta',      'blue',   '', '')
call <SID>HighLight('clojureMacro',     'blue',   '', '')
call <SID>HighLight('clojureDeref',     'blue',   '', '')
call <SID>HighLight('clojureQuote',     'blue',   '', '')
call <SID>HighLight('clojureRepeat',    'blue',   '', '')
call <SID>HighLight('clojureRepeat',    'blue',   '', '')
call <SID>HighLight('clojureUnquote',   'blue',   '', '')
call <SID>HighLight('clojureAnonArg',   'blue',   '', '')
call <SID>HighLight('clojureDispatch',  'blue',   '', '')
call <SID>HighLight('clojureString',    'green',  '', '')
call <SID>HighLight('clojureRegexp',    'green',  '', '')
call <SID>HighLight('clojureKeyword',   'green',  '', '')
call <SID>HighLight('clojureDefine',    'purple', '', '')
call <SID>HighLight('clojureSpecial',   'purple', '', '')
call <SID>HighLight('clojureVariable',  'yellow', '', '')
call <SID>HighLight('clojureBoolean',   'orange', '', '')
call <SID>HighLight('clojureNumber',    'orange', '', '')
call <SID>HighLight('clojureConstant',  'orange', '', '')
call <SID>HighLight('clojureCharacter', 'orange', '', '')

" Scala {{{2

call <SID>HighLight('scalaPackage',         'red',    '', '')
call <SID>HighLight('scalaVar',             'cyan',   '', '')
call <SID>HighLight('scalaDefName',         'blue',   '', '')
call <SID>HighLight('scalaBackTick',        'blue',   '', '')
call <SID>HighLight('scalaMethodCall',      'blue',   '', '')
call <SID>HighLight('scalaXml',             'green',  '', '')
call <SID>HighLight('scalaString',          'green',  '', '')
call <SID>HighLight('scalaBackTick',        'green',  '', '')
call <SID>HighLight('scalaEmptyString',     'green',  '', '')
call <SID>HighLight('scalaStringEscape',    'green',  '', '')
call <SID>HighLight('scalaMultiLineString', 'green',  '', '')
call <SID>HighLight('scalaTypeSpecializer', 'yellow', '', '')
call <SID>HighLight('scalaDefSpecializer',  'yellow', '', '')
call <SID>HighLight('scalaType',            'yellow', '', '')
call <SID>HighLight('scalaCaseType',        'yellow', '', '')
call <SID>HighLight('scalaAnnotation',      'orange', '', '')
call <SID>HighLight('scalaSymbol',          'orange', '', '')
call <SID>HighLight('scalaUnicode',         'orange', '', '')
call <SID>HighLight('scalaBoolean',         'orange', '', '')
call <SID>HighLight('scalaNumber',          'orange', '', '')
call <SID>HighLight('scalaChar',            'orange', '', '')
call <SID>HighLight('scalaImport',          'purple', '', '')
call <SID>HighLight('scalaDef',             'purple', '', '')
call <SID>HighLight('scalaVal',             'purple', '', '')
call <SID>HighLight('scalaClass',           'purple', '', '')
call <SID>HighLight('scalaTrait',           'purple', '', '')
call <SID>HighLight('scalaObject',          'purple', '', '')
call <SID>HighLight('scalaKeywordModifier', 'purple', '', '')
call <SID>HighLight('scalaDocComment',      'commnt', '', '')
call <SID>HighLight('scalaComment',         'commnt', '', '')
call <SID>HighLight('scalaDocTags',         'commnt', '', '')
call <SID>HighLight('scalaLineComment',     'commnt', '', '')

" Diff {{{2

call <SID>HighLight('DiffDelete', 'red',   '',     '')
call <SID>HighLight('DiffChange', 'blue',  '',     '')
call <SID>HighLight('DiffAdd',    'green', '',     '')
call <SID>HighLight('DiffText',   'line',  'blue', '')

" Cleanup {{{2

" Remove the highlight function as it's no longer needed.
" Will cause problems reloading the theme if not deleted.
delfunction <SID>HighLight
let g:colors_name = 'jinx'
