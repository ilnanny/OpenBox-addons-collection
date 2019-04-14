# Path to your oh-my-zsh installation.
ZSH="/home/swampyx/.oh-my-zsh/"

# Set name of the theme to load.
# Look in ~/.oh-my-zsh/themes/
# Optionally, if you set this to "random", it'll load a random theme each
# time that oh-my-zsh is loaded.
ZSH_THEME="agnoster"

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to change how often to auto-update (in days).
#export UPDATE_ZSH_DAYS=1

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# The optional three formats: "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load? (plugins can be found in ~/.oh-my-zsh/plugins/*)
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
#plugins=(git)

# User configuration

#export PATH=$HOME/bin:/usr/local/bin:$PATH
# export MANPATH="/usr/local/man:$MANPATH"

source $ZSH/oh-my-zsh.sh

# You may need to manually set your language environment
export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi

# Compilation flags
export ARCHFLAGS="-arch x86_64"

# ssh
# export SSH_KEY_PATH="~/.ssh/dsa_id"

# Lines configured by zsh-newuser-install
export HISTFILE=~/.histfile
export HISTSIZE=100000
export SAVEHIST=$HISTSIZE
#export LC_ALL=C

setopt hist_ignore_all_dups
setopt autocd
#setopt correctall

export CFLAGS="-march=native -O3 -pipe -fstack-protector-strong --param=ssp-buffer-size=4"
export CXXFLAGS="-march=native -O3 -pipe -fstack-protector-strong --param=ssp-buffer-size=4"

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

emulate sh -c 'source /etc/profile'

if [[ $(whoami) != "root" ]]; then
    cal
fi

function git_prompt_info() {
  ref=$(git symbolic-ref HEAD 2> /dev/null) || return
  echo "$ZSH_THEME_GIT_PROMPT_PREFIX${ref#refs/heads/}$ZSH_THEME_GIT_PROMPT_SUFFIX"
}


#-----------------------------
# Dircolors
#-----------------------------
export LS_COLORS='rs=0:di=01;34:ln=01;36:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:su=37;41:sg=30;43:tw=30;42:ow=34;42:st=37;44:ex=01;32:';

#------------------------------
# Keybindings
#------------------------------
#~ bindkey -v
#~ typeset -g -A key
#~ bindkey '\e[3~' delete-char
#~ bindkey '\e[1~' beginning-of-line
#~ bindkey '\e[4~' end-of-line
#~ bindkey '\e[2~' overwrite-mode
#~ bindkey '^?' backward-delete-char
#~ bindkey '^[[1~' beginning-of-line
#~ bindkey '^[[5~' up-line-or-history
#~ bindkey '^[[3~' delete-char
#~ bindkey '^[[6~' down-line-or-history
#~ bindkey '^[[A' up-line-or-search
#~ bindkey '^[[D' backward-char
#~ bindkey '^[[B' down-line-or-search
#~ bindkey '^[[C' forward-char
#~ # for rxvt
#~ bindkey "\e[8~" end-of-line
#~ bindkey "\e[7~" beginning-of-line
#~ # for gnome-terminal
#~ bindkey "\eOH" beginning-of-line
#~ bindkey "\eOF" end-of-line


#------------------------------
# Comp stuff
#------------------------------
zmodload zsh/complist
autoload -Uz compinit
zstyle ':completion:*' matcher-list '' 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
#~ compinit
#~ zstyle :compinstall filename '${HOME}/.zshrc'

#~ zstyle ':completion:*:pacman:*' force-list always
#~ zstyle ':completion:*:*:pacman:*' menu yes select

#~ zstyle ':completion:*:default' list-colors ${(s.:.)LS_COLORS}

#~ zstyle ':completion:*:*:kill:*' menu yes select
#~ zstyle ':completion:*:kill:*'   force-list always

#~ zstyle ':completion:*:*:killall:*' menu yes select
#~ zstyle ':completion:*:killall:*'   force-list always


#------------------------------
# Export stuff
#------------------------------
export XDG_CONFIG_HOME="$HOME/.config"
export USE_CCACHE=1
export EDITOR='joe'
export BROWSER='chromium'
export WEBBROWSER='chromium'
export GOROOT=/usr/lib/go
export GOOS='linux'
export FILEMANAGER='pcmanfm'
export TERM='xterm'
export GOPATH="$HOME/GO"
export GOBIN="$HOME/GO/bin"
export GOMAXPROCS=2
#export GOPKGS="$HOME/GO/pkg"
export QTDIR=/usr/include/QtCore
#export CC="colorgcc"
export CCACHE_PATH="/usr/bin"
export CCACHE_SLOPPINESS="include_file_mtime,time_macros,file_macro"
#export CCACHE_DIR=/media/ccache
export DBI_DRIVER='mysql'
export PATH="/usr/lib/ccache/bin:$PATH:/usr/share/perl6/vendor/bin"
#export PS1="%B%n%b[%~]: "
export PROG="$HOME/Other/Programare"
export PZN="$PROG/Personal projects"
export SIDEF="$PROG/Sidef"
#export JOHANA="$PROG/Johana"
#export VEGA="$PROG/Vega"
export CORVINUS="$PROG/corvinus2"
export WER="$PROG/perl-scripts"
export FUN="$PROG/Fun scripts"

#------------------------------
# Alias stuff
#------------------------------
alias df='df -hT'                           # human readable, print filetype
alias du='du -d1 -h'                        # max depth, human readable
alias free='free -h'                        # human readable
alias cp='cp -v'                            # verbose copy
alias mv='mv -v'                            # verbose move
alias rm='rm -v'                            # verbove remove
alias rmdir='rmdir -v'                      # verbose remove dir
alias mkdir='mkdir -p -v'                   # create if not exist, verbose
alias ln='ln -v'                            # verbose link
alias wget='wget -c'                        # continues/resumes
alias chmod='chmod -c'
alias chown='chown -c'
alias subr='sub-renamer -r'
#alias rcp='rsync -v --progress'
#alias rmv='rsync -v --progress --remove-source-files'

## Alias Color Commands
alias dir='ls --color=auto --format=vertical'
alias vdir='ls --color=auto --format=long'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias ls='ls --color=auto --human-readable --group-directories-first --classify'
alias less='less -g -r'

## Other aliases
alias p='rlwrap perl6 --optimize=3 $@'
alias perltidy='perltidy -l=127 -f -kbl=1 -bbb -bbc -bbs -b -ple -bt=2 -pt=2 -sbt=2 -bvt=0 -sbvt=1 -cti=1 -bar -lp -anl'
alias music="youtube-viewer -A -n -m -s --res=audio --min-seconds=60 --max-seconds=480 $@"
alias favmusic="youtube-viewer -F -m -n --res=audio --std-input=:anp\ :re=\\\\p{cyrillic} --page \$1"
alias rmusic="youtube-viewer -A -m -n -s --res=audio --min-seconds=60 --max-seconds=480 -rv $@"
alias randalias="$SIDEF/bin/sidef -E 'say(%F<#{ENV{:HOME}}/youtube-viewer.txt>.open_r.lines.rand)'"
alias yv="youtube-viewer"
#alias inxi="inxi -F -x -f -o -p"
alias url2pdf="wkhtmltopdf --use-xserver --enable-javascript --enable-smart-shrinking --images --enable-external-links --load-error-handling ignore --javascript-delay 3500 $@"
alias locatepm="locatepm -b"
alias install-perl="perlbrew install -Doptimize='-march=native -Ofast -pipe' -j 2 --noman --notest --thread --multi $@"
alias plint="perl -MO=Lint,all $@"
alias roxy="rlwrap $SIDEF/bin/sidef /home/swampyx/Other/Programare/MYPKGS/smart-units/smart-units.sf"
alias sidef="$SIDEF/bin/sidef"
#alias vega="$VEGA/bin/vega"
#alias johana="$JOHANA/bin/johana"
#alias jh="$JOHANA/bin/johana"
alias sf="$SIDEF/bin/sidef"
alias corvin="$CORVINUS/bin/corvin"
alias rusmusic="perl -MList::Util=shuffle -E 'system(q{mpv}, q{--no-video}, shuffle(glob(q{~/Music/Rusa\ net/Converted/*}), glob(q{~/Music/{Altele,Rusa,Recenta\ rusa,Rusa\ Noua}/*}), glob(q{~/Music/*.{mp4,mp3,webm}})))'"
alias dirmusic="perl -E 'for(glob(\"\*\")){push@songs,\$_ if -f\$_;}system(qw(mpv --shuffle --no-video),@songs)'"
#alias rusmusic="perl -MList::Util=shuffle -E 'system q{mpv}, q{--no-video}, shuffle(glob(q{~/Videos/Rusa/*}))'"
#alias dkms_nvidia="dkms install -m nvidia -v $(perl -E'say`pacman -Qi nvidia-dkms`=~/^Version\h*:\h*([^-]+)/m') -k $@"
#alias percritic='perlcritic --statistics'
#alias mkpm='h2xs -A -a -b 5.10.1 -X --skip-exporter --skip-warnings --skip-ppport --skip-autoloader -n $@'
alias plspellcheck="perl $WER/Analyzers/perl_code_spellcheck.pl --scan=all $@"

# Local scripts
alias merge-images="perl $WER/Image/gd_star_trails.pl"
alias mmerge-images="perl $WER/Image/magick_star_trails.pl"
alias similar-imgs="perl $WER/Image/gd_similar_images.pl"
alias img2html="perl $WER/Image/img2html.pl"
alias img2ascii="perl $WER/Image/img2ascii.pl"
alias scgrep="perl $WER/Greppers/scgrep"
alias any_to_3gp="perl $WER/Converters/any_to_3gp.pl"
alias unidec_renamer="perl $WER/Decoders/unidec_renamer.pl"
alias fdf="perl $WER/Finders/fdf"
alias fsfn="perl $WER/Finders/fsfn.pl"
#alias pview="perl $WER/Visualisators/pview"
alias pview="pl2term"
alias disk-stats="perl $WER/Visualisators/disk-stats.pl"
alias file-monitor="perl $WER/Monitoring/file-monitor"
alias locatepm="perl $WER/Finders/locatepm -i -b"
alias img-rewrite="perl $WER/Image/img_rewrite.pl"
alias sany2mp3="sidef $SIDEF/scripts/Applications/sany2mp3.sf"
alias make_filenames_safe="sidef $SIDEF/scripts/Applications/make_filenames_safe.sf"
alias wave-cmp="perl $WER/Audio/wave-cmp.pl"
alias canly="perl $WER/Analyzers/perl_code_analyzer.pl"
alias img-autocrop="perl $WER/Image/img-autocrop.pl"
alias yafu="rlwrap yafu $@"
alias poem-from-poem="perl $WER/Lingua/poetry_from_poetry.pl"
alias rand-poem="perl $WER/Lingua/poetry_from_poetry_with_variations.pl"

# Support colors in less
export LESS_TERMCAP_mb=$'\E[01;33m'
export LESS_TERMCAP_md=$'\E[01;33m'
export LESS_TERMCAP_me=$'\E[0m'
export LESS_TERMCAP_se=$'\E[0m'
export LESS_TERMCAP_so=$'\E[01;42;33m'
export LESS_TERMCAP_ue=$'\E[0m'
export LESS_TERMCAP_us=$'\E[01;32m'
export TEMP=/tmp


# report about cpu-/system-/user-time of command if running longer than
# 5 seconds
REPORTTIME=5

# watch for everyone but me and root
watch=(notme root)

# automatically remove duplicates from these arrays
typeset -U path cdpath fpath manpath

#------------------------------
# Subroutines
#------------------------------

screencast() {
    ffmpeg -hwaccel vdpau -f alsa -ac 2 -i hw:0,0 -f x11grab -r 30 -s 1920x1080 -i :0.0 -acodec aac -vcodec libx264 -preset ultrafast -crf 10 -threads 0 -y $@
}

preexec() {
    printf '\e]0;%s\a' "$2"
}

over_ssh() {
    if [ -n "${SSH_CLIENT}" ]; then
        return 0
    else
        return 1
    fi
}

confirm() {
    local answer
    echo -ne "zsh: sure you want to run '${YELLOW}$@${NC}' [yN]? "
    read -q answer
        echo
    if [[ "${answer}" =~ ^[Yy]$ ]]; then
        command "${=1}" "${=@:2}"
    else
        return 1
    fi
}

unistream() {
    mpv $(youtube-dl -g $@)
}

confirm_wrapper() {
    if [ "$1" = '--root' ]; then
        local as_root='true'
        shift
    fi

    local runcommand="$1"; shift

#    if [ "${USER}" != 'root' ]; then
#        echo "You cannot execute command: $runcommand"
#        return 1;
#    fi
    confirm "${runcommand}" "$@"
}

poweroff() { confirm_wrapper --root $0 "$@"; }
reboot() { confirm_wrapper --root $0 "$@"; }
hibernate() { confirm_wrapper --root $0 "$@"; }

#[[ -z $DISPLAY && $XDG_VTNR -eq 1 ]] && exec startx
