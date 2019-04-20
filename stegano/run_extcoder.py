import argparse
from typing import Optional

from bitstring import Bits, CreationError

from stegano import textanalyser, wtdict, markov, extendedcoder
from stegano.filehandler import prefix_filename, read_input_file, write_output_file
from stegano.markov import MarkovChain
from stegano.wtdict import WordTypeDictionary

DEFAULT_HEADER_LENGTH = 20


def init_wt_dict(filename: str) -> WordTypeDictionary:
    try:
        loaded = wtdict.load_dict(filename)
        if loaded is None:
            return WordTypeDictionary({})
        else:
            return loaded
    except ValueError:
        return WordTypeDictionary({})


def init_markov_chain(filename: str) -> MarkovChain:
    try:
        loaded = markov.load_markov_chain(filename)
        if loaded is None:
            return MarkovChain(set())
        else:
            return loaded
    except ValueError:
        return MarkovChain(set())


parser = argparse.ArgumentParser(description="Commands for extended steganographic coding")
parser.add_argument("operation", metavar="operation", type=str,
                    choices=["addWordMappings", "removeWordType", "resetDict", "createChain", "resetChain",
                             "encodeBits", "decodeCover"],
                    help="select operation")
parser.add_argument("--subfolder", metavar="subfolder", type=str,
                    help="optional subdirectory for input and output files")
parser.add_argument("--mappings", metavar="mappings", type=str, help="filename of mappings list")
parser.add_argument("--dictionary", metavar="dictionary", type=str, help="filename of word-type dictionary")
parser.add_argument("--chain", metavar="chain", type=str, help="filename of Markov chain")
parser.add_argument("--encodeSpaces", metavar="encodeSpaces", type=bool,
                    help="whether this word-type should encode spaces before each word")
parser.add_argument("--wordType", metavar="wordType", type=str, help="name of the word-type")
parser.add_argument("--headerLength", metavar="headerLength", type=int, help="pre-shared length of cover text header")
parser.add_argument("--noOfStates", metavar="noOfStates", type=int,
                    help="the number of placeholder states to add to the new Markov chain")

args = parser.parse_args()

operation: str = args.operation

if operation.__eq__("addWordMappings"):
    """
    Add a list of mappings (word,bits) to a dictionary.
    """
    mappings_filename: str = prefix_filename(args.subfolder, args.mappings)
    dict_filename: str = args.dictionary
    word_type: str = args.wordType
    encode_spaces: Optional[bool] = args.encodeSpaces

    if dict_filename is None:
        raise ValueError("Filename for word-type dictionary was not provided.")
    else:
        dict_filename = prefix_filename(args.subfolder, dict_filename)
    if word_type is None:
        raise ValueError("Name of the word-type for new mappings was not provided.")
    if encode_spaces is None:
        encode_spaces = True

    if mappings_filename is None:
        mapping_dict = textanalyser.TextAnalyser.read_mapping_dict(encode_spaces=encode_spaces, delimiter=",")
    else:
        mapping_dict = textanalyser.TextAnalyser.read_mapping_dict(mappings_filename=mappings_filename,
                                                                   encode_spaces=encode_spaces,
                                                                   delimiter=",")
    wt_dict = init_wt_dict(dict_filename)
    wt_dict.append_word_type({word_type: mapping_dict})
    print("Added {} mappings under word-type \"{}\"".format(len(mapping_dict.mappings), word_type))
    wtdict.save_dict(wt_dict, dict_filename)
    print("Saved to {}".format(dict_filename))

elif operation.__eq__("resetDict"):
    dict_filename: str = args.dictionary

    if dict_filename is None:
        raise ValueError("Filename for word-type dictionary was not provided.")
    else:
        dict_filename = prefix_filename(args.subfolder, dict_filename)

    wt_dict = WordTypeDictionary({})
    print("Word-type dictionary is now empty.")
    wtdict.save_dict(wt_dict, dict_filename)
    print("Saved to {}".format(dict_filename))

elif operation.__eq__("removeWordType"):
    dict_filename: str = args.dictionary
    word_type: str = args.wordType

    if dict_filename is None:
        raise ValueError("Filename for word-type dictionary was not provided.")
    else:
        dict_filename = prefix_filename(args.subfolder, dict_filename)
    if word_type is None:
        raise ValueError("Name of the word-type to remove was not provided.")
    elif word_type.__eq__(""):
        raise ValueError("Name of the word-type to remove was empty.")

    wt_dict = init_wt_dict(dict_filename)
    if wt_dict.wt_dict is None:
        print("Given dictionary was empty.")
        exit()
    wt_dict.remove_word_type({word_type})
    print("Removed word type \"{}\" from dictionary.".format(word_type))
    wtdict.save_dict(wt_dict, dict_filename)
    print("Saved to {}".format(dict_filename))

elif operation.__eq__("createChain"):
    """
    Create a placeholder Markov chain and save to file.
    """
    chain_filename: str = args.chain
    no_of_states: int = args.noOfStates

    if chain_filename is None:
        raise ValueError("Filename for Markov chain was not provided.")
    else:
        chain_filename = prefix_filename(args.subfolder, chain_filename)
    if no_of_states is None:
        no_of_states = 2
    elif no_of_states < 2:
        raise ValueError("Number of states provided must be at least 2 (including start state \"s0\").")
    elif no_of_states > 100:
        raise ValueError("Number of states provided cannot exceed 100.")

    new_states = set()
    for state_index in range(1, no_of_states):
        new_states.add(("state_name" + str(state_index), "word_type" + str(state_index)))
    markov_chain = MarkovChain(new_states)

    from_state = "s0"
    to_state = "state_name1"
    transitions = {(from_state, to_state, 1)}
    for state_index in range(1, no_of_states - 1):
        from_state = "state_name" + str(state_index)
        to_state = "state_name" + str(state_index + 1)
        transitions.add((from_state, to_state, 1))
    transitions.add((to_state, "s0", 1))
    markov_chain.set_transitions(transitions)

    markov.save_markov_chain(markov_chain, chain_filename)

elif operation.__eq__("resetChain"):
    """
    Create an empty Markov chain and save to file.
    """
    chain_filename: str = args.chain

    if chain_filename is None:
        raise ValueError("Filename for Markov chain was not provided.")
    else:
        chain_filename = prefix_filename(args.subfolder, chain_filename)

    markov_chain = MarkovChain(set())
    print("Markov chain is now empty.")
    markov.save_markov_chain(markov_chain, chain_filename)
    print("Saved to {}.".format(chain_filename))

elif operation.__eq__("encodeBits"):
    """
    Use a Markov chain and a corresponding dictionary of word-types to encode some bits into a cover text.
    """
    chain_filename: str = args.chain
    dict_filename: str = args.dictionary
    input_filename: str = args.input
    output_filename: str = args.output
    header_length: int = args.headerLength

    if chain_filename is None:
        raise ValueError("Filename for Markov chain was not provided.")
    else:
        tree_filename = prefix_filename(args.subfolder, chain_filename)
    if dict_filename is None:
        raise ValueError("Filename for word-type dictionary was not provided.")
    else:
        dict_filename = prefix_filename(args.subfolder, dict_filename)
    if input_filename is None:
        raise ValueError("Filename for input was not provided.")
    else:
        input_filename = prefix_filename(args.subfolder, input_filename)
    if output_filename is None:
        raise ValueError("Filename for output was not provided.")
    else:
        output_filename = prefix_filename(args.subfolder, output_filename)
    if header_length is None:
        header_length = DEFAULT_HEADER_LENGTH
    elif header_length < 1:
        raise ValueError("Header length must be greater than 0.")

    input_message = read_input_file(input_filename)
    try:
        message_bits = Bits(bin=input_message)
    except CreationError:
        raise ValueError("Provided input was not a valid bitstring.")
    if message_bits.__eq__(Bits()):
        raise ValueError("Provided input was empty.")

    markov_chain = markov.load_markov_chain(chain_filename)
    print("Markov chain loaded.")

    wt_dict = init_wt_dict(dict_filename)
    print("Word-type dictionary loaded.")

    print("Encoding cover text with header length {}.".format(header_length))
    cover_text = extendedcoder.encode_message(markov_chain, wt_dict, message_bits, header_length)

    write_output_file(output_filename, cover_text)
    print("Cover text written to {}.".format(output_filename))
