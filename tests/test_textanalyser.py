import unittest
from collections import Counter

from bitstring import Bits

from stegano.textanalyser import TextAnalyser, ANALYSIS_SEPARATOR
from stegano.wtdict import MappingDictionary

TEST_ANALYSIS_FILE = "..\\test_data\\test_analysis.txt"
TEST_INVALID_ANALYSIS_FILE = "..\\test_data\\invalid_analysis.txt"
TEST_BAD_FREQ_ANALYSIS_FILE = "..\\test_data\\invalid_freq.txt"
TEST_MAPPINGS_FILE = "..\\test_data\\test_mappings.txt"
TEST_EMPTY_FILE = "..\\test_data\\empty.txt"


class TestTextAnalyser(unittest.TestCase):
    def test_normalise_mock_frequencies(self):
        mock_set = set()
        mock_set.add(("string", 75))
        mock_set.add(("word", 25))

        mock_return_set = set()
        mock_return_set.add(("string", 0.75))
        mock_return_set.add(("word", 0.25))

        return_set = TextAnalyser.normalise_frequencies(mock_set)
        self.assertSetEqual(return_set, mock_return_set, "Mock set frequencies were not normalised as expected")

    def test_normalise_empty_frequencies(self):
        self.assertSetEqual(TextAnalyser.normalise_frequencies(set()), set())

    def test_read_analysis(self):
        mock_set = set()
        mock_set.add(("one  ", 1))
        mock_set.add(("two  ", 2))

        mock_analysis = TextAnalyser.read_analysis(TEST_ANALYSIS_FILE)
        self.assertSetEqual(mock_set, mock_analysis)

    def test_write_analysis(self):
        mock_set = set()
        mock_set.add(("one  ", 1))
        mock_set.add(("two  ", 2))

        with open(TEST_ANALYSIS_FILE, "w", encoding="utf-8") as handle:
            handle.write("one  ")
            handle.write(ANALYSIS_SEPARATOR)
            handle.write("1")
            handle.write("\n")
            handle.write("two  ")
            handle.write(ANALYSIS_SEPARATOR)
            handle.write("2")
            handle.write("\n")

    def test_read_missing_analysis(self):
        self.assertRaises(IOError, TextAnalyser.read_analysis, "..\\non_existent")

    def test_read_empty_analysis(self):
        mock_analysis = TextAnalyser.read_analysis(TEST_EMPTY_FILE)
        self.assertSetEqual(mock_analysis, set())

    def test_read_analysis_invalid_frequency(self):
        self.assertRaises(ValueError, TextAnalyser.read_analysis, TEST_INVALID_ANALYSIS_FILE)

    def test_read_analysis_invalid_line(self):
        self.assertRaises(ValueError, TextAnalyser.read_analysis, TEST_BAD_FREQ_ANALYSIS_FILE)

    def test_read_mappings(self):
        mock_dict = {
            "zero": Bits(bin="00"),
            "one": Bits(bin="01"),
            "two": Bits(bin="10")
        }

        mock_mappings_dict = TextAnalyser.read_mapping_dict(TEST_MAPPINGS_FILE, True)
        self.assertIsInstance(mock_mappings_dict, MappingDictionary)
        self.assertTrue(mock_mappings_dict.encode_spaces)
        self.assertIsInstance(mock_mappings_dict.mappings, dict)
        self.assertDictEqual(mock_dict, mock_mappings_dict.mappings)

    def test_write_mappings(self):
        with open(TEST_MAPPINGS_FILE, "w", encoding="utf-8") as handle:
            handle.write("zero")
            handle.write(ANALYSIS_SEPARATOR)
            handle.write("00")
            handle.write("\n")
            handle.write("one")
            handle.write(ANALYSIS_SEPARATOR)
            handle.write("01")
            handle.write("\n")
            handle.write("two")
            handle.write(ANALYSIS_SEPARATOR)
            handle.write("10")
            handle.write("\n")

    def test_combine_analyses(self):
        in_1 = {
            ("one", 10),
            ("two", 20),
            ("three", 30),
            ("four", 40),
            ("five", 50),
            ("six", 60),
            ("seven", 70)
        }
        in_2 = {
            ("two", 9),
            ("four", 7),
            ("six", 5),
            ("eight", 4),
            ("ten", 2)
        }
        out_1, out_2, out_3 = TextAnalyser.combine_analyses(in_1, in_2)
        self.assertIsInstance(out_1, Counter)
        self.assertIsInstance(out_2, Counter)
        self.assertIsInstance(out_3, Counter)

        self.assertDictEqual({
            "one": 10,
            "three": 30,
            "five": 50,
            "seven": 70
        }, dict(out_1.items()))

        self.assertDictEqual({
            "eight": 4,
            "ten": 2
        }, dict(out_2.items()))

        self.assertDictEqual({
            "six": 65,
            "four": 47,
            "two": 29
        }, dict(out_3.items()))


if __name__ == '__main__':
    unittest.main()
