import unittest

from bitstring import Bits

from stegano.textanalyser import TextAnalyser, ANALYSIS_SEPARATOR
from stegano.wtdict import MappingDictionary


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

        mock_analysis_filename = "..\\mock_analysis.txt"
        with open(mock_analysis_filename, "w", encoding="utf-8") as handle:
            handle.write("one  ")
            handle.write(ANALYSIS_SEPARATOR)
            handle.write("1")
            handle.write("\n")
            handle.write("two  ")
            handle.write(ANALYSIS_SEPARATOR)
            handle.write("2")
            handle.write("\n")
        mock_analysis = TextAnalyser.read_analysis(mock_analysis_filename)
        self.assertSetEqual(mock_set, mock_analysis)

    def test_read_missing_analysis(self):
        with self.assertRaises(IOError):
            TextAnalyser.read_analysis("..\\non_existent")

    def test_read_empty_analysis(self):
        mock_analysis_filename = "..\\empty.txt"
        with open(mock_analysis_filename, "w", encoding="utf-8") as handle:
            handle.write("")

        mock_analysis = TextAnalyser.read_analysis(mock_analysis_filename)
        self.assertSetEqual(mock_analysis, set())

    def test_read_analysis_invalid_frequency(self):
        mock_analysis_filename = "..\\empty.txt"
        with open(mock_analysis_filename, "w", encoding="utf-8") as handle:
            handle.write("test")
            handle.write(ANALYSIS_SEPARATOR)
            handle.write("notanumber")
            handle.write("\n")

        with self.assertRaises(ValueError):
            TextAnalyser.read_analysis(mock_analysis_filename)

    def test_read_analysis_invalid_line(self):
        mock_analysis_filename = "..\\empty.txt"
        with open(mock_analysis_filename, "w", encoding="utf-8") as handle:
            handle.write("test")
            handle.write("3")
            handle.write("\n")

        with self.assertRaises(ValueError):
            TextAnalyser.read_analysis(mock_analysis_filename)

    def test_read_mappings(self):
        mock_dict = {
            "zero": Bits(bin="00"),
            "one": Bits(bin="01"),
            "two": Bits(bin="10")
        }

        mock_file = "..\\mock_mappings.txt"
        with open(mock_file, "w", encoding="utf-8") as handle:
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
        mock_mappings_dict = TextAnalyser.read_mapping_dict(mock_file, True)
        self.assertIsInstance(mock_mappings_dict, MappingDictionary)
        self.assertTrue(mock_mappings_dict.encode_spaces)
        self.assertIsInstance(mock_mappings_dict.mappings, dict)
        self.assertDictEqual(mock_dict, mock_mappings_dict.mappings)


if __name__ == '__main__':
    unittest.main()
