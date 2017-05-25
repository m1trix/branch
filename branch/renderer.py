from .commit import Commit


class TreeRenderer:
    COMMIT_FORMAT = '{0}     ({1}) {2}'

    def render_tree(self, tree):
        canvas = []
        self._render(tree.root, canvas, 3, '', '  ')
        return canvas

    def _render(self, branch, canvas, context, offset, prefix):
        for i, key in enumerate(branch.children):
            child = branch.children[key]
            new_offset = offset.replace('.', ' ').replace('+', '|')
            new_offset += '   {}'.format(['+', '.'][i == 0])
            self._render(child, canvas, -1, new_offset, '->')
        canvas.append("{0}{1} [{2}]".format(offset, prefix, branch.name))
        if branch.status[0]:
            canvas.append(self._render_changes(offset, 'staged changes'))
        if branch.status[1]:
            canvas.append(self._render_changes(offset, 'unstaged changes'))
        if branch.status[2]:
            canvas.append(self._render_changes(offset, 'untracked files'))
        for i, commit in enumerate(branch.commits):
            if i == context:
                break
            canvas.append(self._render_commit(offset, commit))

    def _render_commit(self, offset, commit):
        return self._render_changes(offset, commit.hash[:7:], commit.message)

    def _render_changes(self, offset, id, title=''):
        offset = offset.replace('.', '|').replace('+', '|')
        return TreeRenderer.COMMIT_FORMAT.format(offset, id, title)
