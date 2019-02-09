from cmd import Cmd

from stegano import textanalyser, huffman


class UserApi(Cmd):
    intro = "Type help or ? to list commands.\n"
    prompt = "(stegano)"
    tree = 0, huffman.HuffmanTree()

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
    def do_print_tree(arg):
        if UserApi.tree[1].left is None:
            print("No Huffman tree has been created. Try create_huffman_tree.")
        elif UserApi.tree[1].left[1].path_code is None:
            reset_tree()
        else:
            huffman.print_tree(huffman_tree=UserApi.tree)

    @staticmethod
    def do_print_table(arg):
        if UserApi.tree[1].left is None:
            print("No Huffman tree has been created. Try create_huffman_tree.")
        elif UserApi.tree[1].left[1].path_code is None:
            reset_tree()
        else:
            huffman.print_table(huffman_tree=UserApi.tree)

    @staticmethod
    def do_analyse_sample(arg):
        """
        Create an analysis of the text sample placed in the root directory.
        An analysis is needed for Huffman steganography.
        """
        textanalyser.TextAnalyser.delete_analysis()
        string_length = parse_integer_arg(arg)[0]
        print("Creating analysis with n=%d" % string_length)
        textanalyser.TextAnalyser.get_analysis(string_length=string_length)


def reset_tree():
    print("The Huffman tree appears to be malformed. Resetting it.")
    UserApi.tree = 0, huffman.HuffmanTree()


def parse_integer_arg(arg):
    return tuple(map(int, arg.split()))


if __name__ == '__main__':
    UserApi().cmdloop()
