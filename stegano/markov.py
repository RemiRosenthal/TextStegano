from typing import Tuple

State = str
Probability = float
Transition = Tuple[State, State, Probability]

START_STATE_LABEL = "s0"


class MarkovError(Exception):
    """Raised when something went logically wrong with a Markov Chain"""
    pass


class MarkovChain:
    """
    A Markov chain is a collection of states with unique labels, and transitions between those states. There are a
    number of constraints.

    * It must have a start state, labelled as s0.
    * It must have at least one other state.
    * All states must have at least one inbound transition so that all states are reachable.
    * All states must have at least one outbound transition so that the chain forms a cycle through s0.
    * Any state except s0 may have a transition to s0.
    * Ignoring all transitions to s0, the chain must have no cycles.
    * No transition has probability 0.
    """

    def __init__(self, states: set):
        self.states = states
        if not self.states.__contains__(START_STATE_LABEL):
            self.states.add(START_STATE_LABEL)
        self.transitions = set()
        self.current_state = START_STATE_LABEL

    def set_transitions(self, transitions: set):
        """
        Set the transitions for this Markov chain. The chain will then be validated.
        :param transitions: A set of transitions, which are 3-tuples (State, State, Probability).
        """
        error_messages = set()
        error_states = set()
        error_probabilities = set()
        error_transitions = set()
        s0_inward = 0
        s0_outward = 0
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
        # TODO check s0 transitions; find loops

        if error_states.__len__() > 0:
            error_messages.add("States in the given transitions were not found in the Markov chain: {}".
                               format(error_states))
        if error_probabilities.__len__() > 0:
            error_messages.add("Some probabilities in the given transitions were invalid: {}".
                               format(error_probabilities))
        if error_transitions.__len__() > 0:
            error_messages.add("Some of the given transitions caused a loop: {}".
                               format(error_transitions))
        if s0_inward == 0:
            error_messages.add("The start state had no inward transitions.")
        if s0_outward == 0:
            error_messages.add("The start state had no outward transitions.")

        if error_messages.__len__() > 0:
            raise MarkovError("The given transitions were invalid: \n{}".format(error_messages))

        self.transitions = transitions

    def transition(self):
        outbound_transitions = set()

    def get_outbound_transitions(self) -> (State, Probability):
        outbound_transitions = set()
        for from_state, to_state, prob in self.transitions:
            if from_state.__eq__(self.current_state):
                outbound_transitions.add((to_state, prob))
        return outbound_transitions
