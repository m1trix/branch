class TreeRenderer:
    COMMIT_FORMAT = '{0}     {1} {2}'

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
        for i, commit in enumerate(branch.commits):
            if i == context:
                break
            canvas.append(self._render_commit(commit, offset))

    def _render_commit(self, commit, offset):
        commit_offset = offset.replace('.', '|').replace('+', '|')
        return TreeRenderer.COMMIT_FORMAT.format(
            commit_offset, commit.hash[:7:], commit.message)
