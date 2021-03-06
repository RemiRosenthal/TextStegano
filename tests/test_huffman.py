import unittest
from typing import Tuple, Set

from bitstring import Bits

from stegano import huffman
from stegano.huffman import HuffmanTree

Symbol = Tuple[str, int]
StringDefinitions = Set[Symbol]
HuffmanTreeWithFrequencies = Tuple[int, HuffmanTree]

TEST_TREE_FILE = "..\\test_data\\huffman_tree.json"
TEST_EMPTY_TREE_FILE = ".\\test_data\\empty_json.json"


class TestHuffman(unittest.TestCase):
    def setUp(self):
        self.string_definitions = set()
        self.string_definitions.add(("stega", 10))
        self.string_definitions.add(("tegan", 7))
        self.string_definitions.add(("egana", 5))
        self.string_definitions.add(("ganal", 5))
        self.string_definitions.add(("analy", 5))
        self.string_definitions.add(("nalys", 3))
        self.string_definitions.add(("alysi", 3))
        self.string_definitions.add(("lysis", 1))
        self.string_definitions.add(("ysis ", 1))
        self.string_definitions.add(("sis 0", 1))

    def test_tree_created(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        self.assertIsInstance(test_huffman[0], int)
        self.assertIsInstance(test_huffman[1], HuffmanTree)

    def test_serialise_tree(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        serial_tree = test_huffman[1].__dict__()
        self.assertIsInstance(serial_tree, dict)
        self.assertEqual(4, len(serial_tree))
        self.assertEqual(None, serial_tree.get("value"))
        self.assertEqual(None, serial_tree.get("path_code"))
        self.assertIsInstance(serial_tree.get("left"), dict)
        self.assertIsInstance(serial_tree.get("right"), dict)

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

    def test_get_tree_leaf_codes(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        huffman.allocate_path_bits(test_huffman)
        path_codes = huffman.get_tree_leaf_codes(test_huffman)
        self.assertNotEqual(set(), path_codes)
        self.assertEqual(10, len(path_codes))

    def test_serialise_tree_codes(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        huffman.allocate_path_bits(test_huffman)
        serial_tree = test_huffman[1].__dict__()
        self.assertIsInstance(serial_tree, dict)
        self.assertIsInstance(serial_tree.get("left"), dict)
        path_code = serial_tree.get("left").get("path_code")
        self.assertEqual("0", path_code)

    def test_deserialise_tree_codes(self):
        serial_tree = {
            "value": None,
            "path_code": None,
            "left": {
                "value": "hello",
                "path_code": "0",
                "left": None,
                "right": None
            },
            "right": {
                "value": None,
                "path_code": None,
                "left": {
                    "value": "world",
                    "path_code": "10",
                    "left": None,
                    "right": None
                },
                "right": {
                    "value": "!",
                    "path_code": "11",
                    "left": None,
                    "right": None
                }
            }
        }
        _, tree = huffman.deserialise_tree(serial_tree)

        self.assertIsInstance(tree, HuffmanTree)
        self.assertIsNone(tree.value)
        self.assertIsNone(tree.path_code)

        self.assertIsInstance(tree.left[1], HuffmanTree)
        self.assertTupleEqual(("hello", 0), tree.left[1].value)
        self.assertEqual(Bits(bin="0"), tree.left[1].path_code)

        self.assertIsInstance(tree.right[1], HuffmanTree)
        self.assertTupleEqual(("!", 0), tree.right[1].right[1].value)
        self.assertEqual(Bits(bin="11"), tree.right[1].right[1].path_code)

    def test_get_set_average_length(self):
        test_set = set()
        test_set.add(Bits(bin="0"))
        test_set.add(Bits(bin="1"))
        test_set.add(Bits(bin="00"))
        test_set.add(Bits(bin="01"))
        test_set.add(Bits(bin="100"))
        average_length = huffman.get_set_average_length(test_set)
        self.assertEqual(9 / 5, average_length)

    def test_get_set_expected_length(self):
        test_set = set()
        test_set.add(Bits(bin="0"))
        test_set.add(Bits(bin="1"))
        test_set.add(Bits(bin="00"))
        test_set.add(Bits(bin="01"))
        test_set.add(Bits(bin="100"))
        average_length = huffman.get_set_expected_length(test_set)
        self.assertEqual(2.375, average_length)

    def test_encode_bits_as_strings(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        huffman.allocate_path_bits(test_huffman)
        output = huffman.encode_bits_as_strings(test_huffman[1], Bits(bin="010011101"))
        self.assertIsNotNone(output)
        self.assertEqual("steganalysegana", output[1])

    def test_encode_bits_as_strings_padded(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        huffman.allocate_path_bits(test_huffman)
        output = huffman.encode_bits_as_strings(test_huffman[1], Bits(bin="011100011010110"))
        self.assertIsNotNone(output)
        self.assertEqual("stegaanalynalysstegastegaganal", output[1])

    def test_encode_bits_as_strings_nothing(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        huffman.allocate_path_bits(test_huffman)
        output = huffman.encode_bits_as_strings(test_huffman[1], Bits())
        self.assertIsNotNone(output)
        self.assertEqual(output[0], Bits())
        self.assertEqual(output[1], "")

    def test_search_tree_for_symbol(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        huffman.allocate_path_bits(test_huffman)
        bits = huffman.search_tree_for_symbol(test_huffman[1], "alysi")
        self.assertEqual(bits, Bits(bin="0010"))
        bits = huffman.search_tree_for_symbol(test_huffman[1], "ysis ")
        self.assertEqual(bits, Bits(bin="1111"))
        bits = huffman.search_tree_for_symbol(test_huffman[1], "sis 0")
        self.assertEqual(bits, Bits(bin="11100"))

    def test_encode_string_as_bits(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        huffman.allocate_path_bits(test_huffman)
        bits = huffman.encode_string_as_bits(test_huffman[1], "stegaalysilysissis 0tegan", 5)
        self.assertEqual(bits, Bits(bin="0b0100101110111100000"))

    def test_has_given_symbol_length(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        self.assertFalse(huffman.has_given_symbol_length(test_huffman, 4))
        self.assertFalse(huffman.has_given_symbol_length(test_huffman, 6))
        self.assertTrue(huffman.has_given_symbol_length(test_huffman, 5))
        self.assertRaises(ValueError, huffman.has_given_symbol_length, None, 1)
        self.assertRaises(ValueError, huffman.has_given_symbol_length, [0, None], 1)

    def test_tree_to_symbols(self):
        test_huffman = huffman.create_tree(self.string_definitions)
        huffman.allocate_path_bits(test_huffman)
        flattened_tree = huffman.tree_to_symbols(test_huffman)
        self.assertIsNotNone(flattened_tree)

        sorted_list = list(self.string_definitions)
        sorted_list.sort(key=lambda x: x[0])
        self.assertEqual(len(flattened_tree), len(sorted_list))
        for i in range(0, len(sorted_list)):
            # We are only interested in the string and frequency from tree nodes.
            this_tuple = flattened_tree[i][0], flattened_tree[i][1]
            self.assertTupleEqual(this_tuple, sorted_list[i])

    def test_variable_length_tree(self):
        self.string_definitions = set()
        self.string_definitions.add(("a", 15))
        self.string_definitions.add(("ba", 4))
        self.string_definitions.add(("abc", 33))
        self.string_definitions.add(("dcba", 17))
        self.string_definitions.add(("abcde", 10))

        test_huffman = huffman.create_tree(self.string_definitions)
        test_passed = has_correct_leaves(test_huffman)
        self.assertTrue(test_passed, "Huffman tree did not have values for all leaves")
        huffman.allocate_path_bits(test_huffman)
        self.assertTrue(has_correct_bits(test_huffman, Bits()), "Huffman tree did not have correct bits for every node")

    def test_load_tree(self):
        test_huffman = huffman.load_tree(TEST_TREE_FILE)[1]
        self.assertIsInstance(test_huffman, HuffmanTree)
        self.assertIsNone(test_huffman.value)
        self.assertIsNone(test_huffman.path_code)

        leaf = test_huffman.right[1].right[1].right[1].left[1].left[1]
        self.assertIsInstance(leaf, HuffmanTree)
        self.assertIsInstance(leaf.value, tuple)
        self.assertEqual("sis 0", leaf.value[0])
        self.assertEqual(Bits(bin="11100"), leaf.path_code)
        self.assertIsNone(leaf.left)
        self.assertIsNone(leaf.right)

    def test_load_tree_empty(self):
        self.assertRaises(ValueError, huffman.load_tree, TEST_EMPTY_TREE_FILE)


def is_correct_tree(huffman_tree: HuffmanTreeWithFrequencies):
    """
    Show that given tree is recursively defined by left and right,
    where left and right can be another Huffman Tree or None.

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
    Show that the given tree has values for all leaf nodes, and only leaf nodes.

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
    Show that the given tree has bits for all non-root nodes, and that they accumulate correctly.

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
