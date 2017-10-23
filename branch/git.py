import sys

from subprocess import PIPE
from subprocess import Popen
from subprocess import run


ENCODING = sys.stdout.encoding


class GitException(Exception):
    pass


class GitInteractor:
    def __init__(self, *command):
        self._command = command

    def __enter__(self):
        self._process = Popen(self._command, stdout=PIPE)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._process.terminate()

    def __iter__(self):
        return self

    def __next__(self):
        line = self._process.stdout.readline().decode(ENCODING)[:-1]
        if line == '':
            raise StopIteration()

        return line


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

    def log(self):
        return GitInteractor(
            'git',
            'log',
            '--all',
            '--oneline',
            '--decorate',
            '--no-color',
            '--parents')

    def _call(self, *command):
        process = run(command, stdout=PIPE)
        process.check_returncode()
        return process.stdout.decode(ENCODING)
