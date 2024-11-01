import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any
from dotenv import load_dotenv
from datasets import load_dataset
from openai import OpenAI
import vllm


class Config(ABC):
    def __init__(self, name: str, type_: str):
        self.name = name
        self.type = type_
        self.config = self.load_config(type_)

    def load_config(self, type_) -> Dict[str, Any]:
        with open("utils/config.json") as f:
            config = json.load(f)
        return config.get(type_, {})

    @abstractmethod
    def load(self):
        pass


class LLM(Config):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, "models")
        self.sampling_params = None
        self.max_model_len = kwargs.get("max_model_len", 8000)
        self.gpu_memory_utilization = kwargs.get("gpu_memory_utilization", 0.9)
        self.temperature = kwargs.get("temperature", 0.6)
        self.top_p = kwargs.get("top_p", 0.95)
        self.max_tokens = kwargs.get("max_tokens", 8000)
        self.llm = self.load()

    def load(self):
        self.model_config = self.config.get(self.name)
        if self.name == "gpt-4o":
            load_dotenv()
            api_key = os.getenv("SECRET_KEY")
            if not api_key:
                raise ValueError("SECRET_KEY not found in environment variables.")
            self.llm = OpenAI(api_key=api_key)
        else:
            self.llm = vllm.LLM(
                model=self.name,
                trust_remote_code=True,
                max_model_len=self.max_model_len,
                gpu_memory_utilization=self.gpu_memory_utilization,
            )
        return self.llm

    def init_sampling_params(self):
        self.sampling_params = vllm.SamplingParams(
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            stop=["</s>", "Human:", "Assistant:", "<|user|>", "<|endoftext|>", "<|pad|>", "<|cls|>"],
        )

    def generate_text(self, prompt: str) -> str:
        if isinstance(self.llm, vllm.LLM):
            if not self.sampling_params:
                self.init_sampling_params()
            outputs = self.llm.generate([prompt], self.sampling_params)
            return outputs[0].outputs[0].text
        else:
            messages = [{"role": "user", "content": prompt}]
            generate_text = self.llm.chat.completions.create(
                model=self.name, messages=messages
            )
            return generate_text.choices[0].message.content.strip()
