from thefuzz import fuzz
from thefuzz import process


def match_candidate_to_candidates(candidate: str, candidates: list[str]) -> tuple[str | None, int]:
    return process.extractOne(candidate, candidates)
    # best_match = None
    # best_score = -1
    #
    # for candidate_item in candidates:
    #     score = fuzz.partial_ratio(candidate, candidate_item)
    #
    #     if score > best_score:
    #         best_score = score
    #         best_match = candidate_item
    #
    # return (best_match, best_score) if best_score >= threshold else (None, 0)
