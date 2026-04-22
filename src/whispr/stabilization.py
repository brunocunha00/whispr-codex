from __future__ import annotations

import string


BOUNDARY_CHARS = set(string.whitespace) | set(",.!?;:")


def clean_hypothesis(text: str) -> str:
    return " ".join(text.split())


def longest_common_prefix(left: str, right: str) -> str:
    limit = min(len(left), len(right))
    index = 0
    while index < limit and left[index] == right[index]:
        index += 1
    return left[:index]


def trim_to_word_boundary(text: str) -> str:
    if not text:
        return ""
    if text[-1] in BOUNDARY_CHARS:
        return text
    for index in range(len(text) - 1, -1, -1):
        if text[index] in BOUNDARY_CHARS:
            return text[: index + 1]
    return ""


class StablePrefixCommitter:
    def __init__(self) -> None:
        self.previous_hypothesis = ""
        self.committed_text = ""

    def observe(self, hypothesis: str) -> str:
        normalized = clean_hypothesis(hypothesis)
        if not normalized:
            self.previous_hypothesis = ""
            return ""
        if not self.previous_hypothesis:
            self.previous_hypothesis = normalized
            return ""
        stable = trim_to_word_boundary(longest_common_prefix(self.previous_hypothesis, normalized))
        self.previous_hypothesis = normalized
        if not stable:
            return ""
        if not stable.startswith(self.committed_text):
            return ""
        delta = stable[len(self.committed_text) :]
        self.committed_text = stable
        return delta

    def flush(self, final_text: str) -> str:
        normalized = clean_hypothesis(final_text)
        if not normalized:
            self.previous_hypothesis = ""
            return ""
        if normalized.startswith(self.committed_text):
            delta = normalized[len(self.committed_text) :]
        else:
            delta = normalized
        self.previous_hypothesis = normalized
        self.committed_text = normalized
        return delta
