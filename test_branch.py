import unittest
from branch import *


class GitMock:
    def prepare_show_branch(self, result):
        self._prepared_show_branch_result = result

    def show_branch(self):
        return self._prepared_show_branch_result


class ProgramMock(Program):
    def __init__(self, git):
        Program.__init__(self)
        self._git = git


class ProgramTest(unittest.TestCase):
    def setUp(self):
        self.git = GitMock()
        self.program = ProgramMock(self.git)

    def test_build_branches(self):
        result = self.program._build_branches('\n'.join([
            '! [master] Initial commit',
            ' ! [branch1] Commit 1',
            '  ! [branch3] Commit 2',
            '   * [branch2] Commit 3',
            '    ! [branch4] Commit 4'
        ]))

        self.assertEqual(result[0].name, 'master')
        self.assertEqual(result[0].description, 'Initial commit')

        self.assertEqual(result[1].name, 'branch1')
        self.assertEqual(result[1].description, 'Commit 1')

        self.assertEqual(result[2].name, 'branch3')
        self.assertEqual(result[2].description, 'Commit 2')

        self.assertEqual(result[3].name, 'branch2')
        self.assertEqual(result[3].description, 'Commit 3')

        self.assertEqual(result[4].name, 'branch4')
        self.assertEqual(result[4].description, 'Commit 4')

        result = self.program._build_branches('[master] Initial commit')
        self.assertEqual(result, [Branch('master')])

    def test_build_branches__when_no_branches_exist(self):
        result = self.program._build_branches('')
        self.assertEqual([], result)

    def test_build_branches__when_single_branch_exist(self):
        result = self.program._build_branches('[master] Initial commit')
        self.assertEqual(result, [Branch('master')])

    def test_calculate_tree__when_branch_tree_is_simple(self):
        # o [master]
        # |   o [branch1]
        #  \ /
        #   o
        #   |
        #   o [branch2]

        branches = [
            Branch('master'),
            Branch('branch1'),
            Branch('branch2')
        ]

        self.program._tree = {
            'master': Branch('master'),
            'branch1': Branch('branch1'),
            'branch2': Branch('branch2')
        }

        self.program._calculate_tree(branches, '\n'.join([
            '*   [master]',
            ' +  [branch1]',
            '*+  [master^]',
            '*++ [branch2]'
        ]))

        # branch2 is parent of master
        self.assertEqual(branches[0].parent, branches[2])
        # master is parent of branch1
        self.assertEqual(branches[1].parent, branches[0])
        # branch2 has no parent
        self.assertEqual(branches[2].parent, None)

    def test_calculate_tree__when_branch_tree_is_complex(self):
        #     o [merge2]
        #    / \
        #   o [merge1]
        #  /  \ \
        # o [master]
        # |   o [branch1]
        #  \ /  /
        #   o  o [branch3]
        #   | /
        #   o [branch2]

        branches = [
            Branch('branch1'),
            Branch('branch2'),
            Branch('branch3'),
            Branch('master'),
            Branch('merge1'),
            Branch('merge2')
        ]

        self.program._tree = {
            'master': Branch('master'),
            'branch1': Branch('branch1'),
            'branch2': Branch('branch2'),
            'branch3': Branch('branch3'),
            'merge1': Branch('merge1'),
            'merge2': Branch('merge2')
        }

        self.program._calculate_tree(branches, '\n'.join([
            '     - [merge2] merge2',
            '  +  * [branch3] 5',
            '    -- [merge1] merge1',
            '+   +* [branch1] 4',
            '   ++* [master] 3',
            '+  ++* [branch1^] 2',
            '+++++* [branch2] 1'
        ]))

        # branch2 is parent of branch1
        self.assertEqual(branches[0].parent, branches[1])
        # None is parent of branch2
        self.assertEqual(branches[1].parent, None)
        # branch2 is parent of branch3
        self.assertEqual(branches[2].parent, branches[1])
        # branch1 is parent of master
        self.assertEqual(branches[3].parent, branches[0])
        # branch1 is parent of merge1
        self.assertEqual(branches[4].parent, branches[0])
        # branch3 is parent of merge2
        self.assertEqual(branches[5].parent, branches[2])

#
#   M A I N
#

if __name__ == '__main__':
    unittest.main()
