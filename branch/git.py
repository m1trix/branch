import sys

from subprocess import PIPE
from subprocess import run


class GitException(Exception):
    pass


class Git:
    def __init__(self):
        self._encoding = sys.stdout.encoding

    def pull(self):
        self._call('git', 'pull', '--rebase')

    def checkout(self, branch):
        self._call('git', 'checkout', branch)

    def rebase(self, branch, over):
        self._call('git', 'rebase', over, branch)

    def remote_branches(self):
        return self._call('git', 'branch', '--remote')

    def show_branch(self):
        return self._call('git', 'show-branch', '--no-color', '--topo-order')

    def log(self, fr=None, to=None):
        command = ['git', 'log', '--pretty=oneline']
        if fr is not None:
            command.append(fr)
        if to is not None:
            command[-1] += '..' + to
        return self._call(*command)

    def _call(self, *command):
        process = run(command, stdout=PIPE)
        process.check_returncode()
        return process.stdout.decode(self._encoding)
