import unittest

from stegano import textanalyser


class MyTestCase(unittest.TestCase):
    def test_normalise_mock_frequencies(self):
        mock_set = set()
        mock_set.add(("string", 75))
        mock_set.add(("word", 25))

        mock_return_set = set()
        mock_return_set.add(("string", 0.75))
        mock_return_set.add(("word", 0.25))

        testtextanalyser = textanalyser.TextAnalyser
        return_set = testtextanalyser.normalise_frequencies(mock_set)
        self.assertSetEqual(return_set, mock_return_set, "Mock set frequencies were not normalised as expected")

    def test_normalise_empty_frequencies(self):
        testtextanalyser = textanalyser.TextAnalyser
        self.assertSetEqual(testtextanalyser.normalise_frequencies(set()), set())


if __name__ == '__main__':
    unittest.main()
