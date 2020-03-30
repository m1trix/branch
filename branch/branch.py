class Stage:

    def __init__(self, staged, unstaged, untracked):
        self._staged = staged
        self._unstaged = unstaged
        self._untracked = untracked

    @property
    def staged(self):
        return self._staged

    @property
    def unstaged(self):
        return self._unstaged

    @property
    def untracked(self):
        return self._untracked


class Branch:
    def __init__(self, ref, names, commits):
        self._ref = ref
        self._names = self._select_names(names)
        self._children = {}
        self._commits = commits
        self._is_remote = self._has_remotes(names)
        self._is_active = False
        self._stage = None

    def _select_names(self, names):
        result = [name for name in names if not name.startswith('origin/')]
        return result or names

    def _has_remotes(self, names):
        for name in names:
            if name.startswith('origin/'):
                return True
        return False

    @property
    def ref(self):
        return self._ref

    @property
    def names(self):
        return self._names

    @names.setter
    def names(self, names):
        self._names = names

    @property
    def is_remote(self):
        return self._is_remote

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, is_active):
        self._is_active = is_active

    @property
    def children(self):
        return self._children

    @property
    def commits(self):
        return self._commits

    @commits.setter
    def commits(self, commits):
        self._commits = commits

    @property
    def stage(self):
        return self._stage

    @stage.setter
    def stage(self, stage):
        self._stage = stage

    @property
    def id(self):
        return self._names[0] if self._names else ''
    
    @property
    def aliases(self):
        return self._names[1:]
    
    def __repr__(self):
        return self._names[0] if self._names else '<?>'
