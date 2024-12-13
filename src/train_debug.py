import os
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import concatenate_datasets
from peft import LoraConfig, get_peft_model
from transformers.trainer_callback import EarlyStoppingCallback

# Environment configuration
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Model and dataset initialization
model_name = "Qwen/Qwen2.5-Coder-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
debug_dataset = load_dataset("json", data_files={"train": "../data/debug_data.jsonl"})

# Preprocessing function
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

# Tokenizing and splitting the dataset
debug_tokenized = debug_dataset.map(preprocess_data, batched=True)
combined_dataset = debug_tokenized["train"].train_test_split(test_size=0.1)

# Loading the base model and configuring LoRA
model = AutoModelForCausalLM.from_pretrained(model_name)
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM",
)
model.enable_input_require_grads()
model = get_peft_model(model, lora_config)
model.train()
model.config.use_cache = False

# Training arguments
training_args = TrainingArguments(
    output_dir="./debug",
    num_train_epochs=10,
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
    greater_is_better=False,
    save_total_limit=2  # Limit the number of checkpoints to 2
)

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=combined_dataset["train"],
    eval_dataset=combined_dataset["test"],
    data_collator=data_collator,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
)

# Training the model
trainer.train()

# Saving the model and tokenizer
model.save_pretrained("./debug")
tokenizer.save_pretrained("./debug")

# Final evaluation
final_metrics = trainer.evaluate()
print(final_metrics)
