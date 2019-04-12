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

    def __init__(self, mappings: Mappings):
        input_mappings = dict((string, bits) for string, bits in mappings)
        self.mappings = {}
        for key, value in input_mappings.items():
            if value not in self.mappings.values():
                self.mappings[key] = value


WTDict = Dict[str, MappingDictionary]


class WordTypeDictionary:
    def __init__(self, wt_dict: WTDict):
        self.wt_dict = wt_dict

    def append_word_type(self, input_dict: WTDict):
        """
        Add to this word-type dictionary the mappings of another dictionary. They each must have a unique word-type
        name and symbols which are unique to the dictionary.
        :param input_dict: the dictionary of new word lists.
        """
        input_keys = input_dict.keys()
        for key in input_keys:
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
        Remove from this word-type dictionary every word list that is specified by the given set.
        Any invalid elements in the set are ignored.
        :param word_types: the set of word-types whose lists should be removed from the dictionary
        """
        pass

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


def dict_loader(dict_filename=DEFAULT_DICT_FILE) -> WordTypeDictionary:
    """
    Attempt to load a JSON file as a word-type dictionary object
    :param dict_filename: the path of the file
    :return: the dictionary object, as long as the file is valid
    """
    pass


def dict_saver(dictionary: WordTypeDictionary, dict_filename=DEFAULT_DICT_FILE):
    """
    Save a word-type dictionary object as a JSON file
    :param dictionary: a dictionary object
    :param dict_filename: the desired path of the file
    """
    pass
