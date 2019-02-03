import queue
import sys
from typing import Tuple, Set

from bitstring import Bits

from stegano.textanalyser import DEFAULT_ANALYSIS_FILE
from stegano.textanalyser import DEFAULT_SAMPLE_FILE
from stegano.textanalyser import TextAnalyser

Frequency = int
Symbol = Tuple[Frequency, str]
StringDefinitions = Set[Symbol]

zero_bit = Bits(bin="0")
one_bit = Bits(bin="1")


class HuffmanTree:
    def __init__(self, left=None, right=None, value: Symbol = None, path_code: Bits = None):
        self.left = left
        self.right = right
        self.value = value
        self.path_code = path_code

    def __lt__(self, other):
        if self.value is None or other.value is None:
            return False
        if self.value[0] == self.value[0]:
            return self.value[1] < other.value[1]
        else:
            return self.value[0] < other.value[0]

    def get_children(self):
        return self.left, self.right


def create_tree(string_definitions: StringDefinitions) -> Tuple[int, HuffmanTree]:
    """
    Construct Huffman tree with all leaf nodes containing values according to their frequencies
    :param string_definitions: the set of tuples of values and their frequencies
    :return: the created tree
    """
    pq = queue.PriorityQueue()

    for symbol in string_definitions:
        # Create 1-node trees from each symbol and add to queue with frequency as priority
        new_node = HuffmanTree(value=symbol)
        pq.put((symbol[0], new_node))

    while pq.qsize() > 1:
        # Take out the two smallest trees and create a new tree with them as children
        right, left = pq.get(), pq.get()
        new_tree = HuffmanTree(left, right)
        pq.put((left[0] + right[0], new_tree))

    return pq.get()


def allocate_path_bits(huffman_tree: Tuple[int, HuffmanTree], prefix: Bits = None):
    """
    Walk the given HuffmanTree and allocate bits to every path.
    Ignores any existing path codes in the given tree.
    The path code value in every node will be an entire cumulative Bit value.
    :param huffman_tree: the tuple containing Huffman (sub)tree and its cumulative priority
    :param prefix: the cumulative bits for the path up until this node. Leave empty when calling on the whole tree.
    """
    tree = huffman_tree[1]
    tree.path_code = prefix

    if tree.left is not None:
        if prefix is None:
            left_code = zero_bit
        else:
            left_code = prefix.__add__(zero_bit)
        allocate_path_bits(tree.left, left_code)

    if tree.right is not None:
        if prefix is None:
            right_code = one_bit
        else:
            right_code = prefix.__add__(one_bit)
        allocate_path_bits(tree.right, right_code)


def print_tree(huffman_tree: Tuple[int, HuffmanTree], indent: str = "", last_node: bool = True):
    sys.stdout.write(indent)
    if last_node:
        sys.stdout.write("└─")
        indent += "  "
    else:
        sys.stdout.write("├─")
        indent += "| "

    this_value = huffman_tree[1].value
    if this_value is not None:
        print("{} [{}] ({})".format(this_value[1], this_value[0], huffman_tree[1].path_code))
        # sys.stdout.write(this_value[1])
        # sys.stdout.write("  ")
        # sys.stdout.write(str(this_value[0]))
    else:
        sys.stdout.write("X ")
        sys.stdout.write("\n")

    left = huffman_tree[1].left
    right = huffman_tree[1].right

    print_last = False
    if right is not None:
        print_tree(right, indent, print_last)

    print_last = True
    if left is not None:
        print_tree(left, indent, print_last)

    sys.stdout.flush()


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


# huff = create_from_sample(string_length=1)
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
