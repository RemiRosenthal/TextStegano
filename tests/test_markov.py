import unittest

from stegano import markov
from stegano.markov import MarkovChain, MarkovError, StateTransitions

TEST_CHAIN_FILE = "..\\test_data\\markov_chain.json"
TEST_EMPTY_CHAIN_FILE = "..\\test_data\\empty_markov_chain.json"
TEST_EMPTY_FILE = "..\\test_data\\empty_json.json"


class TestMarkovChain(unittest.TestCase):
    def setUp(self):
        self.states = {"s1", "s2", "s3", ("s4", "dict")}
        self.test_states = {"s0", "s1", "s2", "s3", "s4"}
        self.test_wt_refs = {"s1": "s1", "s2": "s2", "s3": "s3", "s4": "dict"}

    def test_init(self):
        self.markov_chain = MarkovChain(self.states)
        self.assertSetEqual(self.test_states, self.markov_chain.states)
        self.assertEqual("s0", self.markov_chain.current_state)
        self.assertDictEqual({"s0": None, "s1": None, "s2": None, "s3": None, "s4": None},
                             self.markov_chain.markov_chain)
        self.assertDictEqual(self.test_wt_refs, self.markov_chain.wt_refs)

    def test_init_s0(self):
        self.markov_chain = MarkovChain(self.states.union({"s0"}))
        self.assertSetEqual(self.test_states, self.markov_chain.states)
        self.assertEqual("s0", self.markov_chain.current_state)
        self.assertDictEqual(self.test_wt_refs, self.markov_chain.wt_refs)

    def test_init_s0_tuple(self):
        self.markov_chain = MarkovChain(self.states.union({("s0", "any")}))
        self.assertSetEqual(self.test_states, self.markov_chain.states)
        self.assertEqual("s0", self.markov_chain.current_state)
        self.assertDictEqual(self.test_wt_refs, self.markov_chain.wt_refs)

    def test_dict(self):
        self.markov_chain = MarkovChain(self.states)
        serial_dict = self.markov_chain.__dict__()
        self.assertIsInstance(serial_dict, dict)
        self.assertEqual(2, len(serial_dict))

        self.assertIsInstance(serial_dict.get("chain"), dict)
        self.assertDictEqual({}, serial_dict.get("chain"))

        self.assertIsInstance(serial_dict.get("wt_refs"), dict)
        self.assertDictEqual(self.test_wt_refs, serial_dict.get("wt_refs"))

    def test_get_word_type_for_state(self):
        self.markov_chain = MarkovChain(self.states)
        self.assertEqual("s1", self.markov_chain.get_word_type_for_state("s1"))
        self.assertEqual("dict", self.markov_chain.get_word_type_for_state("s4"))
        self.assertRaises(ValueError, self.markov_chain.get_word_type_for_state, "s0")

    def test_get_current_word_type(self):
        self.markov_chain = MarkovChain(self.states)
        self.markov_chain.current_state = "s1"
        self.assertEqual("s1", self.markov_chain.get_current_word_type())
        self.markov_chain.current_state = "s4"
        self.assertEqual("dict", self.markov_chain.get_current_word_type())
        self.markov_chain.current_state = "s0"
        self.assertIsNone(self.markov_chain.get_current_word_type())


class TestMarkovChainTransitions(unittest.TestCase):
    def setUp(self):
        self.states = {"s1", "s2", "s3", ("s4", "dict")}
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

    def test_dict(self):
        self.markov_chain.set_transitions(self.transitions)
        serial_dict = self.markov_chain.__dict__()
        self.assertEqual(2, len(serial_dict))

        chain_dict = serial_dict.get("chain")
        self.assertIsInstance(chain_dict, dict)
        self.assertEqual(5, len(chain_dict))
        self.assertIsInstance(chain_dict.get("s0"), dict)
        self.assertDictEqual({"s1": 2, "s2": 3}, chain_dict.get("s0"))

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

    def test_ignore_non_cycle(self):
        self.transitions.add(("s1", "s2", 1))
        self.markov_chain.set_transitions(self.transitions)

    def test_get_number_of_paths(self):
        self.markov_chain.set_transitions(self.transitions)
        no_of_paths = markov.get_number_of_paths(self.markov_chain)
        self.assertEqual(3, no_of_paths)

        self.states.add("s5")
        self.markov_chain = MarkovChain(self.states)
        self.transitions.add(("s2", "s5", 1))
        self.transitions.add(("s4", "s5", 1))
        self.transitions.add(("s5", "s0", 1))
        self.markov_chain.set_transitions(self.transitions)
        no_of_paths = markov.get_number_of_paths(self.markov_chain)
        self.assertEqual(6, no_of_paths)

    @unittest.skip
    def test_save(self):
        self.markov_chain.set_transitions(self.transitions)
        markov.save_markov_chain(self.markov_chain)


class TestMarkov(unittest.TestCase):
    def setUp(self):
        self.states = {"s0", "s1", "s2", "s3", "s4"}
        self.wt_refs = {"s1": "s1", "s2": "s2", "s3": "s3", "s4": "dict"}
        self.chain = {
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

    def test_deserialise_chain(self):
        serial_chain = {
            "wt_refs": self.wt_refs,
            "chain": self.chain
        }
        markov_chain = markov.deserialise_markov_chain(serial_chain)

        self.assertIsInstance(markov_chain, MarkovChain)

        self.assertIsInstance(markov_chain.states, set)
        self.assertEqual(5, len(markov_chain.states))
        self.assertSetEqual(self.states, markov_chain.states)

        self.assertIsInstance(markov_chain.markov_chain, dict)
        self.assertEqual(5, len(markov_chain.markov_chain.items()))
        self.assertEqual(2, len(markov_chain.markov_chain.get("s1").transitions))
        self.assertDictEqual({"s4": 0.5, "s3": 0.5}, markov_chain.markov_chain.get("s1").transitions)

        self.assertIsInstance(markov_chain.wt_refs, dict)
        self.assertEqual(4, len(markov_chain.wt_refs.items()))
        self.assertDictEqual(self.wt_refs, markov_chain.wt_refs)

    def test_load_chain(self):
        markov_chain = markov.load_markov_chain(TEST_CHAIN_FILE)

        self.assertIsInstance(markov_chain, MarkovChain)

        self.assertIsInstance(markov_chain.states, set)
        self.assertEqual(10, len(markov_chain.states))
        self.assertIn("s0", markov_chain.states)
        self.assertIn("state_name9", markov_chain.states)

        self.assertIsInstance(markov_chain.markov_chain, dict)
        self.assertEqual(10, len(markov_chain.markov_chain.items()))
        self.assertEqual(1, len(markov_chain.markov_chain.get("s0").transitions))
        self.assertDictEqual({"state_name1": 1}, markov_chain.markov_chain.get("s0").transitions)

        self.assertIsInstance(markov_chain.wt_refs, dict)
        self.assertEqual(9, len(markov_chain.wt_refs.items()))
        self.assertEqual("word_type1", markov_chain.wt_refs.get("state_name1"))

    def test_load_chain_empty_chain(self):
        self.assertRaises(MarkovError, markov.load_markov_chain, TEST_EMPTY_CHAIN_FILE)

    def test_load_chain_empty_file(self):
        self.assertRaises(MarkovError, markov.load_markov_chain, TEST_EMPTY_FILE)


if __name__ == '__main__':
    unittest.main()
