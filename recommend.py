import json
import os
DATA_PATH = os.path.join(os.path.dirname(__file__), "python_projects_by_track.json")

with open(DATA_PATH) as f:
    data = json.load(f)

projects = data["projects"]
tracks = data["tracks"]
track_ids = {t["id"] for t in tracks}
VALID_TIERS = ["beginner", "intermediate", "advanced"]

def get_tracks():
    """Pure: just exposes track metadata for a UI to render (dropdown, cards, etc.)."""
    return tracks

def get_domain_skills(domain, projects):
    """
    All prerequisite skills that appear anywhere in this domain's projects,
    ordered beginner -> intermediate -> advanced so the list itself reads
    as a rough learning progression and familiar/basic skills appear first.
    """
    seen = set()
    ordered = []
    for tier in VALID_TIERS:
        tier_skills = sorted({
            s for p in projects
            if p["track"] == domain and p["tier"] == tier
            for s in p["prerequisite_skills"]
        })
        for s in tier_skills:
            if s not in seen:
                seen.add(s)
                ordered.append(s)
    return ordered

def resolve_skill_selection(domain_skills, indices):
    """
    Pure: turns a list of 1-based indices into the resolved skill set.
    Raises ValueError on an out-of-range index so callers (CLI or API) can
    handle invalid input however fits — reprompt, or return a 400.
    """
    resolved = set()
    for i in indices:
        if not (1 <= i <= len(domain_skills)):
            raise ValueError(f"Index {i} is out of range (1-{len(domain_skills)}).")
        resolved.add(domain_skills[i - 1].lower())
    return resolved

def get_user_level(domain, projects, user_skills):
    """
    Infer how ready the user is for each tier of a given domain by measuring
    how many prerequisite skills of that tier's projects they already have.
    Returns the tier name whose prerequisites they satisfy best.
    """
    domain_projects = [p for p in projects if p["track"] == domain]
    tier_scores = {}

    for tier in VALID_TIERS:
        tier_projects = [p for p in domain_projects if p["tier"] == tier]
        if not tier_projects:
            continue
        total_prereqs = 0
        matched_prereqs = 0
        for p in tier_projects:
            prereqs = {s.lower() for s in p["prerequisite_skills"]}
            total_prereqs += len(prereqs)
            matched_prereqs += len(prereqs & user_skills)
        coverage = matched_prereqs / total_prereqs if total_prereqs else 0
        tier_scores[tier] = coverage

    # Pick the hardest tier where coverage is still reasonably high (>= 60%),
    # otherwise fall back to beginner.
    for tier in ["advanced", "intermediate", "beginner"]:
        if tier_scores.get(tier, 0) >= 0.6:
            return tier
    return "beginner"


def suggest_projects(domain, level, user_skills, top_n=5):
    """
    Return up to top_n projects matching the domain + tier, ranked so that
    projects whose prerequisites the user already satisfies come first,
    and within that, easier projects come before harder ones.
    """
    candidates = [p for p in projects if p["track"] == domain and p["tier"] == level]

    if not candidates:
        print(f"No projects found for domain '{domain}' at tier '{level}'.")
        return []

    def rank_key(p):
        prereqs = {s.lower() for s in p["prerequisite_skills"]}
        missing = prereqs - user_skills
        return (len(missing), p["difficulty_score"])

    ranked = sorted(candidates, key=rank_key)
    return ranked[:top_n]

def format_recommendations(recs, user_skills):
    """
    Pure: turns raw project dicts into plain, JSON-serializable
    recommendation records a frontend can render directly.
    """
    formatted = []
    for p in recs:
        prereqs = {s.lower() for s in p["prerequisite_skills"]}
        missing = sorted(prereqs - user_skills)
        formatted.append({
            "id": p["id"],
            "title": p["title"],
            "description": p["description"],
            "difficulty_label": p["difficulty_label"],
            "difficulty_score": p["difficulty_score"],
            "new_skills": p["new_skills"],
            "missing_prereqs": missing,
        })
    return formatted