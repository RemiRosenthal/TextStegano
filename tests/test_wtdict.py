import unittest

from bitstring import Bits

from stegano import wtdict
from stegano.wtdict import MappingDictionary, WordTypeDictionary


class TestMappingDictionary(unittest.TestCase):
    def setUp(self):
        self.mappings = set()
        self.mappings.add(("penguin", Bits(bin="00")))
        self.mappings.add(("tiger", Bits(bin="01")))
        self.mappings.add(("giraffe", Bits(bin="11")))
        self.mapping_dict = MappingDictionary(self.mappings)

    def test_mappings(self):
        self.assertIsInstance(self.mapping_dict, MappingDictionary)
        mappings = self.mapping_dict.mappings
        self.assertIsInstance(mappings, dict)
        self.assertEqual(3, len(mappings))
        self.assertEqual(Bits(bin="00"), mappings.get("penguin"))
        self.assertEqual(Bits(bin="01"), mappings.get("tiger"))
        self.assertEqual(Bits(bin="11"), mappings.get("giraffe"))
        self.assertEqual(None, mappings.get("ossifrage"))

    def test_duplicate_mappings(self):
        self.mappings.add(("penguin", Bits(bin="100")))
        self.mappings.add(("tiger", Bits(bin="110")))
        self.mappings.add(("giraffe", Bits(bin="111")))
        mapping_dict = MappingDictionary(self.mappings)
        self.assertEqual(3, len(mapping_dict.mappings))

    def test_duplicate_values(self):
        self.mappings.add(("wolf", Bits(bin="00")))
        mapping_dict = MappingDictionary(self.mappings)
        self.assertEqual(3, len(mapping_dict.mappings))

    def test_encode_spaces(self):
        self.assertEqual(True, self.mapping_dict.encode_spaces)
        self.mapping_dict = MappingDictionary(self.mappings, False)
        self.assertEqual(False, self.mapping_dict.encode_spaces)


class TestWordTypeDictionary(unittest.TestCase):
    def setUp(self):
        self.mappings = set()
        self.mappings.add(("penguin", Bits(bin="00")))
        self.mappings.add(("tiger", Bits(bin="01")))
        self.mappings.add(("giraffe", Bits(bin="11")))
        self.mapping_dict = MappingDictionary(self.mappings)
        self.input_dict = {"animals": self.mapping_dict}

        self.mappings = set()
        self.mappings.add(("pen", Bits(bin="00")))
        self.mappings.add(("pencil", Bits(bin="01")))
        self.mappings.add(("paper", Bits(bin="11")))
        self.mapping_dict = MappingDictionary(self.mappings, False)
        self.input_dict.update({"stationery": self.mapping_dict})

        self.wt_dict = WordTypeDictionary(self.input_dict)

    def test_wt_dict(self):
        self.assertIsInstance(self.wt_dict, WordTypeDictionary)
        self.assertEqual(2, len(self.wt_dict.wt_dict))

    def test_create_empty_dict(self):
        self.mappings = set()
        self.mapping_dict = MappingDictionary(self.mappings)
        self.input_dict = {"empty": self.mapping_dict}
        self.wt_dict = WordTypeDictionary(self.input_dict)

        self.assertIsNone(self.wt_dict.wt_dict)

    def test_serialise_dict(self):
        serial_dict = self.wt_dict.__dict__()
        self.assertIsInstance(serial_dict, dict)
        self.assertEqual(2, len(serial_dict))

        mapping_dict = serial_dict.get("animals")
        self.assertEqual(2, len(mapping_dict))
        self.assertEqual(True, mapping_dict.get("encode_spaces"))
        self.assertIsInstance(mapping_dict.get("mappings"), dict)
        self.assertEqual(3, len(mapping_dict.get("mappings")))
        self.assertEqual("00", mapping_dict.get("mappings").get("penguin"))
        self.assertEqual(None, mapping_dict.get("mappings").get("pencil"))

        mapping_dict = serial_dict.get("stationery")
        self.assertEqual(2, len(mapping_dict))
        self.assertEqual(False, mapping_dict.get("encode_spaces"))
        self.assertIsInstance(mapping_dict.get("mappings"), dict)
        self.assertEqual(3, len(mapping_dict.get("mappings")))
        self.assertEqual("01", mapping_dict.get("mappings").get("pencil"))
        self.assertEqual(None, mapping_dict.get("mappings").get("penguin"))

    def test_mapping_dicts(self):
        wt_dict = self.wt_dict.wt_dict
        self.assertIsInstance(wt_dict, dict)

        self.assertIsInstance(wt_dict.get("animals"), MappingDictionary)
        self.assertIsInstance(wt_dict.get("stationery"), MappingDictionary)

        self.assertEqual(3, len(wt_dict.get("animals").mappings))
        self.assertEqual(3, len(wt_dict.get("stationery").mappings))

        self.assertEqual(Bits(bin="00"), wt_dict.get("stationery").mappings.get("pen"))
        self.assertEqual(Bits(bin="00"), wt_dict.get("animals").mappings.get("penguin"))

    def test_update_existing_wt(self):
        new_mappings = set()
        new_mappings.add(("pen", Bits(bin="10")))
        new_mappings.add(("ruler", Bits(bin="101")))
        mapping_dict = MappingDictionary(new_mappings)
        input_dict = {"stationery": mapping_dict}

        self.wt_dict.append_word_type(input_dict)

        self.assertEqual(4, len(self.wt_dict.wt_dict.get("stationery").mappings))
        self.assertEqual(Bits(bin="10"), self.wt_dict.wt_dict.get("stationery").mappings.get("pen"))
        self.assertEqual(Bits(bin="101"), self.wt_dict.wt_dict.get("stationery").mappings.get("ruler"))

    def test_update_new_wt(self):
        new_mappings = set()
        new_mappings.add(("apple", Bits(bin="1")))
        new_mappings.add(("burger", Bits(bin="00")))
        new_mappings.add(("salad", Bits(bin="01")))
        mapping_dict = MappingDictionary(new_mappings)
        input_dict = {"food": mapping_dict}

        self.wt_dict.append_word_type(input_dict)

        self.assertEqual(3, len(self.wt_dict.wt_dict))
        food_mappings = self.wt_dict.wt_dict.get("food").mappings
        self.assertEqual(3, len(food_mappings))
        self.assertEqual(Bits(bin="1"), food_mappings.get("apple"))
        self.assertEqual(Bits(bin="00"), food_mappings.get("burger"))
        self.assertEqual(Bits(bin="01"), food_mappings.get("salad"))

    def test_update_empty_wt(self):
        new_mappings = set()
        mapping_dict = MappingDictionary(new_mappings)
        input_dict = {"empty": mapping_dict}

        self.wt_dict.append_word_type(input_dict)

        self.assertEqual(2, len(self.wt_dict.wt_dict))
        self.assertIsNone(self.wt_dict.wt_dict.get("empty"))

    def test_duplicate_words(self):
        new_mappings = set()
        new_mappings.add(("giraffe", Bits(bin="1")))
        new_mappings.add(("cube", Bits(bin="00")))
        mapping_dict_1 = MappingDictionary(new_mappings)
        new_mappings = set()
        new_mappings.add(("cube", Bits(bin="01")))
        new_mappings.add(("grass", Bits(bin="11")))
        mapping_dict_2 = MappingDictionary(new_mappings)
        input_dict = {"misc": mapping_dict_1, "misc_2": mapping_dict_2}

        self.wt_dict.append_word_type(input_dict)

        self.assertEqual(4, len(self.wt_dict.wt_dict))
        misc_mappings = self.wt_dict.wt_dict.get("misc").mappings
        self.assertEqual(1, len(misc_mappings))
        self.assertEqual(Bits(bin="00"), misc_mappings.get("cube"))
        self.assertEqual(None, misc_mappings.get("giraffe"))

        misc_mappings = self.wt_dict.wt_dict.get("misc_2").mappings
        self.assertEqual(1, len(misc_mappings))
        self.assertEqual(Bits(bin="11"), misc_mappings.get("grass"))
        self.assertEqual(None, misc_mappings.get("cube"))

        misc_mappings = self.wt_dict.wt_dict.get("nothing")
        self.assertIsNone(misc_mappings)

    def test_remove_word(self):
        remove_set = {"penguin"}
        self.wt_dict.remove_word(remove_set)
        self.assertEqual(2, len(self.wt_dict.wt_dict))

        mappings = self.wt_dict.wt_dict.get("animals").mappings
        self.assertEqual(2, len(mappings))
        self.assertEqual(None, mappings.get("penguin"))
        self.assertEqual(Bits(bin="01"), mappings.get("tiger"))

    def test_remove_no_words(self):
        remove_set = set()
        self.wt_dict.remove_word(remove_set)
        self.assertEqual(2, len(self.wt_dict.wt_dict))

        mappings = self.wt_dict.wt_dict.get("animals").mappings
        self.assertEqual(3, len(mappings))
        self.assertEqual(Bits(bin="00"), mappings.get("penguin"))

    def test_remove_multiple_words(self):
        remove_set = {"penguin", "tiger", "pen"}
        self.wt_dict.remove_word(remove_set)
        self.assertEqual(2, len(self.wt_dict.wt_dict))

        mappings = self.wt_dict.wt_dict.get("animals").mappings
        self.assertEqual(1, len(mappings))
        self.assertEqual(None, mappings.get("penguin"))
        self.assertEqual(None, mappings.get("tiger"))
        self.assertEqual(Bits(bin="11"), mappings.get("giraffe"))

        mappings = self.wt_dict.wt_dict.get("stationery").mappings
        self.assertEqual(2, len(mappings))
        self.assertEqual(None, mappings.get("pen"))
        self.assertEqual(Bits(bin="01"), mappings.get("pencil"))

    def test_remove_all_words(self):
        remove_set = {"penguin", "tiger", "giraffe", "pencil", "pen", "paper"}
        self.wt_dict.remove_word(remove_set)
        self.assertIsNone(self.wt_dict.wt_dict)

    def test_remove_word_type(self):
        remove_set = {"animals"}
        self.wt_dict.remove_word_type(remove_set)
        self.assertEqual(1, len(self.wt_dict.wt_dict))

        mapping_dict = self.wt_dict.wt_dict.get("animals")
        self.assertIsNone(mapping_dict)

    def test_remove_all_word_types(self):
        remove_set = {"animals", "stationery"}
        self.wt_dict.remove_word_type(remove_set)
        self.assertIsNone(self.wt_dict.wt_dict)

    def test_generate_state_definitions(self):
        state_definitions = self.wt_dict.generate_state_definitions()
        self.assertIsInstance(state_definitions, list)
        self.assertListEqual(["animals", "stationery"], state_definitions)


class TestWTDict(unittest.TestCase):
    def test_deserialise_dict(self):
        serial_dict = {
            "animals": {
                "encode_spaces": True, "mappings": {
                    "penguin": "00",
                    "tiger": "01",
                    "giraffe": "11"
                }}
        }
        wt_dict = wtdict.deserialise_dict(serial_dict)

        self.assertIsInstance(wt_dict, dict)
        self.assertEqual(1, len(wt_dict))
        mappings = wt_dict.get("animals").mappings
        self.assertEqual(3, len(mappings))
        self.assertEqual(Bits(bin="00"), mappings.get("penguin"))
        self.assertEqual(None, mappings.get("lion"))

    def test_load_dict(self):
        wtdict.load_dict()


if __name__ == '__main__':
    unittest.main()
