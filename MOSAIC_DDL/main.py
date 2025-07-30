"""
main.py

This module contains the main function of MOSAIC_DDL.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from generator import Generator
import evaluation_procedures_1
import evaluation_procedures_2
import finetuning_procedures
import validation_procedures
import config_framework
import datetime
import sys


def main() -> None:
    """
    Runs MOSAIC_DDL.

    Before you run the framework, please make sure to adjust the following configuration variables in config_framework.py to suitable values for your machine:
    - MODEL_NAME (the name of the model you want to use)
    - LORA_MODEL_OUTPUT_DIRECTORY (the directory to store the lora weights)
    - LORA_MODEL_LOGGING_DIRECTORY (the directory to store the training log)
    - LORA_MODEL_FINAL_OUTPUT_DIRECTORY (the directory marking the final checkpoint of the training procedure and hence the final model)
    - LORA_MODEL_MERGED_OUTPUT_DIRECTORY (the directory to store the merged model)

    Feel free to also adjust the model used through the OpenRouter API.

    Please note that the fine-tuning process can be highly individual based on the model and other factors. The provided code simply acts as an example which ran on our system.

    Also, do not forget to add your OpenRouter API Key and potentially the Hugging Face access token to a .env file in the current working directory.
    """

    # General information
    print(
        f"{'\033[41m'}Started Running MOSAIC_DDL: {datetime.datetime.now()}{'\033[0m'}")

    # Create framework by loading configuration
    print(f"{'\033[31m'}Creating Framework...{'\033[0m'}")
    framework = Generator(config_framework.CONFIG)

    # Try loading the sampling procedures module or create it and then load it
    print(f"{'\033[31m'}Loading Sampling Procedures...{'\033[0m'}")
    try:
        from sampling_procedures import register_all_sampling_procedures
    except ImportError:
        print("WARNING: The sampling procedure file has not yet been created. it is now created and the execution of the framework is aborted so that the empty function stubs can be implemented. --- Depending on the size/complexity of your sampling functions, it may make sense to outsource certain parts to other files and import them into the sampling_procedures.py file.\n")
        framework.generate_sampling_procedure_stubs()
        sys.exit("FRAMEWORK EXECUTION ABORTED")

    # Register the sampling procedures
    print(f"{'\033[31m'}Registering Sampling Procedures...{'\033[0m'}")
    register_all_sampling_procedures(framework)

    # Generate seeds for specified domains
    print(f"{'\033[31m'}Generating Seeds...{'\033[0m'}")
    """framework.generate_seeds(
        ["occasion", "medical", "financial", "legal", "educational", "social"])"""

    # Generate documents for specified domains
    print(f"{'\033[31m'}Generating Documents...{'\033[0m'}")
    """framework.generate_documents(
        ["occasion", "medical", "financial", "legal", "educational", "social"])"""

    # Run validation procedures
    print(f"{'\033[31m'}Running Validation Procedures...{'\033[0m'}")
    """validation_procedures.run_validation_procedures()"""

    # Run finetuning procedures
    print(f"{'\033[31m'}Running Fine-Tuning Procedures...{'\033[0m'}")
    """finetuning_procedures.finetune_model()
    finetuning_procedures.load_and_merge_model()"""

    # Run evaluation procedures
    print(f"{'\033[31m'}Running Evaluation Procedures...{'\033[0m'}")
    """evaluation_procedures_1.run_evaluation_procedure_1(
        ["occasion", "medical", "financial", "legal", "educational", "social"])"""
    """evaluation_procedures_2.run_evaluation_procedure_2([15, 30, 45])"""

    # General information
    print(
        f"{'\033[41m'}Finished Running MOSAIC_DDL: {datetime.datetime.now()}{'\033[0m'}")


if __name__ == "__main__":
    main()
