import re

from .branch import Branch
from .commit import Commit

BRANCH_KNOT = '^([\\s*+-]+?)\\s\\[(.+?)(?:[~^]\\d*)*\\]'


class Tree:
    def __init__(self, branches, remotes):
        self._branches = branches
        self._remotes = [
            branches[name] for name in remotes if name in branches
        ]
        for branch in self._remotes:
            branch.is_remote = True

    def __getitem__(self, name):
        return self._branches[name]

    @property
    def remotes(self):
        return self._remotes

    @property
    def root(self):
        return self._branches['master']


class TreeBuilder:
    def __init__(self, git):
        self._git = git
        self._include_commits = False

    def include_commits(self, include_commits):
        self._include_commits = include_commits
        return self

    def build(self):
        parts = re.split('-+\n', self._git.show_branch())
        branches = self._build_branches(parts[0])
        remotes = [
            row.replace('*', ' ').replace('origin/', '').strip()
            for row in self._git.remote_branches().split('\n')
        ]

        tree = Tree({branch.name: branch for branch in branches}, remotes)
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
        knots = self._parse_knots(raw_data)
        self._calculate_parents(knots, tree, branches)
        self._ensure_master_is_root(tree)
        self._fill_in_child_branches(branches)

    def _parse_knots(self, raw_data):
        lines = raw_data.split('\n')
        matchers = [re.match(BRANCH_KNOT, line) for line in lines]
        return [matcher.group(1, 2) for matcher in matchers if matcher]

    def _calculate_parents(self, knots, tree, branches):
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

    def _ensure_master_is_root(self, tree):
        master = tree['master']
        while master.has_parent:
            parent = master.parent
            master.parent, parent.parent = parent.parent, master

    def _fill_in_child_branches(self, branches):
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
