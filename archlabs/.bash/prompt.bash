#!/bin/bash
# shellcheck disable=2034

# Simple prompt for bash
# Written by Nathaniel Maia, 2018

# shell specific prompts

# using '' not "" means it will be evaluated when used as the prompt NOT when defined (below)
# this allows putting at the top of the file before the functions/variables have been defined

# add some handy history commands, see `history --help`
PROMPT_COMMAND='export exitcode=$?; history -n; history -w; history -c; history -r;'
PROMPT_COMMAND+='__git_ps1 "$(__title)${MAGENTA}${PROMPT_LNBR1}$(__exitcode) '
PROMPT_COMMAND+='${PROMPT_USERFMT}${MAGENTA}\w$(__ranger)${RESET}" '
PROMPT_COMMAND+='" ${PROMPT_MULTILINE}${MAGENTA}${PROMPT_LNBR2}${PROMPT_ARROW}'

if [[ $(whoami) == 'root' ]]; then
    PROMPT_COMMAND+=' ${PROMPT_USERCOL}#${RESET} "'
else
    PROMPT_COMMAND+=' ${PROMPT_USERCOL}\$${RESET} "'
fi

PS2='==> '
PS3='choose: '
PS4='|${BASH_SOURCE} ${LINENO}${FUNCNAME[0]:+ ${FUNCNAME[0]}()}|  '

## ----------------------------------------------------------- ##

# bash uses \[..\]to wrap non printing chars
# this avoids issues with completion/history
RESET='\[\e[0m\]'     BOLD='\[\e[1m\]'
RED='\[\e[31m\]'      GREEN='\[\e[32m\]'
YELLOW='\[\e[1;33m\]' BLUE='\[\e[34m\]'
MAGENTA='\[\e[35m\]'  CYAN='\[\e[36m\]'

shopt -q promptvars || shopt promptvars >/dev/null 2>&1

# basic settings

: "${PROMPT_MULTILINE="\\n"}"

if [[ $(whoami) == 'root' ]]; then
    : "${PROMPT_USERCOL="$RED"}"
    : "${PROMPT_USERFMT="$PROMPT_USERCOL\\u$RESET@$RED\\h "}"
else
    : "${PROMPT_USERCOL="$CYAN"}"
    : "${PROMPT_USERFMT=""}"
fi

# avoid fancy symbol in the linux terminal
if [[ $PROMPT_MULTILINE ]]; then
    : "${PROMPT_LNBR1="┌"}"  # ┌ ┏ ╓ ╒
    : "${PROMPT_LNBR2="└"}"  # └ ┗ ╙ ╘
    : "${PROMPT_ARROW=">"}"  # ➜ ➤ ► ▻ ▸ ▹ ❯
fi

# git settings
: "${GIT_PS1_SHOWUPSTREAM="verbose git"}"
: "${GIT_PS1_SHOWDIRTYSTATE="true"}"
: "${GIT_PS1_SHOWCOLORHINTS="true"}"
: "${GIT_PS1_SHOWSTASHSTATE="true"}"
: "${GIT_PS1_SHOWUNTRACKEDFILES="true"}"


# print last command's exit code in red
__exitcode()
{
    # shellcheck disable=2154
    (( exitcode == 0 )) || printf " \e[31m$?"
}

# print blue '(r)' when in a nested ranger shell
__ranger()
{
    if [[ $RANGER_LEVEL ]]; then
        (( RANGER_LEVEL == 1 )) && printf " $BLUE(ranger)" || printf " $BLUE(ranger:$RANGER_LEVEL)"
    fi
}

# set the terminal title
__title()
{
    [[ $TERM =~ (xterm|rxvt|st) ]] && printf "%s" '\[\033]0;$TERM: $(basename $SHELL) - \w\007\]'
    return 0
}

## Git functions below

# check whether printf supports -v
__git_printf_supports_v=
printf -v __git_printf_supports_v -- '%s' true >/dev/null 2>&1

__git_eread()
{
    test -r "$1" && IFS=$'\r\n' read -r "$2" <"$1"
}

__git_ps1_colorize_gitstring()
{
    local bad_color="$RED"
    local ok_color="$GREEN"
    local flags_color="$BLUE"
    local branch_color=""
    [[ $detached = no ]] && branch_color="$ok_color" || branch_color="$bad_color"
    c="$branch_color$c"
    z="$RESET$z"
    [[ "$w" = "*" ]] && w="$bad_color$w"
    [[ -n "$i" ]] && i="$ok_color$i"
    [[ -n "$s" ]] && s="$flags_color$s"
    [[ -n "$u" ]] && u="$bad_color$u"
    r="$RESET$r"
}

__git_ps1_show_upstream()
{
    local key value
    local svn_remote svn_url_pattern count n
    local upstream=git legacy="" verbose="" name=""
    local svn_remote=()

    # get some config options from git-config
    local output
    output="$(git config -z --get-regexp '^(svn-remote\..*\.url|bash\.showupstream)$' 2>/dev/null | tr '\0\n' '\n ')"
    while read -r key value; do
        case "$key" in
            bash.showupstream)
                GIT_PS1_SHOWUPSTREAM="$value"
                [[ $GIT_PS1_SHOWUPSTREAM ]] || { p=""; return; } ;;
            svn-remote.*.url)
                svn_remote[$((${#svn_remote[@]} + 1))]="$value"
                svn_url_pattern="$svn_url_pattern\\|$value"
                upstream=svn+git ;; # default upstream is SVN if available, else git
        esac
    done <<< "$output"

    # parse configuration values
    for option in ${GIT_PS1_SHOWUPSTREAM}; do
        case "$option" in
            git|svn) upstream="$option" ;;
            verbose) verbose=1 ;;
            legacy) legacy=1  ;;
            name) name=1 ;;
        esac
    done

    # Find our upstream
    case "$upstream" in
        git)  upstream="@{upstream}" ;;
        svn*)
            local -a svn_upstream
            svn_upstream=($(git log --first-parent -1 --grep="^git-svn-id: \(${svn_url_pattern#??}\)" 2>/dev/null))
            if [[ ${#svn_upstream[@]} -ne 0 ]]; then
                upstream=${svn_upstream[${#svn_upstream[@]} - 2]}
                upstream=${upstream%@*}
                local n_stop="${#svn_remote[@]}"
                local n=1
                while (( n <= n_stop )); do upstream=${upstream#${svn_remote[$n]}}; ((n++)); done
                [[ -z $upstream ]] && upstream=${GIT_SVN_ID:-git-svn} || upstream=${upstream#/}
            elif [[ "svn+git" = "$upstream" ]]; then
                upstream="@{upstream}"
            fi
    esac

    # Find how many commits we are ahead/behind our upstream
    if [[ -z $legacy ]]; then
        count="$(git rev-list --count --left-right "$upstream"...HEAD 2>/dev/null)"
    else
        # produce equivalent output to --count for older versions of git
        local commits
        if commits="$(git rev-list --left-right "$upstream"...HEAD 2>/dev/null)"; then
            local commit behind=0 ahead=0
            for commit in $commits; do
                case "$commit" in
                    "<"*) ((behind++)) ;;
                    *)    ((ahead++))  ;;
                esac
            done
            count="$behind	$ahead"
        else
            count=""
        fi
    fi

    # calculate the result
    if [[ -z $verbose ]]; then
        case "$count" in
            "") p=""      ;; # no upstream
            "0	0") p="=" ;; # equal to upstream
            "0	"*) p=">" ;; # ahead of upstream
            *"	0") p="<" ;; # behind upstream
            *) p="<>"        # diverged from upstream
        esac
    else
        case "$count" in
            "") p=""                                ;; # no upstream
            "0	0") p="="                           ;; # equal to upstream
            "0	"*) p="+${count#0	}"          ;; # ahead of upstream
            *"	0") p="-${count%	0}"         ;; # behind upstream
            *) p="+${count#*	}-${count%	*}" ;; # diverged from upstream
        esac
        if [[ -n $count && -n $name ]]; then
            __git_ps1_upstream_name=$(git rev-parse --abbrev-ref "$upstream" 2>/dev/null)
            if [[ $pcmode = yes && $ps1_expanded = yes ]]; then
                p="$p \${__git_ps1_upstream_name}"
            else
                p="$p ${__git_ps1_upstream_name}"
                unset __git_ps1_upstream_name
            fi
        fi
    fi
}

__git_ps1 ()
{
    local pcmode=no
    local detached=no
    local ps1pc_start=''
    local ps1pc_end=' $(__prompt "dummy_arg")'
    local printf_format=' (%s)'

    case "$#" in
        2|3) pcmode=true
            ps1pc_start="$1"
            ps1pc_end="$2"
            printf_format="${3:-$printf_format}"
            PS1="$ps1pc_start$ps1pc_end"
            export PS1 ;;
        0|1) printf_format="${1:-$printf_format}" ;;
        *) return $exitcode ;;
    esac

    local ps1_expanded=true
    [[ -z ${ZSH_VERSION-} ]] || [[ -o PROMPT_SUBST ]] || ps1_expanded=no
    [[ -z ${BASH_VERSION-} ]] || shopt -q promptvars || ps1_expanded=no

    local repo_info rev_parse_exit_code
    repo_info="$(git rev-parse --git-dir --is-inside-git-dir \
        --is-bare-repository --is-inside-work-tree --short HEAD 2>/dev/null)"
    rev_parse_exit_code="$?"

    [[ -z $repo_info ]] && return $exitcode

    local short_sha=""
    if [[ $rev_parse_exit_code = "0" ]]; then
        short_sha="${repo_info##*$'\n'}"
        repo_info="${repo_info%$'\n'*}"
    fi
    local inside_worktree="${repo_info##*$'\n'}"
    repo_info="${repo_info%$'\n'*}"
    local bare_repo="${repo_info##*$'\n'}"
    repo_info="${repo_info%$'\n'*}"
    local inside_gitdir="${repo_info##*$'\n'}"
    local g="${repo_info%$'\n'*}"

    if [[ "true" = "$inside_worktree" && -n ${GIT_PS1_HIDE_IF_PWD_IGNORED-} && $(git config --bool bash.hideIfPwdIgnored) != "false" ]] && git check-ignore -q .; then
        return $exitcode
    fi

    local r b step total
    r="" b="" step="" total=""
    if [[ -d $g/rebase-merge ]]; then
        __git_eread "$g/rebase-merge/head-name" b
        __git_eread "$g/rebase-merge/msgnum" step
        __git_eread "$g/rebase-merge/end" total
        [[ -f $g/rebase-merge/interactive ]] && r="|REBASE-i" || r="|REBASE-m"
    else
        if [[ -d $g/rebase-apply ]]; then
            __git_eread "$g/rebase-apply/next" step
            __git_eread "$g/rebase-apply/last" total
            if [[ -f $g/rebase-apply/rebasing ]]; then
                __git_eread "$g/rebase-apply/head-name" b
                r="|REBASE"
            elif [[ -f $g/rebase-apply/applying ]]; then
                r="|AM"
            else
                r="|AM/REBASE"
            fi
        elif [[ -f $g/MERGE_HEAD ]]; then
            r="|MERGING"
        elif [[ -f $g/CHERRY_PICK_HEAD ]]; then
            r="|CHERRY-PICKING"
        elif [[ -f $g/REVERT_HEAD ]]; then
            r="|REVERTING"
        elif [[ -f $g/BISECT_LOG ]]; then
            r="|BISECTING"
        fi

        if [[ -n $b ]]; then
            :  # no need to do anything, b has already been set
        elif [[ -h $g/HEAD ]]; then
            b="$(git symbolic-ref HEAD 2>/dev/null)" # symlink symbolic ref
        else
            local head=""
            __git_eread "$g/HEAD" head || return $exitcode
            # is it a symbolic ref?
            b="${head#ref: }"
            if [[ $head = "$b" ]]; then
                detached=true
                b="$(
                case "${GIT_PS1_DESCRIBE_STYLE-}" in
                    (contains) git describe --contains HEAD ;;
                    (branch) git describe --contains --all HEAD ;;
                    (tag) git describe --tags HEAD ;;
                    (describe) git describe HEAD ;;
                    (default|*) git describe --tags --exact-match HEAD ;;
                esac 2>/dev/null)" || b="$short_sha..."
                b="($b)"
            fi
        fi
    fi

    [[ -n $step && -n $total ]] && r="$r $step/$total"

    local w i s u c p
    w="" i="" s="" u="" c="" p=""

    if [[ "true" = "$inside_gitdir" ]]; then
        [[ "true" = "$bare_repo" ]] && c="BARE:" || b="GIT_DIR!"
    elif [[ "true" = "$inside_worktree" ]]; then
        if [[ ${GIT_PS1_SHOWDIRTYSTATE-} == true && $(git config --bool bash.showDirtyState) != "false" ]]; then
            git diff --no-ext-diff --quiet || w="*"
            git diff --no-ext-diff --cached --quiet || i="+"
            [[ -z "$short_sha" && -z "$i" ]] && i="#"
        fi
        if [[ ${GIT_PS1_SHOWSTASHSTATE-} == true ]] && git rev-parse --verify --quiet refs/stash >/dev/null; then
            s="$"
        fi

        if [[ ${GIT_PS1_SHOWUNTRACKEDFILES-} == true && "$(git config --bool bash.showUntrackedFiles)" != "false" ]] && \
                git ls-files --others --exclude-standard --directory --no-empty-directory --error-unmatch -- ':/*' >/dev/null 2>/dev/null; then
            u="%${ZSH_VERSION+%}"
        fi
        [[ -n ${GIT_PS1_SHOWUPSTREAM-} ]] && __git_ps1_show_upstream
    fi

    local z="${GIT_PS1_STATESEPARATOR-" "}"

    # no color option for bash/zsh unless in PROMPT_COMMAND mode
    if [[ $pcmode == true && ${GIT_PS1_SHOWCOLORHINTS-} == true || ! ($BASH_VERSION || $ZSH_VERSION) ]]; then
        __git_ps1_colorize_gitstring
    fi

    b=${b##refs/heads/}
    if [[ $pcmode == true && $ps1_expanded == true ]]; then
        export __git_ps1_branch_name=$b
        b='${__git_ps1_branch_name}'
    fi

    local f="$w$i$s$u"
    local gitstring="$c$b${f:+$z$f}$r$p"

    if [[ $pcmode == true ]]; then
        if [[ ${__git_printf_supports_v-} != true ]]; then
            gitstring=$(printf -- "$printf_format" "$gitstring")
        else
            printf -v gitstring -- "$printf_format" "$gitstring"
        fi
        PS1="$ps1pc_start$gitstring$ps1pc_end"
    else
        printf -- "$printf_format" "$gitstring"
    fi
    export PS1
    return $exitcode
}

