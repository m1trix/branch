class Commit:
    def __init__(self, id, message):
        self._id = id
        self._message = message

    @property
    def message(self):
        return self._message

    def __repr__(self):
        return '{}: {}'.format(self._id, self._message)

    @property
    def id(self):
        return self._id

    def __eq__(self, other):
        return isinstance(other, Commit) and (self._hash == other._hash)
