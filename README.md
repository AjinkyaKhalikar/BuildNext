# BuildNext

**BuildNext** is a developer upskilling platform that recommends personalized project ideas based on a user's domain and existing skills, and pairs each recommendation with an **AI Tutor** that guides the learner through the project without ever handing over the finished code.

Instead of scrolling through generic "100 project ideas" lists, BuildNext asks what you already know, figures out your skill tier, and surfaces projects that are challenging enough to teach you something new — then stays with you as a Socratic mentor while you build.

---

## ✨ Features

- **Skill-based project recommendation** — Select a domain/track and the skills you already have; BuildNext infers your level (beginner / intermediate / advanced) and ranks projects accordingly.
- **Gap-aware ranking** — Projects are sorted so the ones closest to your current skill set (fewest missing prerequisites, lowest difficulty) come first.
- **AI Tutor, not an answer key** — A Gemini-powered mentor that gives hints, asks guiding questions, and explains concepts from first principles — but never writes the solution for you.
- **Prerequisite-aware coaching** — The tutor is told exactly which prerequisite skills you're missing so it can adjust its explanations to your actual gaps.
- **Domain-specific extras** — For AI/ML track projects, the tutor proactively suggests a relevant dataset to get you started.
- **REST API + lightweight frontend** — A FastAPI backend exposes recommendation and tutoring endpoints, consumed by a simple static frontend.

---

## 🧠 How It Works

1. **Pick a track** (domain) — e.g. Web Development, AI/ML, etc.
2. **Select the skills you already have** from that track's skill list.
3. BuildNext computes your **skill tier** by measuring how much of each tier's prerequisite skills you already cover.
4. It returns the **top matching projects** for your tier, ranked by fewest missing prerequisites and lowest difficulty.
5. Pick a project and **start an AI Tutor session** — the tutor knows the project spec and your missing prerequisites, and coaches you through it with hints and guiding questions instead of code.

---

## 🏗️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3** | Core language |
| **FastAPI** | REST API framework serving recommendation & tutor endpoints |
| **Pydantic** | Request/response data validation |
| **CORS Middleware** | Allows the static frontend to call the API from any origin during development |
| **Google Gemini API** (`google-genai`) | Powers the conversational AI Tutor (`gemini-3.1-flash-lite`) |
| **python-dotenv** | Loads the Gemini API key from a `.env` file |
| **rich** | Pretty-prints Markdown tutor responses when run from the CLI |

### Frontend
| Technology | Purpose |
|---|---|
| **HTML** (`index.html`) | Static single-page frontend that talks to the FastAPI backend |

### Data
| File | Purpose |
|---|---|
| `python_projects_by_track.json` | Dataset of tracks, skills, and project definitions (tier, difficulty, prerequisites, new skills taught, etc.) used to power recommendations |

---

## 📁 Project Structure

```
BuildNext/
├── main.py                          # FastAPI app & route definitions
├── recommend.py                     # Recommendation engine (tiering, ranking, formatting)
├── ai_tutor.py                      # Gemini-powered AI Tutor (session management + CLI mode)
├── index.html                       # Static frontend
├── python_projects_by_track.json    # Project/track/skill dataset
├── .gitignore
└── README.md
```

---

## 🔌 API Reference

The backend exposes the following endpoints (see `main.py`):

### Recommendations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tracks` | List all available domains/tracks |
| `GET` | `/tracks/{domain}/skills` | List all prerequisite skills for a track, ordered beginner → advanced |
| `POST` | `/tracks/{domain}/recommendations` | Submit selected skills, receive ranked project recommendations |

**Request body for `/tracks/{domain}/recommendations`:**
```json
{
  "skills": ["python", "html", "css"]
}
```

### AI Tutor

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tutor/start` | Start a tutoring session for a chosen project |
| `POST` | `/tutor/message` | Send a question/message to an active tutor session |

**Request body for `/tutor/start`:**
```json
{
  "proj_id": "some-project-id",
  "missing_prereqs": ["recursion", "list comprehensions"]
}
```

**Request body for `/tutor/message`:**
```json
{
  "session_id": "returned-session-id",
  "question": "How should I approach the search function?"
}
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A [Google Gemini API key](https://ai.google.dev/)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AjinkyaKhalikar/BuildNext.git
   cd BuildNext
   ```

2. **Install dependencies**
   ```bash
   pip install fastapi uvicorn pydantic python-dotenv google-genai rich
   ```

3. **Configure your environment**

   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run the backend**
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

5. **Open the frontend**

   Open `index.html` directly in your browser (or serve it with any static file server). It will call the local FastAPI backend for recommendations and tutoring.

### Running the AI Tutor from the CLI

`ai_tutor.py` can also be run standalone for quick testing:
```bash
python ai_tutor.py
```
You'll be prompted for a project ID, after which you can chat with the tutor directly in the terminal.

---

## 🗺️ Roadmap Ideas

- User accounts and progress tracking across sessions
- Persistent chat history for tutor sessions
- Additional tracks beyond the current dataset
- Deployment guide / Docker support

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open a pull request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 👤 Author

**Ajinkya Khalikar**
GitHub: [@AjinkyaKhalikar](https://github.com/AjinkyaKhalikar)
