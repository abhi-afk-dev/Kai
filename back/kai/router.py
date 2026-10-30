import re

DOMAINS = {
    "github": ["github", "repo", "repos", "repository", "repositories", "commit", "commits",
               "pull request", "pr", "issue", "issues", "branch", "branches", "readme", "gist"],
    "canva": ["canva", "design", "designs", "poster", "presentation", "slide deck", "slides",
              "brand kit", "template", "templates", "logo", "flyer", "banner", "thumbnail"],
    "workspace": ["google", "gdoc", "gdocs", "google doc", "google docs", "docs", "doc",
                  "sheet", "sheets", "spreadsheet", "drive", "gmail", "email", "emails",
                  "inbox", "calendar", "meeting", "event", "events", "schedule"],
    "research": ["research", "deep dive", "analyze", "analysis", "investigate", "compare",
                 "comparison", "in depth", "in-depth", "study", "report on"],
    "web": ["search", "latest", "news", "today", "current", "price", "weather", "score",
            "look up", "lookup", "http", "https", "www", "url", "website", "link"],
}

PRIORITY = ["github", "canva", "workspace", "research", "web"]

_PAT = {d: [re.compile(rf"(?<!\w){re.escape(w)}(?!\w)", re.I) for w in ws]
        for d, ws in DOMAINS.items()}

ACTION = re.compile(r"\b(then|and then|after that|save|write|put|add|create|make|send|upload|post|push)\b", re.I)

CHAT = [
    re.compile(r"^\s*(hi|hey|hello|yo|sup|thanks|thank you|ok|okay|cool|nice|great|good (morning|night|evening))\b[\s!.,?]*$", re.I),
    re.compile(r"\b(how are you|who are you|what can you do|tell me a joke|what'?s up)\b", re.I),
]


def score(prompt: str) -> dict:
    s = {}
    for d, pats in _PAT.items():
        n = sum(1 for p in pats if p.search(prompt))
        if n:
            s[d] = n
    return s


def route_agent(prompt: str):
    """criteria_hands: returns web | research | github | workspace | canva | None"""
    s = score(prompt)
    if not s:
        return None
    return max(s, key=lambda d: (s[d], -PRIORITY.index(d)))


def route_mode(prompt: str):
    """criteria_orchestrator: returns conversational | single_tasked | master_loop"""
    if any(p.search(prompt) for p in CHAT):
        return "conversational"

    s = score(prompt)
    if not s:
        return "conversational"

    tools = [d for d in s if d in ("github", "canva", "workspace")]
    info = [d for d in s if d in ("research", "web")]

    if len(tools) >= 2:
        return "master_loop"
    if tools and info and ACTION.search(prompt):
        return "master_loop"
    return "single_tasked"


async def get_decision(criteria: dict, prompt: str):
    """Drop-in replacement for router.get_decision."""
    if "master_loop" in criteria:
        return route_mode(prompt)
    return route_agent(prompt)