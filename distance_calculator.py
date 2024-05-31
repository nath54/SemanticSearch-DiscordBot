"""_summary_
"""

from typing import Callable

import numpy as np
import torch
from torch import nn

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


    #
    def find_common_words(self, txt1: str, txt2: str) -> int:
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
                                            padding=True,
                                            return_tensors="pt",
                                            return_attention_mask=True)

        #
        tk2 = self.embedding_calc.tokenizer(txt2,
                                            max_length=512,
                                            truncation=True,
                                            padding=True,
                                            return_tensors="pt",
                                            return_attention_mask=True)

        #
        x1 = self.embedding_calc.embeddings(tk1)
        x2 = self.embedding_calc.embeddings(tk2)

        q = self.embedding_calc.att_query(x1)
        k = self.embedding_calc.att_key(x2)

        softmax: nn.Softmax = nn.Softmax()
        att_mtx = softmax(q*k.T / torch.sqrt(q.shape[1]))

        att = torch.mean(att_mtx)

        score: float = 0

        for i, t in enumerate(tk1):
            if t in tk2:
                score += att[i].item()

        return score


    #
    def calculate_distance_embed(self,
                                 txt1: str,
                                 lst: list[str],
                                 dist_fn: Callable = dist_square) -> list[float]:
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
                                                        [txt1] + lst)
        #
        return [dist_fn(embs[0], embs[i+1]) for i in range(0, len(lst))]


    #
    def calculate_distance_common_words(self,
                                        txt1: str,
                                        lst: list[str]) -> list[float]:
        """_summary_

        Args:
            txt1 (str): _description_
            lst (list[str]): _description_

        Returns:
            list[float]: _description_
        """

        #
        return [-self.find_common_words(txt1, lst[i]) \
                    for i in range(0, len(lst))]


    #
    def calculate_distance_both(self,
                                txt1: str,
                                lst: list[str],
                                coef_common_words: float = 1.0,
                                dist_fn: Callable = dist_square
                               ) -> list[float]:
        """_summary_

        Args:
            txt1 (str): _description_
            lst (list[str]): _description_
            coef_common_words (float, optional): _description_. Defaults to 1.0.
            dist_fn (Callable, optional): _description_. Defaults to dist_square.

        Returns:
            list[float]: _description_
        """

        #
        embs: list[np.ndarray] = self.embedding_calc.get_sentence_embeddings(
                                                        [txt1] + lst)
        #
        return [
            dist_fn(embs[0], embs[i+1])\
                - coef_common_words * self.find_common_words(txt1, lst[i]) \
            for i in range(0, len(lst))]
