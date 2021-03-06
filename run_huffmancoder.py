import argparse

from bitstring import Bits, CreationError

from stegano import huffman
from stegano.filehandler import prefix_filename, read_input_file, \
    write_output_file


def print_with_heading(message: str, heading: str):
    header_symbol = "---------------"
    print(header_symbol)
    print(heading)
    print(header_symbol)
    print(message)


parser = argparse.ArgumentParser(
    description="Commands for reverse Huffman steganographic coding")
parser.add_argument("operation", metavar="operation", type=str,
                    choices=["createTree", "encodeBits",
                             "decodeCover", "exportMappings",
                             "analyseTree"], help="select operation")
parser.add_argument("--subfolder", metavar="subfolder", type=str,
                    help="optional subdirectory for input and "
                         "output files")
parser.add_argument("--analysis", metavar="analysis", type=str,
                    help="filename of frequency analysis")
parser.add_argument("--tree", metavar="tree", type=str,
                    help="filename of Huffman tree")
parser.add_argument("--input", metavar="input", type=str,
                    help="filename of secret message / cover text "
                         "input")
parser.add_argument("--output", metavar="output", type=str,
                    help="filename of output")
parser.add_argument("--symbolLen", metavar="symbolLen", type=int,
                    help="symbol length of cover text")

args = parser.parse_args()

operation: str = args.operation

if operation.__eq__("createTree"):
    """
    Create a tree from a word analysis.
    """
    analysis_filename: str = prefix_filename(args.subfolder,
                                             args.analysis)
    tree_filename: str = args.tree

    if tree_filename is None:
        raise ValueError(
            "Filename for Huffman tree was not provided.")
    else:
        tree_filename = prefix_filename(args.subfolder, tree_filename)

    if analysis_filename is None:
        raise ValueError(
            "Filename for frequency analysis was not provided.")

    tree = huffman.create_from_analysis(analysis_filename)
    huffman.allocate_path_bits(tree)
    print("Huffman tree created.")

    huffman.save_tree(tree[1], tree_filename)
    print("Saved to {}.".format(tree_filename))

elif operation.__eq__("encodeBits"):
    """
    Use a Huffman tree to encode some bits into a cover text.
    """
    tree_filename: str = args.tree
    input_filename: str = args.input
    output_filename: str = args.output

    if tree_filename is None:
        raise ValueError(
            "Filename for Huffman tree was not provided.")
    else:
        tree_filename = prefix_filename(args.subfolder, tree_filename)
    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    else:
        input_filename = prefix_filename(args.subfolder,
                                         input_filename)
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    else:
        output_filename = prefix_filename(args.subfolder,
                                          output_filename)

    input_message = read_input_file(input_filename)
    try:
        message_bits = Bits(bin=input_message)
    except CreationError:
        raise ValueError("Provided input was not a valid bitstring.")
    if message_bits.__eq__(Bits()):
        raise ValueError("Provided input was empty.")

    huffman_tree = huffman.load_tree(tree_filename)
    if huffman_tree is None or huffman_tree[1] is None:
        print("Given Huffman tree was empty.")
        exit()
    print("Huffman tree loaded.")

    _, cover_text = huffman.encode_bits_as_strings(huffman_tree[1],
                                                   message_bits)
    write_output_file(output_filename, cover_text)
    print("Cover text written to {}.".format(output_filename))

elif operation.__eq__("decodeCover"):
    """
    Decode a cover text into the original text using the same 
    Huffman tree it was encoded with.
    """
    tree_filename: str = args.tree
    input_filename: str = args.input
    output_filename: str = args.output
    symbol_length: int = args.symbolLen

    if tree_filename is None:
        raise ValueError(
            "Filename for Huffman tree was not provided.")
    else:
        tree_filename = prefix_filename(args.subfolder, tree_filename)
    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    else:
        input_filename = prefix_filename(args.subfolder,
                                         input_filename)
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    else:
        output_filename = prefix_filename(args.subfolder,
                                          output_filename)
    if symbol_length is None or symbol_length < 1:
        raise ValueError("Symbol length provided was not valid.")

    input_cover = read_input_file(input_filename)
    if input_cover.__eq__(""):
        raise ValueError("Provided input was empty.")

    huffman_tree = huffman.load_tree(tree_filename)
    print("Huffman tree loaded.")

    if not huffman.has_given_symbol_length(huffman_tree,
                                           symbol_length):
        raise ValueError(
            "Given Huffman tree did not contain symbols matching "
            "the given symbol length.")

    message_bits = huffman.encode_string_as_bits(huffman_tree[1],
                                                 input_cover,
                                                 symbol_length)
    write_output_file(output_filename, message_bits.bin)
    print("Secret message written to {}.".format(output_filename))

elif operation.__eq__("exportMappings"):
    """
    Load a Huffman tree, search it for all word-bit mappings, 
    and export them as a list.
    """
    tree_filename: str = args.tree
    output_filename: str = args.output

    if tree_filename is None:
        raise ValueError(
            "Filename for Huffman tree was not provided.")
    else:
        tree_filename = prefix_filename(args.subfolder, tree_filename)
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    else:
        output_filename = prefix_filename(args.subfolder,
                                          output_filename)

    huffman_tree = huffman.load_tree(tree_filename)
    print("Huffman tree loaded.")

    symbol_list = huffman.tree_to_symbols(huffman_tree)
    mappings = sorted(((x.lower(), z) for x, y, z in symbol_list),
                      key=lambda m: (m[1].bin.__len__(), m[1].uint))
    output = ""
    for value, bits in mappings:
        output = output + value + "," + bits.bin + "\n"
    write_output_file(output_filename, output)
    print("Mappings written to {}.".format(output_filename))

elif operation.__eq__("analyseTree"):
    """
    Load a Huffman tree and print some statistics.
    """
    tree_filename: str = args.tree

    if tree_filename is None:
        raise ValueError(
            "Filename for Huffman tree was not provided.")
    else:
        tree_filename = prefix_filename(args.subfolder, tree_filename)

    huffman_tree = huffman.load_tree(tree_filename)
    if huffman_tree is None or huffman_tree[1] is None:
        raise ValueError("Provided Huffman tree was empty.")
    print("Huffman tree loaded.")

    path_codes = huffman.get_tree_leaf_codes(huffman_tree)
    print_with_heading("{}".format(len(path_codes)),
                       "Number of Symbols in Tree")
    expected_length = huffman.get_set_expected_length(path_codes)
    print_with_heading("{}".format(expected_length),
                       "Expected Length of Path Codes in Tree")
    average_length = huffman.get_set_average_length(path_codes)
    print_with_heading("{}".format(average_length),
                       "Average Length of Path Codes in Tree")
