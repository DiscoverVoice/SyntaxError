from langchain_community.llms import vllm
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
        llm = vllm.VLLM(model=self.name,
                        trust_remote_code=True,
                        max_new_tokens=1024,
                        top_k=10,
                        top_p=0.95,
                        temperature=0.1
                        )


class DataConfig(Config):
    def __init__(self, name):
        super().__init__(name, "datasets")


    def load(self):
        self.data_config = self.config.get(self.name)

