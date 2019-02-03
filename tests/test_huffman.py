import unittest
from typing import Tuple, Set

from bitstring import Bits

from stegano import huffman
from stegano.huffman import HuffmanTree

Symbol = Tuple[str, int]
StringDefinitions = Set[Symbol]
HuffmanTreeWithFrequencies = Tuple[int, HuffmanTree]


class TestHuffman(unittest.TestCase):

    def setUp(self):
        self.string_definitions = set()
        self.string_definitions.add((10, "stega"))
        self.string_definitions.add((7, "tegan"))
        self.string_definitions.add((5, "egana"))
        self.string_definitions.add((5, "ganal"))
        self.string_definitions.add((5, "analy"))
        self.string_definitions.add((3, "nalys"))
        self.string_definitions.add((3, "alysi"))
        self.string_definitions.add((1, "lysis"))

    def test_tree_created(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        self.assertIsInstance(test_huffman[0], int)
        self.assertIsInstance(test_huffman[1], HuffmanTree)

    def test_tree_has_nodes(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        test_passed = test_huffman is not None
        self.assertTrue(test_passed, "Huffman tree was empty")
        test_passed = test_passed and is_correct_tree(test_huffman)
        self.assertTrue(test_passed, "Huffman tree was not recursively defined by at least 1 subtree")

    def test_tree_has_leaves(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        test_passed = has_correct_leaves(test_huffman)
        self.assertTrue(test_passed, "Huffman tree did not have values for all leaves")

    def test_tree_has_non_leaf_values(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        test_huffman[1].value = (1, "value")

        test_passed = has_correct_leaves(test_huffman)
        self.assertFalse(test_passed, "Huffman tree was recognised as correct even though a non-leaf had a value")

    def test_tree_missing_leaf_values(self):
        test_huffman = huffman.create_tree(self.string_definitions)

        node = test_huffman[1]
        while node.left is not None:
            node = node.left[1]
        node.value = None

        test_passed = has_correct_leaves(test_huffman)
        self.assertFalse(test_passed, "Huffman tree was recognised as correct even a leaf node was missing a value")

    def test_allocate_path_bits(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        huffman.allocate_path_bits(test_huffman)
        self.assertTrue(has_correct_bits(test_huffman, Bits()), "Huffman tree did not have correct bits for every node")

    def test_print_tree(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        huffman.print_tree(test_huffman)


def is_correct_tree(huffman_tree: HuffmanTreeWithFrequencies):
    """
    Show that given tree is recursively defined by left and right,
    where left and right can be another Huffman Tree or None
    :param huffman_tree: Huffman tree with priority values
    :return: true if tree matches definition
    """
    if huffman_tree is None:
        return True
    else:
        tree = huffman_tree[1]
        if is_correct_tree(tree.left) and is_correct_tree(tree.right):
            return True


def has_correct_leaves(huffman_tree: HuffmanTreeWithFrequencies):
    """
    Show that the given tree has values for all leaf nodes, and only leaf nodes
    :param huffman_tree: Huffman tree with priority values
    :return: true if tree has correct leaves
    """
    tree = huffman_tree[1]
    if tree.left is None and tree.right is None:
        if tree.value is None:
            return False
        else:
            return True
    else:
        if tree.value is not None:
            return False
        else:
            return has_correct_leaves(tree.left) and has_correct_leaves(tree.right)


def has_correct_bits(huffman_tree: HuffmanTreeWithFrequencies, bits: Bits):
    """
    Show that the given tree has bits for all non-root nodes, and that they accumulate correctly
    :param bits:
    :param huffman_tree:
    :return:
    """
    if huffman_tree is None:
        return True

    tree = huffman_tree[1]
    if not tree.path_code.__eq__(bits):
        return False

    left_code = bits.__add__(Bits(bin="0"))
    right_code = bits.__add__(Bits(bin="1"))
    return has_correct_bits(tree.left, left_code) and has_correct_bits(tree.right, right_code)


if __name__ == '__main__':
    unittest.main()
