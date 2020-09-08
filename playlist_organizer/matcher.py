from dataclasses import dataclass, field
from itertools import zip_longest
from typing import List, Dict

from playlist_organizer.client.base import Track


@dataclass
class MatchResult:
    only_left: List[Track] = field(default_factory=list)
    only_right: List[Track] = field(default_factory=list)
    found: Dict[Track, Track] = field(default_factory=dict)


class TrackMatcher:
    def match(self, left: List[Track], right: List[Track]) -> MatchResult:
        result = MatchResult()

        for t1, t2 in zip_longest(left, right):
            if t1 and t2:
                result.found[t1] = t2
            elif t1 and not t2:
                result.only_left.append(t1)
            elif not t1 and t2:
                result.only_right.append(t2)
        return result
