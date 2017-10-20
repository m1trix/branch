import re

from .branch import Branch
from .commit import Commit

COMMIT_PATTERN = '([a-z0-9]+)\s+([a-z0-9]+)\s+(?:\((.+?)\))?\s*(.*)'
INITIAL_STATUS = [False, False, False]

STAGED_FILES = 0
UNSTAGED_FILES = 1
UNTRACKED_FILES = 2


class Tree:
    def __init__(self, branches, root='master'):
        self._branches = branches
        self._active = self._find_active(branches.values())
        self._root = branches[root]

    def _find_active(self, branches):
        for branch in branches:
            if branch.is_active:
                return branch

    def __getitem__(self, name):
        return self._branches[name]

    @property
    def root(self):
        return self._root

    @property
    def active(self):
        return self._active

    @property
    def branches(self):
        return self._branches.values()


class TreeBuilder:
    def __init__(self, git):
        self._git = git

    def build(self):
        branches = {}
        queue = []
        branch = None

        for line in self._git.log():
            matcher = re.match(COMMIT_PATTERN, line.strip())
            if not matcher:
                continue

            commit = Commit(
                matcher.group(1), matcher.group(2), matcher.group(4))
            if matcher.group(3):
                entries = matcher.group(3).split(', ')
                names = []
                is_active = False
                display_name = None
                for name in entries:
                    name = name.strip()
                    if name.startswith('tag: '):
                        continue

                    if name.startswith('HEAD -> '):
                        name = name[8:]
                        display_name = name
                        is_active = True

                    names.append(name)
                if len(names) > 0:
                    branch = Branch(names, active=is_active, name=display_name)
                    branches[branch.id] = branch
                    new_queue = []
                    for child in queue:
                        if child.commits[-1].parent == commit.hash:
                            child.parent = branch
                            branch.children[child.id] = child

                        else:
                            new_queue.append(child)

                    queue = new_queue
                    queue.append(branch)

            branch.commits.append(commit)

        root = self._select_root(queue)
        for branch in queue:
            if branch.id != root.id:
                branch.parent = root
        return Tree(branches, root=root.id)

    def _select_root(self, queue):
        preferred = [branch for branch in queue if branch.id == 'master']
        if len(preferred) > 0:
            return preferred[0]
        return queue[0]
