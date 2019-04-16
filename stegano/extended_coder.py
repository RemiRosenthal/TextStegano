from functools import reduce
from typing import List, Tuple

from bitstring import Bits

from stegano.markov import MarkovChain
from stegano.wtdict import WordTypeDictionary, MappingDictionary


def words_to_cover_text(words: List[Tuple[str, bool]], capitalise_start=True) -> str:
    """
    Given a list of words and their encode_spaces properties, form a cover text.
    :param words: the list of tuples containing the words and their properties
    :param capitalise_start: if true, capitalise the first letter of the cover text
    :return: the cover text as a string
    """
    cover_text = ""
    if words is None or words.__len__() == 0:
        return cover_text

    first_word = words[0][0]
    if capitalise_start:
        first_word = first_word[0].upper() + first_word[1:]

    cover_text = cover_text + first_word
    for word, encode_spaces in words[1:]:
        if encode_spaces:
            cover_text += " "
        cover_text += word
    return cover_text


def encode_bits_as_words(chain: MarkovChain, wt_dict: WordTypeDictionary, bits: Bits) -> list:
    """
    Given a bit stream, a Markov chain, and a word-type dictionary, encode a cover text.
    Every state in the Markov chain, except the start state s0, must have a corresponding word-type in the given
    dictionary with at least one word.

    If the word-type dictionary does not have path bits to match the end of the input exactly, it will append 0s
    until the function can complete.

    :param chain: a Markov chain with states
    :param wt_dict: a corresponding dictionary of word-types
    :param bits: the input bits
    :return: an ordered list of words encoded by the system
    """
    if bits is None or bits.__eq__(Bits()):
        raise ValueError("Bits cannot be None or empty.")

    words = []
    prefix = bits
    while len(prefix) > 0:
        chain.transition()
        if chain.current_state.__eq__("s0"):
            chain.transition()
        word_type = chain.current_state
        mapping_dict = wt_dict.wt_dict.get(word_type)
        if mapping_dict is None:
            raise ValueError("Unable to find mapping dictionary for word-type {}".format(word_type))

        word = retrieve_word_from_mappings(prefix, mapping_dict, True)
        words.append((word, mapping_dict.encode_spaces))
        bit_length = len(mapping_dict.mappings.get(word))
        prefix = prefix[bit_length:]
    return words


def retrieve_word_from_mappings(bits: Bits, mapping_dict: MappingDictionary, allow_padding=True) -> str:
    """
    Given a string of bits, attempt to find a word in the given mapping dictionary that corresponds to the first
    n bits.
    :param bits: the entire message that needs to be decoded
    :param mapping_dict: the dictionary of mappings
    :param allow_padding: if true, then 0s will be appended to bits if necessary to find a mapping
    :return: the retrieved word
    """
    if mapping_dict is None:
        raise ValueError("Mapping dictionary cannot be None.")
    elif len(mapping_dict.mappings.items()) == 0:
        raise ValueError("Given mappings were empty.")
    if bits is None:
        raise ValueError("Bits cannot be None.")

    reverse_dict = {y: x for x, y in mapping_dict.mappings.items()}
    f = lambda x, y: x if x > y else y
    longest_bits = reduce(lambda x, y: f(x, y), map(len, reverse_dict.keys()))
    prefix = bits[:longest_bits].bin
    while prefix.__len__() > 0:
        value = reverse_dict.get(Bits(bin=prefix))
        if value is not None:
            return value
        prefix = prefix[:len(prefix) - 1]

    # No exact match has been found
    if allow_padding:
        prefix = bits.bin
        while prefix.__len__() < longest_bits:
            prefix = prefix + "0"
            value = reverse_dict.get(Bits(bin=prefix))
            if value is not None:
                return value

    raise ValueError("Unable to find any matches or near-matches in the mapping dictionary using the given bits.")
