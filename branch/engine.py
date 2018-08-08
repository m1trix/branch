import argparse

from .controller import Command
from .controller import FlagOption
from .controller import Option
from .display import Message
from .renderer import TreeRenderer


PROGRAM_HELP = 'Used to view and manage local git branches.'
PULL_COMMAND_HELP = 'Pulls all remote branches and rebases local ones over' + \
    ' their respective parrents.'
WIPE_COMMAND_HELP = 'Deletes all local alias branches.'

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
            tree = self._detect_tree(options.get('commits', False))
            if command is None:
                render_commits = options.get('commits', False)
                self._display.render(TreeRenderer().render_tree(tree))
                return

            if command == 'pull':
                self._display.render(TreeRenderer().render_tree(tree))
                self._pull_remotes(tree)
                if options.get('wipe', False):
                    tree = self._detect_tree(options.get('commits', False))
                    self._wipe(tree)
                return

            if command == 'wipe':
                self._wipe(tree)
                return

        except(KeyboardInterrupt):
            return

    def _detect_tree(self, include_commits):
        return self._git.tree(include_commits)

    def _pull_remotes(self, tree):
        self._display.message('Checking out to {}', tree.root.id)
        self._git.checkout(tree.root.id)

        self._display.message('Pulling remote {} ...', tree.root.id)
        self._git.pull()

        self._rebase_children(tree.root)

    def _rebase_children(self, root):
        self._display.message("Rebasing any '{}' child branches...", root.id)
        for branch in root.children.values():
            if branch.is_remote is False:
                self._display.message(
                    "  Rebasing '{0}' over '{1}' ...", branch.id, root.id)
                self._git.rebase(branch.id, root.id)
            self._rebase_children(branch)

    def _wipe(self, tree):
        self._display.message('Collecting alias branches ...')
        head = tree.head

        for branch in tree.branches:
            aliases = branch.aliases
            if len(aliases) is 0:
                continue

            self._display.message('Deleting: {} ...', ', '.join(aliases))
            self._git.checkout(branch.id)
            self._git.delete_branches(aliases)

        self._display.message('Success.')
        self._git.checkout(head.id)

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
