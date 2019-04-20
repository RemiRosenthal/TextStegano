import argparse

from bitstring import Bits, CreationError

from stegano.encrypt import Encryptor
from stegano.filehandler import prefix_filename, DEFAULT_ENCODING, read_input_file, write_output_file

DEFAULT_KEY = bytes(b'xqKRXGO5RO7JLxE_jAHmA9L_uolEOjDvcGYBo2AgapM=')

parser = argparse.ArgumentParser(description="Utility commands")
parser.add_argument("operation", metavar="operation", type=str,
                    choices=["encrypt", "decrypt", "generateKey", "charEncode", "charDecode"],
                    help="select operation")
parser.add_argument("--subfolder", metavar="subfolder", type=str,
                    help="optional subdirectory for input and output files")
parser.add_argument("--encoding", metavar="encoding", type=str,
                    help="name of encoding method; default utf_8")
parser.add_argument("--key", metavar="key", type=str,
                    help="string representation of private key")
parser.add_argument("--input", metavar="input", type=str, help="filename of input")
parser.add_argument("--output", metavar="output", type=str, help="filename of output")

args = parser.parse_args()

operation: str = args.operation

if operation.__eq__("encrypt"):
    input_filename: str = prefix_filename(args.subfolder, args.input)
    output_filename: str = prefix_filename(args.subfolder, args.output)
    key: bytes = None if args.key is None else bytes(args.key, encoding=DEFAULT_ENCODING)

    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    if key is None:
        key = DEFAULT_KEY

    message_bits = read_input_file(input_filename)
    try:
        ciphertext_bits = Bits(bin=message_bits)
    except CreationError:
        raise ValueError("Provided input was not a valid bitstring.")
    if ciphertext_bits.__eq__(Bits()):
        raise ValueError("Provided input was empty.")

    bits = Bits(bytes=Encryptor(key).encrypt_bytes(ciphertext_bits.bytes))
    print("Input encrypted.")

    write_output_file(output_filename, bits.bin)
    print("Ciphertext written to {}".format(output_filename))

elif operation.__eq__("decrypt"):
    input_filename: str = prefix_filename(args.subfolder, args.input)
    output_filename: str = prefix_filename(args.subfolder, args.output)
    key: bytes = None if args.key is None else bytes(args.key, encoding=DEFAULT_ENCODING)

    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    if key is None:
        key = DEFAULT_KEY

    message_bits = read_input_file(input_filename)
    try:
        ciphertext_bits = Bits(bin=message_bits)
    except CreationError:
        raise ValueError("Provided input was not a valid bitstring.")
    if ciphertext_bits.__eq__(Bits()):
        raise ValueError("Provided input was empty.")

    bits = Bits(bytes=Encryptor(key).decrypt(ciphertext_bits.bytes))
    print("Input decrypted.")

    write_output_file(output_filename, bits.bin)
    print("Plaintext written to {}".format(output_filename))

elif operation.__eq__("generateKey"):
    new_key = Encryptor.generate_key()
    print("SAVE THE FOLLOWING KEY EXACTLY AS WRITTEN:")
    print(new_key.decode(DEFAULT_ENCODING))

elif operation.__eq__("charEncode"):
    input_filename: str = prefix_filename(args.subfolder, args.input)
    output_filename: str = prefix_filename(args.subfolder, args.output)
    encoding: str = args.encoding

    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    if encoding is None:
        encoding = DEFAULT_ENCODING

    message = read_input_file(input_filename, encoding)
    if message.__eq__(""):
        raise ValueError("Provided input was empty.")

    try:
        message_bits = Bits(bytes=str.encode(message, encoding))
    except LookupError:
        raise ValueError("Provided encoding \"{}\" is not valid.".format(encoding)) from None
    print("Input encoded as binary using {}.".format(encoding))

    write_output_file(output_filename, message_bits.bin, encoding)
    print("Binary output written to {}".format(output_filename))

elif operation.__eq__("charDecode"):
    input_filename: str = prefix_filename(args.subfolder, args.input)
    output_filename: str = prefix_filename(args.subfolder, args.output)
    encoding: str = args.encoding

    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    if encoding is None:
        encoding = DEFAULT_ENCODING

    message_str = read_input_file(input_filename, encoding)
    try:
        message_bits = Bits(bin=message_str)
    except CreationError:
        raise ValueError("Provided input was not a valid bitstring.")
    if message_bits.__eq__(Bits()):
        raise ValueError("Provided input was empty.")

    try:
        message = bytes.decode(message_bits.bytes, encoding)
    except UnicodeDecodeError:
        raise ValueError("Failed to decode input using \"{}\" encoding.".format(encoding)) from None
    print("Input decoded from binary using {}.")

    write_output_file(output_filename, message, encoding)
    print("Output written to {}".format(output_filename))
