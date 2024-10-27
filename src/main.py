import asyncio
from vllm import AsyncLLMEngine
from transformers import AutoTokenizer

async def generate_text(prompt):
    engine = AsyncLLMEngine()
    tokenizer = AutoTokenizer.from_pretrained("01-ai/Yi-Coder-1.5B-Chat")

    model_inputs = tokenizer(prompt, return_tensors="pt").input_ids
    output = await engine.generate(model_inputs, max_new_tokens=512)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    print(response)

# 비동기 실행
prompt = "Please write a C++ code for merge sort."
asyncio.run(generate_text(prompt))
