from typing import List, Dict
from math import exp

# Simple, interpretable scorer. Replace with embeddings later.

WEIGHTS = {
    "education": 0.3,
    "experience": 0.55,
    "location": 0.1,
    "skills": 0.05,
}

ROLE_FAMILY = {
    "Analyst": "Analyst",
    "Associate": "Associate",
    "VP": "VP",
    "Director": "Director",
    "Managing Director": "MD",
}

EB_FAMILY = {
    "Evercore", "Guggenheim", "Moelis", "PJT Partners", "Lazard", "Centerview"
}


def norm_company(c: str) -> str:
    return (c or "").strip()


def school_score(a: Dict, b: Dict) -> float:
    sa = {e.get("school") for e in a.get("education", []) if e.get("school")}
    sb = {e.get("school") for e in b.get("education", []) if e.get("school")}
    if not sa or not sb:
        return 0.0
    if sa & sb:
        return 1.0
    return 0.0


def grad_year_score(a: Dict, b: Dict) -> float:
    ya = [e.get("grad_year") for e in a.get("education", []) if e.get("grad_year")]
    yb = [e.get("grad_year") for e in b.get("education", []) if e.get("grad_year")]
    if not ya or not yb:
        return 0.0
    da = min(ya); db = min(yb)
    return exp(-abs((da - db))/4.0)


def company_overlap(a: Dict, b: Dict) -> float:
    ca = {norm_company(e.get("company")) for e in a.get("experiences", []) if e.get("company")}
    cb = {norm_company(e.get("company")) for e in b.get("experiences", []) if e.get("company")}
    if not ca or not cb:
        return 0.0
    inter = len(ca & cb)
    union = len(ca | cb)
    return inter / union if union else 0.0


def location_score(a: Dict, b: Dict) -> float:
    la = (a.get("location") or a.get("city") or "").split(",")[0].strip()
    lb = (b.get("location") or b.get("city") or "").split(",")[0].strip()
    if not la or not lb:
        return 0.0
    return 1.0 if la == lb else 0.0


def score_pair(a: Dict, b: Dict) -> float:
    edu = 0.6 * school_score(a, b) + 0.4 * grad_year_score(a, b)
    exp_score = company_overlap(a, b)
    loc = location_score(a, b)
    # skills = 0 (placeholder)
    return WEIGHTS["education"]*edu + WEIGHTS["experience"]*exp_score + WEIGHTS["location"]*loc


def rank_similar(source: Dict, candidates: List[Dict], top_k: int = 20):
    scored = []
    sid = source.get("id")
    for c in candidates:
        if sid and c.get("id") == sid:
            continue
        s = score_pair(source, c)
        scored.append({"person": c, "score": round(s, 4)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]