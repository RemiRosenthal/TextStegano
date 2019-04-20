import argparse

from bitstring import Bits, CreationError

from stegano import wtdict, huffman
from stegano.wtdict import WordTypeDictionary


def prefix_filename(subfolder: str, filename: str) -> str:
    if subfolder is not None:
        return "..\\" + subfolder + "\\" + filename
    return "..\\" + filename


def read_input_file(filename: str) -> str:
    try:
        with open(filename, "r", encoding="utf-8") as handle:
            text = handle.read()
            return text
    except IOError:
        print("Could not read file " + filename)


def write_output_file(filename: str, data: str):
    try:
        with open(filename, "w", encoding="utf-8") as handle:
            handle.write(data)
    except IOError:
        print("Could not write to file " + filename)


parser = argparse.ArgumentParser(description="Commands for reverse Huffman steganographic coding")
parser.add_argument("operation", metavar="operation", type=str,
                    choices=["createTree", "encodeBits", "decodeCover"],
                    help="select operation")
parser.add_argument("--subfolder", metavar="subfolder", type=str,
                    help="optional subdirectory for input and output files")
parser.add_argument("--analysis", metavar="analysis", type=str, help="filename of frequency analysis")
parser.add_argument("--tree", metavar="tree", type=str, help="filename of Huffman tree")
parser.add_argument("--input", metavar="input", type=str, help="filename of secret message / cover text input")
parser.add_argument("--output", metavar="output", type=str, help="filename of secret message / cover text output")

args = parser.parse_args()

operation: str = args.operation

if operation.__eq__("createTree"):
    """
    Create a tree from a word analysis.
    """
    analysis_filename: str = prefix_filename(args.subfolder, args.analysis)
    tree_filename: str = args.tree

    if tree_filename is None:
        raise ValueError("Filename for Huffman tree was not provided.")
    else:
        tree_filename = prefix_filename(args.subfolder, tree_filename)

    if analysis_filename is None:
        raise ValueError("Filename for frequency analysis was not provided.")

    tree = huffman.create_from_analysis(analysis_filename)
    huffman.allocate_path_bits(tree)
    print("Huffman tree created.")

    huffman.save_tree(tree[1], tree_filename)
    print("Saved to {}".format(tree_filename))

elif operation.__eq__("encodeBits"):
    """
    Use a Huffman tree to encode some bits into a cover text.
    """
    tree_filename: str = args.tree
    input_filename: str = args.input
    output_filename: str = args.output

    if tree_filename is None:
        raise ValueError("Filename for Huffman tree was not provided.")
    else:
        tree_filename = prefix_filename(args.subfolder, tree_filename)
    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    else:
        input_filename = prefix_filename(args.subfolder, input_filename)
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    else:
        output_filename = prefix_filename(args.subfolder, output_filename)

    input_message = read_input_file(input_filename)
    try:
        message_bits = Bits(bin=input_message)
    except CreationError:
        raise ValueError("Provided input was not a valid bitstring.")
    if message_bits.__eq__(Bits()):
        raise ValueError("Provided input was empty.")

    huffman_tree = huffman.load_tree(tree_filename)
    print("Huffman tree loaded.")

    _, cover_text = huffman.encode_bits_as_strings(huffman_tree[1], message_bits)
    write_output_file(output_filename, cover_text)
    print("Cover text written to {}".format(output_filename))
