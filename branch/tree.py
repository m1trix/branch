import re

from .branch import Branch
from .commit import Commit

COMMIT_PATTERN = '([a-z0-9]+)\s+([a-z0-9]+)\s+(\(.+?\))?\s*(.*)'
INITIAL_STATUS = [False, False, False]

STAGED_FILES = 0
UNSTAGED_FILES = 1
UNTRACKED_FILES = 2


class Tree:
    def __init__(self, branches, root='master', active='master'):
        self._branches = branches
        self._active = self._find_active(branches.values(), active)
        self._root = branches[root]
        self._remotes = []

    def _find_active(self, branches, active):
        for branch in branches:
            if active in branch.names:
                return branch

    def __getitem__(self, name):
        return self._branches[name]

    @property
    def remotes(self):
        return self._remotes

    @property
    def root(self):
        return self._root

    @property
    def active(self):
        return self._active


class TreeBuilder:
    def __init__(self, git):
        self._git = git

    def build(self):
        branches = {}
        queue = []
        active = 'master'
        branch = None

        for line in self._git.log():
            matcher = re.match(COMMIT_PATTERN, line.strip())
            if not matcher:
                continue

            commit = Commit(
                matcher.group(1), matcher.group(2), matcher.group(4))
            if matcher.group(3):
                entries = matcher.group(3)[1:-1].split(', ')
                names = []
                for name in entries:
                    name = name.strip()
                    if name.startswith('tag: '):
                        continue

                    if name.startswith('HEAD -> '):
                        name = name[8:]
                        active = name

                    names.append(name)
                branch = Branch(names)
                branches[branch.name] = branch
                new_queue = []
                for child in queue:
                    if child.commits[-1].parent == commit.hash:
                        child.parent = branch
                        branch.children[child.name] = child

                    else:
                        new_queue.append(child)

                queue = new_queue
                queue.append(branch)

            branch.commits.append(commit)

        return Tree(branches, active=active, root=queue[0].name)
