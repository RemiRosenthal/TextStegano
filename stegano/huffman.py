from bitstring import BitArray
from dahuffman import HuffmanCodec

from stegano.textanalyser import DEFAULT_ANALYSIS_FILE
from stegano.textanalyser import DEFAULT_SAMPLE_FILE
from stegano.textanalyser import TextAnalyser


class HuffmanTree:
    @staticmethod
    def from_file(sample_filename=DEFAULT_SAMPLE_FILE, analysis_filename=DEFAULT_ANALYSIS_FILE,
                  string_length=1):
        string_definitions = TextAnalyser.get_analysis(sample_filename, analysis_filename, string_length)
        if string_definitions:
            return HuffmanCodec.from_frequencies(dict(string_definitions))  # TODO new implementation needed
        else:
            raise IOError("Could not read or generate text analysis")

    @staticmethod
    def from_sample(sample_filename=DEFAULT_SAMPLE_FILE, analysis_filename=DEFAULT_ANALYSIS_FILE, string_length=1):
        TextAnalyser.print_analysis(TextAnalyser.analyse_sample(sample_filename, string_length), analysis_filename)
        return HuffmanTree.from_file(sample_filename, analysis_filename, string_length)




huff = HuffmanTree.from_sample(string_length=1)
#huff = HuffmanTree.from_file()
huff.print_code_table()
encoded = huff.encode("uo")
print(encoded)
z = list(encoded)
print(z)
print(encoded.decode("utf-16"))
bits = BitArray(bytes=encoded)
print(bits.bin)
print(huff.decode(BitArray(bin="0b00000101").bytes))
print(huff.decode(encoded))
