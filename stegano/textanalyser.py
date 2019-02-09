import collections
import re
from functools import reduce

ANALYSIS_SEPARATOR = ","
DEFAULT_SAMPLE_FILE = "..\\sample_text.txt"
DEFAULT_ANALYSIS_FILE = "..\\analysis.txt"


class TextAnalyser:
    # Attempt to analyse a text sample for a statistical profile of string frequencies.
    # The length of that string can be specified, otherwise is 1 by default.
    @staticmethod
    def analyse_sample(sample_filename=DEFAULT_SAMPLE_FILE, string_length=1) -> collections.Counter:
        string_definitions = collections.Counter()

        try:
            with open(sample_filename, "r", encoding="utf-8") as handle:
                text = handle.read()  # Read the entire file

            rep = {"\n": "", "\t": ""}  # define desired replacements here

            rep = dict((re.escape(k), v) for k, v in rep.items())
            pattern = re.compile("|".join(rep.keys()))
            text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

            for index in range(len(text) - string_length + 1):
                string_definitions.update({text[index:(index + string_length)]: 1})
        except IOError:
            print("Could not locate or read sample file " + sample_filename)

        return string_definitions

    # Print the strings to the given file
    @staticmethod
    def print_analysis(string_definitions: collections.Counter, analysis_filename=DEFAULT_ANALYSIS_FILE):
        try:
            with open(analysis_filename, "w", encoding="utf-8") as handle:
                for string_def in string_definitions.most_common():
                    handle.write(string_def[0])
                    handle.write(ANALYSIS_SEPARATOR)
                    handle.write(str(string_def[1]))
                    handle.write("\n")
        except IOError:
            print("Could not write analysis file " + analysis_filename)

    # Attempt to read the analysis file and return a set of tuples representing the analysis
    @staticmethod
    def read_analysis(analysis_filename=DEFAULT_ANALYSIS_FILE) -> set:
        string_definitions = set()
        try:
            with open(analysis_filename, "r", encoding="utf-8") as file:
                for line in file:
                    freq_tuple = line.rpartition(ANALYSIS_SEPARATOR)
                    if not freq_tuple[0]:
                        raise ValueError("A line in the analysis appeared to be malformed")
                    if int(freq_tuple[2]) > 0:  # Second part must be a natural integer
                        string_definitions.add((freq_tuple[0], int(freq_tuple[2])))
                    else:
                        replaced = line.replace("\n", "")
                        print(f"Invalid line: \"{replaced}\"")
        except OSError:
            raise IOError("Could not locate or read analysis file " + analysis_filename)

        return string_definitions

    # Attempt to read the analysis file if one exists, otherwise generate a new analysis
    @staticmethod
    def get_analysis(sample_filename=DEFAULT_SAMPLE_FILE, analysis_filename=DEFAULT_ANALYSIS_FILE,
                     string_length=1) -> set:
        try:
            return TextAnalyser.read_analysis(analysis_filename)
        except IOError:
            TextAnalyser.print_analysis(TextAnalyser.analyse_sample(sample_filename, string_length))
            return TextAnalyser.read_analysis(analysis_filename)

    # For a set of strings and their frequencies, normalise the frequencies such that they all add to 1
    @staticmethod
    def normalise_frequencies(string_definitions: set) -> set:
        normalised = set()
        if string_definitions:
            total = reduce(lambda x, y: x + y, map(lambda x: int(x[1]), string_definitions))

            for string_def in string_definitions:
                normalised.add((string_def[0], int(string_def[1]) / total))

        return normalised
