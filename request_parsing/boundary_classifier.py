
import re

from request_parsing.internal_models import (
    BoundaryLabel,
    BoundaryPrediction,
    BoundarySignalType,
    CandidateBoundary,
)


class BoundaryClassifier:
    """Classify candidate boundaries using conservative lexical rules."""

    _ACTION_VERBS = frozenset(
        {
            "add",
            "analyze",
            "analyse",
            "answer",
            "build",
            "calculate",
            "check",
            "classify",
            "clean",
            "compare",
            "compute",
            "configure",
            "convert",
            "create",
            "debug",
            "delete",
            "derive",
            "describe",
            "design",
            "display",
            "draw",
            "edit",
            "evaluate",
            "execute",
            "explain",
            "explore",
            "export",
            "fetch",
            "find",
            "fix",
            "generate",
            "give",
            "help",
            "implement",
            "improve",
            "install",
            "inspect",
            "launch",
            "list",
            "load",
            "make",
            "modify",
            "open",
            "optimize",
            "optimise",
            "plot",
            "predict",
            "print",
            "provide",
            "read",
            "recommend",
            "refactor",
            "remove",
            "rename",
            "repair",
            "replace",
            "review",
            "rewrite",
            "run",
            "save",
            "search",
            "send",
            "show",
            "solve",
            "summarize",
            "summarise",
            "test",
            "translate",
            "update",
            "upload",
            "validate",
            "visit",
            "write",
            "choose",
            "download",
            "prioritize",
            "prioritise",
            "publish",
            "simplify",
            "suggest",
            "use",
        }
    )

    _QUESTION_STARTERS = frozenset(
        {
            "what",
            "why",
            "how",
            "where",
            "when",
            "who",
            "which",
            "can",
            "could",
            "should",
            "would",
            "will",
            "is",
            "are",
            "do",
            "does",
            "did",
            "has",
            "have",
        }
    )

    # Each pattern removes a recognized request wrapper from the start.
    _LEADING_WRAPPERS = (
        re.compile(r"^(?:please|kindly)\b[\s,]*", re.IGNORECASE),
        re.compile(
            r"^(?:could|can|would|will)\s+you"
            r"(?:\s+please)?\b[\s,]*",
            re.IGNORECASE,
        ),
        re.compile(
            r"^(?:i would like|i'd like)\s+you\s+to\b[\s,]*",
            re.IGNORECASE,
        ),
        re.compile(
            r"^(?:i need|i want)\s+you\s+to\b[\s,]*",
            re.IGNORECASE,
        ),
        re.compile(
            r"^(?:i need|i want)\s+to\b[\s,]*",
            re.IGNORECASE,
        ),
        re.compile(r"^help\s+me(?:\s+to)?\b[\s,]*", re.IGNORECASE),
        re.compile(r"^(?:then|next)\b[\s,]*", re.IGNORECASE),
        re.compile(r"^after\s+that\b[\s,]*", re.IGNORECASE),
    )

    def classify(
        self,
        text: str,
        candidates: tuple[CandidateBoundary, ...],
    ) -> tuple[BoundaryPrediction, ...]:
        """Return one prediction for every candidate, preserving its order."""
        predictions = []

        for candidate in candidates:
            left_text = text[:candidate.left_end].strip()
            right_text = text[candidate.right_start:].strip()

            trigger = text[
                candidate.trigger_start:candidate.trigger_end
            ].casefold().strip()

            label, evidence = self._classify_candidate(
                text=text,
                candidate=candidate,
                left_text=left_text,
                right_text=right_text,
                trigger=trigger,
            )

            predictions.append(
                BoundaryPrediction(
                    candidate=candidate,
                    label=label,
                    boundary_probability=None,
                    evidence=(evidence,),
                )
            )

        return tuple(predictions)

    def _classify_candidate(
        self,
        text: str,
        candidate: CandidateBoundary,
        left_text: str,
        right_text: str,
        trigger: str,
    ) -> tuple[BoundaryLabel, str]:
        # Rule 1: Explicit sequence markers are strong boundary signals.
        if trigger in {"then", "after that", "and then"}:
            return BoundaryLabel.BOUNDARY, "explicit_sequence_marker"

        # "Next" can be a sequence marker, but can also appear in a noun
        # phrase, so require action-like content on the right.
        if trigger == "next":
            if self._is_action_like(right_text):
                return BoundaryLabel.BOUNDARY, "explicit_sequence_marker"

            return BoundaryLabel.UNCERTAIN, (
                "sequence_marker_without_action_like_right_side"
            )

        # Rule 2: A semicolon is a strong separator in this MVP.
        if candidate.signal_type == BoundarySignalType.SEMICOLON:
            return BoundaryLabel.BOUNDARY, "semicolon_separator"

        # Rule 3: Sentence-ending punctuation.
        if candidate.signal_type == BoundarySignalType.PUNCTUATION:
            has_space_after_punctuation = (
                candidate.trigger_end < len(text)
                and text[candidate.trigger_end].isspace()
            )

            if has_space_after_punctuation:
                return (
                    BoundaryLabel.BOUNDARY,
                    "sentence_terminal_punctuation",
                )

            return (
                BoundaryLabel.CONTINUATION,
                "punctuation_without_following_space",
            )

        # Rule 4: "And" depends on whether both sides look like requests.
        if trigger == "and":
            left_is_action_like = self._is_action_like(left_text)
            right_is_action_like = self._is_action_like(right_text)

            if left_is_action_like and right_is_action_like:
                return (
                    BoundaryLabel.BOUNDARY,
                    "two_action_like_phrases",
                )

            if left_is_action_like and not right_is_action_like:
                return (
                    BoundaryLabel.CONTINUATION,
                    "right_side_not_action_like",
                )

            if not left_is_action_like and right_is_action_like:
                return (
                    BoundaryLabel.UNCERTAIN,
                    "left_side_not_action_like",
                )

            return (
                BoundaryLabel.UNCERTAIN,
                "neither_side_action_like",
            )

        # Rule 5: "Or" commonly connects alternatives.
        if trigger == "or":
            return (
                BoundaryLabel.CONTINUATION,
                "alternative_coordinator",
            )

        # Rule 6: "But" signals contrast, which needs more context.
        if trigger == "but":
            return (
                BoundaryLabel.UNCERTAIN,
                "contrast_requires_context",
            )

        # Rule 7: A comma is weaker evidence than a semicolon.
        if candidate.signal_type == BoundarySignalType.COMMA:
            if (
                self._is_action_like(left_text)
                and self._is_action_like(right_text)
            ):
                return (
                    BoundaryLabel.BOUNDARY,
                    "two_action_like_phrases",
                )

            return (
                BoundaryLabel.UNCERTAIN,
                "comma_without_two_action_like_phrases",
            )

        # Rule 8: Do not invent a decision when evidence is insufficient.
        return BoundaryLabel.UNCERTAIN, "insufficient_boundary_evidence"

    @classmethod
    def _is_action_like(cls, phrase: str) -> bool:
        """Heuristically detect an action-like or question-like phrase."""
        cleaned = phrase.strip()

        # Remove leading punctuation such as a comma.
        cleaned = re.sub(r"^[,;:!?]+\s*", "", cleaned).strip()

        # Strip known request wrappers, including repeated wrappers:
        # "Please, could you open..." -> "open..."
        while cleaned:
            for pattern in cls._LEADING_WRAPPERS:
                updated = pattern.sub("", cleaned, count=1)

                if updated != cleaned:
                    cleaned = updated.strip()
                    break
            else:
                break

            cleaned = re.sub(r"^[,;:!?]+\s*", "", cleaned).strip()

        if not cleaned:
            return False

        # Examine the first whitespace-delimited token, not arbitrary
        # words occurring later in the phrase.
        first_token = cleaned.split()[0].strip(
            ".,?!:;()[]{}\"'"
        ).casefold()

        # A recognized imperative/action verb is action-like.
        if first_token in cls._ACTION_VERBS:
            return True

        # Question-like phrases can also form independent requests:
        # "what is Git?", "how can I fix this?", "can I use Python?"
        if first_token in cls._QUESTION_STARTERS:
            return len(cleaned.split()) >= 2

        return False
