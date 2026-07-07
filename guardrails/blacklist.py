# =========================================================
# BLACKLISTED SENTENCE
# =========================================================
BLACKLIST = [

    "ignore previous instructions",
    "ignore all previous instructions",

    "system prompt",
    "developer prompt",

    "reveal your prompt",
    "show your prompt",

    "show hidden instructions",
    "internal instructions",

    "chain of thought",
    "reason step by step",

    "pretend you are",
    "act as",

    "jailbreak",

    "override",

    "disable safety",

    "api key",
    "secret",

    "print memory"
]


def contains_prompt_injection(query: str):

    query = query.lower()

    for phrase in BLACKLIST:

        if phrase in query:

            return True

    return False
