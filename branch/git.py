import sys
import re
import uuid

from subprocess import PIPE
from subprocess import Popen
from subprocess import run

from .branch import Branch
from .branch import Stage
from .commit import Commit
from .tree import Tree


ENCODING = sys.stdout.encoding


class GitException(Exception):
    pass


class GitInteractor:
    def __init__(self, adapter, command):
        self._adapter = adapter
        self._command = command

    def __enter__(self):
        self._process = Popen(self._command, stdout=PIPE)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._process.terminate()

    def __iter__(self):
        return self

    def __next__(self):
        line = self._process.stdout.readline().decode(ENCODING).strip()
        if line == '':
            raise StopIteration()

        return self._adapter(line)


class Git:
    def branch(self):
        branches = [
            branch.replace('*', '').strip()
            for branch
            in self._call('git', 'branch').split('\n')
            if '*' in branch
        ]
        if len(branches) == 0:
            return 'master'
        return branches[0]

    def pull(self):
        self._call('git', 'pull', '--rebase')

    def checkout(self, branch):
        self._call('git', 'checkout', branch)

    def rebase(self, branch, over):
        self._call('git', 'rebase', over, branch)

    def cherry_pick(self, branch):
        pass

    def remote_branches(self):
        return self._call('git', 'branch', '--remote')

    def show_branch(self):
        return self._call('git', 'show-branch', '--no-color', '--topo-order')

    def status(self):
        return self._call('git', 'status', '--porcelain').split('\n')

    def merged_branches(self):
        rows = self._call('git', 'branch', '--merged', 'master') \
            .strip().split('\n')
        return [
            row.replace('*', '').strip()
            for row
            in rows
            if row.find('master') < 0
        ]

    def delete_branches(self, branches):
        return self._call('git', 'branch', '--delete', *branches)

    def tree(self, include_commits):
        reader = TreeReader(include_commits)
        with self._log() as log:
            data = reader.read(self._branches(), log)
        tree = TreeBuilder.build_tree(data, include_commits)
        tree.head.stage = self._build_stage()
        return tree

    def _log(self):
        return GitInteractor(
            lambda line: LogEntry.from_string(line),
            ['git', 'log', '--all', '--pretty=format:[C:%H][P:%P][R:%D][M:%s]']
        )

    def _branches(self):
        branches = [
            branch.replace('*', '').strip()
            for branch
            in self._call('git', 'branch').split('\n')
            if branch != ''
        ]

        for i, branch in enumerate(branches):
            if '(HEAD ' in branch:
                branches[i] = 'HEAD'

        return branches

    def _build_stage(self):
        output = self.status()
        staged = False
        unstaged = False
        untracked = False
        for row in output:
            if row.strip() == '' or row.startswith('##'):
                continue
            if row.startswith('??'):
                untracked = True
                continue
            if row[1] != ' ':
                unstaged = True
            if row[0] != ' ':
                staged = True

        return Stage(staged, unstaged, untracked)

    def _call(self, *command):
        process = run(command, stdout=PIPE)
        process.check_returncode()
        return process.stdout.decode(ENCODING)


class LogEntry:

    PATTERN = '\[C:(.*?)\]\[P:(.*?)\]\[R:(.*?)\]\[M:(.*)\]'
    HEAD_MARKER = 'HEAD -> '

    def from_string(line):
        matcher = re.match(LogEntry.PATTERN, line)
        if not matcher:
            raise Error('Unexpected log entry: {}'.format(line))
        commit = matcher.group(1)
        parents = LogEntry._build_parents(matcher.group(2))
        branches = LogEntry._build_branches(matcher.group(3))
        message = matcher.group(4)
        is_head = 'HEAD' in branches or LogEntry.HEAD_MARKER in matcher.group(3)
        return LogEntry(commit, parents, branches, message, is_head)

    def _build_parents(parents):
        return parents.split(' ') if parents != '' else []

    def _build_branches(refs):
        refs = refs.replace(LogEntry.HEAD_MARKER, '').split(', ')
        return set(ref for ref in refs if ref != '' and 'tag:' not in ref)

    def __init__(self, commit, parents, branches, message, is_head):
        self._commit = commit
        self._parents = parents
        self._branches = branches
        self._message = message
        self._is_head = is_head

    @property
    def commit(self):
        return self._commit

    @property
    def parents(self):
        return self._parents

    @property
    def branches(self):
        return self._branches

    @property
    def message(self):
        return self._message

    @property
    def is_head(self):
        return self._is_head

    def to_commit(self):
        return Commit(self._commit, self._message)


class TreeData:

    def __init__(self, tree, branches, commits, head, root):
        self._tree = tree
        self._branches = branches
        self._commits = commits
        self._head = head
        self._root = root

    @property
    def branches(self):
        return self._branches

    @property
    def head(self):
        return self._head

    @property
    def root(self):
        return self._root

    def commit(self, commit):
        return self._commits.get(commit)

    def children(self, commit):
        return self._tree.get(commit, [])


class TreeReader:

    def __init__(self, _should_include_commits):
        self._should_include_commits = _should_include_commits

    def read(self, branches, log):
        unvisited_branches = set(branches)
        tree, refs, commits, head, root = {}, {}, {}, None, None
        for entry in log:
            for parent in entry.parents:
                tree[parent] = tree.get(parent, []) + [entry.commit]

            if self._should_include_commits:
                commits[entry.commit] = entry.to_commit()

            if entry.is_head:
                head = entry.commit

            branches = [
                branch
                for branch
                in entry.branches
                if branch in unvisited_branches]
            if len(branches) > 0:
                unvisited_branches.difference_update(set(branches))
                refs[entry.commit] = branches

            if len(unvisited_branches) is 0 \
                    and self._is_root(entry.commit, refs, tree):
                root = entry.commit
                break
        return TreeData(tree, refs, commits, head, root)

    def _is_root(self, commit, refs, tree):
        return all(self._has_path(commit, ref, tree) for ref in refs)

    def _has_path(self, commit, ref, tree):
        if commit == ref:
            return True

        if commit not in tree:
            return False

        return any(self._has_path(point, ref, tree) for point in tree[commit])


class TreeBuilder:

    def build_tree(data, should_include_commits):
        branches = TreeBuilder(
            data, should_include_commits
        )._build_branches(data.root, None, {})

        branches[data.head].is_active = True
        return Tree(branches, data.root)

    def __init__(self, data, should_include_commits):
        self._data = data
        self._should_include_commits = should_include_commits

    def _build_branches(self, root, parent, visited):
        commits = []
        for commit in self._walk_tree(root):
            if self._should_include_commits:
                commits.insert(0, self._data.commit(commit))

            if not self._is_branch_point(commit):
                continue

            branch = self._get_branch(commit, commits, visited)
            visited[commit] = branch
            if parent is not None:
                parent.children[branch.ref] = branch

            branches = {commit: branch}
            for child in self._data.children(commit):
                branches.update(self._build_branches(child, branch, visited))

            return branches
        return {}

    def _walk_tree(self, root):
        commit = root
        while commit is not None:
            yield commit
            children = self._data.children(commit)
            commit = children[0] if len(children) > 0 else None

    def _is_branch_point(self, commit):
        children = self._data.children(commit)
        return commit in self._data.branches or len(children) > 1

    def _get_branch(self, commit, commits, visited):
        if commit not in visited:
            return Branch(commit, self._data.branches.get(commit, []), commits)

        branch = visited[commit]
        branch.commits.extend(c for c in commits if c not in branch.commits)
        return branch
