from .commit import Commit

COMMIT_FORMAT = '{}│     ({}) {}'
LINE_LENGTH = 80

CONTEXT = {
    'master': 3
}

ACTIVE_BULLET = '●'
INACTIVE_BULLET = '○'


class TreeRenderer:

    def render_tree(self, tree, commits=False):
        canvas = []
        self._render(canvas, tree.root, commits=commits)
        return canvas

    def _render(self, canvas, branch, first=True, prefix='', commits=False):
        index = 0
        for key, child in branch.children.items():
            pr = first and '  ' or '│ '
            self._render(canvas, child, index == 0, prefix + pr, commits)
            index = 1

        p = first and '╭' or '├'
        bullet = branch.is_active and ACTIVE_BULLET or INACTIVE_BULLET
        name = branch.name
        pipe = branch.children and '╯' or ' '
        canvas.append('{}{}{}{} [{}]'.format(prefix, p, bullet, pipe, name))

        if commits:
            for commit in branch.commits:
                canvas.append('{}│   ‣ {} {}'.format(prefix, commit.hash, commit.message))
