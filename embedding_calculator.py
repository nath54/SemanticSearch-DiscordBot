"""_summary
"""

import os
import torch
from transformers import AutoModel, AutoTokenizer
import numpy as np

from profiling import Profile


# Paths where the models are stored
MODELS_PATH: str = "models/"


#
class EmbeddingCalculator():
    """_summary_

    Raises:
        UserWarning: _description_
        UserWarning: _description_
        UserWarning: _description_
        UserWarning: _description_
        UserWarning: _description_

    Returns:
        _type_: _description_
    """

    #
    def __init__(self, config: dict) -> None:
        self.config = config
        self.model_name: str = self.config["model_name"]
        self.model: AutoModel | None = None
        self.att_query: torch.nn.Module | None = None
        self.att_key: torch.nn.Module | None = None
        self.embeddings: torch.nn.Module | None = None
        self.tokenizer: AutoTokenizer | None = None
        self.use_cuda: bool = self.config["use_cuda"] == 1
        #
        if self.use_cuda and not torch.cuda.is_available():
            raise UserWarning("Try to use cuda, but cuda is not available")
        #
        self.device: str = "cpu"
        if self.use_cuda:
            self.device = "cuda"
        #
        self.get_model()


    #
    def model_forward(self, x, nb_layers: int = -1):
        """_summary_

        Args:
            X (_type_): _description_
            nb_layers (int, optional): _description_. Defaults to -1.

        Returns:
            _type_: _description_
        """

        if self.model is None:
            raise UserWarning("Error, no model used!")

        #
        model: torch.nn.Module = self.model

        #
        if nb_layers == -1 or nb_layers >= len(model.encoder.layers):
            return model(x)
        #
        x = model.embeddings(x)
        #
        for i in range(nb_layers):
            x = model.encoder.layers[i](x)
        #
        x = model.encoder.pooler(x)
        #
        return x


    #
    def model_forward_skip_layers(self, x, skip_layers: list[int]):
        """_summary_

        Args:
            X (_type_): _description_
            skip_layers (list[int], optional): _description_. Defaults to [].

        Returns:
            _type_: _description_
        """


        if self.model is None:
            raise UserWarning("Error, no model used!")

        #
        model: torch.nn.Module = self.model

        #
        if skip_layers == []:
            return model(x)
        #
        x = model.embeddings(x)
        #
        nb_layers: int = len(model.encoder.layers)
        for i in range(nb_layers):
            if not i in skip_layers:
                x = model.encoder.layers[i](x)
        #
        x = model.encoder.pooler(x)
        #
        return x


    #
    def model_forward_pass_only_layers(self, x, pass_layers: list[int]):
        """_summary_

        Args:
            X (_type_): _description_
            pass_layers (list[int], optional): _description_. Defaults to [].

        Returns:
            _type_: _description_
        """

        if self.model is None:
            raise UserWarning("Error, no model!")

        #
        x = self.model.embeddings(x)

        #
        for i in pass_layers:
            if i >= 0 and i < 24:
                x = self.model.encoder.layers[i](x)

        #
        x = self.model.encoder.pooler(x)
        #
        return x


    #
    def get_attention_from_model(self) -> torch.nn.Module | None:
        """_summary_

        Returns:
            torch.nn.Module | None: _description_
        """

        if self.model is None:
            return None
        #
        return self.model.encoder.layers[0].attention


    #
    def get_model(self) -> None:
        """_summary_
        """

        #
        if not os.path.exists(f"./{MODELS_PATH}/{self.model_name}"):
            self.download_model()
        else:
            self.load_downloaded_model()
        #
        print(self.model)
        #
        if self.model is not None:
            self.embeddings = self.model.embeddings
            self.att_query = self.model.encoder.layer[0].attention.self.query
            self.att_key = self.model.encoder.layer[0].attention.self.key


    #
    def load_downloaded_model(self, verbose=True) -> None:
        """_summary_

        Raises:
            UserWarning: _description_
            UserWarning: _description_
        """

        # Printing infos
        if verbose:
            print(f"Loading local model {self.model_name}...")

        #
        self.model = AutoModel.from_pretrained(
                        f"./{MODELS_PATH}/{self.model_name}")

        #
        if not self.model:
            raise UserWarning("Error while loading the model")

        #
        self.tokenizer = AutoTokenizer.from_pretrained(
                          f"./{MODELS_PATH}/{self.model_name}")

        #
        if not self.tokenizer:
            raise UserWarning("Error while loading the tokenizer")

        # Printing infos
        if verbose:
            print(f"{self.model_name} model loaded successfully.")


    #
    def download_model(self) -> None:
        """_summary_

        Raises:
            UserWarning: _description_
            UserWarning: _description_
        """

        #
        print(f"Downloading model {self.model_name}...")

        #
        self.model = AutoModel.from_pretrained(self.model_name)

        #
        if not self.model:
            raise UserWarning("Error while downloading the model")

        #
        self.tokenizer = AutoTokenizer.from_pretrained(
                                            self.model_name)

        #
        if not self.tokenizer:
            raise UserWarning("Error while downloading the tokenizer")

        #
        self.model.save_pretrained(f"./{MODELS_PATH}/{self.model_name}")

        #
        self.tokenizer.save_pretrained(f"./{MODELS_PATH}/{self.model_name}")

        #
        print(f"{self.model_name} model downloaded"
              f" and saved to ./{MODELS_PATH}/{self.model_name}")


    # Function to generate sentence embeddings
    def get_sentence_embeddings(self,
                                sentences: list[str]) -> list[np.ndarray]:
        """_summary_

        Args:
            sentences (list[str]): _description_

        Returns:
            list[np.ndarray]: _description_
        """

        if self.tokenizer is None:
            raise UserWarning("Error, no tokenizer!")

        if self.model is None:
            raise UserWarning("Error, no model!")

        #
        embeddings: list[np.ndarray] = []

        # Profiling
        if self.config["profiling"] == 1:
            p1: Profile = Profile("EmbeddingCalculator.py; Tokenize sentences")

        #
        inputs = self.tokenizer(sentences,
                                max_length=512,
                                truncation=True,
                                padding=True,
                                return_tensors="pt",
                                return_attention_mask=True)

        # Profiling
        if self.config["profiling"] == 1:
            p1.finished(f"Nb sentences tokenized: {len(sentences)}")

        # Profiling
        if self.config["profiling"] == 1:
            p2: Profile = Profile("EmbeddingCalculator.py; Calculate embedding")

        #
        with torch.no_grad():

            #
            outputs = self.model(**inputs)

            #
            last_hidden_state = outputs.last_hidden_state

            # Extract the sentence embedding
            #  (consider averaging or using other methods)
            sentence_embedding = torch.mean(last_hidden_state, dim=1)
            embeddings += [s.cpu().numpy() for s in sentence_embedding]
            #

        # Profiling
        if self.config["profiling"] == 1:
            p2.finished(f"Nb sentence tokenized: {len(sentences)}")

        #
        return embeddings
