from thefuzz import fuzz


def calculate_match_score(candidate: str, vacation: str) -> int:
    return fuzz.partial_ratio(candidate.lower(), vacation.lower())
