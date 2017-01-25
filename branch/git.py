import subprocess
import sys


class Git:
    def __init__(self):
        self._encoding = sys.stdout.encoding

    def remote_branches(self):
        return subprocess.check_output([
            'git',
            'branch',
            '--remote'
        ]).decode(self._encoding)

    def show_branch(self):
        return subprocess.check_output([
            'git',
            'show-branch',
            '--no-color',
            '--topo-order'
        ]).decode(self._encoding)

    def log(self, fr=None, to=None):
        command = ['git', 'log', '--pretty=oneline']
        if fr is not None:
            command.append(fr)
        if to is not None:
            command[-1] += '..' + to
        return subprocess.check_output(command).decode(self._encoding)
