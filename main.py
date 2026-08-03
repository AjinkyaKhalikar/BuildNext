from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from recommend import get_tracks, get_domain_skills, get_user_level, suggest_projects, format_recommendations, projects
from ai_tutor import start_tutor_session, send_tutor_message

app = FastAPI()

# Allow the static frontend (opened as a local file, or served from any
# origin/port during development) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SelectSkills(BaseModel):
    skills: list[str] = []

class SelectProject(BaseModel):
    project_id: str

#Routes for Recommend
@app.get("/tracks")
def show_tracks():
    return get_tracks()

@app.get("/tracks/{domain}/skills")
def get_skills(domain: str):
    return get_domain_skills(domain)

@app.post("/tracks/{domain}/recommendations")
def get_recommendations(domain:str, payload: SelectSkills):
    user_skills = {s.lower() for s in payload.skills}
    level = get_user_level(domain, user_skills)
    recs = suggest_projects(domain, level, user_skills)
    return format_recommendations(recs, user_skills)

#Routes for AI Tutor
class StartTutor(BaseModel):
    proj_id: str
    missing_prereqs: list[str] | None = None

class TutorMessage(BaseModel):
    session_id: str
    question: str

@app.post("/tutor/start")
def tutor_start(payload: StartTutor):
    result = start_tutor_session(payload.proj_id, projects, payload.missing_prereqs)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/tutor/message")
def tutor_message(payload: TutorMessage):
    result = send_tutor_message(payload.session_id, payload.question)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result