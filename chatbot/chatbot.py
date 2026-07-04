"""
Lightweight rule-based FAQ chatbot for cybersecurity/phishing questions.

Uses simple keyword overlap scoring against intents.json rather than a heavy
NLP model, keeping the project dependency-light. Swap this out for a
transformer-based model later if you want more flexible matching.
"""
import json
import os
import re

_INTENTS_PATH = os.path.join(os.path.dirname(__file__), "intents.json")

with open(_INTENTS_PATH, "r", encoding="utf-8") as f:
    _INTENTS_DATA = json.load(f)["intents"]


def _tokenize(text: str) -> set:
    return set(re.findall(r"[a-z0-9']+", text.lower()))


def get_response(user_input: str) -> str:
    """Return the best-matching intent's response for the given user input."""
    if not user_input or not user_input.strip():
        return "Please type a question about phishing or online safety."

    user_tokens = _tokenize(user_input)
    best_score = 0
    best_intent = None

    for intent in _INTENTS_DATA:
        if intent["tag"] == "fallback":
            continue
        for pattern in intent["patterns"]:
            pattern_tokens = _tokenize(pattern)
            if not pattern_tokens:
                continue
            overlap = len(user_tokens & pattern_tokens)
            score = overlap / len(pattern_tokens)
            if score > best_score:
                best_score = score
                best_intent = intent

    if best_intent and best_score >= 0.5:
        import random
        return random.choice(best_intent["responses"])

    fallback = next((i for i in _INTENTS_DATA if i["tag"] == "fallback"), None)
    return fallback["responses"][0] if fallback else "I'm not sure how to answer that."
