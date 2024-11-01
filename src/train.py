import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import concatenate_datasets
from peft import LoraConfig, get_peft_model
from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
from transformers.trainer_callback import EarlyStoppingCallback

model_name = "Qwen/Qwen2.5-Coder-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
qa_dataset = load_dataset("json", data_files={"train": "../data/qa_data.jsonl"})
debug_dataset = load_dataset("json", data_files={"train": "../data/debug_data.jsonl"})

def preprocess_data(examples):
    inputs = [f"{instruction}\n{input_text}" for instruction, input_text in zip(examples["instruction"], examples["input"])]
    outputs = examples["output"]
    model_inputs = tokenizer(inputs, truncation=True, padding="max_length", max_length=4096)
    labels = tokenizer(outputs, truncation=True, padding="max_length", max_length=4096)["input_ids"]
    labels_with_ignore_index = [
        [-100 if mask == 0 else label for label, mask in zip(label_seq, attention_mask)]
        for label_seq, attention_mask in zip(labels, model_inputs["attention_mask"])
    ]
    model_inputs["labels"] = labels_with_ignore_index
    return {
        "input_ids": model_inputs["input_ids"],
        "attention_mask": model_inputs["attention_mask"],
        "labels": labels_with_ignore_index,
    }

qa_tokenized = qa_dataset.map(preprocess_data, batched=True)
debug_tokenized = debug_dataset.map(preprocess_data, batched=True)
combined_dataset = concatenate_datasets(
    [qa_tokenized["train"], debug_tokenized["train"]]
).train_test_split(test_size=0.1)

model = AutoModelForCausalLM.from_pretrained(model_name)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=[
        "q_proj",
        "v_proj"
    ],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM",
    use_dora=True
)
model.enable_input_require_grads()
model = get_peft_model(model, lora_config)
model.train()
model.config.use_cache = False

training_args = TrainingArguments(
    output_dir="./fine_tuned_qwen",
    num_train_epochs=20,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    weight_decay=0.01,
    eval_strategy="steps",
    save_strategy="steps",
    logging_dir="./logs",
    save_steps=50,
    eval_steps=50,
    logging_steps=50,
    fp16=True,
    push_to_hub=False,
    report_to="wandb",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False
)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=combined_dataset["train"],
    eval_dataset=combined_dataset["test"],
    data_collator=data_collator,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
)

trainer.train()

model.save_pretrained("./fine_tuned_qwen_merged")
tokenizer.save_pretrained("./fine_tuned_qwen_merged")

final_metrics = trainer.evaluate()
print(final_metrics)
