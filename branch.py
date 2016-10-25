#!/usr/bin/python
#
#  Simple Git helper that handles branches.
#  It's main purpouse is to rebase all local branches
#  over the master branch after a successful pull.
#
#  Version: 0.0.2
#

import argparse
import subprocess
import sys
import re


class Branch:
    def __init__(self, name, description='', parent=None):
        self._name = name
        self._description = description
        self._parent = parent
        self._children = {}

    def __eq__(self, other):
        if not isinstance(other, Branch):
            return false
        return self._name == other._name

    def __str__(self):
        description = self._description
        if len(description) > 40:
            description = description[:37] + '...'
        return '[{0}] {1}'.format(self._name, description)

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def children(self):
        return self._children

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    def is_parent(self, branch):
        if not self._parent:
            return False
        if self._parent.name == branch.name:
            return True
        return self._parent.is_parent(branch)


class GitException(Exception):
    pass


class GitStash:
    def __enter__(self):
        print('Stashing any existing changes ...')
        output = subprocess.check_output([
            'git',
            'stash'
        ], universal_newlines=True)
        self._stashed = (output.strip() != 'No local changes to save')
        if not self._stashed:
            print('Nothing to stash')
        print('====================\n')

    def __exit__(self, type, value, tb):
        print('\n===================')
        if not self._stashed:
            print('Nothing to unstash. Skipping')
            return
        try:
            print('Unstashing ...')
            subprocess.check_output(['git', 'stash', 'pop'])
        except subprocess.CalledProcessError:
            exit('Failed to pop the stash. Do it manually!')


class Git:
    def stash(self):
        return GitStash()

    def pull_rebase(self):
        if 0 != subprocess.call(['git', 'pull', '--rebase']):
            raise GitException()

    def show_branch(self):
        try:
            return subprocess.check_output([
                'git',
                'show-branch',
                '--no-color',
                '--topo-order'
            ], universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise GitException(e.output)


class Program:
    def __init__(self):
        self._git = Git()
        self._tree = {}
        self._current_branch = 'master'
        self._init_tree()

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('action', choices=['pull'])
        args = parser.parse_args()
        if 'pull' == args.action:
            self._pull_remote_repository()
        self._print_tree(self._find_root(), prefix='  ')

    def _pull_remote_repository(self):
        with self._git.stash():
            try:
                print('Pulling from the remote repository ...')
                self._git.pull_rebase()
            except GitException:
                exit('Failed to pull from remote repository')

    def _find_root(self, branch=None):
        if not branch:
            branch = self._tree['master']
        if not branch.parent:
            return branch
        return self._find_root(branch.parent)

    def _print_tree(self, branch, offset='', prefix="->"):
        print("{0}{1} {2}".format(offset, prefix, str(branch)))
        counter = len(branch.children)
        for _, child in branch.children.items():
            new_offset = offset.replace('`', ' ').replace('+', '|')
            if counter == 1:
                new_offset += '   `'
            else:
                new_offset += '   +'
            self._print_tree(child, offset=new_offset)
            counter -= 1

    def _init_tree(self):
        try:
            parts = re.split('-+\n', self._git.show_branch())
            branches = self._build_branches(parts[0])

            self._tree = {branch.name: branch for branch in branches}
            if len(parts) > 1:
                self._calculate_tree(branches, parts[1])
        except GitException as e:
            exit('Failed to calculate branch tree: ' + e.value)

    def _build_branches(self, output):
        result = []
        for line in output.split('\n'):
            match = re.match('^.*?\\[(.+?)\\]\\s(.+)', line)
            if not match:
                continue
            name, description = match.group(1, 2)
            result.append(Branch(name, description=description))
        return result

    def _calculate_tree(self, branches, output):
        for line in output.split('\n'):
            match = re.match(
                '^([\\s*+-]+?)\\s\\[(.+?)(?:[~^]\\d*)?\\]', line)
            if not match:
                continue
            knot, name = match.group(1, 2)
            for i, c in enumerate(knot):
                if ' ' == c:
                    continue
                if branches[i].name == name:
                    continue
                if not branches[i].parent:
                    branches[i].parent = self._tree[name]
                if self._tree[name].is_parent(branches[i].parent):
                    branches[i].parent = self._tree[name]
        for branch in branches:
            if not branch.parent:
                continue
            branch.parent.children[branch.name] = branch

#
#   M A I N
#

if __name__ == "__main__":
    Program().run()
