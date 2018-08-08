import re

from .branch import Branch
from .commit import Commit

class Tree:
    def __init__(self, branches, root='master'):
        self._branches = branches
        self._head = self._find_head(branches.values())
        self._root = branches[root]

    def _find_head(self, branches):
        for branch in branches:
            if branch.is_active:
                return branch

    def __getitem__(self, name):
        return self._branches[name]

    def __contains__(self, name):
        return name in self._branches

    @property
    def root(self):
        return self._root

    @property
    def head(self):
        return self._head

    @property
    def branches(self):
        return self._branches.values()
