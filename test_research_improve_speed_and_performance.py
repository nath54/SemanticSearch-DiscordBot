from DistanceCalculator import DistanceCalculator
import json



CONFIG_FILE: str = "config.json"

config: dict[str] = {}

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)


distance_calc: DistanceCalculator = DistanceCalculator(config)


"""
Tests sets
"""

#
sentences: list[str] = [
    # TODO
]


tests: list[tuple[str, int]] = [
    # TODO
]


"""
Test function
"""


def test(fn_dists: callable[tuple[str, list[str]], list[float]]) -> float:
    #
    scores: list[float] = []
    #
    embeddings = []
    #
    dists: list[float] = []

    #
    for test in tests:
        #
        dist_min: float = 0
        #
        # TODO


"""
Test skipping last layers of encoder model
"""

# TODO



"""
Test skipping mid layers of encoder model
"""

# TODO


"""
Test using attention to weight sentence words
"""

# TODO


