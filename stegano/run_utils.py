import argparse

from bitstring import Bits, CreationError

from stegano.encrypt import Encryptor

UTF_ENCODING = "utf-8"
DEFAULT_KEY = bytes(b'xqKRXGO5RO7JLxE_jAHmA9L_uolEOjDvcGYBo2AgapM=')


def prefix_filename(subfolder: str, filename: str) -> str:
    if subfolder is not None:
        return "..\\" + subfolder + "\\" + filename
    return "..\\" + filename


def read_input_file(filename: str, encoding="utf-8") -> str:
    try:
        with open(filename, "r", encoding=encoding) as handle:
            text = handle.read()
            return text
    except IOError:
        print("Could not read file " + filename)


def write_output_file(filename: str, data: str, encoding="utf-8"):
    try:
        with open(filename, "w", encoding=encoding) as handle:
            handle.write(data)
    except IOError:
        print("Could not write to file " + filename)


parser = argparse.ArgumentParser(description="Utility commands")
parser.add_argument("operation", metavar="operation", type=str,
                    choices=["encrypt", "decrypt", "generateKey", "charEncode", "charDecode"],
                    help="select operation")
parser.add_argument("--subfolder", metavar="subfolder", type=str,
                    help="optional subdirectory for input and output files")
parser.add_argument("--encoding", metavar="encoding", type=str,
                    help="name of encoding method; default UTF-8")
parser.add_argument("--key", metavar="key", type=str,
                    help="string representation of private key")
parser.add_argument("--input", metavar="input", type=str, help="filename of input")
parser.add_argument("--output", metavar="output", type=str, help="filename of output")

args = parser.parse_args()

operation: str = args.operation

if operation.__eq__("encrypt"):
    input_filename: str = prefix_filename(args.subfolder, args.input)
    output_filename: str = prefix_filename(args.subfolder, args.output)
    key: bytes = None if args.key is None else bytes(args.key, encoding="utf-8")

    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    if key is None:
        key = DEFAULT_KEY

    ciphertext = read_input_file(input_filename)
    try:
        ciphertext_bits = Bits(bin=ciphertext)
    except CreationError:
        raise ValueError("Provided input was not a valid bitstring.")
    if ciphertext_bits.__eq__(Bits()):
        raise ValueError("Provided input was empty.")

    plaintext = Bits(bytes=Encryptor(key).encrypt_bytes(ciphertext_bits.bytes))
    print("Input encrypted.")

    write_output_file(output_filename, plaintext.bin)
    print("Ciphertext written to {}".format(output_filename))

elif operation.__eq__("decrypt"):
    input_filename: str = prefix_filename(args.subfolder, args.input)
    output_filename: str = prefix_filename(args.subfolder, args.output)
    key: bytes = None if args.key is None else bytes(args.key, encoding="utf-8")

    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    if key is None:
        key = DEFAULT_KEY

    ciphertext = read_input_file(input_filename)
    try:
        ciphertext_bits = Bits(bin=ciphertext)
    except CreationError:
        raise ValueError("Provided input was not a valid bitstring.")
    if ciphertext_bits.__eq__(Bits()):
        raise ValueError("Provided input was empty.")

    plaintext = Bits(bytes=Encryptor(key).decrypt(ciphertext_bits.bytes))
    print("Input decrypted.")

    write_output_file(output_filename, plaintext.bin)
    print("Plaintext written to {}".format(output_filename))

elif operation.__eq__("generateKey"):
    new_key = Encryptor.generate_key()
    print("SAVE THE FOLLOWING KEY EXACTLY AS WRITTEN:")
    print(new_key.decode("utf-8"))
