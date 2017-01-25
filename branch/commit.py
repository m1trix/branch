class Commit:
    def __init__(self, hash, message):
        self._hash = hash
        self._message = message

    @property
    def message(self):
        return self._message

    @property
    def hash(self):
        return self._hash

    def __eq__(self, other):
        return isinstance(other, Commit) and (self._hash == other._hash)
