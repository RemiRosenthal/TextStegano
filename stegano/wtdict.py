import json
from collections import namedtuple
from typing import Tuple, Set, Dict

from bitstring import Bits

DEFAULT_DICT_FILE = "..\\word_type_dict.json"

Mapping = Tuple[str, Bits]
Mappings = Set[Mapping]


class MappingDictionary:
    """
    A word list is a single word-type that uniquely defines it, and a non-empty set of mappings between symbols and
    their bit strings.
    """

    def __init__(self, mappings: Mappings, encode_spaces=True):
        input_mappings = dict((string, bits) for string, bits in mappings)
        self.mappings = {}
        for key, value in input_mappings.items():
            if value not in self.mappings.values():
                self.mappings[key] = value
        self.encode_spaces = encode_spaces

    def __dict__(self):
        serial_dict = {}
        serial_dict.update({"encode_spaces": self.encode_spaces})
        to_binary = lambda v: v.bin
        d = {k: to_binary(v) for k, v in self.mappings.items()}
        serial_dict.update({"mappings": d})
        return serial_dict


WTDict = Dict[str, MappingDictionary]


class WordTypeDictionary:
    def __init__(self, wt_dict: WTDict):
        self.wt_dict = wt_dict

    def __dict__(self):
        serial_dict = {}
        for mapping_key in self.wt_dict.keys():
            mapping_dict = self.wt_dict.get(mapping_key)
            serial_dict.update({mapping_key: mapping_dict.__dict__()})
        return serial_dict

    @staticmethod
    def from_dict(wt_dict: str):
        json.loads(wt_dict, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

    def append_word_type(self, input_dict: WTDict):
        """
        Add to this word-type dictionary the mappings of another dictionary. They each must have a unique word-type
        name and symbols which are unique to the dictionary.
        :param input_dict: the dictionary of new word lists.
        """
        input_keys = input_dict.keys()
        for key in input_keys:
            if input_dict.get(key).mappings.__eq__({}):
                continue

            mapping_dict = self.wt_dict.get(key)

            duplicate_values = self.contains_any_words_from_set(set(input_dict.get(key).mappings.items()), key)
            for duplicate_value in duplicate_values:
                del input_dict.get(key).mappings[duplicate_value]

            if mapping_dict is None:
                self.wt_dict.update({key: input_dict.get(key)})
            else:
                mapping_dict.mappings.update(input_dict.get(key).mappings)

    def contains_any_words_from_set(self, pairs: set, exclude_key=None) -> set:
        """
        Look through this word type dictionary. Return the subset of the input set of pairs whose value exists in this
        dictionary under any word-type.
        :param pairs: the set of key-value pairs to check
        :param exclude_key: the key to exclude from the search of the dictionary
        :return: a subset of pairs
        """
        words = set(key for key, value in pairs)
        present_words = set()
        for key, value in self.wt_dict.items():
            if not key.__eq__(exclude_key):
                for item in value.mappings:
                    if item in words:
                        present_words.add(item)
        return present_words

    def remove_word_type(self, word_types: set):
        """
        Remove from this word-type dictionary every word list that is specified by a word-type name in the given set.
        Any invalid elements in the set are ignored.
        :param word_types: the set of word-types whose lists should be removed from the dictionary
        """
        if len(word_types) == 0:
            return
        for item in word_types:
            if self.wt_dict.get(item) is not None:
                del self.wt_dict[item]
            if self.wt_dict.__eq__({}):
                self.wt_dict = None

    def remove_word(self, word_types: set):
        """
        Remove from this word-type dictionary every word that is specified by in the given set.
        Any invalid elements in the set are ignored.
        :param word_types: the set of words that should be removed from the dictionary
        """
        if len(word_types) == 0:
            return
        remove_word_types = set()
        for key, value in self.wt_dict.items():
            mappings = self.wt_dict.get(key).mappings
            for item in word_types:
                if mappings.get(item) is not None:
                    del self.wt_dict.get(key).mappings[item]
            if self.wt_dict.get(key).mappings.__eq__({}):
                remove_word_types.add(key)
        self.remove_word_type(remove_word_types)

    def generate_state_definitions(self) -> list:
        """
        From this word-type dictionary, generate a list of distinct states identified uniquely by their word-type name.
        This list does not explicitly include a start state.
        :param states:
        :return:
        """
        state_definitions = list()
        for word_list in self.wt_dict:
            state_definitions.append(word_list.word_type)
        return state_definitions


def deserialise_dict(wt_dict: dict) -> WTDict:
    """
    Convert a serialised dict (of strings) to a WTDict (of mapping objects)
    :param wt_dict: serialised dict
    :return: a WTDict
    """
    deserialised_dict = {}
    for mapping_key in wt_dict.keys():
        mapping_dict = wt_dict.get(mapping_key)
        mappings = {(x, Bits(bin=y)) for x, y in mapping_dict.get("mappings").items()}
        deserialised_dict.update({mapping_key: MappingDictionary(mappings, mapping_dict.get("encode_spaces"))})
    return deserialised_dict


def load_dict(dict_filename=DEFAULT_DICT_FILE) -> WordTypeDictionary:
    """
    Attempt to load a JSON file as a word-type dictionary object
    :param dict_filename: the path of the file
    :return: the dictionary object, as long as the file is valid
    """
    try:
        with open(dict_filename, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            wt_dict = deserialise_dict(data)
            return WordTypeDictionary(wt_dict)
    except IOError:
        print("Could not read dictionary file " + dict_filename)


def save_dict(dictionary: WordTypeDictionary, dict_filename=DEFAULT_DICT_FILE):
    """
    Save a word-type dictionary object as a JSON file
    :param dictionary: a dictionary object
    :param dict_filename: the desired path of the file
    """
    try:
        with open(dict_filename, "w", encoding="utf-8") as handle:
            json.dump(dictionary, handle)
    except IOError:
        print("Could not write dictionary file " + dict_filename)
