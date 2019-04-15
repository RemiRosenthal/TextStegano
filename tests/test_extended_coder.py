import unittest

from bitstring import Bits

from stegano import extended_coder
from stegano.markov import MarkovChain
from stegano.wtdict import MappingDictionary, WordTypeDictionary


class TestRetrieveWord(unittest.TestCase):
    def setUp(self):
        self.mappings = set()
        self.mappings.add(("penguin", Bits(bin="000")))
        self.mappings.add(("tiger", Bits(bin="001")))
        self.mappings.add(("giraffe", Bits(bin="01")))
        self.mappings.add(("dog", Bits(bin="10")))
        self.mappings.add(("cat", Bits(bin="11")))
        self.mapping_dict = MappingDictionary(self.mappings)

    def test_retrieve_word(self):
        bits = Bits(bin="00101011100101010")
        word = extended_coder.retrieve_word_from_mappings(bits, self.mapping_dict)
        self.assertEqual("tiger", word)

    def test_retrieve_word_padded(self):
        bits = Bits(bin="00")
        word = extended_coder.retrieve_word_from_mappings(bits, self.mapping_dict)
        self.assertEqual("penguin", word)

    def test_retrieve_empty(self):
        bits = Bits()
        word = extended_coder.retrieve_word_from_mappings(bits, self.mapping_dict)
        self.assertEqual("penguin", word)

    def test_retrieve_nothing(self):
        bits = None
        self.assertRaises(ValueError, extended_coder.retrieve_word_from_mappings, bits, self.mapping_dict)


class TestEncodeBits(unittest.TestCase):
    def setUp(self):
        self.mappings = set()
        self.mappings.add(("penguin", Bits(bin="000")))
        self.mappings.add(("tiger", Bits(bin="001")))
        self.mappings.add(("giraffe", Bits(bin="01")))
        self.mappings.add(("dog", Bits(bin="10")))
        self.mappings.add(("cat", Bits(bin="11")))
        self.mapping_dict = MappingDictionary(self.mappings)
        self.input_dict = {"animals": self.mapping_dict}

        self.mappings = set()
        self.mappings.add(("pen", Bits(bin="1")))
        self.mappings.add(("pencil", Bits(bin="00")))
        self.mappings.add(("paper", Bits(bin="01")))
        self.mapping_dict = MappingDictionary(self.mappings)
        self.input_dict.update({"stationery": self.mapping_dict})

        self.mappings = set()
        self.mappings.add(("red", Bits(bin="111")))
        self.mappings.add(("orange", Bits(bin="110")))
        self.mappings.add(("blue", Bits(bin="10")))
        self.mappings.add(("yellow", Bits(bin="01")))
        self.mappings.add(("green", Bits(bin="00")))
        self.mapping_dict = MappingDictionary(self.mappings)
        self.input_dict.update({"colours": self.mapping_dict})

        self.wt_dict = WordTypeDictionary(self.input_dict)

        self.states = {"animals", "stationery", "colours"}
        self.markov_chain = MarkovChain(self.states)

        self.transitions = set()
        self.transitions.add(("s0", "animals", 4))
        self.transitions.add(("s0", "stationery", 2))
        self.transitions.add(("animals", "colours", 0.3))
        self.transitions.add(("animals", "stationery", 0.7))
        self.transitions.add(("stationery", "s0", 0.5))
        self.transitions.add(("stationery", "colours", 0.5))
        self.transitions.add(("colours", "s0", 1))
        self.markov_chain.set_transitions(self.transitions)

