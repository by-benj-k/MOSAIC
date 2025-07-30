"""
evaluation_procedures_2.py

This module contains a memorization evaluation of MOSAIC_DDL by prefix attack the the model and checking for the length of the extracted sequence.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
from suffix_automaton import SuffixAutomaton
from helpers_evaluation import batch_list
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import xml.etree.ElementTree as ET
from huggingface_hub import login
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import config_framework
from tqdm import tqdm
from os import getenv
import seaborn as sns
import pandas as pd
import json

# Constants (change according to your model)
model_name = config_framework.MODEL_NAME
model_path = config_framework.LORA_MODEL_MERGED_OUTPUT_DIRECTORY

# Load environment variables
load_dotenv()

# Login to huggingface
login(token=getenv("HUGGINGFACE_ACCESS_TOKEN"))


def tokenize_all_documents() -> None:
    """
    Tokenizes all documents and store tokens in file.
    """

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Compute number of documents
    number_of_documents = 0
    with open(config_framework.DOCUMENTS, "r", encoding='utf-8') as documents:
        for _ in documents:
            number_of_documents += 1

    # Traverse documents
    with open(config_framework.DOCUMENTS, "r", encoding='utf-8') as documents, open(config_framework.TOKENIZED_DOCUMENTS, "w", encoding='utf-8') as tokenized_documents:
        for _, jsonl_entry in tqdm(enumerate(documents), total=number_of_documents, desc=f"{'\033[34m'}Computing tokens for documents...{'\033[0m'}"):
            # Fetch document content and tokenize it
            document_content = json.loads(jsonl_entry)["document"]
            document_content_tokenized = tokenizer.encode(
                document_content, add_special_tokens=False)

            # Store tokens as list in .jsonl file
            tokens = {"tokens": document_content_tokenized}
            tokenized_documents.write(json.dumps(tokens) + "\n")


def pa_model(prefix_length: int) -> None:
    """
    Uses the document corpus to generate a prefix of specified length for each document, prompts it to the model and checks the document corpus for the longest common substring.

    Parameters:
        prefix_length (int): The length of the prefix to be used.
    """

    # Load model and tokenizer
    model = LLM(model_path, tokenizer=model_name, max_model_len=4096)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Set sampling parameters
    sampling_params = SamplingParams(max_tokens=1024)

    # Combine documents into singular string and construct suffix automaton
    combined_documents = ""

    with open(config_framework.DOCUMENTS, "r", encoding='utf-8') as documents:
        for jsonl_entry in documents:
            combined_documents += json.loads(jsonl_entry)["document"]

    sa = SuffixAutomaton()
    sa.build_sa(combined_documents)

    # Storage for set of prefixes
    string_prefixes = []

    # Compute number of tokenized documents
    number_of_tokenized_documents = 0
    with open(config_framework.TOKENIZED_DOCUMENTS, "r", encoding='utf-8') as documents:
        for _ in documents:
            number_of_tokenized_documents += 1

    # Iterate through pre-tokenized document corpus
    with open(config_framework.TOKENIZED_DOCUMENTS, "r", encoding='utf-8') as tokenized_documents, open(config_framework.PREFIX_EVALUATION_STATISTICS.replace(".txt", f"_{prefix_length}.txt"), "w", encoding='utf-8', buffering=1) as prefix_evaluation_statistics:
        # Iterate through documents and create prefixes
        for _, tokenized_document_entry in tqdm(enumerate(tokenized_documents), total=number_of_tokenized_documents, desc=f"{'\033[34m'}Prefix attacking documents...{'\033[0m'}"):
            # Fetch document content (from precomputed tokens)
            document_content_tokenized = json.loads(
                tokenized_document_entry)["tokens"]

            # Construct tokenized prefix
            tokenized_prefix = document_content_tokenized[:prefix_length]

            # Reconstruct string prefix for model prompt
            string_prefix = tokenizer.decode(
                tokenized_prefix, skip_special_tokens=True)

            # Add to batch
            string_prefixes.append(string_prefix)

            if len(string_prefixes) == config_framework.BATCH_SIZE:
                # Prompt the prefix to the model and check for verbatim memorization by searching the longest common substring in the document corpus
                for prefix_batch in batch_list(string_prefixes, config_framework.BATCH_SIZE):
                    # Batch next set of prefixes
                    batched_prompts = [[{"role": "system", "content": ""}, {
                        "role": "user", "content": prefix}] for prefix in prefix_batch]

                    # Prompt model with batch prefixes
                    model_outputs = model.chat(
                        batched_prompts, sampling_params, use_tqdm=True)
                    outputs = [
                        output.outputs[0].text for output in model_outputs]

                    # Search for longest common substring in document corpus
                    for o in outputs:
                        # Compute longest common substring between output and document corpus
                        lcs = sa.lcs(o)

                        # Tokenize longest common substring
                        lcs_tokenized = tokenizer.encode(
                            lcs, add_special_tokens=False)

                        # Write lcs found for the current prefix to txt file
                        prefix_evaluation_statistics.write(
                            str(lcs_tokenized) + "\n")

                # Reset for next set of tokenized documents
                string_prefixes = []

        # Handle remaining entries
        if string_prefixes:
            # Prompt the prefix to the model and check for verbatim memorization by searching the longest common substring in the document corpus
            for prefix_batch in batch_list(string_prefixes, config_framework.BATCH_SIZE):
                # Batch next set of prefixes
                batched_prompts = [[{"role": "system", "content": ""}, {
                    "role": "user", "content": prefix}] for prefix in prefix_batch]

                # Prompt model with batch prefixes
                model_outputs = model.chat(
                    batched_prompts, sampling_params, use_tqdm=True)
                outputs = [
                    output.outputs[0].text for output in model_outputs]

                # Search for longest common substring in document corpus
                for o in outputs:
                    # Compute longest common substring between output and document corpus
                    lcs = sa.lcs(o)

                    # Tokenize longest common substring
                    lcs_tokenized = tokenizer.encode(
                        lcs, add_special_tokens=False)

                    # Write lcs found for the current prefix to txt file
                    prefix_evaluation_statistics.write(
                        str(lcs_tokenized) + "\n")


def plot_evaluation_statistics(prefix_lengths: list[int]) -> None:
    """
    Runs the plotting procedures for this evaluation.

    Parameters:
        prefix_lengths (list[int]): The prefix lengths which should be used.

    Notes: Small parts of this function were developed with the help of ChatGPT.
    """

    def extract_lengths_of_sequences(prefix_length: int) -> list[int]:
        """
        Uses the prefix attack statistics file to compute an array of the lengths of the lcs sequences.

        Parameters:
            prefix_length (int): The length of the current prefix.

        Returns:
            list[int]: The list of the lcs lengths.
        """

        # Storage for lengths
        lengths_of_sequences = []

        # Traverse prefix statistics file
        with open(config_framework.PREFIX_EVALUATION_STATISTICS.replace(".txt", f"_{prefix_length}.txt"), "r", encoding='utf-8') as prefix_evaluation_statistics:
            for lcs_entry in prefix_evaluation_statistics:
                # Fetch lcs from evaluation statistics file
                lcs = eval(lcs_entry.strip())

                # Retrieve length and store it
                lengths_of_sequences.append(len(lcs))

        return lengths_of_sequences

    def accumulated_cumulative_extracted_sequence_length_distribution() -> None:
        """
        Plots a cumulative length distribution for all given prefix lengths.
        """

        # Fetch lengths of sequences
        lengths_of_sequences = []

        for prefix_length in prefix_lengths:
            lengths_of_sequences.append(
                extract_lengths_of_sequences(prefix_length))

        # Compute dataframe for each prefix length
        all_dfs = []
        for idx, sublist in enumerate(lengths_of_sequences):
            # Fetch minimum and maximum length of extracted sequences
            min_len = min(sublist)
            max_len = max(sublist)

            # Compute x-axis bins and initialize y-axis storage
            x_axs = list(range(min_len, max_len + 1))
            y_axs = []

            # Compute total number of extracted sequences
            total_number_of_sequences = len(sublist)

            # Compute number of sequences for each x-axis value
            for length in x_axs:
                number_of_sequences_at_least_length = sum(
                    1 for curr_length in sublist if curr_length >= length)
                percentage = number_of_sequences_at_least_length / total_number_of_sequences
                y_axs.append(percentage)

            # Store the values in pandas dataframe
            df = pd.DataFrame(
                {"Length of Extracted Sequence": x_axs, "Fraction of Documents": y_axs, "Prefix Length": prefix_lengths[idx]})
            all_dfs.append(df)

        # Combine all dataframes
        combined_df = pd.concat(all_dfs, ignore_index=True)

        # Set theme, set font and create subplots
        sns.set_theme(style="whitegrid",
                      font="Palatino Linotype", font_scale=0.75)
        fig, ax = plt.subplots(figsize=(14, 6))

        # Plot as lines
        sns.lineplot(x="Length of Extracted Sequence",
                     y="Fraction of Documents", hue="Prefix Length", data=combined_df, marker="o")

        # Set title of plot and fix y-axis
        ax.set_title(
            f"Cumulative Distribution of Lengths of Extracted Sequences per Prefix Length", fontsize=15)
        ax.set_xlabel("Length of Extracted Sequence", fontsize=15)
        ax.set_ylabel("Fraction of Documents", fontsize=15)
        ax.tick_params(axis="x", labelsize=15)
        ax.tick_params(axis="y", labelsize=15)
        ax.set_ylim(0, 1)

        # Create zoomed-inset plot in order to see the long tail distribution
        zoomed_inset_ax = inset_axes(
            ax, width="50%", height="50%", loc="upper right")

        # Compute/filter out values for zoomed-inset plot
        zoomed_df = combined_df[combined_df["Fraction of Documents"] <= 0.005]
        sns.lineplot(x="Length of Extracted Sequence", y="Fraction of Documents",
                     hue="Prefix Length", data=zoomed_df, marker="o", ax=zoomed_inset_ax, legend=False)

        # Zoom in on y-axis
        zoomed_inset_ax.set_ylim(
            0, 0.001)
        zoomed_inset_ax.set_xlabel("")
        zoomed_inset_ax.set_ylabel("")
        zoomed_inset_ax.tick_params(axis="x", labelsize=15)
        zoomed_inset_ax.tick_params(axis="y", labelsize=15)

        # Create lines which visualize where the zoomed part is take from in the larger context of the full graph
        mark_inset(parent_axes=ax, inset_axes=zoomed_inset_ax,
                   loc1=3, loc2=4, ec="gray", lw=1)

        # Mark last point for each prefix length
        for prefix in combined_df["Prefix Length"].unique():
            # Fetch values corresponding to current prefix length
            prefix_df = combined_df[combined_df["Prefix Length"] == prefix]

            # Fetch last x-value of prefix length curve
            last_x_value = prefix_df["Length of Extracted Sequence"].max()

            # Draw vertical line there as marker and label it
            ax.axvline(x=last_x_value, ymin=0, ymax=0.05,
                       color="black", linestyle="--")
            ax.text(x=last_x_value, y=0.05, s=str(prefix), ha="center",
                    va="bottom", fontsize=15, color="black")

        # Get legend and plot it
        ax.legend_.remove()
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center",
                   ncol=3, title="Prefix Length", title_fontsize=15, fontsize=15)

        # Adjust path
        path = config_framework.VALIDATION_EVALUATION_FOLDER
        new_path = path + \
            f"evaluate_prefix_extracted_sequence_length_distribution_all_prefix_lengths.pdf"

        # Set tight layout and save image
        plt.tight_layout(rect=[0, 0.15, 1, 0.95])
        plt.savefig(new_path, dpi=200)

    def cumulative_extracted_sequence_length_distribution(lengths_of_sequences: list[int], prefix_length: int) -> None:
        """
        Plots a cumulative length distribution for a given prefix length.

        Parameters:
            lengths_of_sequences (list[int]): The lenghts of the sequences.
            prefix_length (int): The prefix length used to extract the sequences.
        """

        # Fetch minimum and maximum length of extracted sequences
        min_len = min(lengths_of_sequences)
        max_len = max(lengths_of_sequences)

        # Compute x-axis bins and initialize y-axis storage
        x_axs = list(range(min_len, max_len + 1))
        y_axs = []

        # Compute total number of extracted sequences
        total_number_of_sequences = len(lengths_of_sequences)

        # Compute number of sequences for each x-axis value
        for length in x_axs:
            number_of_sequences_at_least_length = sum(
                1 for curr_length in lengths_of_sequences if curr_length >= length)
            percentage = number_of_sequences_at_least_length / total_number_of_sequences
            y_axs.append(percentage)

        # Set theme, set font and create subplots
        sns.set_theme(style="whitegrid",
                      font="Palatino Linotype", font_scale=0.75)
        fig, ax = plt.subplots(figsize=(14, 6))

        # Store the values in pandas dataframe
        df = pd.DataFrame(
            {"Length of Extracted Sequence": x_axs, "Fraction of Documents": y_axs})

        # Plot as lines
        sns.lineplot(x="Length of Extracted Sequence",
                     y="Fraction of Documents", data=df, marker="o")

        # Set title of plot and fix y-axis
        ax.set_title(
            f"Cumulative Distribution of Lengths of Extracted Sequences for a Prefix Length of {prefix_length} Tokens", fontsize=15)
        ax.set_xlabel("Length of Extracted Sequence", fontsize=15)
        ax.set_ylabel("Fraction of Documents", fontsize=15)
        ax.tick_params(axis="x", labelsize=15)
        ax.tick_params(axis="y", labelsize=15)
        ax.set_ylim(0, 1)

        # Create zoomed-inset plot in order to see the long tail distribution
        zoomed_inset_ax = inset_axes(
            ax, width="50%", height="50%", loc="upper right")

        # Compute/filter out values for zoomed-inset plot
        zoomed_df = df[df["Fraction of Documents"] <= 0.005]
        sns.lineplot(x="Length of Extracted Sequence", y="Fraction of Documents",
                     data=zoomed_df, marker="o", ax=zoomed_inset_ax)

        # Zoom in on y-axis
        zoomed_inset_ax.set_ylim(
            0, 0.001)
        zoomed_inset_ax.set_xlabel("")
        zoomed_inset_ax.set_ylabel("")

        # Create lines which visualize where the zoomed part is take from in the larger context of the full graph
        mark_inset(parent_axes=ax, inset_axes=zoomed_inset_ax,
                   loc1=3, loc2=4, ec="gray", lw=1)

        # Adjust path
        path = config_framework.VALIDATION_EVALUATION_FOLDER
        new_path = path + \
            f"evaluate_prefix_extracted_sequence_length_distribution_{prefix_length}.pdf"

        # Set tight layout and save image
        plt.tight_layout(rect=[0, 0.15, 1, 0.95])
        plt.savefig(new_path, dpi=200)

    # Run plotting procedures which are individual to each prefix length
    for prefix_length in prefix_lengths:
        cumulative_extracted_sequence_length_distribution(
            extract_lengths_of_sequences(prefix_length), prefix_length)

    # Run plotting procedures which is for all prefix lengths
    accumulated_cumulative_extracted_sequence_length_distribution()


def run_evaluation_procedure_2(prefix_lengths: list[int]) -> None:
    """
    Runs this evaluation procdeuren. It checks for the quantity of memorized information.

    Parameters:
        prefix_lengths (list[int]): The prefix lenghts which should be used.
    """

    # Tokenize all documents for later use
    tokenize_all_documents()

    for prefix_length in prefix_lengths:
        # Prompt model and store statistics
        pa_model(prefix_length)

    # Plot statistics
    plot_evaluation_statistics(prefix_lengths)
