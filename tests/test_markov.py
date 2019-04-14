import unittest

from stegano.markov import MarkovChain, MarkovError


class TestMarkovChain(unittest.TestCase):
    def setUp(self):
        self.states = {"s1", "s2", "s3", "s4"}
        self.test_states = self.states.union({"s0"})
        self.markov_chain = MarkovChain(self.states)

    def test_init(self):
        self.assertSetEqual(self.test_states, self.markov_chain.states)
        self.assertEqual("s0", self.markov_chain.current_state)
        self.assertSetEqual(set(), self.markov_chain.transitions)

    def test_init_s0(self):
        self.markov_chain = MarkovChain(self.states.union({"s0"}))
        self.assertSetEqual(self.test_states, self.markov_chain.states)
        self.assertEqual("s0", self.markov_chain.current_state)


class TestMarkovChainTransitions(unittest.TestCase):
    def setUp(self):
        self.states = {"s1", "s2", "s3", "s4"}
        self.markov_chain = MarkovChain(self.states)

        self.transitions = set()
        self.transitions.add(("s0", "s1", 2))
        self.transitions.add(("s0", "s2", 3))
        self.transitions.add(("s1", "s3", 0.5))
        self.transitions.add(("s1", "s4", 0.5))
        self.transitions.add(("s2", "s4", 1))
        self.transitions.add(("s3", "s0", 1))
        self.transitions.add(("s4", "s0", 2))

    def test_set_transitions(self):
        self.markov_chain.set_transitions(self.transitions)
        self.assertSetEqual(self.transitions, self.markov_chain.transitions)

    def test_set_transitions_bad_outbound(self):
        self.transitions.add(("s4", "s5", 1))
        self.assertRaises(MarkovError, self.markov_chain.set_transitions, self.transitions)

    def test_set_transitions_bad_inbound(self):
        self.transitions.add(("s5", "s1", 1))
        self.assertRaises(MarkovError, self.markov_chain.set_transitions, self.transitions)

    def test_set_transitions_neg_probability(self):
        self.transitions.add(("s3", "s4", -1))
        self.assertRaises(MarkovError, self.markov_chain.set_transitions, self.transitions)

    def test_set_transitions_zero_probability(self):
        self.transitions.add(("s3", "s4", 0))
        self.assertRaises(MarkovError, self.markov_chain.set_transitions, self.transitions)

    def test_get_outbound_states(self):
        self.markov_chain.set_transitions(self.transitions)
        outbound_states = self.markov_chain.get_outbound_transitions()
        expected = {("s1", 2), ("s2", 3)}
        self.assertSetEqual(expected, outbound_states)

        self.markov_chain.current_state = "s4"
        outbound_states = self.markov_chain.get_outbound_transitions()
        expected = {("s0", 2)}
        self.assertSetEqual(expected, outbound_states)


if __name__ == '__main__':
    unittest.main()
