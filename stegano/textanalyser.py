import os
import re
from collections import Counter
from functools import reduce
from typing import Tuple, Set

from bitstring import Bits

from stegano.wtdict import MappingDictionary

ANALYSIS_SEPARATOR = ","
DEFAULT_SAMPLE_FILE = "..\\sample_text.txt"
DEFAULT_ANALYSIS_FILE = "..\\analysis.txt"
DEFAULT_MAPPINGS_FILE = "..\\mappings.txt"


class TextAnalyser:
    @staticmethod
    def analyse_sample(sample_filename=DEFAULT_SAMPLE_FILE,
                       string_length=1) -> Counter:
        """
        Analyse the given sample text for a statistical profile of
        string frequencies.

        The length of that string can be specified, otherwise it is 1
        by default.
        """
        string_definitions = Counter()
        try:
            with open(sample_filename, "r",
                      encoding="utf-8") as handle:
                text = handle.read()  # Read the entire file

            rep = {"\n": "",
                   "\t": ""}  # define desired replacements here

            rep = dict((re.escape(k), v) for k, v in rep.items())
            pattern = re.compile("|".join(rep.keys()))
            text = pattern.sub(lambda m: rep[re.escape(m.group(0))],
                               text)

            symbol_count = len(text) - string_length + 1
            print("Sample has {} symbols".format(symbol_count))
            for index in range(symbol_count):
                string_definitions.update(
                    {text[index:(index + string_length)]: 1})
        except IOError:
            print(
                "Could not locate or read sample file " +
                sample_filename)

        return string_definitions

    @staticmethod
    def print_analysis(string_definitions: Counter,
                       analysis_filename=DEFAULT_ANALYSIS_FILE,
                       encoding="utf-8"):
        """
        Print the string definitions in the analysis file defined
        by the given filename
        """
        try:
            with open(analysis_filename, "w",
                      encoding=encoding) as handle:
                for string_def in string_definitions.most_common():
                    handle.write(string_def[0])
                    handle.write(ANALYSIS_SEPARATOR)
                    handle.write(str(string_def[1]))
                    handle.write("\n")
        except IOError:
            raise ValueError(
                "Could not write analysis file {}.".format(
                    analysis_filename))
        except LookupError:
            raise ValueError(
                "Could not decode analysis file {} with encoding "
                "\"{}\".".format(
                    analysis_filename, encoding))

    @staticmethod
    def read_analysis(analysis_filename=DEFAULT_ANALYSIS_FILE) -> set:
        """
        Attempt to read the analysis file and return a set of
        tuples representing the analysis
        """
        string_definitions = set()
        try:
            with open(analysis_filename, "r",
                      encoding="utf-8") as file:
                for line in file:
                    freq_tuple = line.rpartition(ANALYSIS_SEPARATOR)
                    if not freq_tuple[0]:
                        raise ValueError(
                            "A line in the analysis appeared to be "
                            "malformed")
                    if int(freq_tuple[
                               2]) > 0:  # Second part must be a
                        # natural integer
                        string_definitions.add(
                            (freq_tuple[0], int(freq_tuple[2])))
                    else:
                        replaced = line.replace("\n", "")
                        print(f"Invalid line: \"{replaced}\"")
        except OSError:
            raise IOError(
                "Could not locate or read analysis file " +
                analysis_filename)

        return string_definitions

    @staticmethod
    def get_analysis(sample_filename=DEFAULT_SAMPLE_FILE,
                     analysis_filename=DEFAULT_ANALYSIS_FILE,
                     string_length=1) -> set:
        """
        Attempt to read the analysis file if one exists, otherwise
        generate a new analysis
        """
        try:
            return TextAnalyser.read_analysis(analysis_filename)
        except IOError:
            TextAnalyser.print_analysis(
                TextAnalyser.analyse_sample(sample_filename,
                                            string_length))
            return TextAnalyser.read_analysis(analysis_filename)

    @staticmethod
    def delete_analysis(analysis_filename=DEFAULT_ANALYSIS_FILE):
        """
        Delete the given analysis file if it exists
        """
        try:
            if os.path.exists(analysis_filename):
                os.remove(analysis_filename)
        except OSError:
            print("Failed to delete the file")

    @staticmethod
    def normalise_frequencies(string_definitions: set) -> set:
        """
        For a set of strings and their frequencies, normalise the
        frequencies such that they all add to 1
        """
        normalised = set()
        if string_definitions:
            total = reduce(lambda x, y: x + y,
                           map(lambda x: int(x[1]),
                               string_definitions))

            for string_def in string_definitions:
                normalised.add(
                    (string_def[0], int(string_def[1]) / total))

        return normalised

    @staticmethod
    def read_mapping_dict(mappings_filename=DEFAULT_MAPPINGS_FILE,
                          encode_spaces=True,
                          delimiter=",") -> MappingDictionary:
        """
        Attempt to read word-bit mappings from the given file and
        return a new MappingDictionary object of those
        mappings.

        :param mappings_filename: full filename of the mappings file
        :param encode_spaces: if creating new word-type from these
        mappings, sets encode_spaces for that word-type
        :param delimiter: the single character separating the word
        and bitstring on each line
        :return: a MappingDictionary object
        """
        mappings = set()
        try:
            with open(mappings_filename, "r",
                      encoding="utf-8") as file:
                for line in file:
                    mapping_tuple = line.rpartition(delimiter)
                    if not mapping_tuple[0]:
                        raise ValueError(
                            "A line in the mappings list appeared "
                            "to be malformed")
                    try:
                        bits = Bits(bin=mapping_tuple[2])
                    except ValueError:
                        raise ValueError(
                            "A line in the mappings list did not "
                            "contain a valid bitstring")
                    mappings.add((mapping_tuple[0], bits))
        except OSError:
            raise IOError(
                "Could not locate or read mappings file " +
                mappings_filename)
        mapping_dict = MappingDictionary(mappings, encode_spaces)

        return mapping_dict

    @staticmethod
    def combine_analyses(analysis_1: Set[Tuple[str, int]],
                         analysis_2: Set[Tuple[str, int]]) -> \
            Tuple[Counter, Counter, Counter]:
        """
        Combine two analyses. The third list in the output will be
        the union of values in both input lists.
        The first two lists in the output will correspond to the
        two inputs, excluding the values in the last output
        list.

        :param analysis_1: the first list of word-frequency pairs
        :param analysis_2: the second list of word-frequency pairs
        :return: three lists as a tuple
        """
        dict_1 = {x: y for x, y in analysis_1}
        counter_2 = Counter()

        shared_words = Counter()

        for word_2, freq_2 in analysis_2:
            freq_1 = dict_1.get(word_2)
            if freq_1 is not None:
                shared_words.update({word_2: freq_2 + freq_1})
                del dict_1[word_2]
            else:
                counter_2.update({word_2: freq_2})

        return Counter(dict_1), counter_2, shared_words
