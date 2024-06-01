"""
This script contains little tests
"""

import time
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
    with open(sentences_file, "r", encoding="utf-8") as file:
        for l in file.readlines():
            l = l.strip()
            if not l.startswith("#") and len(l) > 2:
                test_sentences.append(l)

    #
    with open(search_file, "r", encoding="utf-8") as file:
        for l in file.readlines():
            l = l.strip()
            if not l.startswith("#"):
                l2 = l.split("|")
                if len(l2) == 2:
                    test_searchs.append( (l2[0], int(l2[1])) )

    return test_sentences, test_searchs



#
def test(sentences_file: str,
         searchs_file: str,
         fn_dists: Callable
        ) -> dict:
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


    times: list[float] = []

    #
    for tst in test_searchs:

        #
        time_deb: float = time.time()

        #
        dists: list[float] = fn_dists(tst[0], test_sentences)

        #
        times.append( time.time() - time_deb )

        #
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

    return {
             "score": avg(scores),
             "absolute_scores": abs_score,
             "time_total": sum(times),
             "times": times
           }


##################
# Loading Config #
##################


CONFIG_FILE: str = "config.json"

config: dict[str, str | int] = {}

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)


distance_calc: DistanceCalculator = DistanceCalculator(config)


##################
# Dist functions #
##################


def dist_calc_both_with_att_tk(txt1: str, lst: list[str]):
    """_summary_

    Args:
        txt1 (str): _description_
        lst (list[str]): _description_

    Returns:
        _type_: _description_
    """

    return distance_calc.calculate_distance_both(
            txt1, lst,
            fn_search_syntax=distance_calc.find_common_tokens_with_attention)



def dist_calc_simple_with_att_tk(txt1: str, lst: list[str]):
    """_summary_

    Args:
        txt1 (str): _description_
        lst (list[str]): _description_

    Returns:
        _type_: _description_
    """

    return distance_calc.calculate_distance_common_words(
            txt1, lst,
            fn_search_syntax=distance_calc.find_common_tokens_with_attention)


def dist_calc_only_embed_skip_last_15_layers(txt1: str, lst: list[str]):
    """_summary_

    Args:
        txt1 (str): _description_
        lst (list[str]): _description_

    Returns:
        _type_: _description_
    """

    return distance_calc.calculate_distance_embed(
            txt1, lst,
            embedding_skip_layers={"skip_method": "last_layers", "nb_layers": 15})



def dist_calc_only_embed_skip_last_1_layers(txt1: str, lst: list[str]):
    """_summary_

    Args:
        txt1 (str): _description_
        lst (list[str]): _description_

    Returns:
        _type_: _description_
    """

    return distance_calc.calculate_distance_embed(
            txt1, lst,
            embedding_skip_layers={"skip_method": "last_layers", "nb_layers": 1})



def dist_calc_only_embed_skip_last_5_layers(txt1: str, lst: list[str]):
    """_summary_

    Args:
        txt1 (str): _description_
        lst (list[str]): _description_

    Returns:
        _type_: _description_
    """

    return distance_calc.calculate_distance_embed(
            txt1, lst,
            embedding_skip_layers={"skip_method": "last_layers", "nb_layers": 5})


def dist_calc_only_embed_skip_last_20_layers(txt1: str, lst: list[str]):
    """_summary_

    Args:
        txt1 (str): _description_
        lst (list[str]): _description_

    Returns:
        _type_: _description_
    """

    return distance_calc.calculate_distance_embed(
            txt1, lst,
            embedding_skip_layers={"skip_method": "last_layers", "nb_layers": 20})




###############
# Test basics #
###############


# print("Test basic, both-simple : ", test("tests/simple_test_1/sentences.md",
#                                          "tests/simple_test_1/searchs_1.md",
#                                          distance_calc.calculate_distance_both) )


# print("Test basic, only embed : ", test("tests/simple_test_1/sentences.md",
#                                         "tests/simple_test_1/searchs_1.md",
#                                         distance_calc.calculate_distance_embed) )


# print("Test basic, only syntax-simple : ", test("tests/simple_test_1/sentences.md",
#                                                 "tests/simple_test_1/searchs_1.md",
#                                                 distance_calc.calculate_distance_common_words) )

# print("Test basic, both-att : ", test("tests/simple_test_1/sentences.md",
#                                       "tests/simple_test_1/searchs_1.md",
#                                       dist_calc_both_with_att_tk) )


# print("Test basic, only syntax-att : ", test("tests/simple_test_1/sentences.md",
#                                              "tests/simple_test_1/searchs_1.md",
#                                              dist_calc_simple_with_att_tk) )


##############################################
# Test skipping last layers of encoder model #
##############################################

# 
# print("Test basic, only embed, skip last 20 layers : ", test("tests/simple_test_1/sentences.md",
#                                                              "tests/simple_test_1/searchs_1.md",
#                                                              dist_calc_only_embed_skip_last_20_layers) )


# # 
# print("Test basic, only embed, skip last 15 layers : ", test("tests/simple_test_1/sentences.md",
#                                                              "tests/simple_test_1/searchs_1.md",
#                                                              dist_calc_only_embed_skip_last_15_layers) )


# # 
# print("Test basic, only embed, skip last 5 layers : ", test("tests/simple_test_1/sentences.md",
#                                                              "tests/simple_test_1/searchs_1.md",
#                                                              dist_calc_only_embed_skip_last_5_layers) )


# # 
# print("Test basic, only embed, skip last 1 layers : ", test("tests/simple_test_1/sentences.md",
#                                                              "tests/simple_test_1/searchs_1.md",
#                                                              dist_calc_only_embed_skip_last_1_layers) )

# -> Les résultats montrent bien que ca ne marche pas, en plus, sans doute vu que je l'ai mal codé, c'est aussi plus lent pour la plupart des tests

"""
Bad scores:

Test basic, only embed, skip last 20 layers :  {'score': 0.17143199305438392, 'absolute_scores': [24, 2, 30, 19, 5, 20, 25, 23, 16, 12, 0], 'time_total': 454.3935899734497, 'times': [38.94578981399536, 40.43811106681824, 41.15297293663025, 40.4872989654541, 41.15348768234253, 41.13640999794006, 41.28862261772156, 41.37155771255493, 41.54207491874695, 42.63860011100769, 44.23866415023804]}
Test basic, only embed, skip last 15 layers :  {'score': 0.06921114142709918, 'absolute_scores': [27, 17, 22, 19, 16, 28, 21, 30, 17, 9, 3], 'time_total': 370.1611223220825, 'times': [33.383557081222534, 33.464107036590576, 33.35784029960632, 33.224740743637085, 33.51906418800354, 33.96619153022766, 33.95152187347412, 33.82095789909363, 33.820889949798584, 33.82382106781006, 33.82843065261841]}
Test basic, only embed, skip last 5 layers :  {'score': 0.06480426034364763, 'absolute_scores': [27, 16, 21, 4, 13, 18, 23, 28, 22, 14, 15], 'time_total': 125.00522232055664, 'times': [11.429530382156372, 11.443956851959229, 11.46405839920044, 11.306469202041626, 11.247081279754639, 11.395639896392822, 11.385668516159058, 11.251205682754517, 11.288169860839844, 11.401839256286621, 11.391602993011475]}
Test basic, only embed, skip last 1 layers :  {'score': 0.11785322585136582, 'absolute_scores': [9, 19, 1, 20, 22, 10, 16, 29, 17, 14, 3], 'time_total': 25.996176719665527, 'times': [2.376495361328125, 2.368053913116455, 2.3451623916625977, 2.3603620529174805, 2.3825833797454834, 2.368468999862671, 2.369023323059082, 2.353471517562866, 2.3441293239593506, 2.3653812408447266, 2.3630452156066895]}
"""

#############################################
# Test skipping mid layers of encoder model #
#############################################

# TODO


#################################################
# Test using attention to weight sentence words #
#################################################

# TODO
