"""
finetuning_procedures.py

This module contains the finetuning script and the loading/merging script using LoRA of MOSAIC_DDL. Please note that this procedure might need to be adapted to your available computing power or the model you want to use.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, DataCollatorForLanguageModeling, BitsAndBytesConfig, Trainer
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from huggingface_hub import login
from datasets import load_dataset
from dotenv import load_dotenv
from peft import PeftModel
import config_framework
from os import getenv

# Constants (change according to your model)
model_name = config_framework.MODEL_NAME

# Load environment variables
load_dotenv()

# Login to huggingface
login(token=getenv("HUGGINGFACE_ACCESS_TOKEN"))


def finetune_model() -> None:
    """
    This function finetunes the specified model. Adjustments to the following parameters/variables are necessary.

    - data_files: Path to the generated documents file.
    - output_dir: Path to the result of the fine-tuning process.
    - logging_dir: Path to the logs of the fine-tuning process.

    Additional changes depending on your chosen model might be necessary.
    """

    # Load bitsandbytes config
    bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                    bnb_4bit_compute_dtype="float16", bnb_4bit_use_double_quant=False)

    # Load LoRA configuration
    peft_config = LoraConfig(
        r=64, lora_alpha=16, lora_dropout=0, task_type="CAUSAL_LM", target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])

    # Load the model and prepare it for peft finetuning
    model = AutoModelForCausalLM.from_pretrained(
        model_name, quantization_config=bnb_config, device_map="auto")

    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, peft_config)

    # Load the tokenized corresponding to the model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    # Load the dataset
    dataset = load_dataset(
        "json", data_files=config_framework.DOCUMENTS, split="train")

    # Define tokenization function and tokenize the dataset

    def tokenize(examples):
        inputs = tokenizer(examples["document"])
        return inputs

    tokenized_dataset = dataset.map(
        tokenize, batched=True, remove_columns=["document"])

    # Instantiate data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=False)

    # Specify the training arguments
    trainings_arguments = TrainingArguments(output_dir=config_framework.LORA_MODEL_OUTPUT_DIRECTORY, save_strategy="steps", save_steps=500, save_total_limit=1,
                                            per_device_train_batch_size=2, num_train_epochs=1, learning_rate=5e-4, weight_decay=0.01, logging_dir=config_framework.LORA_MODEL_LOGGING_DIRECTORY, logging_steps=50, report_to="none", fp16=True, bf16=False)

    # Set up trainer
    trainer = Trainer(model=model, args=trainings_arguments,
                      train_dataset=tokenized_dataset, processing_class=tokenizer, data_collator=data_collator)

    # Train the model
    trainer.train()


def load_and_merge_model() -> None:
    """
    This function loads and merges the LoRA adapter weights with the "original" model. Adjustments to the following parameters/variables are necessary.

    - Path in PeftModel.from_pretrained: The path to the output directory on the fine-tuning process. This is not exactly the same path, since an additional directory is created in between for the checkpoints.
    - Path in model.save_pretrained: The path where you want the fully merged model stored.

    Additional changes depending on your chosen model might be necessary.
    """

    base_model = AutoModelForCausalLM.from_pretrained(
        model_name, device_map="auto")
    model = PeftModel.from_pretrained(
        base_model, config_framework.LORA_MODEL_FINAL_OUTPUT_DIRECTORY)
    model = model.merge_and_unload()
    model.save_pretrained(
        config_framework.LORA_MODEL_MERGED_OUTPUT_DIRECTORY)
