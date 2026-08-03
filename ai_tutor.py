import os
import json
from dotenv import load_dotenv
from google import genai
import re
import rich
import uuid

_sessions = {}

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

try:
    from rich.console import Console
    from rich.markdown import Markdown
    _console = Console()
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False 
 
def print_response(text):
    """
    Print a model response. If 'rich' is installed, render markdown
    (headings, bold, code blocks) properly instead of dumping raw '###'
    and '**' characters into the terminal.
    """
    if _HAS_RICH:
        _console.print(Markdown(text))
    else:
        print(text)
    print()

def start_tutor_session(proj_id, projects, missing_prereqs=None):
    """
    Pure-ish: no input()/print(). Creates a chat session and returns
    everything a frontend needs to render the opening state.
    Returns a dict: {"session_id", "title", "intro_messages": [str, ...]}
    or {"error": str} on failure.
    """
    if not API_KEY:
        return {"error": "GEMINI_API_KEY not found. Check your .env file."}

    try:
        proj_details = next(p for p in projects if p["id"] == proj_id)
    except StopIteration:
        return {"error": f"No project found with id '{proj_id}'."}

    missing_note = ""
    if missing_prereqs:
        missing_note = f"""
        The learner is weaker on these specific prerequisites, so explain
        them more from first principles if they come up. Assume they are
        comfortable with everything else listed under prerequisite_skills:
        {missing_prereqs}
        """

    SYSTEM_PROMPT = f"""
        You are an expert programming mentor.
        You help developers complete projects.

        Rules:
        - Never give complete code.
        - Give hints, not solutions.
        - Explain concepts.
        - Help build logic.
        - Use pseudocode if necessary.
        - Ask questions that help the learner think.
        - Keep responses concise: short paragraphs, minimal headings, no more
          than one or two questions at the end.
        {missing_note}
    """

    prompt = f"""{SYSTEM_PROMPT}

Project Information:
{json.dumps(proj_details, indent=2)}"""

    try:
        client = genai.Client(api_key=API_KEY)
        chat = client.chats.create(model="gemini-3.1-flash-lite")
        chat.send_message(prompt)
    except Exception as e:
        return {"error": f"Couldn't start the tutor session: {e}"}

    session_id = str(uuid.uuid4())
    # Keep a reference to `client` here too - if only `chat` is stored, the
    # client object has no other referrers and can get garbage-collected,
    # which closes its underlying HTTP connection and breaks later sends.
    _sessions[session_id] = {"client": client, "chat": chat, "title": proj_details["title"]}

    intro_messages = [f"Tutor ready for '{proj_details['title']}'."]

    if proj_details.get("track") == "ai-ml":
        try:
            suggest_dataset = chat.send_message(
                "Suggest a free dataset link or where to find a dataset for this project."
            )
            intro_messages.append(suggest_dataset.text)
        except Exception as e:
            intro_messages.append(f"Couldn't fetch a dataset suggestion: {e}")

    return {"session_id": session_id, "title": proj_details["title"], "intro_messages": intro_messages}


def send_tutor_message(session_id, question):
    """
    Pure-ish: no input()/print(). Sends a question to an existing session
    and returns the response text. Returns {"error": str} on failure.
    """
    session = _sessions.get(session_id)
    if not session:
        return {"error": "Session not found or has expired."}

    try:
        response = session["chat"].send_message(question)
        return {"text": response.text}
    except Exception as e:
        return {"error": f"Something went wrong reaching the tutor: {e}"}
    
def ai_tutor(proj_id, projects, missing_prereqs=None):
    result = start_tutor_session(proj_id, projects, missing_prereqs)
    if "error" in result:
        print(result["error"])
        return

    print(f"\n{result['intro_messages'][0]} Type 'exit' to quit.\n")
    for msg in result["intro_messages"][1:]:
        print_response(msg)

    session_id = result["session_id"]

    while True:
        question = input("You: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue

        response = send_tutor_message(session_id, question)
        if "error" in response:
            print(response["error"])
            print("Try again, or type 'exit' to quit.")
        else:
            print_response(response["text"])

if __name__ == '__main__':
    proj_id = input("Please enter project id: ")
    ai_tutor(proj_id=proj_id)