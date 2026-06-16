import re


def search_terms_from_keywords(keywords: list[str]) -> list[str]:
    return [term.lower() for term in keywords if len(term) > 2 or term.lower() == "ai"]


def relevance_score(search_terms: list[str], *parts: str | None) -> int:
    searchable_text = " ".join(part or "" for part in parts).lower()
    score = 0
    for term in search_terms:
        if " " in term:
            score += int(term in searchable_text)
            continue
        score += int(re.search(rf"\b{re.escape(term)}\b", searchable_text) is not None)
    return score
