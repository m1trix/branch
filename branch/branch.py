class Branch:
    def __init__(self, names, parent=None, commits=None, active=False):
        self._name = self._select_name(names)
        self._aliases = self._select_aliases(names)
        self._aliases.remove(self._name)
        self._parent = parent
        self._children = {}
        self._status = [False, False, False]
        self._commits = commits or []
        self._is_remote = self._has_remotes(names)
        self._is_active = active

    def _select_name(self, names):
        for name in names:
            if name == 'master':
                return 'master'

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

        return result

    def _has_remotes(self, names):
        for name in names:
            if name.startswith('origin/'):
                return True
        return False

    @property
    def name(self):
        return self._name

    @property
    def aliases(self):
        return self._aliases

    @property
    def is_remote(self):
        return self._is_remote

    @property
    def is_active(self):
        return self._is_active

    @property
    def children(self):
        return self._children

    @property
    def parent(self):
        return self._parent

    @property
    def has_parent(self):
        return self._parent is not None

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def commits(self):
        return self._commits

    @property
    def status(self):
        return self._status

    @commits.setter
    def commits(self, commits):
        self._commits = commits

    @status.setter
    def status(self, status):
        self._status = status

    def is_parent_of(self, branch):
        if not branch or not branch.parent:
            return False
        if self == branch.parent:
            return True
        return self.is_parent_of(branch.parent)
