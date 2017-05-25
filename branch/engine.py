import argparse

from .controller import Command
from .controller import FlagOption
from .controller import Option
from .display import Message
from .tree import TreeBuilder
from .renderer import TreeRenderer


PROGRAM_HELP = 'Used to view and manage local git branches.'
PULL_COMMAND_HELP = 'Pulls all remote branches and rebases local ones over' + \
    ' their respective parrents.'
WIPE_COMMAND_HELP = 'Deletes all local branches that are already merged' + \
    ' the master branch.'

COMMITS_OPTION_HELP = 'Displays commits in the branch tree.'
WIPE_OPTION_HELP = 'Invokes the wipe command after the pull finishes.'


class Engine:
    def __init__(self, git, display, controller):
        self._git = git
        self._display = display
        self._controller = controller

    def run(self):
        try:
            command, options = self._controller.select(self._build_commands())
            initial_tree = self._detect_tree(options.get('commits', False))
            if command is None:
                self._display.render(TreeRenderer().render_tree(initial_tree))
                return
            if command == 'pull':
                self._display.render(TreeRenderer().render_tree(initial_tree))
                self._pull_remotes(initial_tree)
                if options.get('wipe', False):
                    self._wipe()
                return
            if command == 'wipe':
                self._wipe()
                return
        except(KeyboardInterrupt):
            return

    def _detect_tree(self, include_commits):
        return TreeBuilder(self._git).include_commits(include_commits).build()

    def _pull_remotes(self, tree):
        self._display.message('Checking out to {}', tree.root.name)
        self._git.checkout(tree.root.name)

        self._display.message('Pulling remote {} ...', tree.root.name)
        self._git.pull()

        self._rebase_children(tree.root)

    def _rebase_children(self, root):
        self._display.message("Rebasing any '{}' child branches...", root.name)
        for branch in root.children.values():
            if branch.is_remote is False:
                self._display.message(
                    "  Rebasing '{0}' over '{1}' ...", branch.name, root.name)
                self._git.rebase(branch.name, root.name)
            self._rebase_children(branch)

    def _wipe(self):
        self._display.message('Detecting merged branches ...')
        branches = self._git.merged_branches()

        if len(branches) is 0:
            self._display.message('No branches detected.')
            return

        self._display.message('Detected branches: {}.', ', '.join(branches))
        self._display.message('Deleting branches ...')
        self._git.delete_branches(branches)
        self._display.message('Success.')

    def _build_commands(self):
        return [
            Command(None, PROGRAM_HELP, [
                FlagOption('commits', 'c', COMMITS_OPTION_HELP)
            ]),
            Command('pull', PULL_COMMAND_HELP, [
                FlagOption('wipe', 'w', WIPE_OPTION_HELP)
            ]),
            Command('wipe', WIPE_COMMAND_HELP)
        ]
