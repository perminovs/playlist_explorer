from dataclasses import dataclass, field
from typing import Dict, List

from Levenshtein import distance

from playlist_organizer.client.base import Track

MATCH_THRESHOLD = 3


@dataclass
class MatchResult:
    only_left: List[Track] = field(default_factory=list)
    only_right: List[Track] = field(default_factory=list)
    found: Dict[Track, Track] = field(default_factory=dict)


class TrackMatcher:
    def match(self, left: List[Track], right: List[Track]) -> MatchResult:
        result = MatchResult()

        for idx, t1 in enumerate(left):
            best_candidate = right[0]
            best_distance = distance(t1.title, best_candidate.title)
            for t2 in right[1:]:
                new_dist = distance(t1.title, t2.title)
                if new_dist > best_distance:
                    continue
                best_candidate = t2
                best_distance = new_dist

            if best_distance < MATCH_THRESHOLD:
                result.found[t1] = best_candidate
                right.remove(best_candidate)
            else:
                result.only_left.append(t1)

            if not right:
                result.only_left.extend(left[idx + 1 :])
                break

        result.only_right = right

        return result
