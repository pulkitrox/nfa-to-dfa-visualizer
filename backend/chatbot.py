from google import genai
import os
from dotenv import load_dotenv

load_dotenv(override=True)
print("LOADED KEY:", os.getenv("GEMINI_API_KEY"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(question):

    prompt = f"""
    You are an automata theory tutor.
    Explain concepts related to NFA, DFA, subset construction and dead states clearly.
    While answering, ensure replies contain: short paras in points, simple headings. Try not to include symbols that are
    unable to be represented properly on the web-app.
    Question: {question}
    """

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("Gemini API error:", e)
        return f"Error: {str(e)}"
