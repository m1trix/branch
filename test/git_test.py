import unittest
from branch.commit import Commit
from branch.git import Git
from branch.git import LogEntry
from branch.git import TreeBuilder
from branch.git import TreeData
from branch.git import TreeReader


class LogEntryTest(unittest.TestCase):

    def assertEntry(self, entry, commit, parents, branches, message):
        self.assertEqual(entry.commit, commit)
        self.assertEqual(entry.parents, parents)
        self.assertEqual(entry.branches, set(branches))
        self.assertEqual(entry.message, message)

    def test_with_no_parents_and_no_refs(self):
        entry = LogEntry.from_string(
            '[C:a85b5b2][P:][R:][M:That is the message]')
        self.assertEntry(entry, 'a85b5b2', [], [], 'That is the message')

    def test_with_single_parent(self):
        entry = LogEntry.from_string('[C:a85b5b2][P:9abcb6b][R:][M:message]')
        self.assertEntry(entry, 'a85b5b2', ['9abcb6b'], [], 'message')

    def test_with_multiple_parents(self):
        entry = LogEntry.from_string(
            '[C:a85b5b2][P:9abcb6b 27d6e22][R:][M:message]')
        self.assertEntry(entry, 'a85b5b2', ['9abcb6b', '27d6e22'], [], 'message')

    def test_with_single_branch_ref(self):
        entry = LogEntry.from_string(
            '[C:a85b5b2][P:9abcb6b][R:master][M:message]')
        self.assertEntry(entry, 'a85b5b2', ['9abcb6b'], ['master'], 'message')

    def test_with_mutliple_branch_refs(self):
        entry = LogEntry.from_string(
            '[C:a85b5b2][P:9abcb6b][R:master, branch1][M:message]')
        self.assertEntry(
            entry, 'a85b5b2', ['9abcb6b'], ['master', 'branch1'], 'message')

    def test_with_branches_and_tags(self):
        entry = LogEntry.from_string(
            '[C:a85b5b2][P:9abcb6b][R:master, tag: v1][M:message]')
        self.assertEntry(entry, 'a85b5b2', ['9abcb6b'], ['master'], 'message')

    def test_with_head(self):
        entry = LogEntry.from_string(
            '[C:a85b5b2][P:9abcb6b]' +
            '[R:branch1, HEAD -> master, tag: v1][M:message]')
        self.assertEntry(
            entry, 'a85b5b2', ['9abcb6b'], ['master', 'branch1'], 'message')


class TestTreeReader(unittest.TestCase):

    def assertTreeData(self, data=None, branches={},
                       head=None, root=None, tree={}):
        self.assertEqual(data.branches, branches)
        self.assertEqual(data.head, head)
        self.assertEqual(data.root, root)
        self.assertEqual(data._tree.keys(), tree.keys())
        for key in tree.keys():
            self.assertEqual(set(data._tree[key]), set(tree[key]))

    def log_entry(self, hash, parents, message, branches=[]):
        return LogEntry(hash, parents, branches[:], message)

    def test_single_branch_and_single_commit(self):
        data = TreeReader(False).read('210d73e', ['master'], [
            self.log_entry('210d73e', [], 'Commit message', branches=['master'])
        ])

        self.assertTreeData(
            data=data,
            branches={
                '210d73e': ['master']
            },
            head='210d73e',
            root='210d73e',
            tree={})

    def test_multple_branches_with_multiple_commits(self):
        data = TreeReader(False).read('d43991b', ['fixes', 'master', 'feature'], [
            self.log_entry(
                'd43991b', ['e5b122a'], 'Fixed a third bug',
                branches=['fixes']),
            self.log_entry(
                'e5b122a', ['7a1113e'], 'Fixed another bug'),
            self.log_entry(
                '7a1113e', ['b299199'], 'Fixed a bug'),
            self.log_entry(
                '96a5deb', ['7f55dee'], 'Fixed a bug in the features',
                branches=['feature']),
            self.log_entry(
                '7f55dee', ['b299199'], 'Added new features'),
            self.log_entry(
                'b299199', ['2248903'], 'Some message',
                branches=['master']),
            self.log_entry(
                '2248903', [], 'Commit message')
        ])

        self.assertTreeData(
            data=data,
            branches={
                'd43991b': ['fixes'],
                'b299199': ['master'],
                '96a5deb': ['feature']
            },
            head='d43991b',
            root='b299199',
            tree={
                '2248903': ['b299199'],
                'b299199': ['7f55dee', '7a1113e'],
                '7f55dee': ['96a5deb'],
                '7a1113e': ['e5b122a'],
                'e5b122a': ['d43991b']
            })

    def test_unnamed_branch_points(self):
        data = TreeReader(False).read('b7c3625', ['fixes', 'master', 'feature'], [
            self.log_entry('de5005c', ['9d98707'], 'Fixed a third bug',
                           branches=['fixes']),
            self.log_entry('9d98707', ['e6770b0'], 'Fixed another bug'),
            self.log_entry('b7c3625', ['b299199'], 'Major release',
                           branches=['master']),
            self.log_entry('18dcc52', ['e6770b0'], 'Fixed a bug in feature A',
                           branches=['feature']),
            self.log_entry('7f55dee', ['b299199'], 'Added new features'),
            self.log_entry('e6770b0', ['7f55dee'], 'Fixed a bug'),
            self.log_entry('b299199', ['2248903'], 'Some message')
        ])

        self.assertTreeData(
            data=data,
            branches={
                'de5005c': ['fixes'],
                'b7c3625': ['master'],
                '18dcc52': ['feature'],
            },
            head='b7c3625',
            root='b299199',
            tree={
                '2248903': ['b299199'],
                '7f55dee': ['e6770b0'],
                'b299199': ['7f55dee', 'b7c3625'],
                'e6770b0': ['18dcc52', '9d98707'],
                '9d98707': ['de5005c']
            })

    def test_multiname_branches(self):
        data = TreeReader(False).read('e5ff570', ['fixes', 'master', 'feature'], [
            self.log_entry('e5ff570', ['e85997d'], 'Fixed a bug in feature A',
                           branches=['feature']),
            self.log_entry('e85997d', ['c3624d3'], 'Fixed a third bug',
                           branches=['master', 'fixes'])
        ])

        self.assertTreeData(
            data=data,
            branches={
                'e5ff570': ['feature'],
                'e85997d': ['master', 'fixes']
            },
            head='e5ff570',
            root='e85997d',
            tree={
                'e85997d': ['e5ff570'],
                'c3624d3': ['e85997d']
            })

    def test_remote_branches(self):
        data = TreeReader(False).read('e85997d', ['fixes', 'master', 'feature'], [
            self.log_entry('e5ff570', ['e85997d'], 'Fixed a bug in feature A',
                           branches=['feature']),
            self.log_entry('e4f444b', ['e85997d'], 'Fixed a third bug',
                           branches=['origin/release2.2']),
            self.log_entry('e85997d', ['c3624d3'], 'Fixed a bug',
                           branches=['master', 'fixes']),
            self.log_entry('c3624d3', ['032b925'], 'Fixed another bug',
                           branches=['origin/master'])
        ])

        self.assertTreeData(
            data=data,
            branches={
                'e5ff570': ['feature'],
                'e85997d': ['master', 'fixes']
            },
            head='e85997d',
            root='e85997d',
            tree={
                'c3624d3': ['e85997d'],
                'e85997d': ['e4f444b', 'e5ff570']
            })

    def test_merges(self):
        data = TreeReader(False).read('6b261a7', ['fixes', 'master', 'feature'], [
            self.log_entry('6b261a7', ['541b298'], 'Fixed the CLI',
                           branches=['fixes']),
            self.log_entry('541b298', ['76094a4', '0ef17ac'], 'Merge all'),
            self.log_entry('76094a4', ['e85997d'], 'Fixed the UI'),
            self.log_entry('0ef17ac', ['e5ff570'], 'Fixed the doc'),
            self.log_entry('e5ff570', ['e85997d'], 'Fixed the API',
                           branches=['feature']),
            self.log_entry('e85997d', ['c3624d3'], 'Major release',
                           branches=['master'])
        ])

        self.assertTreeData(
            data=data,
            branches={
                '6b261a7': ['fixes'],
                'e5ff570': ['feature'],
                'e85997d': ['master']
            },
            head='6b261a7',
            root='e85997d',
            tree={
                'c3624d3': ['e85997d'],
                'e85997d': ['e5ff570', '76094a4'],
                'e5ff570': ['0ef17ac'],
                '76094a4': ['541b298'],
                '0ef17ac': ['541b298'],
                '541b298': ['6b261a7']
            })

    def test_detached_head_above_master(self):
        data = TreeReader(False).read('541b298', ['master', 'branch'], [
            self.log_entry('6b261a7', ['541b298'], 'Fixed the CLI', branches=['branch']),
            self.log_entry('541b298', ['e85997d'], 'Fixed the API'),
            self.log_entry('e85997d', ['c3624d3'], 'Major release', branches=['master'])
        ])

        self.assertTreeData(
            data=data,
            branches={
                '6b261a7': ['branch'],
                'e85997d': ['master']
            },
            head='541b298',
            root='e85997d',
            tree={
                'c3624d3': ['e85997d'],
                'e85997d': ['541b298'],
                '541b298': ['6b261a7']
            })

    def test_detached_head_below_master(self):
        data = TreeReader(False).read('e85997d', ['master', 'branch'], [
            self.log_entry('6b261a7', ['541b298'], 'Fixed the CLI', branches=['branch']),
            self.log_entry('541b298', ['e85997d'], 'Fixed the API', branches=['master']),
            self.log_entry('e85997d', ['c3624d3'], 'Major release')
        ])

        self.assertTreeData(
            data=data,
            branches={
                '6b261a7': ['branch'],
                '541b298': ['master']
            },
            head='e85997d',
            root='e85997d',
            tree={
                'c3624d3': ['e85997d'],
                'e85997d': ['541b298'],
                '541b298': ['6b261a7']
            })

    def test_ambiguous_head(self):
        data = TreeReader(False).read('541b298', ['master', 'HEAD'], [
            self.log_entry('6b261a7', ['541b298'], 'Fixed the CLI', branches=['HEAD']),
            self.log_entry('541b298', ['e85997d'], 'Fixed the API'),
            self.log_entry('e85997d', ['c3624d3'], 'Major release', branches=['master'])
        ])

        self.assertTreeData(
            data=data,
            branches={
                '6b261a7': ['HEAD'],
                'e85997d': ['master']
            },
            head='541b298',
            root='e85997d',
            tree={
                'c3624d3': ['e85997d'],
                'e85997d': ['541b298'],
                '541b298': ['6b261a7']
            })


class TestTreeBuilder(unittest.TestCase):

    def assertCorrectTree(self, tree, head, root, matchers):
        self.assertEqual(tree.head.ref, head)
        self.assertEqual(tree.root.ref, root)
        self.assertNumberOfBranches(tree, len(matchers))
        for matcher in matchers:
            branch = matcher[0]
            self.assertIn(branch, tree)
            self.assertEqual(tree[branch].ref, matcher[0])
            self.assertEqual(tree[branch].names, matcher[1])
            self.assertCorrectBranchCommits(tree[branch], matcher[2])

    def assertNumberOfBranches(self, tree, expected_count):
        actual_count = len(tree.branches)
        template = 'Expected the tree to have {} branches but it has {}'
        self.assertEqual(actual_count, expected_count, template.format(
            expected_count, actual_count
        ))

    def assertCorrectBranchCommits(self, branch, commits):
        self.assertBranchCommitsCount(branch, len(commits))
        for actual, expected in zip(branch.commits, commits):
            self.assertBranchCommitHash(branch, actual, expected[0])
            self.assertEqual(actual.message, expected[1])

    def assertBranchCommitsCount(self, branch, expected):
        actual = len(branch.commits)
        template = 'Expected branch {} to have {} commits but it has {}'
        self.assertEqual(actual, expected, template.format(
            branch.names, expected, actual))

    def assertBranchCommitHash(self, branch, commit, expected):
        actual = commit.id
        template = 'Expected branch {} to have commit "{}" but it had "{}"'
        self.assertEqual(actual, expected, template.format(
            branch.names, expected, actual))

    def assertBranchRelations(self, tree, expected):
        for branch in tree.branches:
            if branch.ref in expected:
                actual_children = set(branch.children.keys())
                expected_children = set(expected[branch.ref])
                self.assertSetEqual(actual_children, expected_children)
            else:
                self.assertEqual(branch.children, {})

    def tree_data(self, tree={}, branches={},
                  head=None, root=None, commits={}):
        return TreeData(tree, branches, commits, head, root)

    def commits(self, commits):
        return {
            hash: Commit(hash, message)
            for hash, message
            in commits.items()
        }

    def test_single_branch_and_single_commit(self):
        data = self.tree_data(
            head='210d73e',
            root='210d73e',
            tree={},
            branches={
                '210d73e': ['master']
            },
            commits=self.commits({
                '210d73e': 'Commit message'
            }))

        tree = TreeBuilder.build_tree(data, True)

        self.assertCorrectTree(tree, '210d73e', '210d73e', [
            ('210d73e', ['master'], [
                ('210d73e', 'Commit message')
            ])
        ])

    def test_multple_branches_with_multiple_commits(self):
        data = self.tree_data(
            head='d43991b',
            root='b299199',
            tree={
                '2248903': ['b299199'],
                'b299199': ['7f55dee', '7a1113e'],
                '7f55dee': ['96a5deb'],
                '7a1113e': ['e5b122a'],
                'e5b122a': ['d43991b']
            },
            branches={
                'b299199': ['master'],
                '96a5deb': ['feature'],
                'd43991b': ['fixes']
            },
            commits=self.commits({
                'd43991b': 'Fixed a third bug',
                'e5b122a': 'Fixed another bug',
                '7a1113e': 'Fixed a bug',
                '96a5deb': 'Fixed a bug in the features',
                '7f55dee': 'Added new features',
                'b299199': 'Some message',
                '2248903': 'Commit message'
            }))

        tree = TreeBuilder.build_tree(data, True)

        self.assertCorrectTree(tree, 'd43991b', 'b299199', [
            ('b299199', ['master'], [
                ('b299199', 'Some message')]),
            ('d43991b', ['fixes'], [
                ('d43991b', 'Fixed a third bug'),
                ('e5b122a', 'Fixed another bug'),
                ('7a1113e', 'Fixed a bug')]),
            ('96a5deb', ['feature'], [
                ('96a5deb', 'Fixed a bug in the features'),
                ('7f55dee', 'Added new features')]),
        ])
        self.assertBranchRelations(tree, {
            'b299199': ['d43991b', '96a5deb']
        })

    def test_unnamed_branch_points(self):
        data = self.tree_data(
            head='b7c3625',
            root='b299199',
            tree={
                '2248903': ['b299199'],
                'b299199': ['7f55dee', 'b7c3625'],
                '7f55dee': ['e6770b0'],
                'e6770b0': ['9d98707', '18dcc52'],
                '9d98707': ['de5005c']
            },
            branches={
                'b7c3625': ['master'],
                '18dcc52': ['feature'],
                'de5005c': ['fixes']
            },
            commits=self.commits({
                'de5005c': 'Fixed a third bug',
                '9d98707': 'Fixed another bug',
                'b7c3625': 'Major release',
                '18dcc52': 'Fixed a bug in the features',
                '7f55dee': 'Added new features',
                'e6770b0': 'Fixed a bug',
                'b299199': 'Some message'
            }))

        tree = TreeBuilder.build_tree(data, True)

        self.assertCorrectTree(tree, 'b7c3625', 'b299199', [
            ('de5005c', ['fixes'], [
                ('de5005c', 'Fixed a third bug'),
                ('9d98707', 'Fixed another bug')]),
            ('18dcc52', ['feature'], [
                ('18dcc52', 'Fixed a bug in the features')]),
            ('e6770b0', [], [
                ('e6770b0', 'Fixed a bug'),
                ('7f55dee', 'Added new features')]),
            ('b7c3625', ['master'], [
                ('b7c3625', 'Major release')]),
            ('b299199', [], [
                ('b299199', 'Some message')])
        ])
        self.assertBranchRelations(tree, {
            'b299199': ['b7c3625', 'e6770b0'],
            'e6770b0': ['de5005c', '18dcc52']
        })

    def test_multiname_branches(self):
        data = self.tree_data(
            head='e5ff570',
            root='e85997d',
            tree={
                'c3624d3': ['e85997d'],
                'e85997d': ['e5ff570']
            },
            branches={
                'e85997d': ['master', 'fixes'],
                'e5ff570': ['feature']
            },
            commits=self.commits({
                'e5ff570': 'Fixed a bug in the features',
                'e85997d': 'Fixed a third bug'
            }))

        tree = TreeBuilder.build_tree(data, True)

        self.assertCorrectTree(tree, 'e5ff570', 'e85997d', [
            ('e5ff570', ['feature'], [
                ('e5ff570', 'Fixed a bug in the features')]),
            ('e85997d', ['master', 'fixes'], [
                ('e85997d', 'Fixed a third bug')]),
        ])
        self.assertBranchRelations(tree, {
            'e85997d': ['e5ff570']
        })

    def test_dead_end_branches(self):
        data = self.tree_data(
            head='e85997d',
            root='e85997d',
            tree={
                '032b925': ['c3624d3'],
                'c3624d3': ['e85997d'],
                'e85997d': ['e5ff570', 'e4f444b']
            },
            branches={
                'e85997d': ['master', 'fixes'],
                'e5ff570': ['feature']
            },
            commits=self.commits({
                'e5ff570': 'Fixed a bug in a feature',
                'e4f444b': 'Release 2.2',
                'e85997d': 'Fixed a bug',
                'c3624d3': 'Fixed another bug'
            }))

        tree = TreeBuilder.build_tree(data, True)

        self.assertCorrectTree(tree, 'e85997d', 'e85997d', [
            ('e5ff570', ['feature'], [
                ('e5ff570', 'Fixed a bug in a feature')]),
            ('e85997d', ['master', 'fixes'], [
                ('e85997d', 'Fixed a bug')]),
        ])
        self.assertBranchRelations(tree, {
            'e85997d': ['e5ff570']
        })

    def test_merges(self):
        data = self.tree_data(
            head='6b261a7',
            root='e85997d',
            tree={
                'c3624d3': ['e85997d'],
                'e85997d': ['e5ff570', '76094a4'],
                'e5ff570': ['0ef17ac'],
                '76094a4': ['541b298'],
                '0ef17ac': ['541b298'],
                '541b298': ['6b261a7']
            },
            branches={
                '6b261a7': ['fixes'],
                'e5ff570': ['feature'],
                'e85997d': ['master']
            },
            commits=self.commits({
                '6b261a7': 'Fixed the CLI',
                '541b298': 'Merge all',
                '76094a4': 'Fixed the UI',
                '0ef17ac': 'Fixed the doc',
                'e5ff570': 'Fixed the API',
                'e85997d': 'Major release'
            }))

        tree = TreeBuilder.build_tree(data, True)

        self.assertCorrectTree(tree, '6b261a7', 'e85997d', [
            ('6b261a7', ['fixes'], [
                ('6b261a7', 'Fixed the CLI'),
                ('541b298', 'Merge all'),
                ('0ef17ac', 'Fixed the doc'),
                ('76094a4', 'Fixed the UI')]),
            ('e5ff570', ['feature'], [
                ('e5ff570', 'Fixed the API')]),
            ('e85997d', ['master'], [
                ('e85997d', 'Major release')]),
        ])
        self.assertBranchRelations(tree, {
            'e85997d': ['e5ff570', '6b261a7'],
            'e5ff570': ['6b261a7']
        })

    def test_detached_head_above_master(self):
        data = self.tree_data(
            head='e5ff570',
            root='e85997d',
            tree={
                'e85997d': ['e5ff570'],
                'e5ff570': ['6b261a7']
            },
            branches={
                '6b261a7': ['fixes'],
                'e85997d': ['master']
            },
            commits=self.commits({
                '6b261a7': 'Fixed the CLI',
                'e5ff570': 'Fixed the API',
                'e85997d': 'Major release'
            }))

        tree = TreeBuilder.build_tree(data, True)

        self.assertCorrectTree(tree, 'e5ff570', 'e85997d', [
            ('6b261a7', ['fixes'], [('6b261a7', 'Fixed the CLI')]),
            ('e5ff570', [], [('e5ff570', 'Fixed the API')]),
            ('e85997d', ['master'], [('e85997d', 'Major release')])
        ])
        self.assertBranchRelations(tree, {
            'e85997d': ['e5ff570'],
            'e5ff570': ['6b261a7']
        })

    def test_detached_head_below_master(self):
        data = self.tree_data(
            head='e85997d',
            root='e85997d',
            tree={
                'e85997d': ['e5ff570'],
                'e5ff570': ['6b261a7']
            },
            branches={
                '6b261a7': ['fixes'],
                'e5ff570': ['master']
            },
            commits=self.commits({
                '6b261a7': 'Fixed the CLI',
                'e5ff570': 'Fixed the API',
                'e85997d': 'Major release'
            }))

        tree = TreeBuilder.build_tree(data, True)

        self.assertCorrectTree(tree, 'e85997d', 'e85997d', [
            ('6b261a7', ['fixes'], [('6b261a7', 'Fixed the CLI')]),
            ('e5ff570', ['master'], [('e5ff570', 'Fixed the API')]),
            ('e85997d', [], [('e85997d', 'Major release')])
        ])
        self.assertBranchRelations(tree, {
            'e85997d': ['e5ff570'],
            'e5ff570': ['6b261a7']
        })

    def test_ambiguous_head(self):
        data = self.tree_data(
            head='e5ff570',
            root='e85997d',
            tree={
                'e85997d': ['e5ff570'],
                'e5ff570': ['6b261a7']
            },
            branches={
                '6b261a7': ['HEAD'],
                'e85997d': ['master']
            },
            commits=self.commits({
                '6b261a7': 'Fixed the CLI',
                'e5ff570': 'Fixed the API',
                'e85997d': 'Major release'
            }))

        tree = TreeBuilder.build_tree(data, True)

        self.assertCorrectTree(tree, 'e5ff570', 'e85997d', [
            ('6b261a7', ['HEAD'], [('6b261a7', 'Fixed the CLI')]),
            ('e5ff570', [], [('e5ff570', 'Fixed the API')]),
            ('e85997d', ['master'], [('e85997d', 'Major release')])
        ])
        self.assertBranchRelations(tree, {
            'e85997d': ['e5ff570'],
            'e5ff570': ['6b261a7']
        })
