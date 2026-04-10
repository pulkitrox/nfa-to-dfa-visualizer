# The input to the converter function will be the 5 tuples of the Finite State Machine. This is what the input might look like
# after parsing the input from the webiste application:
'''
states = ["q0", "q1", "q2"]

alphabet = ["0", "1"]

start = "q0"

final = ["q2"]

transitions = {
    "q0": {
        "0": ["q0", "q1"],
        "1": ["q0"]
    },
    "q1": {
        "1": ["q2"]
    },
    "q2": {}
}
'''
# The function returns the dfa_transitions and steps (stepwise results while converting the nfa to dfa)
def convert_nfa_to_dfa(states, alphabet, start, final, transitions):

    dfa_states = [] 
    #Stores all dfa states discovered so far
    dfa_transitions = {} 
    #stores the transition table of the dfa
    steps = []
    #stores every step of subset construction
    #An entry might look like this:
    '''
    {
        "current_state": {"q0"},
        "symbol": "0",
        "next_state": {"q0","q1"}
    }
    '''

    start_state = frozenset([start])

    queue = [start_state]

    dfa_states.append(start_state)
    # The algorithm uses a Queue in BFS manner approach, to process the nfa and create the corresponding dfa

    while queue: # We keep applying the same process until no new dfa state is found similar to what we do in class

        current = queue.pop(0)

        dfa_transitions[current] = {}

        for symbol in alphabet:

            next_states = set() #Since the dfa state is a set of nfa states

            for s in current: # we check for corresponding transitions from the input

                if s in transitions and symbol in transitions[s]:
                    next_states.update(transitions[s][symbol])

            next_states = frozenset(next_states)

            dfa_transitions[current][symbol] = next_states

            steps.append({
                "current_state": set(current),
                "symbol": symbol,
                "next_state": set(next_states)
            })

            if next_states not in dfa_states: #We append the formed state only if it has not been added to the list before
                dfa_states.append(next_states)
                queue.append(next_states)

    return dfa_transitions, steps