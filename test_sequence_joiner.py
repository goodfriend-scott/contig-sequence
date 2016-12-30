import unittest
from Bio import SeqIO

import sequence_joiner as sj

class BaseSeqJoinGraphTestCase(unittest.TestCase):
    FILENAME = 'example.fasta'
    RECOMBINED_SEQUENCE = None
    def setUp(self):
        self.seq_records = [s for s in SeqIO.parse(self.FILENAME, 'fasta')]
        self.graph = sj.SeqJoinGraph.graph_from_seq_records(self.seq_records)

    def test_correct_sequence(self):
        if self.RECOMBINED_SEQUENCE is not None:
            seq = self.graph.sequence()
            self.assertEqual(seq, self.RECOMBINED_SEQUENCE)


class BaseLinearFileLoadedTestCase(BaseSeqJoinGraphTestCase):
    FILENAME = 'example.fasta'
    RECOMBINED_SEQUENCE = 'ATTAGACCTGCCGGAATAC'
    ROOT_NAME = 'Frag_56'
    END_NAME = 'Frag_59'
    def test_seq_join_graph_state(self):
        self.assertEqual(len(self.graph.nodes), len(self.seq_records))
        self.assertEqual(len(self.graph.root_nodes()), 1)
        self.assertEqual(self.graph.root_nodes()[0].seq_record.name, self.ROOT_NAME)
        self.assertEqual(len(self.graph.end_nodes()), 1)
        self.assertEqual(self.graph.end_nodes()[0].seq_record.name, self.END_NAME)

    def test_seq_join_longest_path_linearity(self):
        longest_path = sj.SeqJoinLongestPath(self.graph)
        self.assertTrue(longest_path.is_linear_graph())

    def test_seq_join_longest_path_equivalence(self):
        longest_path = sj.SeqJoinLongestPath(self.graph)
        self.assertEqual(longest_path.linear_longest_path(), longest_path.dfs_longest_path())


class SingleFragmentLinearTestCase(BaseLinearFileLoadedTestCase):
    FILENAME = 'single.fasta'
    RECOMBINED_SEQUENCE = 'ATCG'
    ROOT_NAME = 'Single'
    END_NAME = 'Single'


class CircularDNATestCase(BaseSeqJoinGraphTestCase):
    FILENAME = 'circular.fasta'
    def test_seq_join_graph_state(self):
        self.assertEqual(self.graph.root_nodes(), [])
        self.assertEqual(self.graph.end_nodes(), [])

    def test_exception_raised(self):
        with self.assertRaises(sj.LinearSequenceAssertionFailure):
            self.graph.sequence()

    def test_seq_join_longest_path(self):
        longest_path = sj.SeqJoinLongestPath(self.graph)
        self.assertFalse(longest_path.is_linear_graph())
        self.assertEqual(longest_path.longest_path, longest_path.dfs_longest_path())


class SingleFragmentCircularDNATestCase(CircularDNATestCase):
    FILENAME = 'single_circular.fasta'


class EmptyFastaFileTestCase(BaseSeqJoinGraphTestCase):
    FILENAME = 'empty.fasta'
    def test_sequence_exception_raise(self):
        with self.assertRaises(sj.NoFragmentsException):
            self.graph.sequence()


class SmallCyclesDNATestCase(BaseSeqJoinGraphTestCase):
    """
    SmallCyclesDNATestCase tests if the dfs maximum path solver works with small cycles existing.

    Longest path is  1-2-3. However, there are additional possible paths thanks to there being
    cycle-forming edges: 2->1, 3->2.
    """
    FILENAME = 'simple_branching_cycle.fasta'
    RECOMBINED_SEQUENCE = 'ATCGAATCGA'
    def test_terminal_nodes(self):
        self.assertEqual(len(self.graph.root_nodes()), 0)
        self.assertEqual(len(self.graph.end_nodes()), 0)

    def test_maximum_path_non_linearity(self):
        longest_path = sj.SeqJoinLongestPath(self.graph)
        self.assertFalse(longest_path.is_linear_graph())

    def test_maximum_path_uses_dfs(self):
        longest_path = sj.SeqJoinLongestPath(self.graph)
        self.assertEqual(longest_path.longest_path, longest_path.dfs_longest_path())


class SkipFragmentsDNATestCase(BaseSeqJoinGraphTestCase):
    """
    SkipFragmentsDNATestCase tests if the dfs maximum path solver works with matching skips.

    Longest path is 1-2-3. However, 1->3 also matches.
    """
    FILENAME = 'simple_branching_skip.fasta'
    RECOMBINED_SEQUENCE = 'AAAAGTAGTGA'

if __name__ == '__main__':
    unittest.main()