import unittest

from stegano import markov
from stegano.markov import MarkovChain, MarkovError, StateTransitions


class TestMarkovChain(unittest.TestCase):
    def setUp(self):
        self.states = {"s1", "s2", "s3", "s4"}
        self.test_states = self.states.union({"s0"})
        self.markov_chain = MarkovChain(self.states)

    def test_init(self):
        self.assertSetEqual(self.test_states, self.markov_chain.states)
        self.assertEqual("s0", self.markov_chain.current_state)
        self.assertDictEqual({"s0": None, "s1": None, "s2": None, "s3": None, "s4": None},
                             self.markov_chain.markov_chain)

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
        self.assertEqual(5, len(self.markov_chain.markov_chain))
        self.assertIsInstance(self.markov_chain.markov_chain.get("s0"), StateTransitions)
        self.assertDictEqual({"s1": 2, "s2": 3}, self.markov_chain.markov_chain.get("s0").transitions)

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

    def test_set_transitions_s0_no_outbound(self):
        self.transitions = {x for x in self.transitions if not x[0].__eq__("s0")}
        self.assertRaises(MarkovError, self.markov_chain.set_transitions, self.transitions)

    def test_set_transitions_s0_no_inbound(self):
        self.transitions = {x for x in self.transitions if not x[1].__eq__("s0")}
        self.assertRaises(MarkovError, self.markov_chain.set_transitions, self.transitions)

    def test_get_outbound_transitions(self):
        self.markov_chain.set_transitions(self.transitions)
        self.markov_chain.current_state = "s0"
        outbound_transitions = self.markov_chain.get_outbound_transitions()
        self.assertIsInstance(outbound_transitions, StateTransitions)
        self.assertEqual(2, len(outbound_transitions.transitions))
        self.assertEqual(2, outbound_transitions.transitions.get("s1"))
        self.assertEqual(3, outbound_transitions.transitions.get("s2"))

        self.markov_chain.current_state = "s4"
        outbound_transitions = self.markov_chain.get_outbound_transitions()
        self.assertIsInstance(outbound_transitions, StateTransitions)
        self.assertEqual(1, len(outbound_transitions.transitions))
        self.assertEqual(2, outbound_transitions.transitions.get("s0"))

    def test_accumulate_transitions(self):
        self.markov_chain.set_transitions(self.transitions)
        self.markov_chain.current_state = "s0"
        accum = self.markov_chain.accumulate_transitions()
        self.assertIsInstance(accum, list)
        self.assertEqual(2, len(accum))
        self.assertTrue(any(x[1] == 5) for x in accum)

    def test_transition(self):
        self.markov_chain.set_transitions(self.transitions)
        self.markov_chain.current_state = "s0"
        self.markov_chain.transition()
        self.assertIn(self.markov_chain.current_state, {"s1", "s2"})

        self.markov_chain.transition()
        self.assertIn(self.markov_chain.current_state, {"s3", "s4"})

        self.markov_chain.transition()
        self.assertEqual("s0", self.markov_chain.current_state)

    def test_find_2_cycle(self):
        self.transitions.add(("s4", "s2", 1))
        self.assertRaises(MarkovError, self.markov_chain.set_transitions, self.transitions)

    def test_find_3_cycle(self):
        self.transitions = {x for x in self.transitions if not x[1].__eq__("s3")}
        self.transitions.add(("s4", "s3", 1))
        self.transitions.add(("s3", "s1", 1))
        self.assertRaises(MarkovError, self.markov_chain.set_transitions, self.transitions)

    @unittest.skip
    def test_save(self):
        self.markov_chain.set_transitions(self.transitions)
        markov.save_markov_chain(self.markov_chain)


class TestMarkov(unittest.TestCase):
    def test_deserialise_chain(self):
        serial_chain = {
            "s1": {
                "s4": 0.5,
                "s3": 0.5
            },
            "s0": {
                "s1": 2,
                "s2": 3
            },
            "s2": {
                "s4": 1
            },
            "s4": {
                "s0": 2
            },
            "s3": {
                "s0": 1
            }
        }
        markov_chain = markov.deserialise_markov_chain(serial_chain)

        self.assertIsInstance(markov_chain, MarkovChain)
        self.assertEqual(5, len(markov_chain.markov_chain.items()))
        self.assertEqual(2, len(markov_chain.markov_chain.get("s1").transitions))
        self.assertDictEqual({"s4": 0.5, "s3": 0.5}, markov_chain.markov_chain.get("s1").transitions)

    def test_load_chain(self):
        markov.load_markov_chain()


if __name__ == '__main__':
    unittest.main()
