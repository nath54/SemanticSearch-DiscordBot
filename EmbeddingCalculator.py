import torch
import os
from transformers import AutoModel, AutoTokenizer
import numpy as np

from profiling import Profile


MODELS_PATH: str = "models/"

#
class EmbeddingCalculator():
    
    
    #
    def __init__(self, config: dict) -> None:
        self.config = config
        self.model_name: str = self.config["model_name"]
        self.model: AutoModel | None = None
        self.tokenizer: AutoTokenizer | None = None
        self.use_cuda: bool = (self.config["use_cuda"] == 1)
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
    def model_forward(self, X, nb_layers: int = -1):
        #
        if nb_layers == -1 or nb_layers >= len(self.model.encoder.layers):
            return self.model(X)
        #
        X = self.model.embeddings(X)
        #
        for i in range(nb_layers):
            X = self.model.encoder.layers[i](X)
        #
        X = self.model.encoder.pooler(X)
        #
        return X
    
    
    #
    def model_forward_skip_layers(self, X, skip_layers: list[int] = []):
        #
        if skip_layers == []:
            return self.model(X)
        #
        X = self.model.embeddings(X)
        #
        nb_layers: int = len(self.model.encoder.layers)
        for i in range(nb_layers):
            if not i in skip_layers:
                X = self.model.encoder.layers[i](X)
        #
        X = self.model.encoder.pooler(X)
        #
        return X
    
    
    #
    def model_forward_pass_only_layers(self, X, pass_layers: list[int] = []):
        #
        if pass_layers == []:
            return self.model(X)
        #
        X = self.model.embeddings(X)
        #
        nb_layers: int = len(self.model.encoder.layers)
        for i in pass_layers:
            if i >= 0 and i < 24:
                X = self.model.encoder.layers[i](X)
        #
        X = self.model.encoder.pooler(X)
        #
        return X
    
    
    #
    def get_attention_from_model(self) -> torch.nn.Module | None:
        if self.model == None:
            return None
        #
        return self.model.encoder.layers[0].attention


    #
    def get_model(self) -> None:
        if not os.path.exists(f"./{MODELS_PATH}/{self.model_name}"):
            self.download_model()
        else:
            self.load_downloaded_model()
        #
        # print(f"Model : {self.model_name}")
        # print(self.model)
        # print(f"\n\ntest : {self.model.encoder.layer[0].attention}")
        # input("press enter to exit")
        # exit()


    #
    def load_downloaded_model(self) -> None:
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
        #
        print(f"{self.model_name} model loaded successfully.")


    #
    def download_model(self) -> None:
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
        #
        embeddings: list[torch.Tensor] = []
        #
        if self.config["profiling"] == 1:
            p1: Profile = Profile(f"EmbeddingCalculator.py; Tokenize sentences")
    
        #
        inputs = self.tokenizer(sentences,
                                max_length=512,
                                truncation=True,
                                padding=True,
                                return_tensors="pt",
                                return_attention_mask=True)
        
        if self.config["profiling"] == 1:
            p1.finished([f"Nb sentences tokenized: {len(sentences)}"])
        #
        if self.config["profiling"] == 1:
            p2: Profile = Profile("EmbeddingCalculator.py; Calculate embedding")
        #
        with torch.no_grad():
            outputs = self.model(**inputs)
            #
            last_hidden_state = outputs.last_hidden_state
            # Extract the sentence embedding
            #  (consider averaging or using other methods)
            sentence_embedding = torch.mean(last_hidden_state, dim=1)
            embeddings += [s.cpu().numpy() for s in sentence_embedding]
            #
        #
        if self.config["profiling"] == 1:
            p2.finished([f"Nb sentence tokenized: {len(sentences)}"])
        #
        return embeddings
