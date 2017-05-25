from .commit import Commit

COMMIT_FORMAT = '{0}     ({1}) {2}'
ACTIVE_BRANCH_TEMPLATE = '{0}{1} [*{2}*]'
INCATIVE_BRANCH_TEMPLATE = '{0}{1} [ {2} ]'


class TreeRenderer:

    def render_tree(self, tree):
        canvas = []
        self._render(tree.active, tree.root, canvas, 3, '', '  ')
        return canvas

    def _render(self, active, branch, canvas, context, offset, prefix):
        for i, key in enumerate(branch.children):
            child = branch.children[key]
            new_offset = offset.replace('.', ' ').replace('+', '|')
            new_offset += '   {}'.format(['+', '.'][i == 0])
            self._render(active, child, canvas, -1, new_offset, '->')

        self._render_branch(canvas, offset, prefix, active, branch)
        self._render_status(canvas, offset, branch)
        for commit in branch.commits[:context]:
            self._render_commit(canvas, offset, commit)

    def _render_branch(self, canvas, offset, prefix, active, branch):
        template = INCATIVE_BRANCH_TEMPLATE
        if branch == active:
            template = ACTIVE_BRANCH_TEMPLATE
        canvas.append(template.format(offset, prefix, branch.name))

    def _render_status(self, canvas, offset, branch):
        if branch.status[0]:
            self._render_changes(canvas, offset, 'staged changes')
        if branch.status[1]:
            self._render_changes(canvas, offset, 'unstaged changes')
        if branch.status[2]:
            self._render_changes(canvas, offset, 'untracked files')

    def _render_commit(self, canvas, offset, commit):
        self._render_changes(canvas, offset, commit.hash[:7:], commit.message)

    def _render_changes(self, canvas, offset, id, title=''):
        offset = offset.replace('.', '|').replace('+', '|')
        canvas.append(COMMIT_FORMAT.format(offset, id, title))
