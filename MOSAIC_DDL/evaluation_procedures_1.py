"""
evaluation_procedures_1.py

This module contains a memorization evaluation of MOSAIC_DDL by questioning the model and checking for correctness.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from itertools import chain, combinations
from helpers_evaluation import batch_list
from vllm import LLM, SamplingParams
import xml.etree.ElementTree as ET
from huggingface_hub import login
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from rapidfuzz import fuzz
from typing import Union
from pathlib import Path
import config_framework
import seaborn as sns
from tqdm import tqdm
from os import getenv
import pandas as pd
import numpy as np
import math
import json
import sys


# Constants (change according to your model)
model_name = config_framework.MODEL_NAME
model_path = config_framework.LORA_MODEL_MERGED_OUTPUT_DIRECTORY

# Load environment variables
load_dotenv()

# Login to huggingface
login(token=getenv("HUGGINGFACE_ACCESS_TOKEN"))


def compute_domain_to_text_types_to_number_of_seeds_and_documents() -> dict:
    """
    Computes a dictionary mapping domain id to a dictionary mapping text types to tuple (number of seed, number of documents per seed)

    Returns:
        dict: The computed dictionary.
    """

    # Compute dictionary mapping domain id to dictionary mapping texttypes to tuple (number of seed, number of documents per seed)
    domain_to_text_types_to_number_of_seeds_and_documents = {}
    config_tree = ET.parse(config_framework.CONFIG)
    config_root = config_tree.getroot()

    for domain in config_root.find("domains").findall("domain"):
        text_types = [texttype.get("id") for texttype in domain.find(
            "texttypes").findall("texttype")]
        text_types_number_of_seeds = [texttype.get(
            "number_of_seeds") for texttype in domain.find("texttypes").findall("texttype")]
        text_types_documents_per_seed = [texttype.get(
            "documents_per_seed") for texttype in domain.find("texttypes").findall("texttype")]

        domain_to_text_types_to_number_of_seeds_and_documents[domain.get("id")] = {
            key: (int(value1), int(value2)) for key, value1, value2 in zip(text_types, text_types_number_of_seeds, text_types_documents_per_seed) if int(value1) > 0}

    return domain_to_text_types_to_number_of_seeds_and_documents


def make_hashable(value: Union[str, int, list[str]]) -> Union[str, int, tuple]:
    """
    Converts an unhashable list into a tuple which is hashable.

    Parameters:
        value (Union[str, int, list[str]]): The input object.

    Returns:
        Union[str, int, tuple]: Either returns element unchanged or converts list to tuple.
    """

    if isinstance(value, list):
        return tuple(value)
    return value


def compute_keys_and_values_of_seed(inputDict: dict) -> set[tuple[str, Union[str, int, list[str]]]]:
    """
    Computes the set of all keys and values of a potentially nested dictionary structure.

    Parameters:
        inputDict (dict): The dictionary of which we want to fetch all keys.

    Returns:
        set[tuple[str, Union[str, int, list[str]]]]: The set containing all keys.
    """

    # Storage for keys
    keys = set()

    if isinstance(inputDict, dict):
        for key, value in inputDict.items():
            if key == "domain" or key == "text_type":
                continue

            if isinstance(value, list):
                list_has_dict = False
                for subDict in value:
                    if isinstance(subDict, dict):
                        keys.update(compute_keys_and_values_of_seed(subDict))
                        list_has_dict = True

                if not list_has_dict:
                    keys.add((key, make_hashable(value)))
            else:
                keys.add((key, make_hashable(value)))

    return keys


def deduplicate_list(list: list) -> list:
    """
    Takes in a list and returns the same list without duplicate entries while preserving the order.

    Parameters:
        list (list): The input list.

    Returns:
        list: The deduplicated list.
    """

    # Storage for final list and for set keeping track of entries
    seen = set()
    deduplicated_list = []

    for s in list:
        if s not in seen:
            seen.add(s)
            deduplicated_list.append(s)

    return deduplicated_list


def construct_questions() -> None:
    """
    This function constructs a catalogue of questions for all domains (the domain selection will happen at a later stage). The questions are constructed based on the information that can be reconstructed from the blank seeds.
    """

    # Compute a  dictionary mapping domain to text types and text types to number of seeds and number of documents per seed of that text type.
    domain_to_text_types_to_number_of_seeds_and_documents = compute_domain_to_text_types_to_number_of_seeds_and_documents()

    # Fetch actual frequency probabilities for all attributes
    config_tree = ET.parse(config_framework.CONFIG)
    config_root = config_tree.getroot()
    frequencies = {}
    for domain in config_root.find("domains").findall("domain"):
        for domain_attribute in domain.findall("domainAttribute"):
            frequencies[domain_attribute.get(
                "id")] = float(domain_attribute.get("frequency"))
        for entity in domain.find("entities").findall("entity"):
            for entity_attribute in entity.findall("entityAttribute"):
                frequencies[entity_attribute.get(
                    "id")] = float(entity_attribute.get("frequency"))

    # Traverse seeds
    with open(config_framework.SEEDS, "r", encoding='utf-8') as seeds, open(config_framework.BLANK_SEEDS, "r", encoding='utf-8') as blank_seeds, open(config_framework.QUESTIONS, "w", encoding='utf-8', buffering=1) as questions_file:
        # Load first seed
        seed = seeds.readline()
        if seed != "":
            seed = json.loads(seed)
        else:
            return

        # Seed counter (index)
        seed_idx = 0

        # Instantiate iterator for looping over blank seeds
        blank_seeds_iter = iter(blank_seeds)

        while True:
            for texttype in domain_to_text_types_to_number_of_seeds_and_documents[seed["domain"]]:
                for _ in range(domain_to_text_types_to_number_of_seeds_and_documents[seed["domain"]][texttype][0]):
                    # Retrieve all key/value pairs from original seed
                    current_seed_entry = compute_keys_and_values_of_seed(seed)
                    remaining_seed_entries = current_seed_entry.copy()

                    # Fetch domain attributes with frequency 1.0 of domain corresponding to the current seed
                    domain_attributes = set()
                    for domain in config_root.find("domains").findall("domain"):
                        if domain.get("id") == seed["domain"]:
                            for domain_attribute in domain.findall("domainAttribute"):
                                if float(domain_attribute.get("frequency")) == 1.0:
                                    domain_attributes.add(
                                        domain_attribute.get("id"))

                    # Check whether there is at least one domain attribute with frequency 1.0, otherwise abort
                    if len(domain_attributes) == 0:
                        print(
                            f"WARNING: No domain attribute with frequency 1.0 has been specified for the domain \"{seed["domain"]}\". In order to use this evaluation procedure, there must be at least one such attribute which can be given to the model as base information. Please provide such an attribute and restart the evaluation.\n")
                        sys.exit("FRAMEWORK EXECUTION ABORTED")

                    # Compute power set of domain attributes
                    domain_attributes_list = list(domain_attributes)
                    power_set_iterator = chain.from_iterable(
                        combinations(domain_attributes_list, size) for size in range(1, len(domain_attributes_list) + 1))
                    domain_attributes_power_set_list = [list(subset)
                                                        for subset in power_set_iterator]

                    domain_attributes_power_set_list = [
                        sorted(subset) for subset in domain_attributes_power_set_list]
                    domain_attributes_power_set_list.sort(
                        key=lambda subset: (len(subset), subset))

                    for _ in range(domain_to_text_types_to_number_of_seeds_and_documents[seed["domain"]][texttype][1]):
                        try:
                            blank_seed_entry = compute_keys_and_values_of_seed(
                                json.loads(next(blank_seeds_iter)))

                            current_seed_entry.difference_update(
                                blank_seed_entry)
                        except StopIteration:
                            break

                    # Compute key/value pairs which are included in the union of the blank seeds
                    remaining_seed_entries.difference_update(
                        current_seed_entry)

                    # Iterate through key/value pairs and construct question for each key
                    questions = []
                    for (key, _) in remaining_seed_entries:
                        # Compute questions
                        for q_idx, question_base_information in enumerate(domain_attributes_power_set_list):
                            # Skip question creation if attribute which is being asked about is in base information
                            if key in question_base_information:
                                continue

                            # Fetch values for question base information
                            question_base_information_keys_and_values = {
                                (key, value) for key, value in remaining_seed_entries if key in question_base_information}

                            # Skip question creation if base information values were never mentioned in union of all blank seeds created from one seed
                            if len(question_base_information_keys_and_values) == 0:
                                continue

                            # Create question name
                            question_name = "q_" + \
                                str(q_idx) + "_" + \
                                str(frequencies[key]) + "_" + str(key)
                            questoin_base_information_strings = [
                                f"{key}={value}" for key, value in question_base_information_keys_and_values]
                            question = question_name + ":Given the following information: " + \
                                "; ".join(questoin_base_information_strings) + \
                                ". What is the value of \"" + str(key) + "\"?"

                            questions.append(question)

                    # Deduplicate list
                    questions = deduplicate_list(questions)

                    # Assemble dictionary for .jsonl file (if multiple questions for the same attribute - might not be the same entity - exist, they are merged into one; during the correctness check however, we look for all correct answers)
                    questions_dict = {f"questions_seed_{seed_idx}": questions}

                    # Add domain identifier
                    questions_dict["domain"] = seed["domain"]

                    # Write questions to .jsonl file
                    questions_file.write(json.dumps(questions_dict) + "\n")

                    # Update seed index
                    seed_idx += 1

                    # Load next seed
                    seed = seeds.readline()
                    if seed != "":
                        seed = json.loads(seed)
                    else:
                        return


def get_seed_by_index(seed_idx: int) -> dict[str, Union[str, int]]:
    """
    Returns the i-th seed from a .jsonl file.

    Parameters:
        seed_idx (int): The row to extract.

    Returns:
        dict[str, Union[str, int]]: The .jsonl entry.
    """

    # Iterate through file and count lines
    with open(config_framework.SEEDS, "r", encoding='utf-8') as seeds:
        for idx, jsonl_entry in enumerate(seeds):
            if idx == seed_idx:
                return json.loads(jsonl_entry)


def get_attribute_values(attribute_name: str, dictionary: dict) -> set[str]:
    """
    Uses an attribute name to fetch all values corresponding to the attribute name in a seed.

    Parameters:
        attribute_name (str): The name of the attribute (key).
        jsonl_entry (dict): The jsonl entry to search through.

    Returns:
        set[str]: A set with all corrsponding values.
    """

    # Storage for answers
    attributes_values = set()

    for key, value in dictionary.items():
        if key == attribute_name:
            if isinstance(value, list):
                # If attribute is a list of strings
                attributes_values.update(str(v) for v in value)
            else:
                attributes_values.update({value})
        elif isinstance(value, list):
            for sub_dictionary in value:
                if isinstance(sub_dictionary, dict):
                    # If value is a list of dictionaries, as for an entity
                    attributes_values.update(get_attribute_values(
                        attribute_name, sub_dictionary))

    return attributes_values


def qa_model(domain_name: str) -> None:
    """
    Prompts model defined at the top of the file with the questions created for each seed and stores some statistics about how well facts are memorized (answered correctly). It does this for the seeds of the specified domain.

    Parameters:
        domain (str): The domain for which this evaluation procedure should be run.
    """

    # Count number of total questions/seeds
    number_of_question_seeds = 0
    with open(config_framework.QUESTIONS, "r", encoding='utf-8') as question_file:
        for _ in question_file:
            number_of_question_seeds += 1

    # Load model
    model = LLM(model_path, tokenizer=model_name, max_model_len=4096)

    # Set sampling parameters
    sampling_params = SamplingParams(max_tokens=256)

    # Load frequencies and attribute names for logging setup
    config_tree = ET.parse(config_framework.CONFIG)
    config_root = config_tree.getroot()
    frequencies = set()
    attributes = set()
    number_of_question_types = 0
    for domain in config_root.find("domains").findall("domain"):
        if domain.get("id") == domain_name:
            for domain_attribute in domain.findall("domainAttribute"):
                frequencies.add(float(domain_attribute.get("frequency")))
                attributes.add(domain_attribute.get("id"))

                if float(domain_attribute.get("frequency")) == 1.0:
                    number_of_question_types += 1
            for entity in domain.find("entities").findall("entity"):
                for entity_attribute in entity.findall("entityAttribute"):
                    frequencies.add(float(entity_attribute.get("frequency")))
                    attributes.add(entity_attribute.get("id"))

    # Power set size without the empty set (number of attributes providing base information)
    number_of_question_types = 2 ** number_of_question_types - 1

    # Storage for logging
    zero_dictionary_frequency = {str(key): 0 for key in frequencies}
    questions_asked_frequency = [
        zero_dictionary_frequency.copy() for _ in range(number_of_question_types)]
    questions_answered_correctly_frequency = [
        zero_dictionary_frequency.copy() for _ in range(number_of_question_types)]

    zero_dictionary_attribute = {str(key): 0 for key in attributes}
    questions_asked_attribute = zero_dictionary_attribute.copy()
    questions_answered_correctly_attribute = zero_dictionary_attribute.copy()

    # Iterate through questions of seeds, prompt model and store some statistics about how many questions were answered correctly
    with open(config_framework.QUESTIONS, "r", encoding='utf-8') as question_file:
        for seed_idx, question_entry in tqdm(enumerate(question_file), total=number_of_question_seeds, desc=f"{'\033[34m'}Evaluating model...{'\033[0m'}"):
            # Load list of questions (all questions of one seed) and proceed if domain matches
            data = json.loads(question_entry)

            if data["domain"] != domain_name:
                continue

            question_list = data[f"questions_seed_{seed_idx}"]

            # Fetch original seed being questioned in the current iteration
            seed = get_seed_by_index(seed_idx)

            for question_batch in batch_list(question_list, config_framework.BATCH_SIZE):
                # Batch next set of questions
                batched_prompts = [[{"role": "system", "content": "You are a knowledgeable, helpful and concise assistant. If possible, answer in a single word, otherwise in as few words as possible. If you do not posses knowledge of the answer, answer with \"unknown\"."}, {
                    "role": "user", "content": question.split(":", 1)[1]}] for question in question_batch]

                # Extract attribute names from batch
                question_numbers = [int(question.split(":")[0].split("_", 3)[
                                        1]) for question in question_batch]
                question_attribute_frequencies = [float(question.split(":")[0].split("_", 3)[
                                                        2]) for question in question_batch]
                question_attribute_names = [question.split(":")[0].split(
                    "_", 3)[3] for question in question_batch]

                # Prompt model with batched questions
                model_outputs = model.chat(
                    batched_prompts, sampling_params, use_tqdm=True)
                outputs = [output.outputs[0].text for output in model_outputs]

                # Fetch correct answers given the question attribute names
                correct_answers = [get_attribute_values(
                    attribute_name, seed) for attribute_name in question_attribute_names]

                # Check correctness of the outputs by fuzzy matching the expected correct answers
                correctness = []
                for answers, output in zip(correct_answers, outputs):
                    correctness_evaluation = all(fuzz.partial_ratio(
                        str(answer).lower(), str(output).lower()) >= 95 for answer in answers)
                    correctness.append(correctness_evaluation)

                # Update statistics
                for idx in range(len(batched_prompts)):
                    questions_asked_frequency[question_numbers[idx]][str(
                        question_attribute_frequencies[idx])] += 1
                    questions_asked_attribute[question_attribute_names[idx]] += 1

                    if correctness[idx] == True:
                        questions_answered_correctly_frequency[question_numbers[idx]][str(
                            question_attribute_frequencies[idx])] += 1
                        questions_answered_correctly_attribute[question_attribute_names[idx]] += 1

                # Write current evaluation numbers to txt file
                with open(config_framework.QUESTION_EVALUATION_STATISTICS.replace(".txt", f"_{domain_name}.txt"), "w", encoding='utf-8', buffering=1) as question_evaluation_statistics:
                    question_evaluation_statistics.write(
                        str(questions_asked_frequency) + "\n")
                    question_evaluation_statistics.write(
                        str(questions_answered_correctly_frequency) + "\n")
                    question_evaluation_statistics.write(
                        str(questions_asked_attribute) + "\n")
                    question_evaluation_statistics.write(
                        str(questions_answered_correctly_attribute) + "\n")


def plot_evaluation_statistics(domain_ids: str) -> None:
    """
    Runs the plotting procedures for this evaluation.

    Parameters:
        domain_ids (list[str]): The domain ids (names) for which this evaluation procedure should be run.

    Notes: Small parts of this function were developed with the help of ChatGPT.
    """

    def accumulated_bar_plot_correct_answers_by_frequency() -> None:
        """
        Open all question evaluation statistics files and accumulates each one separately into one dictionary and then these resulting dictionaries also across domains into one dictionary. Then bar plots the number of correct answers.
        """

        # Create pattern for file search
        base_path = Path(config_framework.QUESTION_EVALUATION_STATISTICS)
        directory = base_path.parent
        stem = base_path.stem
        suffix = base_path.suffix
        pattern = f"{stem}_*{suffix}"

        # Accumulate dictionaries of all domains
        accumulate_dictionaries_by_domain_questions_asked_frequency = []
        accumulate_dictionaries_by_domain_questions_answered_correctly_frequency = []

        # Loop through all files matching the pattern
        for file in directory.glob(pattern):
            with open(file, "r", encoding='utf-8') as f:
                f_full_file = f.readlines()
                f_questions_asked_frequency = eval(f_full_file[0].strip())
                f_questions_answered_correctly_frequency = eval(
                    f_full_file[1].strip())

                # Temporary result storage to sum up each list of dictionaries
                temp_questions_asked_frequency = {}
                temp_questions_answered_correctly_frequency = {}

                # Sum up dictionaries separately and store them in lists
                for dictionary in f_questions_asked_frequency:
                    for key, value in dictionary.items():
                        temp_questions_asked_frequency[key] = temp_questions_asked_frequency.get(
                            key, 0) + value
                accumulate_dictionaries_by_domain_questions_asked_frequency.append(
                    temp_questions_asked_frequency)

                for dictionary in f_questions_answered_correctly_frequency:
                    for key, value in dictionary.items():
                        temp_questions_answered_correctly_frequency[key] = temp_questions_answered_correctly_frequency.get(
                            key, 0) + value
                accumulate_dictionaries_by_domain_questions_answered_correctly_frequency.append(
                    temp_questions_answered_correctly_frequency)

        # Sum up accumulated dictionaries
        accumulated_dictionary_questions_asked_frequency = {}
        accumulated_dictionary_questions_answered_correctly_frequency = {}

        for dictionary in accumulate_dictionaries_by_domain_questions_asked_frequency:
            for key, value in dictionary.items():
                accumulated_dictionary_questions_asked_frequency[key] = accumulated_dictionary_questions_asked_frequency.get(
                    key, 0) + value

        for dictionary in accumulate_dictionaries_by_domain_questions_answered_correctly_frequency:
            for key, value in dictionary.items():
                accumulated_dictionary_questions_answered_correctly_frequency[key] = accumulated_dictionary_questions_answered_correctly_frequency.get(
                    key, 0) + value

        # Sort dictionaries according to frequency in decreasing order
        accumulated_dictionary_questions_asked_frequency = dict(sorted(
            accumulated_dictionary_questions_asked_frequency.items(), key=lambda item: float(item[0]), reverse=True))
        accumulated_dictionary_questions_answered_correctly_frequency = dict(sorted(
            accumulated_dictionary_questions_answered_correctly_frequency.items(), key=lambda item: float(item[0]), reverse=True))

        # Comptue lists of values
        accumulated_dictionary_questions_asked_frequency_list = [
            v for v in accumulated_dictionary_questions_asked_frequency.values()]
        accumulated_dictionary_questions_answered_correctly_frequency_list = [
            v for v in accumulated_dictionary_questions_answered_correctly_frequency.values()]
        questions_answered_correctly_frequency_percentage_list = []

        for qacfl, qafl in zip(accumulated_dictionary_questions_answered_correctly_frequency_list, accumulated_dictionary_questions_asked_frequency_list):
            if qafl == 0.0:
                questions_answered_correctly_frequency_percentage_list.append(
                    0.0)
                continue

            questions_answered_correctly_frequency_percentage_list.append(
                qacfl/qafl)

        # Set theme, set font and create subplot
        sns.set_theme(style="whitegrid", font="Palatino Linotype")
        fig, axs = plt.subplots(figsize=(14, 6))

        # Store these values in a pandas dataframe
        df = pd.DataFrame({"Frequency": list(accumulated_dictionary_questions_asked_frequency.keys(
        )), "Correct": questions_answered_correctly_frequency_percentage_list})

        # Set correct layer of the bars
        axs.bar(df["Frequency"], df["Correct"], label="Correct", color="green")

        # Set title, axis labels and limits
        axs.set_title(
            "Questions Answered Correctly Grouped by Frequency", fontsize=15)
        axs.set_ylabel("Questions Answered Correctly", fontsize=15)
        axs.set_xlabel("Attribute Frequency", fontsize=15)
        axs.tick_params(axis="x", labelsize=15)
        axs.tick_params(axis="y", labelsize=15)
        axs.set_ylim(0, 1)

        # Draw percentages for the individual bar plots
        for bar_idx in range(len(accumulated_dictionary_questions_asked_frequency)):
            # Compute y-axis midpoint for the bars
            y_answered_correctly = questions_answered_correctly_frequency_percentage_list[
                bar_idx] / 2

            # Set text inside bars
            axs.text(bar_idx, y_answered_correctly,
                     f"{(questions_answered_correctly_frequency_percentage_list[bar_idx])*100:.0f}%", ha="center", va="center", color="black", fontsize=12)

        # Get legend from first subplot and plot it in the center for all subplots (since it is the same legend for all subplots)
        handles, labels = axs.get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=15)

        # Adjust path
        path = config_framework.VALIDATION_EVALUATION_FOLDER
        new_path = path + "evaluate_questions_correct_by_frequency_all_domains.pdf"

        # Set tight layout and save image
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        plt.savefig(new_path, dpi=200)

    def bar_plot_correct_answers_by_frequency() -> None:
        """
        Plots a bar chart for each subset of the domain attribute power set used for questioning and groups them according to frequency. The bars themselves represent the number of correctly answered questions.
        """

        # Compute set of base information attributes used for plot labelling
        config_tree = ET.parse(config_framework.CONFIG)
        config_root = config_tree.getroot()
        domain_attributes = set()
        for domain in config_root.find("domains").findall("domain"):
            if domain.get("id") == domain_name:
                for domain_attribute in domain.findall("domainAttribute"):
                    if float(domain_attribute.get("frequency")) == 1.0:
                        domain_attributes.add(
                            domain_attribute.get("id"))

        domain_attributes_list = list(domain_attributes)
        power_set_iterator = chain.from_iterable(
            combinations(domain_attributes_list, size) for size in range(1, len(domain_attributes_list) + 1))
        domain_attributes_power_set_list = [list(subset)
                                            for subset in power_set_iterator]

        domain_attributes_power_set_list = [
            sorted(subset) for subset in domain_attributes_power_set_list]
        domain_attributes_power_set_list.sort(
            key=lambda subset: (len(subset), subset))

        # Determine the number of plots and the corresponding grid size
        number_of_plots = len(questions_asked_frequency)
        number_of_columns = math.ceil(math.sqrt(number_of_plots))
        number_of_rows = math.ceil(number_of_plots / number_of_columns)

        # Set theme, set font and create subplots
        sns.set_theme(style="whitegrid", font="Palatino Linotype")
        fig, axs = plt.subplots(number_of_rows, number_of_columns, figsize=(
            number_of_columns * 7, number_of_rows * 5))
        axs = axs.flatten()

        # Plot actual content as bar plots, where each bar consist of a correct section and the bars are separated according to frequency
        for plot_idx in range(number_of_plots):
            # Fetch axis and extract dictionaries
            ax = axs[plot_idx]
            questions_asked_frequency_dictionary = questions_asked_frequency[plot_idx]
            questions_answered_correctly_frequency_dictionary = questions_answered_correctly_frequency[
                plot_idx]

            # Sort dictionaries according to frequency in decreasing order
            questions_asked_frequency_dictionary = dict(sorted(
                questions_asked_frequency_dictionary.items(), key=lambda item: float(item[0]), reverse=True))
            questions_answered_correctly_frequency_dictionary = dict(sorted(
                questions_answered_correctly_frequency_dictionary.items(), key=lambda item: float(item[0]), reverse=True))

            # Convert to lists and compute percentages by element wise divison
            questions_asked_frequency_list = np.array(
                [v for v in questions_asked_frequency_dictionary.values()])
            questions_answered_correctly_frequency_list = np.array(
                [v for v in questions_answered_correctly_frequency_dictionary.values()])
            questions_answered_correctly_frequency_percentage_list = []

            for qacfl, qafl in zip(questions_answered_correctly_frequency_list, questions_asked_frequency_list):
                if qafl == 0.0:
                    questions_answered_correctly_frequency_percentage_list.append(
                        0.0)
                    continue

                questions_answered_correctly_frequency_percentage_list.append(
                    qacfl/qafl)

            # Store these values in a pandas dataframe
            df = pd.DataFrame({"Frequency": list(questions_asked_frequency_dictionary.keys(
            )), "Correct": questions_answered_correctly_frequency_percentage_list})

            # Set correct layer of the bars
            ax.bar(df["Frequency"], df["Correct"],
                   label="Correct", color="green")

            # Set title, axis labels and limits
            ax.set_title(
                f"Attribute-Set:\n {",\n".join(
                    domain_attributes_power_set_list[plot_idx])}", fontsize=15)
            ax.set_ylabel("Questions Answered Correctly", fontsize=15)
            ax.set_xlabel("Attribute Frequency", fontsize=15)
            ax.tick_params(axis="x", labelsize=15)
            ax.tick_params(axis="y", labelsize=15)
            ax.set_ylim(0, 1)

            # Draw percentages for the individual bar plots
            for bar_idx in range(len(questions_asked_frequency_dictionary)):
                # Compute y-axis midpoint for the bars
                y_answered_correctly = questions_answered_correctly_frequency_percentage_list[
                    bar_idx] / 2

                # Set text inside bars
                ax.text(bar_idx, y_answered_correctly,
                        f"{(questions_answered_correctly_frequency_percentage_list[bar_idx])*100:.0f}%", ha="center", va="center", color="black", fontsize=12)

        # Remove empty axes
        for ax in axs[number_of_plots:]:
            fig.delaxes(ax)

        # Set title for full plot png
        fig.suptitle(
            "Questions Answered Correctly Grouped by Base-Information-Attribute-Sets and Frequency", fontsize=15)

        # Get legend from first subplot and plot it in the center for all subplots (since it is the same legend for all subplots)
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=15)

        # Adjust path
        path = config_framework.VALIDATION_EVALUATION_FOLDER
        new_path = path + \
            f"evaluate_questions_correct_by_frequency_{domain_name}.pdf"

        # Set tight layout and save image
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        plt.savefig(new_path, dpi=200)

    def bar_plot_correct_answers_by_attribute() -> None:
        """
        Plots a bar chart containing a bar for every attribute. The bars themselves represent the number of correctly answered questions.
        """

        # Set theme, set font and create subplot
        sns.set_theme(style="whitegrid", font="Palatino Linotype")
        fig, axs = plt.subplots(figsize=(14, 6))

        # Convert to lists and compute percentages by element wise division
        questions_asked_attribute_list = np.array(
            [v for v in questions_asked_attribute.values()])
        questions_answered_correctly_attribute_list = np.array(
            [v for v in questions_answered_correctly_attribute.values()])
        questions_answered_correctly_attribute_percentage_list = []

        attribute_names = [k for k in questions_asked_attribute.keys()]

        for qacal, qaal in zip(questions_answered_correctly_attribute_list, questions_asked_attribute_list):
            if qaal == 0.0:
                questions_answered_correctly_attribute_percentage_list.append(
                    0.0)
                continue
            questions_answered_correctly_attribute_percentage_list.append(
                qacal/qaal)

        # Store these values in pandas dataframe
        df = pd.DataFrame({"Attribute": attribute_names,
                          "Correct": questions_answered_correctly_attribute_percentage_list})

        # Sort values in decreasing order of attribute names
        df = df.sort_values(by="Attribute")

        # Set correct layer of the bars
        axs.bar(df["Attribute"], df["Correct"], label="Correct", color="green")

        # Set title and axis labels
        axs.set_title(
            "Questions Answered Correctly Grouped by Attribute Names", fontsize=15)
        axs.set_ylabel("Questions Answered Correctly", fontsize=15)
        axs.set_xlabel("Attribute Name", fontsize=15)
        axs.set_xticklabels(df["Attribute"], rotation=45, ha="right")
        axs.tick_params(axis="y", labelsize=15)
        axs.set_ylim(0, 1)
        # axs.set_yscale("log")

        # Get legend from subplot and plot it in the center
        handles, labels = axs.get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=15)

        # Adjust path
        path = config_framework.VALIDATION_EVALUATION_FOLDER
        new_path = path + \
            f"evaluate_questions_correct_by_attribute_{domain_name}.pdf"

        # Set tight layout and save image
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        plt.savefig(new_path, dpi=200)

    for domain_name in domain_ids:
        # Fetch question evaluation statistics
        with open(config_framework.QUESTION_EVALUATION_STATISTICS.replace(".txt", f"_{domain_name}.txt"), "r", encoding='utf-8') as question_evaluation_statistics:
            full_file = question_evaluation_statistics.readlines()
            questions_asked_frequency = eval(full_file[0].strip())
            questions_answered_correctly_frequency = eval(full_file[1].strip())
            questions_asked_attribute = eval(full_file[2].strip())
            questions_answered_correctly_attribute = eval(full_file[3].strip())

        # Run plotting procedures which are individual to each domain
        bar_plot_correct_answers_by_frequency()
        bar_plot_correct_answers_by_attribute()

    # Run plotting procedure which is for all domains
    accumulated_bar_plot_correct_answers_by_frequency()


def run_evaluation_procedure_1(domain_ids: list[str]) -> None:
    """
    Runs this evaluation procdeure for the specified domain. It checks for the quality of memorized information. This procedure only looks at one of the configured domains at a time, since the resulting plots would not be very clear. Furthermore, for this procedure to work, there must be at least one domain attribute for each domain with frequency 1.0 which can be used as base information for the model. Ignoring this will lead to an abortion of the evaluation.

    Parameters:
        domain_ids (str): The domain ids (names) for which this evaluation procedure should be run.
    """

    # Construct questions
    construct_questions()

    # Prompt model and store statistics
    for domain_name in domain_ids:
        qa_model(domain_name)

    # Plot statistics
    plot_evaluation_statistics(domain_ids)
