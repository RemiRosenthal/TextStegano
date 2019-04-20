import argparse

from stegano.filehandler import prefix_filename, DEFAULT_ENCODING
from stegano.textanalyser import TextAnalyser

parser = argparse.ArgumentParser(description="Commands for text analysis")
parser.add_argument("operation", metavar="operation", type=str,
                    choices=["analyseSample"],
                    help="select operation")
parser.add_argument("--subfolder", metavar="subfolder", type=str,
                    help="optional subdirectory for input and output files")
parser.add_argument("--encoding", metavar="encoding", type=str,
                    help="name of encoding method; default utf_8")
parser.add_argument("--input", metavar="input", type=str, help="filename of input")
parser.add_argument("--output", metavar="output", type=str, help="filename of output")
parser.add_argument("--symbolLen", metavar="symbolLen", type=int, help="length of each symbol for frequency analysis")

args = parser.parse_args()

operation: str = args.operation

if operation.__eq__("analyseSample"):
    input_filename: str = prefix_filename(args.subfolder, args.input)
    output_filename: str = prefix_filename(args.subfolder, args.output)
    symbol_length: int = args.symbolLen
    encoding: str = args.encoding

    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    if symbol_length is None:
        symbol_length = 1
    elif symbol_length < 1:
        raise ValueError("Symbol length provided was not valid.")
    if encoding is None:
        encoding = DEFAULT_ENCODING

    print("Analysing input file {} with symbol length {}.".format(input_filename, symbol_length))
    analysis = TextAnalyser.analyse_sample(input_filename, symbol_length)

    TextAnalyser.print_analysis(analysis, output_filename, encoding)
    print("Frequency analysis written to {}".format(output_filename))
