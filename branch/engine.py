import argparse

from .controller import Command
from .controller import FlagOption
from .controller import Option
from .display import Message
from .tree import TreeBuilder
from .renderer import TreeRenderer


class Engine:
    def __init__(self, git, display, controller):
        self._git = git
        self._display = display
        self._controller = controller

    def run(self):
        try:
            command, options = self._controller.select(self._build_commands())
            initial_tree = self._detect_tree(options.get('commits', False))
            if command is None or command == 'full':
                self._display.render(TreeRenderer().render_tree(initial_tree))
                return
            if command == 'pull':
                self._display.render(TreeRenderer().render_tree(initial_tree))
                self._pull_remotes(initial_tree)
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
        self._display.message('Rebasing {} child branches...', root.name)
        for branch in root.children.values():
            if branch.is_remote is False:
                self._display.message(
                    '  Rebasing {0} over {1}...', branch.name, root.name)
                self._git.rebase(branch.name, root.name)
            self._rebase_children(branch)

    def _build_commands(self):
        return [
            Command(None, 'manages local git branches', [
                FlagOption('commits', 'c', 'displays commit information')
            ]),
            Command('full', 'displays the whole branch tree', [
                FlagOption('commits', 'c', 'displays commit information')
            ]),
            Command('pull', 'pulls all remote branches and rebases local ones')
        ]
