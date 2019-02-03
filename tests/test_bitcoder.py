import unittest
from stegano import bitcoder


class TestBitCoder(unittest.TestCase):
    def test_weird_to_bits(self):
        testbitcoder = bitcoder.BitCoder
        self.assertEqual(testbitcoder.text_to_bits("ह𐍈"), "11100000101001001011100111110000100100001000110110001000",
                         "Failed to encode string as bits")

    def test_weird_from_bits(self):
        testbitcoder = bitcoder.BitCoder
        self.assertEqual(testbitcoder.text_from_bits("11100000101001001011100111110000100100001000110110001000"), "ह𐍈",
                         "Failed to decode bits as string")

    def test_long_to_bits(self):
        testbitcoder = bitcoder.BitCoder
        self.assertEqual(testbitcoder.text_to_bits("This is a nice, long sentence."),
                         "010101000110100001101001011100110010000001101001011100110010000001100001001000000110111001101001011000110110010100101100001000000110110001101111011011100110011100100000011100110110010101101110011101000110010101101110011000110110010100101110",
                         "Failed to encode string as bits")

    def test_long_from_bits(self):
        testbitcoder = bitcoder.BitCoder
        self.assertEqual(testbitcoder.text_from_bits(
            "0101010001101000011010010111001100100000011100110111010001110010011010010110111001100111001000000110111101100110001000000111010001100101011110000111010001110011001000000110100101110011001000000111000001110010011001010111010001110100011110010010000001101100011011110110111001100111001011000010000001110100011011110110111100100001"),
            "This string of texts is pretty long, too!",
            "Failed to decode bits as string")


if __name__ == '__main__':
    unittest.main()
