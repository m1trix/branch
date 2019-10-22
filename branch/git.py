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
from .utils import find, contains, map


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
        branches, trees, head, master, root = {}, {}, None, None, None
        context = 3
        with self._log() as log:
            for node in log:
                if node.branches:
                    branch = Branch(node.ref, node.branches, [])
                    if node.ref in branches:
                        branch = branches[node.ref]
                        branch.names = node.branches
                    elif node.ref in trees:
                        branch.children[trees[node.ref].ref] = trees[node.ref]
                    branches[node.ref] = branch
                    trees[node.ref] = branch
                    if include_commits:
                        branch.commits.append(node.to_commit())

                for parent in node.parents:
                    if parent in branches:
                        branches[parent].children[trees[node.ref].ref] = trees[node.ref]
                    elif parent in trees:
                        branch = Branch(parent, [], [])
                        branch.children[node.ref] = trees[node.ref]
                        branch.children[parent] = trees[parent]
                        branches[parent] = branch
                    trees[parent] = trees[node.ref]

                del trees[node.ref]

                if node.is_active:
                    head = node.ref

                if 'master' in node.branches:
                    master = node.ref

                if len(trees) == 1:
                    root = next(iter(trees))

                if head and master and root:
                    break

        return Tree(head, root, branches.values())

    def _log(self):
        return GitInteractor(
            lambda line: TreeNode.from_string(line),
            ['git', 'log', '--all', '--pretty=format:[C:%H][P:%P][R:%D][M:%s]']
        )

    def _branches(self):
        return (
            branch.replace('*', '').strip()
            for branch
            in self._call('git', 'branch').split('\n')
            if branch != '' and '(HEAD detached ' not in branch
        )

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

class TreeNode:

    PATTERN = '\\[C:(.*?)\\]\\[P:(.*?)\\]\[R:(.*?)\\]\\[M:(.*)\\]'
    HEAD_MARKER = 'HEAD -> '

    @staticmethod
    def from_string(line):
        matcher = re.match(TreeNode.PATTERN, line)
        if not matcher:
            raise Exception('Unexpected log entry: {}'.format(line))
        ref = matcher.group(1)
        parents = TreeNode._build_parents(matcher.group(2))
        branches = TreeNode._build_branches(matcher.group(3))
        message = matcher.group(4)
        is_active = contains(branches, TreeNode._is_head)
        branches = map(branches, lambda b: b.replace(TreeNode.HEAD_MARKER, ''))

        return TreeNode(ref, branches, parents, message, is_active)

    @staticmethod
    def _build_parents(parents):
        return parents.split(' ') if parents != '' else []

    @staticmethod
    def _build_branches(refs):
        return [
            ref
            for ref
            in refs.split(', ')
            if ref != '' and 'tag:' not in ref
        ]

    @staticmethod
    def _is_head(branch):
        return branch.startswith(TreeNode.HEAD_MARKER)

    def __init__(self, ref, branches, parents, message, is_active):
        self._ref = ref
        self._branches = branches
        self._parents = parents
        self._message = message
        self._is_active = is_active

    @property
    def ref(self):
        return self._ref

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
    def is_active(self):
        return self._is_active

    def to_commit(self):
        return Commit(self._ref, self._message)
