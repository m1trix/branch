import argparse

from .controller import Command
from .controller import FlagOption
from .controller import Option
from .tree import TreeBuilder
from .renderer import TreeRenderer


class Engine:
    def __init__(self, git, display, controller):
        self._git = git
        self._display = display
        self._controller = controller

    def run(self):
        command, options = self._controller.select(self._build_commands())
        self._tree = TreeBuilder(self._git) \
            .include_commits(options.get('commits', False)) \
            .build()
        if command is None or command == 'full':
            self._display.render(TreeRenderer().render_tree(self._tree))

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
