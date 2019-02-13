import warnings
from cmd import Cmd

from bitstring import Bits
from cryptography.fernet import InvalidToken

from stegano import textanalyser, huffman
from stegano.bitcoder import BitCoder
from stegano.encrypt import Encryptor
from stegano.huffman import HuffmanTree

UTF_ENCODING = "utf-16"
DEFAULT_KEY = bytes(b'xqKRXGO5RO7JLxE_jAHmA9L_uolEOjDvcGYBo2AgapM=')


class UserError(Exception):
    """Raised when the user input is malformed"""
    pass


class UserApi(Cmd):
    intro = "Type help or ? to list commands.\n"
    prompt = "(stegano)"
    tree = 0, huffman.HuffmanTree()
    key = DEFAULT_KEY
    last_symbol_length = 0

    @staticmethod
    def do_create_huffman_tree(arg):
        """
        Create a Huffman tree for reverse Huffman encoding steganography.
        A frequency analysis is needed before a tree can be created.
        Huffman steganography functions will fail before running this command.
        """
        incomplete_tree = huffman.create_from_analysis()
        huffman.allocate_path_bits(incomplete_tree)
        UserApi.tree = incomplete_tree

    @staticmethod
    def do_huffman_encode_text(arg):
        """
        Use a Huffman tree to encode some text in a cover text.
        """
        message = parse_message(arg)
        if message is None:
            print("Please provide a valid string to encode.")
        else:
            if check_tree(UserApi.tree[1]):
                print_with_heading(message, "Original")
                encrypted = get_encryptor().encrypt_bytes(str.encode(message, UTF_ENCODING))
                print_with_heading(str(encrypted), "Encrypted")
                bits = Bits(bytes=encrypted)
                output = (huffman.encode_bits_as_strings(UserApi.tree[1], bits))[1]
                print_with_heading(output, "Encoded")

    @staticmethod
    def do_huffman_decode_text(arg):
        """
        Decode a cover text into the original text using the same Huffman tree it was encoded with.
        """
        cover_text_args = parse_cover_text(arg)
        if cover_text_args is None:
            print("Please provide a valid cover text to decode.")
        else:
            message, symbol_length = cover_text_args
            if symbol_length == 0:
                symbol_length = UserApi.last_symbol_length

            if symbol_length != 0:
                UserApi.last_symbol_length = symbol_length
                if check_tree(UserApi.tree[1]):
                    decoded = huffman.encode_string_as_bits(UserApi.tree[1], message, symbol_length)
                    trimmed_bits = BitCoder.trim_bits(decoded)
                    try:
                        print_with_heading(message, "Encoded")
                        decrypted = get_encryptor().decrypt(trimmed_bits.bytes)
                        print_with_heading(str(decrypted), "Decrypted")
                        output = bytes.decode(decrypted, UTF_ENCODING)
                        print_with_heading(output, "Original")
                    except InvalidToken:
                        print("Failed to decrypt the given message. Were the correct text and symbol length provided?")
            else:
                print("Please provide the length of each symbol in the message.")

    @staticmethod
    def do_print_tree(arg):
        if check_tree(UserApi.tree[1]):
            huffman.print_tree(huffman_tree=UserApi.tree)

    @staticmethod
    def do_print_table(arg):
        if check_tree(UserApi.tree[1]):
            huffman.print_table(huffman_tree=UserApi.tree)

    @staticmethod
    def do_analyse_sample(arg):
        """
        Create an analysis of the text sample placed in the root directory.
        An analysis is needed for Huffman steganography.
        """
        symbol_length = parse_symbol_length(arg)
        if symbol_length is None:
            symbol_length = 1
        textanalyser.TextAnalyser.delete_analysis()
        UserApi.last_symbol_length = symbol_length
        print("Creating analysis with n=%d" % symbol_length)
        textanalyser.TextAnalyser.get_analysis(string_length=symbol_length)
        print("Done")

    @staticmethod
    def do_generate_key(arg):
        new_key = Encryptor.generate_key()
        print("Set key: %s -- please keep it somewhere safe" % new_key)
        UserApi.key = new_key

    @staticmethod
    def do_set_key(arg):
        new_key = arg
        print("Set key: %s" % new_key)
        UserApi.key = new_key
        try:
            get_encryptor().encrypt_string("")
        except ValueError:
            warnings.warn("The provided key may not work -- it should be 32 url-safe base64-encoded bytes.")


def reset_tree():
    print("The Huffman tree appears to be malformed. Resetting it.")
    UserApi.tree = 0, huffman.HuffmanTree()


def check_tree(huffman_tree: HuffmanTree) -> bool:
    if huffman_tree.left is None or huffman_tree.right is None:
        print("No Huffman tree has been created. Try create_huffman_tree first.")
        return False
    elif huffman_tree.left[1].path_code is None or huffman_tree.right[1].path_code is None:
        reset_tree()
        return False
    else:
        return True


def get_encryptor():
    return Encryptor(UserApi.key)


def print_with_heading(message: str, heading: str):
    header_symbol = "---------------"
    print(header_symbol)
    print(heading)
    print(header_symbol)
    print(message)


def parse_symbol_length(arg):
    integer_args = parse_integer_arg(arg)
    if integer_args:
        string_length = integer_args[0]
        if string_length > 0:
            return string_length
    return None


def parse_message(arg):
    if str.__eq__(arg, ""):
        return None
    return arg


def parse_cover_text(arg):
    args = arg.split()
    if args:
        last_arg = args[args.__len__() - 1]
        try:
            symbol_length = int(last_arg)
        except ValueError:
            symbol_length = 0

        if symbol_length == 0:
            message = arg
        else:
            message = str.rsplit(arg, " ", 1)[0]

        if str.__eq__(message, ""):
            return None

        return message, symbol_length
    return None


def parse_integer_arg(arg):
    return tuple(map(int, arg.split()))


def parse_bits_arg(arg):
    return Bits(bin=map(str, arg.split()))


if __name__ == '__main__':
    UserApi().cmdloop()
