import queue

from bitstring import Bits

from stegano.textanalyser import DEFAULT_ANALYSIS_FILE
from stegano.textanalyser import DEFAULT_SAMPLE_FILE
from stegano.textanalyser import TextAnalyser

from dahuffman import HuffmanCodec


class HuffmanTree:
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def get_children(self):
        return self.left, self.right


def create_tree(string_definitions):
    pq = queue.PriorityQueue()

    for string_def in string_definitions:
        pq.put(string_def)

    while pq.qsize() > 1:
        l, r = pq.get(), pq.get()
        this_node = HuffmanTree(l, r)
        pq.put((l[0] + r[0], this_node))

    return pq.get()


def encode_bits_as_strings(self):
    """
    Given a bit stream, use the HuffmanTree to return the matching string of characters.

    The output will match the statistical distribution of the sample it was made with as much as possible,
    although limited by the necessity of an unambiguous HuffmanTree structure.
    :return:
    """
    pass


def encode_string_as_bits(self):
    """
    Given a string of characters, use the HuffmanTree to to encode it as a matching stream of bits.

    The given string must be valid with respect to the HuffmanTree (i.e. it should be a string as generated from
    encode_bits_as_strings).
    """
    pass


def assign_values(node, prefix="", code=None):
    if code is None:
        code = {}

    # Left subtree
    if isinstance(node[1].left[1], HuffmanTree):
        assign_values(node[1].left, prefix + "0", code)
    else:  # or leaf
        code[node[1].left[1]] = prefix + "0"

    # Right subtree
    if isinstance(node[1].right[1], HuffmanTree):
        assign_values(node[1].right, prefix + "1", code)
    else:  # or leaf
        code[node[1].right[1]] = prefix + "1"

    return code


def print_table(string_definitions: set, code):
    for i in sorted(string_definitions, reverse=True):
        print(i[1], '{:6.2f}'.format(i[0], code[i[1]]))


def create_from_analysis(sample_filename=DEFAULT_SAMPLE_FILE, analysis_filename=DEFAULT_ANALYSIS_FILE,
                         string_length=1):
    string_definitions = TextAnalyser.get_analysis(sample_filename, analysis_filename, string_length)
    if string_definitions:
        # return HuffmanCodec.from_frequencies(dict(string_definitions))  # TODO new implementation needed
        tree = create_tree(string_definitions)
        code = assign_values(tree)
        print_table(string_definitions, code)
        return tree

    else:
        raise IOError("Could not read or generate text analysis")


def create_from_sample(sample_filename=DEFAULT_SAMPLE_FILE, analysis_filename=DEFAULT_ANALYSIS_FILE,
                       string_length=1):
    TextAnalyser.print_analysis(TextAnalyser.analyse_sample(sample_filename, string_length), analysis_filename)
    return create_from_analysis(sample_filename, analysis_filename, string_length)


huff = create_from_sample(string_length=1)
# huff = HuffmanTree.from_file()
# huff.print_code_table()


"""
original = "Okay, this is epic"
print("Original = ", original)
encoded = original.encode()
encoded = encoded + (bytearray(1))
print("Bytes = ", list(encoded))

# sent = huff.decode_from_bitarray(encoded)
# sent = huff.decode(encoded)
# sent = ""
sent = huff.decode(encoded)
# Data gets transferred as last printed
print("Encoded and transferred text = ", sent)

decoded = ""
# assert length is multiple of 3
for x in range(0, len(sent)):
    y = sent[x:x + 3]
    decoded = decoded + huff.encode(y)
    x += 3
decoded = huff.encode(sent)
# decoded = huff.encode_as_bitarray(sent)
# decoded = ""
print("Decoded bytes = ", list(decoded))
decoded = decoded[:-1]

print("Decoded text = ", decoded.decode())
"""