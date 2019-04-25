import json
import random
from itertools import accumulate
from typing import Tuple, Set, Optional, Union

State = str
Probability = float
Transition = Tuple[State, State, Probability]
Transitions = Set[Transition]

DEFAULT_MARKOV_FILE = "..\\sample\\markov_chain.json"

START_STATE_LABEL = "s0"


class MarkovError(Exception):
    """Raised when something went logically wrong with a Markov
    Chain"""
    pass


class StateTransitions:
    """
    A set of outbound transitions for a state is a non-empty set of
    elements, each with a unique and valid state
    label and non-zero probability.
    """
    def __init__(self, transitions: Set[Tuple[State, Probability]]):
        input_transitions = dict(
            (label, prob) for label, prob in transitions)
        self.transitions = {}
        for key, value in input_transitions.items():
            if value > 0:
                self.transitions[key] = value

    def __dict__(self):
        serial_dict = {}
        for k, v in self.transitions.items():
            serial_dict.update({k: v})
        return serial_dict


class MarkovChain:
    """
    A Markov chain is a collection of states with unique labels,
    and state transitions defining the outbound transitions
    for every state. There are a number of constraints on the chain.

    * It must have a start state, labelled as s0.
    * It must have at least one other state.
    * Any state except s0 may have a transition to s0.
    * Ignoring all transitions to s0, the chain must have no cycles.
    * No transition has probability 0.

    It is possible that the Markov chain is made up of multiple
    connected components and is not fully connected,
    so not all states are guaranteed to be reachable from s0. Care
    should be taken when defining transitions.
    """

    def __init__(self, states: Set[Union[State, Tuple[State, str]]]):
        self.states = {START_STATE_LABEL}
        self.wt_refs = {}
        for state in states:
            if isinstance(state, tuple):
                if state[0].__eq__(START_STATE_LABEL):
                    continue
                self.wt_refs.update({state[0]: state[1]})
                self.states.add(state[0])
            else:
                self.states.add(state)
                if not state.__eq__(START_STATE_LABEL):
                    self.wt_refs.update({state: state})

        self.markov_chain = {}
        for state in self.states:
            self.markov_chain.update({state: None})

        self.current_state = START_STATE_LABEL

    def __dict__(self):
        serial_dict = {}

        serial_dict.update({"wt_refs": self.wt_refs})

        chain = {}
        for from_state in self.markov_chain.keys():
            transitions = self.markov_chain.get(from_state)
            if transitions is not None:
                chain.update({from_state: transitions.__dict__()})

        serial_dict.update({"chain": chain})
        return serial_dict

    def get_current_word_type(self) -> Optional[str]:
        """
        Retrieve the word-type referred to by the current state.
        Returns None if current state is s0.

        :return: the word-type
        """
        if self.current_state.__eq__(START_STATE_LABEL):
            return None
        else:
            return self.get_word_type_for_state(self.current_state)

    def get_word_type_for_state(self, state_name: State) -> str:
        """
        Retrieve the word-type referred to by the state of the
        given name, if such a state exists.

        This word-type is equal to the state name by default,
        unless otherwise specified.

        :param state_name: the name of state to search for
        :return: the corresponding word-type
        """
        word_type = self.wt_refs.get(state_name)
        if word_type is None:
            raise ValueError(
                "No state of name {} exists in the Markov "
                "chain.".format(
                    state_name))
        return word_type

    def set_transitions(self, transitions: Transitions):
        """
        Validate and set transitions for this Markov chain from the
        given set. Check for cycles in the chain.

        :param transitions: A set of transitions, which are
        3-tuples (State, State, Probability).
        """
        self.validate_transitions(transitions)

        for from_state, to_state, prob in transitions:
            outbound_transitions = self.markov_chain.get(from_state)
            if outbound_transitions is None:
                # noinspection PyTypeChecker
                self.markov_chain.update(
                    {from_state: StateTransitions({(to_state, prob)})}
                )
            else:
                self.markov_chain.get(from_state).transitions.update(
                    {to_state: prob})
        self.find_cycles()

    def validate_transitions(self, transitions: Transitions):
        error_messages = set()
        error_states = set()
        error_probabilities = set()
        error_transitions = set()
        s0_outward = 0
        s0_inward = 0
        for from_state, to_state, prob in transitions:
            if from_state not in self.states:
                error_states.add(from_state)
            if to_state not in self.states:
                error_states.add(to_state)
            if prob <= 0:
                error_probabilities.add((from_state, to_state))
            if from_state.__eq__(to_state):
                error_transitions.add(from_state)
            if from_state.__eq__(START_STATE_LABEL):
                s0_outward += 1
            elif to_state.__eq__(START_STATE_LABEL):
                s0_inward += 1
        if error_states.__len__() > 0:
            error_messages.add(
                "States in the given transitions were not found in "
                "the Markov chain: {}".format(
                    error_states))
        if error_probabilities.__len__() > 0:
            error_messages.add(
                "Some probabilities in the given transitions were "
                "invalid: {}".format(
                    error_probabilities))
        if error_transitions.__len__() > 0:
            error_messages.add(
                "States in the given transitions pointed to "
                "themselves: {}".format(
                    error_transitions))
        if s0_inward == 0:
            error_messages.add(
                "The start state had no inward transitions.")
        if s0_outward == 0:
            error_messages.add(
                "The start state had no outward transitions.")
        if error_messages.__len__() > 0:
            raise MarkovError(
                "The given transitions were invalid: \n{}".format(
                    error_messages))

    def find_cycles(self, current_state=START_STATE_LABEL,
                    visited=None, stack=None):
        if stack is None:
            stack = []
        if visited is None:
            visited = set()

        transitions = self.markov_chain.get(current_state).transitions
        visited.add(current_state)
        for outbound_state in transitions.keys():
            if outbound_state in stack:
                if not outbound_state.__eq__(START_STATE_LABEL):
                    raise MarkovError(
                        "Found a loop at transition {} to {}".format(
                            current_state, outbound_state))
            if outbound_state not in visited:
                self.find_cycles(outbound_state, visited,
                                 stack + [current_state])

    def get_outbound_transitions(self) -> StateTransitions:
        """
        Get the outbound transitions for the current state as
        a dictionary of Transition types.

        :return: the outbound transitions
        """
        # noinspection PyTypeChecker
        outbound_transitions: StateTransitions = self.markov_chain.\
            get(self.current_state)
        return outbound_transitions

    def accumulate_transitions(self) -> list:
        """
        Create a list of outbound transitions from the current
        state, each paired with an accumulated probability.
        That accumulated probability, for each transition, is the
        sum of the transition's probability and all of those
        that came before it in the list.

        e.g. [("x", 0.3), ("y", 0.5), ("z", 0.2)] -> [("x", 0.3),
        ("y", 0.8), ("z", 1.0)]

        :return: the list of transitions
        """
        outbound_transitions = self.get_outbound_transitions()
        accum = zip(outbound_transitions.transitions.keys(),
                    accumulate(
                        outbound_transitions.transitions.values()))
        return list(accum)

    def transition(self):
        """
        Choose the next state to transition to based on the
        probabilities of all transitions outbound from the current
        state. Set the current state to that state.
        """
        accum = self.accumulate_transitions()
        total = accum[len(accum) - 1][1]
        rand = random.uniform(0, total)
        for state, prob in accum:
            if rand <= prob:
                print("Transitioning to {}".format(state))
                self.current_state = state
                return


def get_number_of_paths(chain: MarkovChain,
                        from_state=START_STATE_LABEL,
                        path_counts=None) -> int:
    """
    Calculate the total number of distinct paths to s0 in the
    chain, starting from the given state.

    :return: the number of paths
    """
    if path_counts is None:
        path_counts = {}

    outbound_states = set(
        chain.markov_chain.get(from_state).transitions.keys())
    number_of_paths = 0

    if START_STATE_LABEL in outbound_states:
        number_of_paths += 1
        outbound_states.remove(START_STATE_LABEL)

    for state in outbound_states:
        number_of_paths += get_number_of_paths(chain, state,
                                               path_counts)

    path_counts.update({from_state: number_of_paths})

    return number_of_paths


def deserialise_markov_chain(markov_dict: dict) -> MarkovChain:
    """
    Convert a serialised dict (of strings) to a Markov chain object.

    :param markov_dict: serialised dict representing the Markov
    chain transitions
    :return: a Markov chain
    """
    wt_refs = markov_dict.get("wt_refs")
    if wt_refs is None:
        raise MarkovError(
            "Input Markov chain did not contain wt_refs attribute.")

    chain = markov_dict.get("chain")
    if chain is None:
        raise MarkovError(
            "Input Markov chain did not contain chain attribute.")

    states = set(wt_refs.keys()).union({START_STATE_LABEL})
    markov_chain = MarkovChain(states)
    markov_chain.wt_refs = wt_refs
    transitions = set()
    for state in states:
        if chain.get(state) is None:
            print(
                "State {} declared in word-type mappings, but not "
                "used.".format(
                    state))
        else:
            transitions.update(
                {(state, x, y) for x, y in chain.get(state).items()})
    # noinspection PyTypeChecker
    markov_chain.set_transitions(transitions)

    return markov_chain


def load_markov_chain(chain_filename=DEFAULT_MARKOV_FILE) ->\
        MarkovChain:
    """
    Attempt to load a JSON file as a Markov chain object.

    :param chain_filename: the path of the file
    :return: the Markov chain object, as long as the file is valid
    """
    try:
        with open(chain_filename, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            return deserialise_markov_chain(data)
    except IOError:
        raise ValueError("Could not read Markov chain file {}".format(
            chain_filename))


def save_markov_chain(markov_chain: MarkovChain,
                      chain_filename=DEFAULT_MARKOV_FILE):
    """
    Save a Markov chain object as a JSON file.

    :param markov_chain: a Markov Chain object
    :param chain_filename: the desired path of the file
    """
    try:
        with open(chain_filename, "w", encoding="utf-8") as handle:
            json.dump(markov_chain, handle, indent=2,
                      default=lambda o: o.__dict__())
    except IOError:
        raise ValueError(
            "Could not write Markov chain file {}.".format(
                chain_filename))
