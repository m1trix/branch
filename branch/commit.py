class Commit:
    def __init__(self, hash, parent, message):
        self._hash = hash
        self._parent = parent
        self._message = message

    @property
    def message(self):
        return self._message

    def __repr__(self):
        return '{} -> {}: {}'.format(self._hash, self._parent, self._message)

    @property
    def hash(self):
        return self._hash

    @property
    def parent(self):
        return self._parent

    def __eq__(self, other):
        return isinstance(other, Commit) and (self._hash == other._hash)
