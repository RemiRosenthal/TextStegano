import argparse
from typing import Optional

from stegano import textanalyser, wtdict
from stegano.wtdict import WordTypeDictionary


def prefix_filename(subfolder: str, filename: str) -> str:
    if subfolder is not None:
        return "..\\" + subfolder + "\\" + filename
    return "..\\" + filename


def init_wt_dict(filename: str) -> WordTypeDictionary:
    loaded = WordTypeDictionary({})
    try:
        loaded = wtdict.load_dict(filename)
    except ValueError:
        return loaded
    return WordTypeDictionary({})


parser = argparse.ArgumentParser(description="Commands for extended steganographic coding")
parser.add_argument("operation", metavar="operation", type=str,
                    choices=["addWordMappings", "removeWordType", "resetDict"],
                    help="select operation")
parser.add_argument("--subfolder", metavar="subfolder", type=str,
                    help="optional subdirectory for input and output files")
parser.add_argument("--mappings", metavar="mappings", type=str, help="filename of mappings list")
parser.add_argument("--dictionary", metavar="dictionary", type=str, help="filename of word-type dictionary")
parser.add_argument("--encodeSpaces", metavar="encodeSpaces", type=bool,
                    help="whether this word-type should encode spaces before each word")
parser.add_argument("--wordType", metavar="wordType", type=str, help="name of the word-type")

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

    wt_dict = init_wt_dict(dict_filename)
    if wt_dict.wt_dict is None:
        print("Given dictionary was empty.")
        exit()
    wt_dict.remove_word_type({word_type})
    print("Removed word type \"{}\" from dictionary.".format(word_type))
    wtdict.save_dict(wt_dict, dict_filename)
    print("Saved to {}".format(dict_filename))
