import bisect
import queue
import sys
import warnings
from typing import Tuple, Set, Optional

from bitstring import Bits
from tabulate import tabulate

from stegano.textanalyser import DEFAULT_ANALYSIS_FILE
from stegano.textanalyser import DEFAULT_SAMPLE_FILE
from stegano.textanalyser import TextAnalyser

Frequency = int
Symbol = Tuple[str, Frequency]
StringDefinitions = Set[Symbol]

zero_bit = Bits(bin="0")
one_bit = Bits(bin="1")


class HuffmanTree:
    def __init__(self, left=None, right=None, value: Symbol = None, path_code: Bits = None):
        self.left = left
        self.right = right
        self.value = value
        self.path_code = path_code

    def __eq__(self, other):
        if self is None and other is None:
            return True

        # Value
        if self.value is None:
            if other.value is not None:
                return False
        else:
            if self.value != other.value:
                return False

        # Path code
        if self.path_code is None:
            if other.path_code is not None:
                return False
        else:
            if self.path_code != other.path_code:
                return False

        # Left tree
        if not self.left.__eq__(other.left):
            return False

        # Right tree
        if not self.right.__eq__(other.right):
            return False

        return True

    def __hash__(self):
        return hash(repr(self))

    def __lt__(self, other):
        if self.value is None or other.value is None:
            return False
        if self.value[0] == self.value[0]:
            return self.value[1] < other.value[1]
        else:
            return self.value[0] < other.value[0]

    def get_children(self):
        return self.left, self.right


class HuffmanError(Exception):
    """Raised when something went logically wrong with a Huffman Tree"""
    pass


def create_tree(string_definitions: StringDefinitions) -> Tuple[int, HuffmanTree]:
    """
    Construct Huffman tree with all leaf nodes containing values according to their frequencies
    :param string_definitions: the set of tuples of values and their frequencies
    :return: the created tree
    """
    pq = queue.PriorityQueue()

    for symbol in sorted(string_definitions):
        # Create 1-node trees from each symbol and add to queue with frequency as priority
        new_node = HuffmanTree(value=symbol)
        pq.put((symbol[1], new_node))

    while pq.qsize() > 1:
        # Take out the two smallest trees and create a new tree with them as children
        right, left = pq.get(), pq.get()
        new_tree = HuffmanTree(left, right)
        pq.put((left[0] + right[0], new_tree))

    return pq.get()


def allocate_path_bits(huffman_tree: Tuple[int, HuffmanTree], prefix: Bits = None):
    """
    Walk the given HuffmanTree and allocate bits to every path.
    Ignores and overwrites any existing path codes in the given tree.
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


def allocate_path_bits_it(huffman_tree: Tuple[int, HuffmanTree]):
    tree = huffman_tree[1]
    stack = [(Bits(), tree)]

    while stack:
        bits, this_tree = stack.pop(0)
        if this_tree.left is None and this_tree.right is None:
            this_tree.path_code = bits
        else:
            stack.append((bits.__add__(zero_bit), tree.left[1]))
            stack.append((bits.__add__(one_bit), tree.right[1]))


def encode_bits_as_strings(tree: HuffmanTree, bits: Bits, string_prefix: str = "") -> \
        Tuple[Bits, str]:
    """
    Given a bit stream and a Huffman tree, return the appropriate string of symbols.

    The output will match the statistical distribution of the sample it was made with as much as possible,
    although limited by the necessity of an unambiguous HuffmanTree structure.

    If the Huffman tree does not have path bits to match the input exactly, it will append 0s until the function can
    complete.

    :param tree: a Huffman tree with path bits allocated
    :param bits: the input bits
    :param string_prefix: the so-far accumulated string. Leave empty when calling manually
    :return: a Tuple of the remaining bits and the accumulated string made up of symbols in the Huffman tree
    """
    if bits is None or bits.__eq__(Bits()):
        return Bits(), string_prefix

    if tree.left is not None and tree.right is not None:  # This tree has subtrees
        left_tree = tree.left[1]
        right_tree = tree.right[1]
        if left_tree.path_code is None or right_tree.path_code is None:
            raise HuffmanError("When encoding bits as strings, a node was missing a path code")
        else:
            if bits.startswith(left_tree.path_code):
                remaining_bits, accumulated_string = encode_bits_as_strings(left_tree, bits, string_prefix)
            elif bits.startswith(right_tree.path_code):
                remaining_bits, accumulated_string = encode_bits_as_strings(right_tree, bits, string_prefix)
            else:
                # Binary sequence does not match a leaf value. Must pad with 0s
                padded_bits = bits.__add__(Bits(bin="0"))
                return padded_bits, string_prefix

            if tree.path_code is None:  # This tree is a root node
                if bits is None:  # We are out of bits, so we can return the final string
                    return remaining_bits, accumulated_string
                else:  # Continue recursively processing the remaining bits
                    return encode_bits_as_strings(tree, remaining_bits, accumulated_string)
            else:
                return remaining_bits, accumulated_string
    elif tree.left is None and tree.right is None:  # This tree is a leaf node
        if tree.path_code is None:
            raise HuffmanError("When encoding bits as strings, a leaf node was missing a path code")
        else:
            if bits.startswith(tree.path_code):
                accumulated_string = string_prefix + tree.value[0]
                if bits.__eq__(tree.path_code):
                    remaining_bits = None
                else:
                    remaining_bits = bits[tree.path_code.length:]
                return remaining_bits, accumulated_string
            else:
                warnings.warn("When encoding bits as strings, some unencodable bits were left over")
                return bits, string_prefix
    else:
        raise HuffmanError("The given Huffman tree contained a node with exactly 1 child tree")


def search_tree_for_symbol(huffman_tree: HuffmanTree, symbol: str) -> Bits:
    if huffman_tree.left is not None and huffman_tree.right is not None:
        left_tree = huffman_tree.left[1]
        right_tree = huffman_tree.right[1]

        left_result = search_tree_for_symbol(left_tree, symbol)
        if left_result is not None:
            return left_result

        right_result = search_tree_for_symbol(right_tree, symbol)
        if right_result is not None:
            return right_result
    else:
        if huffman_tree.value[0].__eq__(symbol):
            return huffman_tree.path_code


def encode_string_as_bits(huffman_tree: HuffmanTree, input_string: str, symbol_length: int) -> Bits:
    """
    Given a string of characters, use the HuffmanTree to to encode it as a matching stream of bits.

    The given string must be valid with respect to the HuffmanTree (i.e. it should be a string as generated from
    encode_bits_as_strings).
    """
    if symbol_length < 1:
        raise ValueError("An invalid symbol length was specified.")

    cover_text_length = input_string.__len__()
    if symbol_length > cover_text_length:
        warnings.warn("Cover text is smaller than the given symbol length. Padding with spaces.")
        padding = " " * (symbol_length - cover_text_length)
        input_string = input_string.__add__(padding)
        cover_text_length = input_string.__len__()
    elif not cover_text_length % symbol_length == 0:
        warnings.warn("Cover text is not a multiple of the given symbol length. Padding with spaces.")
        padding = " " * (symbol_length - (cover_text_length % symbol_length))
        input_string = input_string.__add__(padding)
        cover_text_length = input_string.__len__()
    reps = cover_text_length // symbol_length

    bits = Bits()
    for x in range(0, reps):
        start_index = symbol_length * x
        this_symbol = input_string[start_index:start_index + symbol_length]
        symbol_bits = search_tree_for_symbol(huffman_tree, this_symbol)
        bits = bits.__add__(symbol_bits)

    return bits


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
        print("{} [{}] ({})".format(this_value[0], this_value[1], huffman_tree[1].path_code))
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


def flatten_tree(huffman_tree: Tuple[int, HuffmanTree]) -> list:
    """
    Turn a Huffman tree into a list ordered by value
    :param huffman_tree: the huffman_tree to flatten
    :return: a list containing all nodes in that tree in value order
    """
    this_tree = huffman_tree[1]
    left_tree = this_tree.left
    right_tree = this_tree.right

    if left_tree is not None and right_tree is not None:
        this_list = flatten_tree(left_tree)
        for item in flatten_tree(right_tree):
            bisect.insort_left(this_list, item)
    else:  # Leaf node
        this_list = list()
        this_tuple = this_tree.value[0], this_tree.value[1], this_tree.path_code
        this_list.append(this_tuple)

    return this_list


def _format_binary(node: Tuple[str, int, Optional[Bits]]):
    if node[2] is None:
        return node[0], node[1], "N/A"
    else:
        return node[0], node[1], node[2].bin


def print_table(huffman_tree: Tuple[int, HuffmanTree]):
    print(tabulate(map(_format_binary, flatten_tree(huffman_tree)), headers=["Value", "Freq", "Bits"]))
    print()


def create_from_analysis(analysis_filename=DEFAULT_ANALYSIS_FILE):
    """
    Read a frequency analysis file and construct a Huffman tree, without path bits.
    :param sample_filename: The relative location of the sample text file. Needed in case the analysis does not exist.
    :param analysis_filename: The relative location of the analysis file.
    :param string_length: The length of every string in the frequency analysis
    :return: A Huffman tree without bits allocated to each node
    """
    string_definitions = TextAnalyser.read_analysis(analysis_filename)
    if string_definitions:
        tree = create_tree(string_definitions)
        return tree
    else:
        raise IOError("Could not read or generate text analysis")


def create_from_sample(sample_filename=DEFAULT_SAMPLE_FILE, analysis_filename=DEFAULT_ANALYSIS_FILE,
                       string_length=1):
    """
    Create a frequency analysis file from a text sample. Then, construct a Huffman tree, without path bits.
    :param sample_filename: The relative location of the sample text file.
    :param analysis_filename: The desired relative location of the generated analysis file.
    :param string_length: The length of every string in the frequency analysis
    :return: A Huffman tree without bits allocated to each node
    """
    TextAnalyser.print_analysis(TextAnalyser.analyse_sample(sample_filename, string_length), analysis_filename)
    return create_from_analysis(sample_filename)


def tree_depth(huffman_tree: Tuple[int, HuffmanTree]) -> int:
    """
    Find the depth of the longest branch in the tree
    """
    pass