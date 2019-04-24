import random
from functools import reduce
from typing import List, Tuple

from bitstring import Bits

from stegano.markov import MarkovChain, START_STATE_LABEL
from stegano.wtdict import WordTypeDictionary, MappingDictionary

DEFAULT_HEADER_LENGTH = 20


class ExtendedCoderError(Exception):
    """Raised when something went logically wrong with a coding process."""
    pass


def encode_message(chain: MarkovChain, wt_dict: WordTypeDictionary, bits: Bits, header_length=DEFAULT_HEADER_LENGTH
                   ) -> str:
    """
    Given a header length, a secret message as bits, a Markov chain, and a word-type dictionary, encode a cover text
    including a header which contains the length of the message.
    The message may be no more than (2^header_length) bits long.
    :param chain: a Markov chain with states
    :param wt_dict: a corresponding dictionary of word-types
    :param bits: the input bits
    :param header_length: the pre-shared length, in bits, of the header
    :return: the cover text as a string
    """
    if bits is None or bits.__eq__(Bits()):
        raise ValueError("Bits cannot be None or empty.")
    message_length = len(bits)
    header = get_fixed_length_header(message_length, header_length)
    full_message = header + bits
    words = encode_bits_as_words(chain, wt_dict, full_message)
    cover_text = words_to_cover_text(words, True)
    return cover_text


def decode_cover_text(wt_dict: WordTypeDictionary, cover_text: str, header_length=DEFAULT_HEADER_LENGTH) -> Bits:
    """
    Given a valid cover text containing a header, and the correct header length and word-type dictionary, retrieve the
    secret message.
    :param wt_dict: a dictionary of word-types
    :param cover_text: the cover text consisting of a header and message
    :param header_length: the pre-shared length, in bits, of the header
    :return: the retrieved secret message as bits
    """
    if cover_text is None:
        raise ValueError("Cover text cannot be None.")
    message = Bits()
    if cover_text.__len__() == 0:
        return message

    header_bits, trailing_bits, cover_text = fixed_size_decode(wt_dict, cover_text, header_length)
    message_length = get_message_length_from_header(header_bits) - len(trailing_bits)
    message = message.__add__(trailing_bits)

    message_bits, trailing_bits, cover_text = fixed_size_decode(wt_dict, cover_text, message_length)
    if len(cover_text) > 0:
        print("Warning: there were {} characters left over in the cover text. "
              "Please verify the provided header length.".format(len(cover_text)))
    message = message.__add__(message_bits)

    return message


def fixed_size_decode(wt_dict: WordTypeDictionary, cover_text: str, data_length: int) -> \
        Tuple[Bits, Bits, str]:
    """
    Given a valid cover text and word-type dictionary, retrieve the message of the desired length.
    :param wt_dict: a dictionary of word-types
    :param cover_text: a full or partial cover text containing the message
    :param data_length: the exact number of bits that should be decoded from the cover text
    :return: a tuple containing the retrieved message bits; trailing bits from the last word decoded (if any); and the
    remaining cover text after decoding
    """
    message = Bits()
    longest_word_length = len(get_longest_word_in_dictionary(wt_dict))
    while message.len < data_length:
        if cover_text.__len__() == 0:
            raise ValueError("Cover text was too short for expected {} bits of data".format(data_length))
        word, bits = get_word_from_cover_text(wt_dict, cover_text, longest_word_length)
        message = message.__add__(bits)
        cover_text = (cover_text[len(word):]).lstrip()
    trailing_bits = message[data_length:]
    message = message[:data_length]
    return message, trailing_bits, cover_text


def get_fixed_length_header(message_length: int, header_length: int) -> Bits:
    """
    Encode an integer length as a binary header.
    :param message_length: the integer to encode
    :param header_length:
    :return:
    """
    if message_length > pow(2, header_length) + 1:
        raise ValueError("Message was too long for header_length to represent.")
    if message_length == 0:
        raise ValueError("Message cannot be of length 0.")

    header = ("{0:0" + str(header_length) + "b}").format(message_length - 1)
    header = _stream_randomiser(header)  # randomise structure of bits in header
    return Bits(bin=header)


def get_message_length_from_header(header: Bits) -> int:
    header = _stream_randomiser(header.bin)
    message_length = Bits(bin=header).uint + 1
    return message_length


def _stream_randomiser(bits: str) -> str:
    """
    Randomise the bits in a given string using a pseudo-random stream cipher.
    This cipher may be different per system, but is repeatable on every run.
    :param bits: the input bit string
    :return: the altered bit string
    """
    r = random.Random()
    r.seed("pseudorandom")
    xor = lambda x: "1" if (int(x) != r.randint(0, 1)) else "0"
    bits = list(map(xor, bits))
    return "".join(bits)


def get_longest_word_in_dictionary(wt_dict: WordTypeDictionary) -> str:
    """
    Find and return the longest word in the given dictionary, under any word-type. Makes no guarantees which of
    several equally-longest words are returned.
    :param wt_dict: the word-type dictionary
    :return: the single longest word
    """
    longest = ""
    longer = lambda x, y: x if len(x) > len(y) else y
    for mapping in wt_dict.wt_dict.values():
        wt_longest = reduce(longer, mapping.mappings)
        longest = longer(wt_longest, longest)
    return longest


def get_word_from_cover_text(wt_dict: WordTypeDictionary, cover_text: str, word_length_bound: int) -> Tuple[str, Bits]:
    """
    Using a given word-type dictionary, retrieve and return the first word found in the cover text that exists in
    the dictionary. Assumes that the cover text has spaces between words, and all words not preceded by spaces (such as
    punctuation) are not a prefix or suffix of any other such word.
    :param wt_dict: the dictionary of words
    :param cover_text: the cover text
    :param word_length_bound: the length of the longest word in the word-type dictionary, used to bound the search
    :return: a tuple of the first word found and its bit string
    """
    if len(wt_dict.wt_dict.items()) == 0:
        raise ValueError("Given word-type dictionary was empty.")
    if word_length_bound == 0:
        raise ValueError("Given word length upper bound cannot be 0.")
    if len(cover_text) == 0:
        raise ValueError("Given cover text was empty.")
    elif len(cover_text) < word_length_bound:
        word_length_bound = len(cover_text)

    if cover_text[0].__eq__(" "):
        cover_text = cover_text[1:]
    first_space_index = cover_text.find(" ", 1)
    if 0 < first_space_index < word_length_bound:
        word_length_bound = first_space_index

    for i in range(word_length_bound, 0, -1):
        word = cover_text[:i].lower()
        for mapping_dict in wt_dict.wt_dict.values():
            value = mapping_dict.mappings.get(word)
            if value is not None:
                return word, value

    word = cover_text[:word_length_bound]
    raise ExtendedCoderError("Unable to find a word in the given cover text (at {}...) with the given parameters".
                             format(word))


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


def encode_bits_as_words(chain: MarkovChain, wt_dict: WordTypeDictionary, bits: Bits, pad_text=True) -> list:
    """
    Given a bit stream, a Markov chain, and a word-type dictionary, retrieve a corresponding list of words.
    Every state in the Markov chain, except the start state s0, must have a corresponding word-type in the given
    dictionary with at least one word.

    If the word-type dictionary does not have path bits to match the end of the input exactly, it will append 0s
    until the function can complete.

    :param chain: a Markov chain with states
    :param wt_dict: a corresponding dictionary of word-types
    :param bits: the input bits
    :param pad_text: if true, generate cover text from random bits until the Markov chain reaches state s0
    :return: an ordered list of words encoded by the system
    """
    if bits is None or bits.__eq__(Bits()):
        raise ValueError("Bits cannot be None or empty.")

    words = []
    prefix = bits
    while len(prefix) > 0:
        chain.transition()
        if chain.current_state.__eq__(START_STATE_LABEL):
            chain.transition()

        word, word_bits, encode_spaces = _encode_next_word(chain, wt_dict, prefix)
        words.append((word, encode_spaces))
        bit_length = len(word_bits)
        prefix = prefix[bit_length:]

    if pad_text:
        # add filler bits until s0 reached
        while not chain.current_state.__eq__(START_STATE_LABEL):
            chain.transition()
            if chain.current_state.__eq__(START_STATE_LABEL):
                break
            longest_word = get_longest_word_in_dictionary(wt_dict)
            pseudo_random_bits = Bits(bin="".join(random.choice(["0", "1"]) for _ in range(len(longest_word))))
            word, word_bits, encode_spaces = _encode_next_word(chain, wt_dict, pseudo_random_bits)
            words.append((word, encode_spaces))

    return words


def _encode_next_word(chain: MarkovChain, wt_dict: WordTypeDictionary, bits: Bits) -> Tuple[str, Bits, bool]:
    word_type = chain.get_current_word_type()
    mapping_dict = wt_dict.wt_dict.get(word_type)
    if mapping_dict is None:
        raise ValueError("Unable to find mapping dictionary for word-type {}".format(word_type))

    try:
        word = retrieve_word_from_mappings(bits, mapping_dict, True)
    except ValueError:
        raise ValueError("Failed to retrieve a word for word-type {}".format(word_type))
    return word, mapping_dict.mappings.get(word), mapping_dict.encode_spaces


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

    prefix = bits[:longest_bits].bin + "..."
    raise ValueError("Unable to find any matches or near-matches in the mapping dictionary using the given bits, {}."
                     .format(prefix))
