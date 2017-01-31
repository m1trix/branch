import re

from .branch import Branch
from .commit import Commit

BRANCH_KNOT = '^([\\s*+-]+?)\\s\\[(.+?)(?:[~^]\\d*)*\\]'


class Tree:
    def __init__(self, branches):
        self._branches = branches
        self._root = None

    def __getitem__(self, name):
        return self._branches[name]

    @property
    def root(self):
        if self._root is None:
            self._root = self._find_root(self._branches['master'])
        return self._root

    def _find_root(self, branch):
        if not branch.has_parent:
            return branch
        return self._find_root(branch.parent)


class TreeBuilder:
    def __init__(self, git):
        self._git = git
        self._include_commits = False

    def include_commits(self, include_commits):
        self._include_commits = include_commits
        return self

    def build(self):
        remote_branches = [
            row.replace('*', ' ').strip()
            for row
            in self._git.remote_branches().split('\n')
        ]

        parts = re.split('-+\n', self._git.show_branch())
        branches = self._build_branches(parts[0])

        tree = Tree({branch.name: branch for branch in branches})
        len(parts) > 1 and self._build_tree(tree, branches, parts[1])

        if self._include_commits:
            for branch in branches:
                self._build_commits(branch)
        return tree

    def _build_branches(self, raw_data):
        lines = raw_data.split('\n')
        matchers = [re.match('^.*?\\[(.+?)\\]', line) for line in lines]
        return [Branch(matcher.group(1)) for matcher in matchers if matcher]

    def _build_tree(self, tree, branches, raw_data):
        lines = raw_data.split('\n')
        matchers = [re.match(BRANCH_KNOT, line) for line in lines]
        knots = [matcher.group(1, 2) for matcher in matchers if matcher]
        for knot, name in knots:
            for i, c in enumerate(knot):
                if ' ' == c:
                    continue
                if branches[i].name == name:
                    continue
                if branches[i].parent is None:
                    branches[i].parent = tree[name]
                if branches[i].parent.is_parent_of(tree[name]):
                    branches[i].parent = tree[name]
                if branches[i].name == 'master' and branches[i].parent is not None:
                    branches[i].parent.parent = branches[i]
                    branches[i].parent = None
        for branch in branches:
            if branch.has_parent:
                branch.parent.children[branch.name] = branch

    def _build_commits(self, branch):
        if not branch.has_parent:
            output = self._git.log(fr=branch.name)
        else:
            output = self._git.log(fr=branch.parent.name, to=branch.name)
        lines = [line for line in output.strip().split('\n') if line != '']
        commits = [line.split(maxsplit=1) for line in lines]
        branch.commits = [Commit(hash, message) for hash, message in commits]
