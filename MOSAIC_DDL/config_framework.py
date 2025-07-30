"""
config_framework.py

This module contains the parameters of MOSAIC_DDL that can be adjusted.

Author: Benjamin Koch
Date: July 2025
"""

# Seed generation parameters
EII_LEVEL_MAPPING = {"low": 0, "moderate": 1, "high": 2}

# Document generation parameters
MODEL = "openai/gpt-4o-mini"
MAXIMUM_NUMBER_OF_CONCURRENT_REQUESTS = 10

# Configuration file path
CONFIG = "MOSAIC_DDL/configurations/configuration.xml"

# Output file path
SEEDS = "MOSAIC_DDL/generations/seeds.jsonl"
BLANK_SEEDS = "MOSAIC_DDL/generations/blank_seeds.jsonl"
DOCUMENTS = "MOSAIC_DDL/generations/documents.jsonl"
QUESTIONS = "MOSAIC_DDL/generations/questions.jsonl"
TOKENIZED_DOCUMENTS = "MOSAIC_DDL/generations/tokenized_documents.jsonl"
VALIDATION_EVALUATION_FOLDER = "MOSAIC_DDL/results/"

QUESTION_EVALUATION_STATISTICS = "MOSAIC_DDL/results/question_evaluation_statistics.txt"
PREFIX_EVALUATION_STATISTICS = "MOSAIC_DDL/results/prefix_evaluation_statistics.txt"

# Sampling procedures file path
SAMPLING_PROCEDURES = "MOSAIC_DDL/sampling_procedures.py"

# Fine-tuning and Evaluation parameters
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"
LORA_MODEL_OUTPUT_DIRECTORY = "PLACEHOLDER"
LORA_MODEL_LOGGING_DIRECTORY = "PLACEHOLDER"
LORA_MODEL_FINAL_OUTPUT_DIRECTORY = "PLACEHOLDER"
LORA_MODEL_MERGED_OUTPUT_DIRECTORY = "PLACEHOLDER"
BATCH_SIZE = 128
