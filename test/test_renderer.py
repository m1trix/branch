from branch.renderer import *
from branch.tree import *
from branch.branch import *
from branch.commit import *

from collections import OrderedDict
import unittest


class RendererTest(unittest.TestCase):
    def test_rendering_of_single_active_branch(self):
        result = TreeRenderer().render_tree(Tree({
            'master': Branch(['master'], active=True)
        }))

        self.assertEqual(result, [
            '╭●  [master]'
        ])

    def test_rendering_of_single_non_active_branch(self):
        result = TreeRenderer().render_tree(Tree({
            'master': Branch(['master'], active=False)
        }))

        self.assertEqual(result, [
            '╭○  [master]'
        ])

    def test_rendering_of_multiple_branches(self):
        master = Branch(['master'], active=True)
        master.children['branch1'] = Branch(['branch1'], parent=master)
        master.children['branch2'] = Branch(['branch2'], parent=master)

        tree = Tree({
            'master': master,
            'branch1': master.children['branch1'],
            'branch2': master.children['branch2']
        })

        self.assertEqual(TreeRenderer().render_tree(tree), [
            '  ╭○  [branch1]',
            '  ├○  [branch2]',
            '╭●╯ [master]'
        ])

    def test_rendering_of_deeper_heirarchy(self):
        master = Branch(['master'])
        branch1 = Branch(['branch1'], parent=master)
        branch2 = Branch(['branch2'], parent=master)
        branch3 = Branch(['branch3'], parent=master)
        branch4 = Branch(['branch4'], parent=branch1)
        branch5 = Branch(['branch5'], parent=branch1)
        branch6 = Branch(['branch6'], parent=branch2)
        branch7 = Branch(['branch7'], parent=branch2, active=True)
        branch8 = Branch(['branch8'], parent=branch2)
        branch9 = Branch(['branch9'], parent=branch6)

        master.children['branch1'] = branch1
        master.children['branch2'] = branch2
        master.children['branch3'] = branch3

        branch1.children['branch4'] = branch4
        branch1.children['branch5'] = branch5

        branch2.children['branch6'] = branch6
        branch2.children['branch7'] = branch7
        branch2.children['branch8'] = branch8

        branch6.children['branch9'] = branch9

        tree = Tree({
            'master': master,
            'branch1': branch1,
            'branch2': branch2,
            'branch3': branch3,
            'branch4': branch4,
            'branch5': branch5,
            'branch6': branch6,
            'branch7': branch7,
            'branch8': branch8
        })

        self.assertEqual(TreeRenderer().render_tree(tree), [
            '    ╭○  [branch4]',
            '    ├○  [branch5]',
            '  ╭○╯ [branch1]',
            '  │   ╭○  [branch9]',
            '  │ ╭○╯ [branch6]',
            '  │ ├●  [branch7]',
            '  │ ├○  [branch8]',
            '  ├○╯ [branch2]',
            '  ├○  [branch3]',
            '╭○╯ [master]'
        ])

    def test_rendering_of_deeper_heirarchy_with_commits(self):
        master = Branch(['master'], commits=[
            Commit('0000001', None, 'Commit 1'),
            Commit('0000002', None, 'Commit 2'),
            Commit('0000003', None, 'Commit 3')
        ])
        branch1 = Branch(['branch1'], parent=master, commits=[
            Commit('0000004', None, 'Commit 4')
        ])
        branch2 = Branch(['branch2'], parent=master, active=True, commits=[
            Commit('0000005', None, 'Commit 5')
        ])
        branch3 = Branch(['branch3'], parent=branch2, commits=[
            Commit('0000006', None, 'Commit 6'),
            Commit('0000007', None, 'Commit 7')
        ])
        branch4 = Branch(['branch4'], parent=branch2, commits=[
            Commit('0000008', None, 'Commit 8')
        ])
        branch5 = Branch(['branch5'], parent=branch3, commits=[
            Commit('0000009', None, 'Commit 9'),
            Commit('0000010', None, 'Commit 10'),
            Commit('0000011', None, 'Commit 11'),
            Commit('0000012', None, 'Commit 12')
        ])

        master.children['branch1'] = branch1
        master.children['branch2'] = branch2
        branch2.children['branch3'] = branch3
        branch2.children['branch4'] = branch4
        branch3.children['branch5'] = branch5

        tree = Tree({
            'master': master,
            'branch1': branch1,
            'branch2': branch2,
            'branch3': branch3,
            'branch4': branch4,
            'branch5': branch5
        })

        self.assertEqual(TreeRenderer().render_tree(tree, commits=True), [
            '  ╭○  [branch1]',
            '  │   ‣ 0000004 Commit 4',
            '  │   ╭○  [branch5]',
            '  │   │   ‣ 0000009 Commit 9',
            '  │   │   ‣ 0000010 Commit 10',
            '  │   │   ‣ 0000011 Commit 11',
            '  │   │   ‣ 0000012 Commit 12',
            '  │ ╭○╯ [branch3]',
            '  │ │   ‣ 0000006 Commit 6',
            '  │ │   ‣ 0000007 Commit 7',
            '  │ ├○  [branch4]',
            '  │ │   ‣ 0000008 Commit 8',
            '  ├●╯ [branch2]',
            '  │   ‣ 0000005 Commit 5',
            '╭○╯ [master]',
            '│   ‣ 0000001 Commit 1',
            '│   ‣ 0000002 Commit 2',
            '│   ‣ 0000003 Commit 3'
        ])
