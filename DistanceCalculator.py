from EmbeddingCalculator import EmbeddingCalculator
import numpy as np

class DistanceCalculator():
    def __init__(self, model_name: str, use_cuda: bool = False):
        #
        self.embedding_calc: EmbeddingCalculator = EmbeddingCalculator(
            model_name=model_name,
            use_cuda=use_cuda
        )
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
    
    
    def calculate_distance_embed(self, txt1: str, txt2: str, ) -> float:
        #
        embs: list[np.ndarray] = self.embedding_calc.get_sentence_embeddings(
                                                        [txt1, txt2])
        #
        return np.linalg.norm(embs[0] - embs[1])


    def calculate_distance_common_words(self, txt1: str, txt2: str) -> float:
        #
        embs: list[np.ndarray] = self.embedding_calc.get_sentence_embeddings(
                                                        [txt1, txt2])
        #
        return -self.find_common_words(txt1, txt2)


    def calculate_distance_both(self,
                                txt1: str,
                                txt2: str,
                                coef_common_words: float = 1.0
                               ) -> float:
        #
        embs: list[np.ndarray] = self.embedding_calc.get_sentence_embeddings(
                                                        [txt1, txt2])
        #
        return np.linalg.norm(embs[0] - embs[1]) \
                - coef_common_words * self.find_common_words(txt1, txt2)



