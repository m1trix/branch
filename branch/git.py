import sys

from subprocess import PIPE
from subprocess import run


class GitException(Exception):
    pass


class Git:
    def __init__(self):
        self._encoding = sys.stdout.encoding

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
        self.checkout('master')
        return self._call('git', 'branch', '--delete', *branches)

    def log(self):
        return self._call('git', 'log', '--all', '--oneline', '--decorate',
                          '--no-color', '--parents').split('\n')

    def _call(self, *command):
        process = run(command, stdout=PIPE)
        process.check_returncode()
        return process.stdout.decode(self._encoding)
