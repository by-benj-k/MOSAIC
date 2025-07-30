"""
helpers_document_generation.py

This module contains the parallelized document generation of MOSAIC_DDL.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from dotenv import load_dotenv
from tqdm.asyncio import tqdm
import config_framework
from os import getenv
import requests
import asyncio
import random
import httpx
import json
import copy
import sys
import os

# Load environment variables
load_dotenv()

# Define API parts
OPEN_ROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPEN_ROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPEN_ROUTER_API_HEADERS = {
    "Authorization": f"Bearer {OPEN_ROUTER_API_KEY}", "Content-Type": "application/json"}


async def get_model_response(system: str, seed: str, client: httpx.AsyncClient, semaphore: asyncio.Semaphore) -> str:
    """
    Returns the model response to the provided prompt.

    Parameters:
        system (str): The system information which is used for text generation.
        seed (str): The seed information which is used for text generation.

    Returns:
        str: The model response.
    """

    # Create prompt
    system_prompt = {"role": "system", "content": system}

    user_prompt = {"role": "user", "content": seed}

    full_prompt = {"model": config_framework.MODEL,
                   "messages": [system_prompt, user_prompt]}

    # Post request to model using the semaphore which ensure that only a certain number of parallel requests are posted
    async with semaphore:
        try:
            response = await client.post(OPEN_ROUTER_API_URL, headers=OPEN_ROUTER_API_HEADERS, json=full_prompt, timeout=60)
            response.raise_for_status()
            completion = response.json()
            return completion["choices"][0]["message"]["content"]
        except Exception as e:
            return f"An error occurred: {str(e)}"


def get_credits_of_API_key() -> str:
    """
    Returns the remaining number of tokens of the API key.

    Returns:
        str: The information regarding credit usage of the API key.
    """

    # Fetch number of credits
    response = requests.get(
        url="https://openrouter.ai/api/v1/auth/key",
        headers={
            "Authorization": f"Bearer {getenv("OPENROUTER_API_KEY")}"
        }
    )

    try:
        # Convert to dictionary-type for easy access of response fields
        response = response.json()

        return f"{'\033[32m'}Credit usage (total): {response["data"]["usage"]} Credits remaining: {response["data"]["limit_remaining"]}{'\033[0m'}"
    except (KeyError, ValueError):
        return f"{'\033[32m'}Error: Unexpected response structure or failed to properly parse JSON{'\033[0m'}"


def delete_seed_fields_probabilistically(seed: str, probabilities: dict[str, float]) -> str:
    """
    Recursively deletes fields of the seed probabilistically.

    Parameters:
        seed (str): The seed to modify.
        probabilities (dict[str, float]): A dictionary mapping the attribute names to their respective probability of being included.

    Returns:
        str: The modified/blanked out seed.
    """

    # Check whether seed is dictionary or list
    if isinstance(seed, dict):
        for attribute in list(seed.keys()):
            if attribute == "domain" or attribute == "text_type":
                continue
            if isinstance(seed[attribute], list) and all(isinstance(l, dict) for l in seed[attribute]):
                # Attribute is start of humans, animals, vehicles or objects list; hence recursively delete seed or delete entity entry if it is simply empty
                if len(seed[attribute]) == 0:
                    del seed[attribute]
                else:
                    seed[attribute] = delete_seed_fields_probabilistically(
                        seed[attribute], probabilities)
            else:
                # Attribute is simple entry/value; hence fetch probability of attribute (based on second letter)
                probability = probabilities[attribute]

                # Probability defines the probability of being included; hence < probability means excluded
                if random.random() > probability:
                    del seed[attribute]

    elif isinstance(seed, list):
        return [delete_seed_fields_probabilistically(
            attribute, probabilities) for attribute in seed]

    return seed


def filter_dictionary_keys(dictionary: dict, allowed_attributes: set[str]) -> dict:
    """
    Filters out all key value pairs in the dictionary which do not have their key occurring in the allowed attributes set.

    Parameters:
        dictionary (dict): The dictionary to filter.
        allowed_attributes (set[str]): A set of keys which should be kept in the dictionary.

    Returns:
        dict: The filtered dictionary.
    """

    # Storage for filtered dictionary
    filtered_dictionary = {}

    for key, value in dictionary.items():
        if isinstance(value, list):
            # Filter list of dictionaries
            filtered_dictionary_list = []
            for sub_dictionary in value:
                if isinstance(sub_dictionary, dict):
                    filtered_sub_dictionary = {
                        key: value for key, value in sub_dictionary.items() if key in allowed_attributes}

                    # If this dictionary is not empty, add it to filtered list
                    if filtered_sub_dictionary:
                        filtered_dictionary_list.append(
                            filtered_sub_dictionary)

            # If this filtered list is not empty, add it to filtered dictionary
            if filtered_dictionary_list:
                filtered_dictionary[key] = filtered_dictionary_list
        else:
            # Filter singular key value pair
            if key in allowed_attributes:
                filtered_dictionary[key] = value

    return filtered_dictionary


async def generate_document_file(system: list[str], seeds_file_path: str, documents_file_path: str, blank_seeds_file_path: str, number_of_text_types: int, domain_to_text_types_to_number_of_seeds_and_documents: dict[str, dict[str, tuple[int, int]]], probabilities: dict[str, float]) -> None:
    """
    Create a .jsonl file containing the LLM-based generations of documents based on the previously generated seeds.

    Parameters:
        system (list[str]): The system prompts which should be used.
        seeds_file_path (str): The path to the seeds file.
        documents_file_path (str): The path to the documents file.
        blank_seeds_file_path (str): The path to the blank seeds file.
        number_of_text_types (int): The number of text types.
        domain_to_text_types_to_number_of_seeds_and_documents (dict[str, dict[str, tuple[int, int]]]): A dictionary mapping domain to text types and text types to number of seeds and number of documents per seed of that text type.
        probabilities (dict[str, float]): A dictionary mapping the attribute names to their respective probability of being included.
    """

    # Semaphore to control number of concurrent API requests
    semaphore = asyncio.Semaphore(
        config_framework.MAXIMUM_NUMBER_OF_CONCURRENT_REQUESTS)

    # Read seed from .jsol file, blank seed, prompt model, write response to .jsonl file
    idx = 0
    async with httpx.AsyncClient() as client:
        with open(seeds_file_path, "r", encoding='utf-8') as seeds, open(documents_file_path, "w", encoding='utf-8', buffering=1) as documents, open(blank_seeds_file_path, "w", encoding='utf-8', buffering=1) as blank_seeds:
            # Load first seed
            seed = seeds.readline()
            if seed != "":
                seed = json.loads(seed)
            else:
                return

            # Go through all text types in order
            outer_progress_bar = tqdm(
                total=number_of_text_types, desc=f"{'\033[34m'}Processing text types...{'\033[0m'}", position=0)
            while True:
                for texttype in domain_to_text_types_to_number_of_seeds_and_documents[seed["domain"]]:
                    middle_progess_bar = tqdm(
                        total=domain_to_text_types_to_number_of_seeds_and_documents[seed["domain"]][texttype][0], desc=f"{'\033[34m'}Processing seeds of text type...{'\033[0m'}", leave=False, position=1)

                    # Go through all seeds belonging to that text type
                    for _ in range(domain_to_text_types_to_number_of_seeds_and_documents[seed["domain"]][texttype][0]):
                        inner_progess_bar = tqdm(
                            total=domain_to_text_types_to_number_of_seeds_and_documents[seed["domain"]][texttype][1], desc=f"{'\033[34m'}Generating documents for current seed...{'\033[0m'}", leave=False, position=2)

                        # Go through all documents that should be generated for that text type and that seed
                        tasks_scheduled = []
                        for _ in range(domain_to_text_types_to_number_of_seeds_and_documents[seed["domain"]][texttype][1]):
                            # Fetch attributes which can be included in text type
                            allowed_attributes = set(system[idx][1].split(","))

                            # Filter seed based on attributes which should be included in seed
                            if allowed_attributes == {"all"}:
                                # Do nothing since all attributes should be used
                                seed_modified = copy.deepcopy(seed)
                            elif allowed_attributes and "all" not in allowed_attributes:
                                # Filter out attributes which do not belong to text type
                                allowed_attributes.add("domain")
                                seed_modified = filter_dictionary_keys(
                                    copy.deepcopy(seed), allowed_attributes)
                            else:
                                print(
                                    "WARNING: Please specify either \"all\" OR list the attributes you wish to occurr in the text type!")
                                sys.exit("FRAMEWORK EXECUTION ABORTED")

                            # Deleted fields probabilistically according to specified frequency of attribute
                            seed_modified = delete_seed_fields_probabilistically(
                                seed_modified, probabilities)

                            # Post process blanked seed to remove empty entity clauses
                            seed_modified = {key: value for key, value in seed_modified.items() if not (
                                isinstance(value, list) and value == [{}])}

                            # Add information about text type to seed
                            seed_modified["text_type"] = texttype

                            blank_seeds.write(json.dumps(seed_modified) + "\n")

                            task_for_scheduling = get_model_response(system[idx][0],
                                                                     json.dumps(seed_modified), client, semaphore)

                            tasks_scheduled.append(task_for_scheduling)

                            idx += 1

                        # Await responses/coroutines of concurrent API requests
                        for coroutine in asyncio.as_completed(tasks_scheduled):
                            model_response = await coroutine
                            documents.write(json.dumps(
                                {"document": model_response}) + "\n")
                            documents.flush()
                            inner_progess_bar.update(1)

                        # Load next seed
                        seed = seeds.readline()
                        if seed != "":
                            seed = json.loads(seed)
                        else:
                            outer_progress_bar.update(1)
                            inner_progess_bar.close()
                            middle_progess_bar.close()
                            outer_progress_bar.close()

                            # Show remaining number of credits on API key
                            print(get_credits_of_API_key())
                            return

                        inner_progess_bar.close()
                        middle_progess_bar.update(1)

                        # Show remaining number of credits on API key
                        tqdm.write(
                            f"Credits after last seed: {get_credits_of_API_key()}")

                    middle_progess_bar.close()
                    outer_progress_bar.update(1)
