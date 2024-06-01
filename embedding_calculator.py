"""_summary
"""

from typing import Optional

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
    def model_forward(self, **args):
        """_summary_

        Args:
            x (_type_): _description_

        Raises:
            UserWarning: _description_

        Returns:
            _type_: _description_
        """

        if self.model is None:
            raise UserWarning("Error, no model used!")

        return self.model(**args)


    #
    def model_forward_skip_last_layers(self,
                                       input_ids: torch.Tensor,
                                       attention_mask: Optional[torch.Tensor] = None,
                                       nb_layers: int = -1) -> torch.Tensor:
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
        if nb_layers == -1 or nb_layers >= len(self.model.encoder.layer):
            return self.model(input_ids=input_ids)
        #
        x: torch.Tensor = self.model.embeddings(input_ids=input_ids)
        #
        for i in range(nb_layers):
            if attention_mask is not None and False:
                x = self.model.encoder.layer[i](x, attention_mask=attention_mask)[0]
            else:
                x = self.model.encoder.layer[i](x)[0]
        #
        x = self.model.pooler(x)
        #
        return x


    #
    def model_forward_skip_layers(self,
                                  input_ids: torch.Tensor,
                                  attention_mask: Optional[torch.Tensor] = None,
                                  skip_layers: Optional[list[int]] = None) -> torch.Tensor:
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
        if skip_layers is None or skip_layers == []:
            return self.model(input_ids=input_ids)
        #
        x = self.model.embeddings(input_ids=input_ids)
        #
        nb_layers: int = len(self.model.encoder.layer)
        for i in range(nb_layers):
            if not i in skip_layers:
                if attention_mask is not None and False:
                    x = self.model.encoder.layer[i](x, attention_mask=attention_mask)[0]
                else:
                    x = self.model.encoder.layer[i](x)[0]
        #
        x = self.model.encoder.pooler(x)
        #
        return x


    #
    def model_forward_pass_only_layers(self,
                                       input_ids: torch.Tensor,
                                       attention_mask: Optional[torch.Tensor] = None,
                                       pass_layers: Optional[list[int]] = None) -> torch.Tensor:
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
        x = self.model.embeddings(input_ids=input_ids)

        #
        if pass_layers is not None:
            #
            for i in pass_layers:
                if i >= 0 and i < 24:
                    if attention_mask is not None and False:
                        x = self.model.encoder.layer[i](x, attention_mask=attention_mask)[0]
                    else:
                        x = self.model.encoder.layer[i](x)[0]

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
        return self.model.encoder.layer[0].attention


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
    def download_model(self, verbose=True) -> None:
        """_summary_

        Raises:
            UserWarning: _description_
            UserWarning: _description_
        """

        #
        if verbose:
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
        if verbose:
            print(f"{self.model_name} model downloaded"
                f" and saved to ./{MODELS_PATH}/{self.model_name}")


    # Function to generate sentence embeddings
    def get_sentence_embeddings(self,
                                sentences: list[str],
                                embedding_skip_layers: dict | None = None) -> list[np.ndarray]:
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
                                padding='max_length',
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
            last_hidden_state: torch.Tensor

            #
            if embedding_skip_layers is not None and \
               embedding_skip_layers.get("skip_method") is not None and \
               embedding_skip_layers["skip_method"] == "last_layers" and \
               embedding_skip_layers.get("nb_layers") is not None:
                #
                last_hidden_state = self.model_forward_skip_last_layers(
                                        **inputs,
                                        nb_layers=embedding_skip_layers["nb_layers"])
                #
            elif embedding_skip_layers is not None and \
               embedding_skip_layers.get("skip_method") is not None and \
               embedding_skip_layers["skip_method"] == "skip_layers" and \
               embedding_skip_layers.get("layers_to_skip") is not None:
                #
                last_hidden_state = self.model_forward_skip_layers(
                                        **inputs,
                                        skip_layers=embedding_skip_layers["layers_to_skip"])
                #
            elif embedding_skip_layers is not None and \
               embedding_skip_layers.get("skip_method") is not None and \
               embedding_skip_layers["skip_method"] == "skip_layers" and \
               embedding_skip_layers.get("layers_to_pass") is not None:
                #
                last_hidden_state = self.model_forward_pass_only_layers(
                                        **inputs,
                                        pass_layers=embedding_skip_layers["layers_to_pass"])
                #
            else:
                #
                outputs = self.model(**inputs)
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
