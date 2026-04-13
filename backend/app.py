from flask import Flask, render_template, request, redirect, url_for
from converter import convert_nfa_to_dfa
from visualize import draw_dfa, draw_nfa
from chatbot import ask_gemini
import markdown
from google import genai
import os
from dotenv import load_dotenv
from visualize import draw_cumulative_steps
load_dotenv()
latest_steps = []
latest_dfa = {}
latest_dfa_text = ""
latest_nfa_transitions = {}
latest_nfa_states = []
latest_nfa_alphabet = []
latest_nfa_start = ""
latest_nfa_final = []
latest_step_images = []
def format_dfa_as_text(dfa_transitions):
    lines = []

    for state in dfa_transitions:

        # Format current state
        if len(state) == 0:
            state_str = "d"
        else:
            state_str = ",".join(sorted(state))

        for symbol in dfa_transitions[state]:
            next_state = dfa_transitions[state][symbol]

            # Format next state
            if len(next_state) == 0:
                next_str = "d"
            else:
                next_str = ",".join(sorted(next_state))

            lines.append(f"{state_str} {symbol} {next_str}")

    return "\n".join(lines)
app = Flask(__name__ ,
            template_folder= "../frontend/templates",
            static_folder= "../frontend/static")
@app.route('/')
def home():
    return redirect(url_for('dashboard'))
@app.route('/input')
def input_page():
    return render_template("index.html")
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/visualizer')
def visualizer():
    return render_template("results.html", steps = latest_steps, dfa = latest_dfa, dfa_text = latest_dfa_text, start_state = latest_dfa_start, final_states= latest_dfa_final,
                           nfa_transitions = latest_nfa_transitions, nfa_states = latest_nfa_states, nfa_alphabet = latest_nfa_alphabet, nfa_start = latest_nfa_start,
                           nfa_final = latest_nfa_final)
@app.route('/steps-visual')
def steps_visual():
    return render_template(
        "steps_visual.html",
        steps=latest_steps,
        images=latest_step_images
    )

@app.route('/chatbot')
def chatbot_page():
    return render_template("chatbot.html")
@app.route('/chat', methods = ['POST'])
def chat():
    question = request.form["question"]
    try:
        reply = ask_gemini(question)
        reply_html = markdown.markdown(reply)

    except Exception:
        reply_html = "<b>Error:</b> Chatbot unavailable. Try again later."

    return render_template("chatbot.html", reply=reply_html)
@app.route('/convert', methods = ['POST'])
def convert(): # parses the input and extracts all information in required form, calls the other functions to display results
    try:    
        start = request.form['start']
        final = [f.strip() for f in request.form['final'].split(',')]
        transition_input = request.form['transitions']
        transitions = {}
        states = set()
        alphabet = set()
        errors = []

        for i, line in enumerate(transition_input.strip().split("\n"), start=1):

            if not line.strip():
                continue

            parts = line.split()

            if len(parts) != 3:
                errors.append(f"Line {i}: Invalid format → '{line}'")
                continue

            state, symbol, targets = parts

            # Validate state
            if not state.startswith("q"):
                errors.append(f"Line {i}: Invalid state '{state}'")

            # Validate symbol
            if len(symbol) != 1:
                errors.append(f"Line {i}: Symbol must be single character → '{symbol}'")

            target_states = [t.strip() for t in targets.split(",")]

            # Validate target states
            for t in target_states:
                if not t.startswith("q"):
                    errors.append(f"Line {i}: Invalid target state '{t}'")

            # Only add if no errors for this line
            if len(errors) == 0:
                states.add(state)
                states.update(target_states)
                alphabet.add(symbol)

                if state not in transitions:
                    transitions[state] = {}

                transitions[state][symbol] = target_states

        if errors:
            return render_template("index.html", error=errors)
        
        states = list(states)
        alphabet = sorted(list(alphabet))

        if start not in states:
                raise ValueError("Start state not found in transitions")

        for f in final:
                    if f not in states:
                        raise ValueError(f"Invalid final state: {f}")


        dfa_transitions, steps = convert_nfa_to_dfa(states, alphabet, start, final, transitions)
        step_images = draw_cumulative_steps(steps, final)

        global latest_step_images
        latest_step_images = step_images
        dfa_start = start
        draw_nfa(states, transitions, start, final)
        draw_dfa(dfa_transitions, start, final)
        dfa_text = format_dfa_as_text(dfa_transitions)
        # -------- Store for Visualizer --------
        global latest_steps, latest_dfa, latest_dfa_text, latest_dfa_start, latest_dfa_final
        global latest_nfa_transitions, latest_nfa_states, latest_nfa_alphabet, latest_nfa_start, latest_nfa_final
        latest_steps = steps
        latest_dfa = dfa_transitions
        latest_dfa_text = dfa_text
        latest_dfa_start = dfa_start        
        latest_dfa_final = final    
        latest_nfa_transitions = transitions
        latest_nfa_states = states
        latest_nfa_alphabet = alphabet
        latest_nfa_start = start
        latest_nfa_final = final

            # -------- Redirect to Visualizer --------
        return redirect(url_for('visualizer'))
    except Exception as e:
        import traceback
        print("ERROR:", e)
        print(traceback.format_exc())
        return f"<pre>{traceback.format_exc()}</pre>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host= "0.0.0.0", port=port)