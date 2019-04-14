import random
from itertools import accumulate
from typing import Tuple, Set

State = str
Probability = float
Transition = Tuple[State, Probability]
Transitions = Set[Transition]

START_STATE_LABEL = "s0"


class MarkovError(Exception):
    """Raised when something went logically wrong with a Markov Chain"""
    pass


class StateTransitions:
    """
    A set of outbound transitions for a state is a non-empty set of elements, each with a unique and valid state
    label and non-zero probability.
    """

    def __init__(self, transitions: Transitions):
        input_transitions = dict((label, prob) for label, prob in transitions)
        self.transitions = {}
        for key, value in input_transitions.items():
            if value > 0:
                self.transitions[key] = value


class MarkovChain:
    """
    A Markov chain is a collection of states with unique labels, and state transitions defining the outbound transitions
    for every state. There are a number of constraints on the chain.

    * It must have a start state, labelled as s0.
    * It must have at least one other state.
    * Any state except s0 may have a transition to s0.
    * Ignoring all transitions to s0, the chain must have no cycles.
    * No transition has probability 0.

    It is possible that the Markov chain is made up of multiple connected components and is not fully connected,
    so not all states are guaranteed to be reachable from s0. Care should be taken when defining transitions.
    """

    def __init__(self, states: set):
        self.states = states
        if not self.states.__contains__(START_STATE_LABEL):
            self.states.add(START_STATE_LABEL)
        self.current_state = START_STATE_LABEL
        self.markov_chain = {}
        for state in self.states:
            self.markov_chain.update({state: None})

    def set_transitions(self, transitions: Transitions):
        """
        Validate and set transitions for this Markov chain from the given set. Check for cycles in the chain.
        :param transitions: A set of transitions, which are 3-tuples (State, State, Probability).
        """
        self.validate_transitions(transitions)

        for from_state, to_state, prob in transitions:
            outbound_transitions = self.markov_chain.get(from_state)
            if outbound_transitions is None:
                self.markov_chain.update({from_state: StateTransitions({(to_state, prob)})})
            else:
                self.markov_chain.get(from_state).transitions.update({to_state: prob})
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
            error_messages.add("States in the given transitions were not found in the Markov chain: {}".
                               format(error_states))
        if error_probabilities.__len__() > 0:
            error_messages.add("Some probabilities in the given transitions were invalid: {}".
                               format(error_probabilities))
        if error_transitions.__len__() > 0:
            error_messages.add("States in the given transitions pointed to themselves: {}".
                               format(error_transitions))
        if s0_inward == 0:
            error_messages.add("The start state had no inward transitions.")
        if s0_outward == 0:
            error_messages.add("The start state had no outward transitions.")
        if error_messages.__len__() > 0:
            raise MarkovError("The given transitions were invalid: \n{}".format(error_messages))

    def find_cycles(self):
        walk = ["s0"]
        index = 0

        while index < len(walk):
            transitions = self.markov_chain.get(walk[index]).transitions
            # if transitions.get(walk[index]) is not None:
            #     raise MarkovError("Found a loop at state {}".format(walk[index]))
            for outbound_state in transitions.keys():
                if not outbound_state.__eq__("s0"):
                    if outbound_state in walk[:index + 1]:
                        raise MarkovError("Found a loop at transition {} to {}".format(walk[index], outbound_state))
                    else:
                        walk.append(outbound_state)
            index += 1

    def get_outbound_transitions(self) -> (State, Probability):
        """
        :return: the outbound transitions for the current state as a dictionary of Transition types
        """
        # noinspection PyTypeChecker
        outbound_transitions: StateTransitions = self.markov_chain.get(self.current_state)
        return outbound_transitions

    def accumulate_transitions(self) -> list:
        outbound_transitions = self.get_outbound_transitions()
        accum = zip(outbound_transitions.transitions.keys(), accumulate(outbound_transitions.transitions.values()))
        return list(accum)

    def transition(self):
        accum = self.accumulate_transitions()
        total = accum[len(accum) - 1][1]
        rand = random.uniform(0, total)
        for state, prob in accum:
            if rand <= prob:
                print("Transitioning to {}".format(state))
                self.current_state = state
                return
