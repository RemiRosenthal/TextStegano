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
        word = extended_coder.retrieve_word_from_mappings(bits, self.mapping_dict, True)
        self.assertEqual("tiger", word)

    def test_retrieve_word_padded(self):
        bits = Bits(bin="1")
        word = extended_coder.retrieve_word_from_mappings(bits, self.mapping_dict, True)
        self.assertEqual("dog", word)

    def test_retrieve_word_no_padding(self):
        bits = Bits(bin="1")
        self.assertRaises(ValueError, extended_coder.retrieve_word_from_mappings, bits, self.mapping_dict, False)

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

    def test_encode_bits_as_string(self):
        bits = Bits(bin="00101011100101010")
        words = extended_coder.encode_bits_as_words(self.markov_chain, self.wt_dict, bits)
        longest_bit_string = 3
        shortest_bit_string = 2
        self.assertTrue(len(words) >= -(-len(bits) // longest_bit_string))
        self.assertTrue(len(words) <= -(-len(bits) // shortest_bit_string))


class TestCoverText(unittest.TestCase):
    def setUp(self):
        self.words = [
            ("a", True),
            ("Lion", True),
            ("had", True),
            ("come", True),
            ("to", True),
            ("the", True),
            ("end", True),
            ("of", True),
            ("his", True),
            ("days", True),
            ("and", True),
            ("lay", True),
            ("sick", True),
            ("unto", True),
            ("death", True),
            ("at", True),
            ("the", True),
            ("mouth", True),
            ("of", True),
            ("his", True),
            ("cave", True),
            (",", False),
            ("gasping", True),
            ("for", True),
            ("breath", True),
            (".", False)
        ]

    def test_words_to_cover_text(self):
        cover_text = extended_coder.words_to_cover_text(self.words, True)
        self.assertEqual("A Lion had come to the end of his days and lay sick unto death at the mouth of his cave, "
                         "gasping for breath.", cover_text)

    def test_words_to_cover_text_no_capitalise(self):
        cover_text = extended_coder.words_to_cover_text(self.words, False)
        self.assertEqual("a Lion had come to the end of his days and lay sick unto death at the mouth of his cave, "
                         "gasping for breath.", cover_text)
