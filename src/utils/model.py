import os
import json
import torch
from abc import ABC, abstractmethod
from typing import Dict, Any
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from vllm.lora.request import LoRARequest
import vllm
import openai
import re
import logging


class LLM(ABC):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.kwargs = kwargs
        self.llm = None

    @abstractmethod
    def load(self):
        pass
    
    @abstractmethod
    def generate_text(self, prompt):
        pass
    
    def preprocess_text(self, text):
        text = re.sub(r"\\\(", "`", text)
        text = re.sub(r"\\\)", "`", text)
        return text

class OpenAI(LLM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load()
        
    def load(self):
        load_dotenv()
        api_key = os.getenv("SECRET_KEY")
        if not api_key:
            raise ValueError("SECRET_KEY not found in environment variables.")
        self.llm = openai.OpenAI(api_key=api_key)
    
    def generate_text(self, prompt):
        prompt = self.preprocess_text(prompt)
        messages = [{"role": "user", "content": prompt}]
        output = self.llm.chat.completions.create(
            model=self.name, messages=messages
        )
        return output.choices[0].message.content.strip()
        
class LocalLLM(LLM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_model_len = kwargs.get("max_model_len", 2048)
        self.gpu_memory_utilization = kwargs.get("gpu_memory_utilization", 0.9)
        self.temperature = kwargs.get("temperature", 0.4)
        self.top_p = kwargs.get("top_p", 0.95)
        self.repetition_penalty = kwargs.get("repetition_penalty", 1.2)
        self.max_tokens = kwargs.get("max_tokens", 3096)
        self.load()
    
    def load(self):
        logging.getLogger("vllm").setLevel(logging.WARNING)
        self.llm = vllm.LLM(
            model=self.name,
            trust_remote_code=True,
            max_model_len=self.max_model_len,
            gpu_memory_utilization=self.gpu_memory_utilization,
        )
        self.sampling_params = vllm.SamplingParams(
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            stop=["</s>", "Human:", "Assistant:", "<|user|>", "<|endoftext|>", "<|pad|>", "<|cls|>"],
        )
    
    def generate_text(self, prompt):
        prompt = self.preprocess_text(prompt)
        outputs = self.llm.generate([prompt], self.sampling_params)
        return outputs[0].outputs[0].text

class LoRALLM(LocalLLM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load()
        
    def load(self):
        model = AutoModelForCausalLM.from_pretrained(self.name, trust_remote_code=True, torch_dtype=torch.float16).to("cuda")
        self.tokenizer = AutoTokenizer.from_pretrained(self.name, trust_remote_code=True)
        self.llm = PeftModel.from_pretrained(model, self.name, torch_dtype=torch.float16).to("cuda")
        self.sampling_params = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_new_tokens": self.max_tokens,
            "repetition_penalty": self.repetition_penalty,
        }
        
    def generate_text(self, prompt):
        prompt = self.preprocess_text(prompt)
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        
        with torch.no_grad():
            outputs = self.llm.generate(
                **inputs, 
                **self.sampling_params,
            )
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        if answer.startswith(prompt):
           answer = answer[len(prompt):].strip()

        if "---" in answer:
           answer = answer.split("---")[0].strip()
        return answer