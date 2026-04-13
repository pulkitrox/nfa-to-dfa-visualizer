# The input for the draw_nfa function will look like this:
# Note we don't have to pass the symbols as another argument, since they are present in transtions.
'''
states = ["q0","q1","q2"]

alphabet = ["0","1"]

start = "q0"

final = ["q2"]

transitions = {
    "q0": {
        "0": ["q0","q1"],
        "1": ["q0"]
    },
    "q1": {
        "1": ["q2"]
    },
    "q2": {}
}
'''
from graphviz import Digraph
def draw_nfa(states, transitions, start, final):
    dot = Digraph()
    for state in states:
        if state in final: #Checks for the final states, and represents them as double-circled nodes
            dot.node(state,shape = "doublecircle")
        else:
            dot.node(state) #Otherwise, normal states
    dot.node("", shape = "none")
    dot.edge("", start) #this helps us intialize/mark the start state of the nfa

    edge_map = {}
    for state in transitions:
        for symbol in transitions[state]:
            for target in transitions[state][symbol]:

                key = (state, target)

                if key not in edge_map:
                    edge_map[key] = []

                edge_map[key].append(symbol)

    # Now create edges with merged labels
    for (state, target), symbols in edge_map.items():
        label = "/".join(sorted(symbols))
        dot.edge(state, target, label=label)
    dot.attr(rankdir="LR")
    dot.render("frontend/static/nfa", format = "png", cleanup = True) #stores image in png format
# The input for the draw_dfa fucntion will look like this:
# Note, we don't pass the states as a separate argument, as after conversion, new states are mentioned in the dfa_transtions argument.
'''
dfa_transitions = {

    frozenset({"q0"}): {
        "0": frozenset({"q0","q1"}),
        "1": frozenset({"q0"})
    },

    frozenset({"q0","q1"}): {
        "0": frozenset({"q0","q1"}),
        "1": frozenset({"q0","q2"})
    },

    frozenset({"q0","q2"}): {
        "0": frozenset({"q0","q1"}),
        "1": frozenset({"q0"})
    }
}
'''
def draw_dfa(dfa_transitions, start, final):
    dot = Digraph()
    start_state = frozenset([start])
    for state in dfa_transitions:
        if(len(state) == 0):
            label = "d"
        else:
            label = ",".join(sorted(state)) #since graphviz requires string input, we convert the state names to one string using .join()
        if any(s in final for s in state):
            dot.node(label, shape = "doublecircle") #Checks for final states and marks them as double circled nodes
        else:
            dot.node(label) #otherwise normal states
    start_label = ",".join(sorted(start_state))
    dot.node("", shape ="none")
    dot.edge("", start) # initializes the start state
    for state in dfa_transitions:
        if len(state) == 0:
            from_label = "d"
        else:
            from_label = ",".join(sorted(state))

        edge_map = {}

    for state in dfa_transitions:

        # Convert current state to label
        if len(state) == 0:
            from_label = "d"
        else:
            from_label = ",".join(sorted(state))

        for symbol in dfa_transitions[state]:
            next_state = dfa_transitions[state][symbol]

            # Convert next state to label
            if len(next_state) == 0:
                to_label = "d"
            else:
                to_label = ",".join(sorted(next_state))

            key = (from_label, to_label)

            if key not in edge_map:
                edge_map[key] = []

            edge_map[key].append(symbol)

    #  Draw merged edges
    for (from_label, to_label), symbols in edge_map.items():
        label = "/".join(sorted(symbols))
        dot.edge(from_label, to_label, label=label)
        dot.attr(rankdir="LR")
        dot.render("frontend/static/dfa", format="png", cleanup=True)

def draw_cumulative_steps(steps, final_states):
    from graphviz import Digraph

    images = []

    def label(s):
        if not s:
            return "d"
        return ",".join(sorted(list(s)))

    for i in range(len(steps)):

        dot = Digraph(format='png')
        dot.attr(rankdir="LR")

        edge_map = {}  # (from, to) → [symbols]

        # ---- Collect edges up to step i ----
        for j in range(i + 1):
            step = steps[j]

            curr = label(step["current_state"])
            nxt = label(step["next_state"])
            sym = str(step["symbol"])

            key = (curr, nxt)

            if key not in edge_map:
                edge_map[key] = []

            edge_map[key].append(sym)

            # ---- Nodes ----
            if any(s in final_states for s in step["current_state"]):
                dot.node(curr, shape="doublecircle")
            else:
                dot.node(curr)

            if any(s in final_states for s in step["next_state"]):
                dot.node(nxt, shape="doublecircle")
            else:
                dot.node(nxt)

        # ---- Draw edges (merged labels) ----
        for (curr, nxt), symbols in edge_map.items():

            label_str = "/".join(sorted(set(symbols)))

            # Highlight only newest edge
            latest = steps[i]
            latest_curr = label(latest["current_state"])
            latest_nxt = label(latest["next_state"])

            if curr == latest_curr and nxt == latest_nxt:
                dot.edge(curr, nxt, label=label_str, color="red", penwidth="2")
            else:
                dot.edge(curr, nxt, label=label_str)

        # ---- Render ----
        filename = f"frontend/static/step_{i}"
        dot.render(filename, cleanup=True)

        images.append(f"step_{i}.png")

    return images