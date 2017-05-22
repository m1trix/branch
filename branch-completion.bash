#!/bin/bash

readonly BRANCH="${1}" ; shift


function __branch_incomplete_command() {
    local word="${COMP_WORDS["${COMP_CWORD}"]}"
    if [[ 'pull' == "${word}"* ]] ; then
        COMPREPLY+=('pull')
    fi

    if [[ 'wipe' == "${word}"* ]] ; then
        COMPREPLY+=('wipe')
    fi
}

function __branch_incomplete_option() {
    local word="${COMP_WORDS[COMP_CWORD]}"
    for option in "${@}" ; do
        if [[ "${option}" == "${word}"* ]] ; then
            COMPREPLY+=("${option}")
        fi
    done
}

function __branch_completion() {
    if [[ "${#COMP_WORDS[@]}" == "2" ]] ; then
        __branch_incomplete_option '-c' '--commits'
        __branch_incomplete_command
    fi

    local word="${COMP_WORDS[COMP_CWORD-1]}"
    if [[ "${word}" == 'pull' ]] ; then
        __branch_incomplete_option '-h' '--help' '-w' '--wipe'
    fi

    if [[ "${word}" == 'wipe' ]] ; then
        __branch_incomplete_option '-h' '--help'
    fi
}


complete -F __branch_completion "${BRANCH}"