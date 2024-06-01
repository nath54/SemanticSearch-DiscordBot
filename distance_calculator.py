"""_summary_
"""

from typing import Callable

import numpy as np
import torch
from torch import nn
from math import sqrt

from embedding_calculator import EmbeddingCalculator



#
def dist_square(e1, e2):
    """_summary_

    Args:
        e1 (_type_): _description_
        e2 (_type_): _description_

    Returns:
        _type_: _description_
    """

    return np.linalg.norm(e1 - e2)




#
def find_common_words(txt1: str, txt2: str) -> int:
    """
    Counts the number of common words between two strings (case-insensitive)

    Args:
        txt1 (str): The first string
        txt2 (str): The second string

    Returns:
        int: The number of common words (lowercase)
    """
    # Convert both strings to lowercase and split into word lists
    words1 = set(txt1.lower().split())
    words2 = set(txt2.lower().split())

    # Find the intersection of word sets (common words)
    common_words = words1.intersection(words2)

    return len(common_words)







#
class DistanceCalculator():
    """_summary_

    Raises:
        UserWarning: _description_
        UserWarning: _description_
        UserWarning: _description_

    Returns:
        _type_: _description_
    """


    #
    def __init__(self, config: dict):
        #
        self.embedding_calc: EmbeddingCalculator = EmbeddingCalculator(config)


    # x1 is the text to research, x2 is the research
    def find_common_tokens_with_attention(self, txt1: str, txt2: str) -> float:
        """_summary_

        Args:
            txt1 (str): _description_
            txt2 (str): _description_

        Raises:
            UserWarning: _description_
            UserWarning: _description_
            UserWarning: _description_

        Returns:
            float: _description_
        """

        #
        if self.embedding_calc.tokenizer is None:
            raise UserWarning("Error, no tokenizers!")
        #
        if self.embedding_calc.embeddings is None:
            raise UserWarning("Error, no initial embeddings!")
        #
        if self.embedding_calc.att_query is None or \
           self.embedding_calc.att_key is None:
            #
            raise UserWarning("Error, no attention!")

        #
        tk1 = self.embedding_calc.tokenizer(txt1,
                                            max_length=512,
                                            truncation=True,
                                            padding='max_length',
                                            return_tensors="pt")["input_ids"]

        #
        tk2 = self.embedding_calc.tokenizer(txt2,
                                            max_length=512,
                                            truncation=True,
                                            padding='max_length',
                                            return_tensors="pt")["input_ids"]

        #
        x1 = self.embedding_calc.embeddings(tk1).view(512, 1024)
        x2 = self.embedding_calc.embeddings(tk2).view(512, 1024)

        q = self.embedding_calc.att_query(x1)
        k = self.embedding_calc.att_key(x2)

        dim_k = q.shape[1]

        # softmax: nn.Softmax = nn.Softmax(dim=-1)

        att_mtx = torch.matmul(q, k.T) / sqrt(dim_k)

        # att_mtx = softmax( d )

        att = torch.mean(att_mtx, dim=1)

        score: float = 0

        for i, t in enumerate(tk1[0]):
            if t > 2 and t in tk2[0]:
                score += att[i].item()

        return score


    #
    def calculate_distance_embed(self,
                                 txt1: str,
                                 lst: list[str],
                                 dist_fn: Callable = dist_square,
                                 embedding_skip_layers: dict | None = None
                                ) -> list[float]:
        """_summary_

        Args:
            txt1 (str): _description_
            lst (list[str]): _description_
            dist_fn (Callable, optional): _description_. Defaults to dist_square.

        Returns:
            list[float]: _description_
        """

        #
        embs: list[np.ndarray] = self.embedding_calc.get_sentence_embeddings(
                                                        [txt1] + lst,
                                                        embedding_skip_layers)
        #
        return [dist_fn(embs[0], embs[i+1]) for i in range(0, len(lst))]


    #
    def calculate_distance_common_words(self,
                                        txt1: str,
                                        lst: list[str],
                                        fn_search_syntax: Callable = find_common_words
                                       ) -> list[float]:
        """_summary_

        Args:
            txt1 (str): _description_
            lst (list[str]): _description_
            fn_search_syntax (Callable, optional): _description_. Defaults to find_common_words.

        Returns:
            list[float]: _description_
        """

        #
        return [-fn_search_syntax(txt1, lst[i]) \
                    for i in range(0, len(lst))]


    #
    def calculate_distance_both(self,
                                txt1: str,
                                lst: list[str],
                                coef_common_words: float = 1.0,
                                dist_fn: Callable = dist_square,
                                fn_search_syntax: Callable = find_common_words,
                                embedding_skip_layers: dict | None = None
                               ) -> list[float]:
        """_summary_

        Args:
            txt1 (str): _description_
            lst (list[str]): _description_
            coef_common_words (float, optional): _description_. Defaults to 1.0.
            dist_fn (Callable, optional): _description_. Defaults to dist_square.
            fn_search_syntax (Callable, optional): _description_. Defaults to find_common_words.

        Returns:
            list[float]: _description_
        """

        #
        embs: list[np.ndarray] = self.embedding_calc.get_sentence_embeddings(
                                                        [txt1] + lst,
                                                        embedding_skip_layers)
        
        #
        return [
            dist_fn(embs[0], embs[i+1])\
                - coef_common_words * fn_search_syntax(txt1, lst[i]) \
            for i in range(0, len(lst))]
