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
        shortest_bit_string = 1
        self.assertGreaterEqual(len(words), -(-len(bits) // longest_bit_string))
        self.assertLessEqual(len(words), -(-len(bits) // shortest_bit_string))


class TestListToCoverText(unittest.TestCase):
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

    def test_words_to_cover_text_empty(self):
        cover_text = extended_coder.words_to_cover_text([])
        self.assertEqual("", cover_text)


class TestEncodeMessage(unittest.TestCase):
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

    def test_get_fixed_length_header(self):
        self.assertEqual("1100101011110000", extended_coder.get_fixed_length_header(618, 16).bin)
        self.assertEqual("11001000", extended_coder.get_fixed_length_header(1, 8).bin)
        self.assertEqual("00110111", extended_coder.get_fixed_length_header(256, 8).bin)

    def test_get_fixed_length_header_inverses(self):
        # Headers generated should have a property whereby each number has an inverse number, whose inverse is the
        # original number.
        numbers_to_test = {618, 1, 65536}
        for number in numbers_to_test:
            header = extended_coder.get_fixed_length_header(number, 16).bin
            inverse_number = Bits(bin=header).uint + 1
            inverse_header = extended_coder.get_fixed_length_header(inverse_number, 16).bin
            self.assertEqual(number, Bits(bin=inverse_header).uint + 1)

    def test_get_fixed_length_header_exact(self):
        self.assertEqual("01001", extended_coder.get_fixed_length_header(17, 4).bin)

    def test_get_fixed_length_header_long_message(self):
        self.assertRaises(ValueError, extended_coder.get_fixed_length_header, 18, 4)

    def test_get_fixed_length_header_zero_length_message(self):
        self.assertRaises(ValueError, extended_coder.get_fixed_length_header, 0, 4)

    def test_get_message_length_from_header(self):
        self.assertEqual(618, extended_coder.get_message_length_from_header(Bits(bin="1100101011110000")))
        self.assertEqual(1, extended_coder.get_message_length_from_header(Bits(bin="11001000")))
        self.assertEqual(256, extended_coder.get_message_length_from_header(Bits(bin="00110111")))

    def test_encode_message(self):
        bits = Bits(bin="0100101110010110100101")
        header_length = 6
        cover_text = extended_coder.encode_message(self.markov_chain, self.wt_dict, bits, header_length)
        longest_bit_string = 3
        longest_word = 7
        shortest_bit_string = 1
        shortest_word = 3

        neg_total_message_length = -(len(bits) + header_length)
        minimum_chars = (-(neg_total_message_length // longest_bit_string)) * (shortest_word + 1) - 1
        maximum_chars = (-(neg_total_message_length // shortest_bit_string)) * (longest_word + 1) - 1
        self.assertGreaterEqual(len(cover_text), minimum_chars)
        self.assertLessEqual(len(cover_text), maximum_chars)

    def test_encode_message_zero_header(self):
        bits = Bits(bin="0100101110010110100101")
        header_length = 0
        self.assertRaises(ValueError, extended_coder.encode_message, self.markov_chain, self.wt_dict, bits,
                          header_length)

    def test_encode_message_empty_bits(self):
        bits = Bits()
        header_length = 6
        self.assertRaises(ValueError, extended_coder.encode_message, self.markov_chain, self.wt_dict, bits,
                          header_length)
