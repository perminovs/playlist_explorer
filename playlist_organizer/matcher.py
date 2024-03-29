import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from Levenshtein import distance

from playlist_organizer.client.base import Track

MATCH_THRESHOLD = 3
logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    only_left: List[Track] = field(default_factory=list)
    only_right: List[Track] = field(default_factory=list)
    found: Dict[Track, Track] = field(default_factory=dict)
    left_name: str = 'Left'
    right_name: str = 'Right'
    created_at: str = field(default_factory=lambda: datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f'))

    @property
    def name(self) -> str:
        return f'{self.left_name} -> {self.right_name} ({self.created_at})'


def _distance(s1: str, s2: str) -> int:
    return distance(_normalize(s1), _normalize(s2))


class TrackMatcher:
    def __init__(self, match_threshold: int = MATCH_THRESHOLD):
        self._match_threshold = match_threshold

    def match(self, left: List[Track], right: List[Track]) -> MatchResult:
        result = MatchResult()

        for idx, t1 in enumerate(left):
            best_candidate = right[0]
            best_distance = _distance(t1.title, best_candidate.title)
            for t2 in right[1:]:
                new_dist = _distance(t1.title, t2.title)
                if new_dist > best_distance:
                    continue
                best_candidate = t2
                best_distance = new_dist

            if best_distance <= self._match_threshold:
                result.found[t1] = best_candidate
                right.remove(best_candidate)
            else:
                logger.debug(
                    'Pair not found for %s\nBest candidate: %s\nLevenshtein distance=%s',
                    t1,
                    best_candidate,
                    best_distance,
                )
                result.only_left.append(t1)

            if not right:
                result.only_left.extend(left[idx + 1 :])
                break

        result.only_right = right

        return result


def _normalize(raw: str) -> str:
    replaced = raw.lower().replace('remastered', '').replace('remaster', '').strip()
    return ''.join(r for r in replaced if r.isalpha() or r.isdigit())
