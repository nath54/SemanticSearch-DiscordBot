import torch
import os
from transformers import AutoModel, AutoTokenizer
import numpy as np


MODELS_PATH: str = "models/"


class EmbeddingCalculator():
    def __init__(self, model_name: str, use_cuda: bool = False) -> None:
        self.model_name: str = model_name
        self.model: AutoModel | None = None
        self.tokenizer: AutoTokenizer | None = None
        self.use_cuda: bool = use_cuda
        #
        if self.use_cuda and not torch.cuda.is_available():
            raise UserWarning("Try to use cuda, but cuda is not available")
        #
        self.device: str = "cpu"
        if self.use_cuda:
            self.device = "cuda"
        #
        self.get_model()

    def get_model(self) -> None:
        if not os.path.exists(f"./{self.model_name}"):
            self.download_model()
        else:
            self.load_downloaded_model()

    def load_downloaded_model(self) -> None:
        print(f"Loading local model {self.model_name}...")
        #
        self.model = AutoModel.from_pretrained(
                        f"./{MODELS_PATH}/{self.model_name}").to(self.device)
        #
        if not self.model:
            raise UserWarning("Error while loading the model")
        #
        self.tokenizer = AutoTokenizer.from_pretrained(
                          f"./{MODELS_PATH}/{self.model_name}").to(self.device)
        #
        if not self.tokenizer:
            raise UserWarning("Error while loading the tokenizer")
        #
        print(f"{self.model_name} model loaded successfully.")

    def download_model(self) -> None:
        print(f"Downloading model {self.model_name}...")
        #
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
        #
        if not self.model:
            raise UserWarning("Error while downloading the model")
        #
        self.tokenizer = AutoTokenizer.from_pretrained(
                                            self.model_name).to(self.device)
        #
        if not self.tokenizer:
            raise UserWarning("Error while downloading the tokenizer")
        #
        res: tuple[str] = self.model.save_pretrained(
                                        f"./{MODELS_PATH}/{self.model_name}")
        #
        if len(res) == 0:
            raise UserWarning("Error while saving the model")
        #
        res = self.tokenizer.save_pretrained(
                                f"./{MODELS_PATH}/{self.model_name}")
        #
        if len(res) == 0:
            raise UserWarning("Error while saving the tokenizer")
        #
        print(f"{self.model_name} model downloaded"
              f" and saved to ./{MODELS_PATH}/{self.model_name}")

    # Function to generate sentence embeddings
    def get_sentence_embeddings(self,
                                sentences: list[str]) -> list[np.ndarray]:
        #
        embeddings: list[torch.Tensor] = []
        #
        sentence: str
        for sentence in sentences:
            #
            inputs = self.tokenizer(sentence,
                                    return_tensors="pt").to(self.device)
            #
            with torch.no_grad():
                outputs = self.model(**inputs)
                last_hidden_state = outputs.last_hidden_state
                # Extract the sentence embedding
                #  (consider averaging or using other methods)
                sentence_embedding = torch.mean(last_hidden_state, dim=1)
                embeddings.append(sentence_embedding.cpu().numpy())
                #
        return embeddings
