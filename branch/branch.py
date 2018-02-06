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
        self._names = names
        self._id = self._select_id(names)
        self._aliases = self._select_aliases(names)
        self._aliases.discard(self._id)
        self._children = {}
        self._commits = commits
        self._is_remote = self._has_remotes(names)
        self._is_active = False
        self._stage = None

    def _select_id(self, names):
        if len(names) == 0:
            return ''

        if 'master' in names:
            return 'master'

        for name in names:
            if not name.startswith('origin/'):
                return name

        return names[0]

    def _select_aliases(self, names):
        result = set()
        for name in names:
            if not name.startswith('origin/'):
                result.add(name)

        if len(result) == 0:
            result = names

        return set(result)

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

    @property
    def id(self):
        # Deprecated
        return self._id

    @property
    def aliases(self):
        # Deprecated
        return self._aliases

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
