class Branch:
    def __init__(self, name, parent=None, commits=[]):
        self._name = name
        self._parent = parent
        self._children = {}
        self._commits = commits

    def __eq__(self, other):
        return isinstance(other, Branch) and (self._name == other._name)

    @property
    def name(self):
        return self._name

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

    @commits.setter
    def commits(self, commits):
        self._commits = commits

    def is_parent_of(self, branch):
        if not branch or not branch.parent:
            return False
        if self == branch.parent:
            return True
        return self.is_parent_of(branch.parent)
