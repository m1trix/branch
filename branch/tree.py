class Tree:
    def __init__(self, branches, root='master'):
        self._branches = branches
        self._active = self._find_active(branches.values())
        self._root = branches[root]

    def _find_active(self, branches):
        for branch in branches:
            if branch.is_active:
                return branch

    @property
    def root(self):
        return self._root

    @property
    def active(self):
        return self._active

    @property
    def branches(self):
        return self._branches.values()

    def __getitem__(self, ref):
        return self._branches[ref]

    def __contains__(self, ref):
        return ref in self._branches
