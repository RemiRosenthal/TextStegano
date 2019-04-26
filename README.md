# TextStegano

TextStegano is a collection of algorithms and supporting tools for text and linguistic steganography.
Using various experimental steganographic techniques, it can transform some binary data into an innocuous cover text meant to resemble a natural language, but unrelated to the input data.

## Prerequisites

This program explicitly supports Python 3.7.x, and is likely to work with any later version of Python 3.

To run each command, please use the package manager [pip](https://pip.pypa.io/en/stable/) to install each of the required packages as follows:

```bash
pip install bitstring
pip install cryptography
```

## Usage

### Available Techniques

The following is an overview of steganographic techniques and how they can be used with this program. See [commands](###Commands) and [arguments](###Arguments) for how to use each command.

#### Reverse Huffman Coding

The Huffman tree, invented by David Huffman (1952) is a special binary tree commonly used to generate the optimal set of mappings between characters and bit-strings in order to compress text as much as possible. A steganographic technique using these trees was developed by Peter Wayner (1992), called "reverse Huffman coding".

To encode a cover text using this technique, one should:
* Run `analyseSample` on a text sample
* Create a Huffman tree from the resulting analysis using `createTree`
* Securely share the Huffman tree with everyone that one wishes to covertly communicate with
* Prepare a secret message in binary form (e.g. using `charEncode`)
* Optionally encrypt that secret message using `encrypt`
* Encode the secret message using `run_huffmancoder.py encodeBits`

The resulting cover text can now be sent over an insecure channel. The receiver should:
* Decode the received cover text using `run_huffmancoder.py decodeCover`
* Decrypt the resulting message if needed using `decrypt`
The receiver will now have the secret data in binary form. If it originally represented text, it can be decoded into that text using `charDecode`.


#### Extended Coding

I have developed an extended steganographic coding technique, inspired by "NICETEXT" (Chapman and Davida, 1997). By creating a word-type dictionary and a "contextual template Markov chain" of states corresponding to word-types, a cover text can be encoded containing many different gramatically-correct sentence structures. It is up to the user to define an effective Markov chain and generate a list of mappings from appropriate frequency lists of words.

To encode a cover text using this technique, one should:
* Prepare a set of frequency lists, one for each word-type as desired - e.g. verbs, nouns, etc. from a text corpus
* Convert each list into a Huffman tree using `createTree` for each
* Convert each tree into the corresponding word-bit mappings using `exportMappings` for each
* Create a new word-type dictionary using `resetDict`
* Append all of the word-bit mapping lists into that new dictionary using `addWordMappings`
* Securely share the word-type dictionary with everyone that one wishes to covertly communicate with
* Also securely share an agreed header length (around 15 is usually appropriate)
* Create a template Markov chain using `createChain`
* Build the new Markov chain into one using all of the word-types in the created dictionary; all possible sequences of states in the chain is a sequence of word-types that should represent a sentence in the target language
* Prepare a secret message in binary form (e.g. using `charEncode`)
* Optionally encrypt that secret message using `encrypt`
* Encode the secret message using `run_extcoder.py encodeBits`

The resulting cover text can now be sent over an insecure channel. The receiver should:
* Decode the received cover text using `run_extcoder.py decodeCover`
* Decrypt the resulting message if needed using `decrypt`
The receiver will now have the secret data in binary form. If it originally represented text, it can be decoded into that text using `charDecode`.


### Commands

TextStegano consists of several functions spread over a number of modules.
[See the explanation for all arguments](###Arguments).

#### Text Analysis

The following commands can be called using the `run_textanalyser.py` file.

* `python run_textanalyser.py analyseSample --subfolder sample --input sample_text.txt --output freq_sample_5.txt --symbolLen 5`
  
  Analyses a sample text for a list of all n-length symbols that make it up (for n = `symbolLen`), and their frequencies. Useful for the reverse Huffman steganographic techinque. It is recommended to supply a long text sample, such as a book, in your desired natural language.


* `python run_textanalyser.py combineFreqs --subfolder sample --input freq_prep.txt --combine freq_adverb.txt --output freq_prepadverb.txt`
  
  Finds all words which appear in two input analyses (`input` and `combine`); outputs those words (with summed frequencies) to a new frequency analysis file; and removes those words from both input analyses - useful for creating a valid word-type dictionary, because no word may exist twice in a word-type dictionary.


#### Huffman Coder

The following commands can be called using the `run_huffmancoder.py` file.

* `python run_huffmancoder.py createTree --subfolder sample --analysis freq_sample_1.txt --tree huffman_tree_1.json`
  
  Creates a Huffman tree from a frequency analysis. The created tree will only be valid for reverse Huffman steganographic encoding if all values in the input analysis are of equal length. Values with a higher frequency will be closer to the root of the Huffman tree, and therefore have a higher probability of being encoded in cover texts.
  To use the output tree for reverse Huffman coding, it must first be securely shared among all authorised parties.

  For reverse Huffman encoding, it is recommended to analyse a text sample to generate a frequency analysis. For the extended coding technique, it is recommended to find a large text corpus of words and their frequencies in your desired natural language.


* `python run_huffmancoder.py encodeBits --subfolder sample --tree huffman_tree_1.json --input input_a.txt --output huff_encoded_1.txt`
  
  Use the reverse Huffman method to encode a cover text from the input secret message. A valid Huffman tree must be supplied, defining the set of fixed-length symbols that will comprise the cover text.


* `python run_huffmancoder.py decodeCover --subfolder sample --tree huffman_tree_5.json --input huff_encoded_5.txt --output huff_decoded.txt --symbolLen 5`
  
  Use the reverse Huffman method to decode an input cover text into the secret message that was hidden inside it. The same Huffman tree that was used to encode the cover text must be supplied, along with a `symbolLen` equal to the length of the symbols in the tree.


* `python run_huffmancoder.py exportMappings --subfolder sample --tree tree_adj.json --output mappings_adj.txt`
  
  Converts a Huffman tree into a list of symbol-bits pairs. Each symbol is a value from the Huffman tree, and each bit-string is the corresponding path code of the node in the tree.
  The resulting list of mappings should have no duplicate values, and no duplicate bit-strings.


* `python run_huffmancoder.py analyseTree --subfolder sample --tree huffman_tree_10.json`
  
  Prints some properties of a Huffman tree: the number of symbols in the tree; and the average and expected path code lengths of the mappings in the tree.


#### Extended Coder

The following commands can be called using the `run_extcoder.py` file.

* `python run_extcoder.py addWordMappings --subfolder sample --mappings mappings_adj.txt --dictionary word_type_dict.json --wordType adj`
  
  Adds a new word-type to the given dictionary under the given name, with the given list of word-bits mappings.


* `python run_extcoder.py resetDict --subfolder sample --dictionary empty_json.json`
  
  Create an empty word-type dictionary at the given file location. Overwrites files!


* `python run_extcoder.py removeWordType --subfolder sample --dictionary word_type_dict.json --wordType adj`
  
  Removes a word-type and its mappings from the given dictionary. The word-type to be removed is the one with the specified name, and there will be no effect if no such word-type exists in the dictionary.


* `python run_extcoder.py createChain --subfolder sample --chain new_markov_chain.json --noOfStates 10`
  
  Creates a placeholder Markov chain with the specified number of states, and the minimal required set of state transitions between those states.

  The output Markov chain will have a `wt_refs` property defining a collection of states as key-value pairs. Each key is the name of a new state, and can be renamed as desired. Each corresponding value must be the name of a word-type in a word-type dictionary. Under the `chain` property, there will be a collection of all states in the Markov chain and all of the outward transitions from each of those states. Every one of these transitions is a pair: the name of the destination state and a non-zero weighting defining how likely that transition is to occur out of all transitions from the state.

  There are a number of constraints on a valid Markov chain:

  * A start state, labelled as s0, is implicitly part of the chain.
  * The chain must have at least one state other than s0.
  * Any state except s0 may have a transition to s0.
  * Except for the transitions into s0, the chain must have no cycles (loops).
  * Every transition must have a non-zero "probability", which will be automatically weighted with the other outward probabilities.

  The output Markov chain should be manually edited as desired. A sample chain is available in `sample\markov_chain.json`.


* `python run_extcoder.py resetChain --subfolder sample --chain empty_markov_chain.json`
  
  Create an empty Markov chain.


* `python run_extcoder.py encodeBits --subfolder sample --chain markov_chain.json --dictionary word_type_dict.json --input input_a.txt --output ext_encoded_a.txt --headerLength 14`
  
  Use the extended method to encode a cover text from the input secret message. A valid model (word-type dictionary and Markov chain) must be supplied, as well as the pre-shared header length.


* `python run_extcoder.py decodeCover --subfolder sample --dictionary word_type_dict.json --input ext_encoded_a.txt --output ext_decoded.txt --headerLength 14`
  
  Use the extended method to decode an input cover text into the secret message that was hidden inside it. The same word-type dictionary and header length that was used to encode the cover text must be supplied, but no Markov chain is needed.


* `python run_extcoder.py analyseChain --subfolder sample --chain markov_chain.json`
  
  Prints the number of unique paths (in one start-to-start cycle) in the given markov chain.


#### Utils

The following commands can be called using the `run_utils.py` file.

* `python run_utils.py encrypt --subfolder sample --input plaintext_in.txt --output encrypted.txt --key BFFeOSw8nUJahkRjiBxASbZ7DehAzwfxIHPoDE33RjI=`
  
  Encrypts a binary input into a binary output. An encrypted input is useful for steganography as it confuses the structure of the bits in the message. It is recommended to encrypt bit-strings before encoding them into a cover text. The receiver should then decode the cover text and decrypt the resulting bit-string into your secret message.


* `python run_utils.py decrypt --subfolder sample --input encrypted.txt --output decrypted.txt --key BFFeOSw8nUJahkRjiBxASbZ7DehAzwfxIHPoDE33RjI=`
  
  Decrypts a binary input into a binary output. The same pre-shared private key should be used as was used to encrypt the message.


* `python run_utils.py generateKey`
  
  Generates a private key. This should be securely shared with parties you wish to communicate with if using encryption.


* `python run_utils.py charEncode --subfolder test_data --input utf8_in.txt --output char_decoded.txt --encoding utf_8`
  
  Encodes some text in the given character encoding system as bits. The default value, `utf_8`, is typical and should work for most text.


* `python run_utils.py charDecode --subfolder test_data --input char_decoded.txt --output utf8_out.txt`
  
  Attempts to decode a binary input into characters using the given character encoding system. This will only work if the bits in the input represent characters in that system.


### Arguments

* `subfolder`: string
  
  Always optional. Without this argument, input and output files will be looked for and created inside the TextStegano root directory. Otherwise, the string supplied to this argument is the name of the relative or absolute path of the subfolder containing the files.


* `encoding`: string
  
  The name of the desired character encoding method. Default is `utf_8`. Must be a standard encoding as listed in https://docs.python.org/2.4/lib/standard-encodings.html.


* `input`: string
  
  The filename of the primary input file. If a `subfolder` is supplied, this argument is appended to the end of the `subfolder` value.


* `output`: string
  
  The filename of the primary output file. If a `subfolder` is supplied, this argument is appended to the end of the `subfolder` value.


* `combine`: string
  
  The filename of the secondary input file to `combineFreqs`. If a `subfolder` is supplied, this argument is appended to the end of the `subfolder` value.


* `analysis`: string
  
  The filename of a frequency analysis input. A frequency analysis must contain 1 or more lines, with each line containing a value-frequency pair, separated by a comma. A value can be any string of characters, and a frequency is a positive integer. No value may be defined more than once within the file. The following is a valid example:
  ```
  foo,100
  bar,75
  ```

* `tree`: string
  
  The filename of a Huffman tree. A Huffman tree is a JSON-formatted dictionary, recursively defined as a set of four attributes:
  * `value`: string - the value contained within the node; must be set to a unique string in all leaf nodes and `null` in all non-leaf nodes
  * `path_code`: string - the binary code representing the node's position in the tree; must be set in all nodes except the root of the tree where it should be `null`
  * `left`: huffman_tree - the nested left-subtree of this tree; every tree must either be a leaf with both `left` and `right` as `null`, or have exactly both `left` and `right` set as valid trees
  * `right`: huffman_tree - the nested right-subtree of this tree
  
  It is not advisable to define a Huffman tree manually; it should be generated by `createTree` as needed.


* `mappings`: string
  
  The filename of a mappings list. A list of mappings must contain 1 or more lines, with each line containing a value-binary pair, separated by a comma. A value can be any string of characters. No value or bit-string may be defined more than once within the file. The following is a valid example:
  ```
  foo,00
  bar,01
  ```

  It is not advisable to define lists of mappings manually; they should be generated by `exportMappings` as needed.


* `dictionary`: string
  
  The filename of a word-type dictionary. A word-type dictionary is a JSON-formatted dictionary, containing one or more "mapping dictionaries", which are each nested dictionaries. Each mapping dictionary has a unique word-type name as its key. Each corresponding value is a nested dictionary defined as follows:
  * `encode_spaces`: boolean - `true` if words in this mapping dictionary should be preceded by spaces when encoded in a cover text
  * `mappings`: dict - a dictionary of value-binary pairs, defined as in a mappings list (see the `mappings` argument); must contain at least two items

  It is not advisable to create a word-type dictionary manually; they should be created by `resetDict` as needed. They can be modified using `addWordMappings` and `removeWordType` or manually using a text editor.


* `chain`: string
  
  The filename of a Markov chain. A Markov chain is a JSON-formatted dictionary defined as follow:
  * `wt_refs`: dict - a dictionary of state-reference pairs. Each "state" defined here is one state in a Markov chain, and each corresponding "reference" is the name of the word-type that the state references
  * `chain`: dict - a dictionary containing every state in the Markov chain as a key, and the corresponding value of each state is a nested dictionary of one or more state-probability pairs defining outbound transitions. Each item in this nested dictionary is an transition to the given state with the given probability

  It is not advisable to create a Markov chain manually; an empty chain can be created using `resetChain` and a template chain can be created using `createChain`. Then, it should be modified using a text editor to manually define a valid Markov chain.


* `symbolLen`: integer
  
  Defines the fixed length of the "symbols" contained in a Huffman tree, and when analysing a sample text. Must be a positive integer. Defaults to 1.


* `encodeSpaces`: boolean
  
  Defines whether or not the words in a list of word-binary mappings should be preceded by spaces when encoded in a cover text. Defaults to `true`.


* `wordType`: string
  
  The name of a word-type for a list of mappings to be added to a word-type dictionary.


* `headerLength`: integer
  
  The pre-shared header length (in bits) used in the extended coder. A higher value can encode more secret data: for a header length of value `n`, up to 2<sup>n</sup> bits of secret information can be encoded. However, a larger value results in a longer cover text. Must be a positive integer. Defaults to 20. A value of between 10 and 15 is recommended for plaintext communication.


* `noOfStates`: integer
  
  The number of placeholder states to add to a new Markov chain (including the start state). Must be an integer greater than 1. Defaults to 2. It is recommended to create a chain with at least one state for every word-type in the corresponding word-type dictionary, plus one (for the start state).


* `key`: string
  
  The string representation of a pre-shared private key, which is treated as a `bytes` object. A valid `key` is 44 alphanumeric characters long, and can be generated using the `generateKey` command. This argument is optional as there is a hard-coded default value, but this is likely to be insecure.
