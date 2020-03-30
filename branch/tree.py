import re

from .branch import Branch
from .commit import Commit


class Tree:
    def __init__(self, head, root, branches):
        self._branches = {b.id: b for b in branches}
        self._head = self._find(head, branches)
        self._root = self._find(root, branches)
        self._head.is_active = True

    def _find(self, ref, branches):
        for branch in branches:
            if branch.ref == ref:
                return branch
        raise Exception('Branch for ' + ref[:7] + ' was not found')

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
