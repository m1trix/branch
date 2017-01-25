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
        self._commits = []

    def __eq__(self, other):
        if not isinstance(other, Branch):
            return false
        return self._name == other._name

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

    @property
    def commits(self):
        return self._commits

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

    def log(self, fr=None, to=None):
        try:
            command = ['git', 'log', '--pretty=oneline']
            if fr:
                command.append(fr)
            if to:
                command[-1] += '..' + to
            return subprocess.check_output(command, universal_newlines=True)
        except subprocess.CalledProcessError:
            exit('Failed to check git log')


class Renderer:
    COMMIT_FORMAT = '{0}     {1:2}: {2}'

    def render(self, branch):
        canvas = []
        self._render(branch, canvas, 3, '', '  ')
        return canvas

    def _render(self, branch, canvas, context, offset, prefix):
        for i, key in enumerate(branch.children):
            child = branch.children[key]
            new_offset = offset.replace('.', ' ').replace('+', '|')
            new_offset += '   {}'.format(['+', '.'][i != 1])
            self._render(child, canvas, -1, new_offset, '->')
        canvas.append("{0}{1} [{2}]".format(offset, prefix, branch.name))
        for i, commit in enumerate(branch.commits):
            if i == context:
                break
            canvas.append(self._render_commit(i, commit, offset))

    def _render_commit(self, i, commit, offset):
        commit_offset = offset.replace('.', '|').replace('+', '|')
        return Renderer.COMMIT_FORMAT.format(commit_offset, i + 1, commit)


class Program:
    def __init__(self):
        self._git = Git()
        self._tree = {}
        self._current_branch = 'master'
        self._root = None

    def run(self):
        parser = argparse.ArgumentParser(allow_abbrev=False)
        parser.add_argument('-p', '--pull', action='store_true',
                            help='pulls from the remote repository')
        parser.add_argument('-m', '--more', action='store_true',
                            help='displays more details in branch tree')
        args = parser.parse_args()

        self._init_tree(args.more)
        if args.pull:
            self._pull_remote_repository()
        self._print_tree()

    def _pull_remote_repository(self):
        with self._git.stash():
            try:
                print('Pulling from the remote repository ...')
                self._git.pull_rebase()
            except GitException:
                exit('Failed to pull from remote repository')

    def _print_tree(self):
        rendering = Renderer().render(self._root)
        for line in rendering:
            print(line)

    def _init_tree(self, details):
        try:
            parts = re.split('-+\n', self._git.show_branch())
            branches = self._build_branches(parts[0])

            self._tree = {branch.name: branch for branch in branches}
            len(parts) > 1 and self._calculate_tree(branches, parts[1])

            self._root = self._find_root()
            details and self._init_details()
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

    def _find_root(self):
        for _, branch in self._tree.items():
            if not branch.parent:
                return branch
        raise IllegalStateError('No root branch found')

    def _init_details(self):
        self._init_commits(self._root)

    def _init_commits(self, branch):
        if not branch.parent:
            output = self._git.log(fr=branch.name)
        else:
            output = self._git.log(fr=branch.parent.name, to=branch.name)
        for line in output.strip().split('\n'):
            if '' == line:
                continue
            _, message = line.split(maxsplit=1)
            branch.commits.append(message)
        for _, child in branch.children.items():
            self._init_commits(child)

#
#   M A I N
#

if __name__ == "__main__":
    Program().run()
