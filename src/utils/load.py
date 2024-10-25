from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
from abc import ABC, abstractmethod
from typing import Dict, Any
import json


class Config(ABC):
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type
        self.config = self.load_config(type)

    def load_config(self, type) -> Dict[str, Any]:
        with open("utils/config.json") as f:
            config = json.load(f)
            config = config[type]
            return config

    @abstractmethod
    def load(self):
        """Abstract method to load specific configuratons"""


class ModelConfig(Config):
    def __init__(self, name):
        super().__init__(name, "models")

    def load(self):
        self.model_config = self.config.get(self.name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_config["repo_id"])
        self.tokenzier = AutoTokenizer.from_pretrained(self.model_config["repo_id"])


class DataConfig(Config):
    def __init__(self, name):
        super().__init__(name, "datasets")


def load(self):
    self.data_config = self.config.get(self.name)


def load_model():
    AutoModelForCausalLM.from_pretrained("", trust_remote_code=True)
    pass
