import re
from typing import Dict

# Extremely small deterministic parser with common finance aliases.
# Swap with an LLM function-calling step later if desired.

COMPANY_ALIASES = {
    "gugg": "Guggenheim",
    "guggenheim": "Guggenheim",
    "evercore": "Evercore",
    "pjt": "PJT Partners",
    "moelis": "Moelis",
    "gs": "Goldman Sachs",
}

ROLE_ALIASES = {
    "m&a": "M&A",
    "ma": "M&A",
    "ib": "Investment Banking",
    "restructuring": "Restructuring",
}

CITY_ALIASES = {"nyc": "New York", "new york": "New York", "sf": "San Francisco"}

SCHOOL_PAT = re.compile(r"(cmu|carnegie mellon|harvard|stanford|upenn|wharton)")
YEAR_PAT = re.compile(r"'?(20\d{2}|19\d{2})")


def parse_nl_query(q: str) -> Dict:
    text = q.lower()

    # Companies
    companies = []
    for k, v in COMPANY_ALIASES.items():
        if re.search(rf"\b{k}\b", text):
            companies.append(v)

    # Roles
    roles = []
    for k, v in ROLE_ALIASES.items():
        if re.search(rf"\b{k}\b", text):
            roles.append(v)

    # School
    school = None
    m = SCHOOL_PAT.search(text)
    if m:
        token = m.group(1)
        school = {
            "cmu": "Carnegie Mellon University",
            "carnegie mellon": "Carnegie Mellon University",
            "harvard": "Harvard University",
            "stanford": "Stanford University",
            "upenn": "University of Pennsylvania",
            "wharton": "University of Pennsylvania",
        }.get(token, token.title())

    # Years (take first two as range heuristically)
    years = YEAR_PAT.findall(text)
    grad_from = grad_to = None
    if years:
        nums = [int(y) for y in years]
        grad_from, grad_to = min(nums), max(nums)

    # City
    location = None
    for k, v in CITY_ALIASES.items():
        if re.search(rf"\b{k}\b", text):
            location = v
            break

    # replace the payload build at the end with:
    payload = {"name": q, "count": 20}  # default page size
    if companies:
        payload["current_company"] = ",".join(sorted(set(companies)))
    if roles:
        payload["role"] = ",".join(sorted(set(roles)))

    # year → single undergraduate_year only if we detected an exact year
    if grad_from and grad_to and grad_from == grad_to:
        payload["undergraduate_year"] = grad_from
    elif grad_from and not grad_to:
        payload["undergraduate_year"] = grad_from

    if location:
        payload["city"] = location

    # sector heuristic
    sector = None
    if any(k in text for k in ["consult", "strategy", "advisory"]):
        sector = "CONSULTING"
    elif any(k in text for k in ["m&a", "ib", "investment banking", "levfin", "restructuring", "equity capital"]):
        sector = "FINANCE"
    if sector:
        payload["sector"] = sector

    return payload