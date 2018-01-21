from .commit import Commit

COMMIT_FORMAT = '{0}     ({1}) {2}'
ACTIVE_BRANCH_TEMPLATE = '{} [*{}*]'
INCATIVE_BRANCH_TEMPLATE = '{} [ {} ]'
BRANCH_ALIAS_TEMPLATE = '[ {} ]'
LINE_LENGTH = 80


class TreeRenderer:

    def render_tree(self, tree):
        canvas = []
        self._render(tree.root, canvas, '', '  ')
        return canvas

    def _render(self, branch, canvas, offset, prefix):
        for i, key in enumerate(branch.children):
            child = branch.children[key]
            new_offset = offset.replace('.', ' ').replace('+', '|')
            new_offset += '   {}'.format(['+', '.'][i == 0])
            self._render(child, canvas, new_offset, '->')

        self._render_branch(canvas, offset + prefix, branch)
        self._render_status(canvas, offset, branch)
        for commit in branch.commits:
            self._render_commit(canvas, offset, commit)

    def _render_branch(self, canvas, prefix, branch):
        parts = [self._render_branch_name(prefix, branch)]
        aliases = sorted(branch.aliases, key=lambda s: len(s))
        for alias in aliases:
            parts.append(BRANCH_ALIAS_TEMPLATE.format(alias))
        result = ''.join(parts)
        extra = 0
        while len(result) > LINE_LENGTH:
            parts.pop()
            extra += 1
            result = ''.join(parts) + '[ +{} more ]'.format(extra)
        canvas.append(result)

    def _render_branch_name(self, prefix, branch):
        template = ACTIVE_BRANCH_TEMPLATE \
            if branch.is_active else INCATIVE_BRANCH_TEMPLATE

        result = template.format(prefix, branch.id)
        extra = len(result) - LINE_LENGTH
        if extra > 0:
            result = template.format(prefix, branch.id[:-extra - 3] + '...')

        return result

    def _render_status(self, canvas, offset, branch):
        if branch.status[0]:
            self._render_changes(canvas, offset, 'staged changes')
        if branch.status[1]:
            self._render_changes(canvas, offset, 'unstaged changes')
        if branch.status[2]:
            self._render_changes(canvas, offset, 'untracked files')

    def _render_commit(self, canvas, offset, commit):
        self._render_changes(canvas, offset, commit.id[:7:], commit.message)

    def _render_changes(self, canvas, offset, id, title=''):
        offset = offset.replace('.', '|').replace('+', '|')
        canvas.append(COMMIT_FORMAT.format(offset, id, title))
