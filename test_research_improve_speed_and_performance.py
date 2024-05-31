"""
This script contains little tests
"""


import json
from typing import Callable

from distance_calculator import DistanceCalculator


#################
# Lib functions #
#################

# Average function
def avg(l: list) -> float:
    """_summary_

    Args:
        l (list): list of values to average

    Returns:
        float: the average of the values of the input list
    """

    #
    if len(l) == 0:
        return 0
    #
    return sum(l)/len(l)



#################
# Test function #
#################


def load_tests(sentences_file: str,
               search_file: str) -> tuple[list[str], list[tuple[str, int]]]:
    """_summary_

    Args:
        sentences_file (str): _description_
        search_file (str): _description_

    Returns:
        tuple[list[str], list[tuple[str, int]]]: _description_
    """

    test_sentences: list[str] = []
    test_searchs: list[tuple[str, int]] = []

    #
    with open(sentences_file, "r", encoding="utf-8") as f:
        # TODO
        pass

    #
    with open(search_file, "r", encoding="utf-8") as f:
        # TODO
        pass

    return test_sentences, test_searchs



#
def test(sentences_file: str,
         searchs_file: str,
         fn_dists: Callable
        ) -> tuple[float, list[int]]:
    """_summary_

    Args:
        sentences_file (str): list of sentences on which the tests will be done
        searchs_file (str): list of query and the id of the wanted sentence
        fn_dists (Callable): distance function that will be called

    Returns:
        tuple[float, list[int]]: the result of the test
    """

    test_sentences, test_searchs = load_tests(sentences_file, searchs_file)


    #
    scores: list[float] = []
    abs_score: list[int] = []

    #
    for tst in test_searchs:
        #
        dists: list[float] = fn_dists(tst[0], test_sentences)
        dists_with_idx: list[tuple[float, int]] = [
            (dists[i], i) for i in range(len(test_sentences))]

        #
        dists_with_idx.sort()

        #
        idx_sol: int = -1
        for i in range(len(test_sentences)):
            if dists_with_idx[i][1] == tst[1]:
                idx_sol = i

        #
        if idx_sol == -1:
            scores.append(0)
            abs_score.append(len(test_sentences))
        else:
            scores.append( 1/(idx_sol+1) )
            abs_score.append(idx_sol)

    return avg(scores), abs_score


##################
# Loading Config #
##################


CONFIG_FILE: str = "config.json"

config: dict[str, str | int] = {}

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)


distance_calc: DistanceCalculator = DistanceCalculator(config)


###############
# Test basics #
###############

print("Test basic, both-simple : ", test("tests/simple_test_1/sentences.md",
                                         "tests/simple_test_1/searchs_1.md",
                                         distance_calc.calculate_distance_both) )


print("Test basic, only embed : ", test("tests/simple_test_1/sentences.md",
                                        "tests/simple_test_1/searchs_1.md",
                                        distance_calc.calculate_distance_embed) )


print("Test basic, only words-simple : ", test("tests/simple_test_1/sentences.md",
                                               "tests/simple_test_1/searchs_1.md",
                                               distance_calc.calculate_distance_common_words) )



##############################################
# Test skipping last layers of encoder model #
##############################################

# TODO



#############################################
# Test skipping mid layers of encoder model #
#############################################

# TODO


#################################################
# Test using attention to weight sentence words #
#################################################

# TODO
