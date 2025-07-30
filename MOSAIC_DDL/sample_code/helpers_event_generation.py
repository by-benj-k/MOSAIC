"""
helpers_generation.py

This module contains some helper functions which are used by multiple generation functions.

Author: Benjamin Koch
Date: June 2025
"""

# Imports
from typing import Callable, TypeVar, Any, Generator
from sample_code import config
from typing import Union
import pandas as pd
import random
import string
import json

# Type variable
T = TypeVar('T')


def get_random_csv_entry(file_path: str, file_length: int, column_name: str) -> str:
    """
    Returns a random entry of the specified file and its respective column.

    Parameters:
        file_path (str): The path to the .csv file.
        file_length (int): The number of rows of the .csv file.
        column_name (str): The name of the column of the .csv file.

    Returns:
        str: The random entry of the .csv file.
    """

    # Read .csv header
    header = pd.read_csv(file_path, nrows=0)
    column_names = header.columns.tolist()

    # Choose random entry in .csv
    random_offset = random.randint(1, file_length)
    full_entry = pd.read_csv(
        file_path, skiprows=random_offset, nrows=1, header=None)

    # Assign initial .csv header
    full_entry.columns = column_names

    # Construct string
    entry = full_entry.at[0, column_name]

    return entry


def get_unique_values_from_function(function: Callable[..., T], number_of_values: int, *args: Any, **kwargs: Any) -> list[T]:
    """
    Samples number_of_values unique values using the provided function.

    Parameters:
        function (Callable[..., T]): The function which should be used.
        number_of_values (int): The number of unique values to sample.
        *args, **kwargs (Any): Arguments to pass to the function provided.

    Returns:
        list[T]: The list of sampled values.
    """

    # Set for seen values
    values = set()

    # Sample number_of_values values
    while len(values) < number_of_values:
        values.add(function(*args, **kwargs))

    return list(values)


def get_random_csv_full(file_path: str, file_length: str) -> pd.DataFrame:
    """
    Returns a random full entry of the specified file.

    Parameters:
        file_path (str): The path to the .csv file.
        file_length (str): The number of rows of the .csv file.

    Returns:
        pd.DataFrame: The random entry of the .csv file.
    """

    # Read .csv header
    header = pd.read_csv(file_path, nrows=0)
    column_names = header.columns.tolist()

    # Choose random entry in .csv
    random_offset = random.randint(1, file_length)
    full_entry = pd.read_csv(
        file_path, skiprows=random_offset, nrows=1, header=None)

    # Assign initial .csv header
    full_entry.columns = column_names

    return full_entry


def batch_list(list_1: list[str], batch_size: int) -> Generator[list[str], None, None]:
    """
    Takes in a list of strings an returns an generator which is used for batched inference with vLLM.

    Parameters:
        list_1 (list[str]): The list of strings from which to create a generator for batching.
        batch_size (int): The size of each batch.

    Returns:
        Generator[list[str], None, None]: The generator with yield type list[str], no specified send or return type.
    """

    # Perform the batching by collecting the "next" batch_size elements from the questions list
    for i in range(0, len(list_1), batch_size):
        yield list_1[i:i + batch_size]


def batch_lists(list_1: list[str], list_2: list[str], batch_size: int) -> Generator[list[str], None, None]:
    """
    Takes in a list of strings an returns an generator which is used for batched inference with vLLM.

    Parameters:
        list_1 (list[str]): The first list of strings from which to create a generator for batching.
        list_2 (list[str]): The first list of strings from which to create a generator for batching.
        batch_size (int): The size of each batch.

    Returns:
        Generator[list[str], None, None]: The generator with yield type list[str], no specified send or return type.
    """

    # Perform the batching by collecting the "next" batch_size elements from the questions list
    for i in range(0, len(list_1), batch_size):
        yield list_1[i:i + batch_size], list_2[i: i + batch_size]


def extract_formatting_fields(unformatted_string: str) -> list[str]:
    """
    Takes in a string with empty formatting clauses and returns which formatting clauses occur in the string as a list.

    Parameters:
        unformatted_string (str): The string which should be scanned for formatting clauses.

    Returns:
        list[str]: The list of names of the formatting clauses.
    """

    return [t[1] for t in string.Formatter().parse(unformatted_string) if t[1]]


def count_number_of_humans() -> int:
    """
    Counts the number of humans generated.

    Returns:
        int: The number of human instances.
    """

    # Traverse document and count lines
    cnt = 0
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
        for _ in humans:
            cnt += 1

    return cnt


def get_random_jsonl_entry(file_path: str, file_length: int) -> dict[str, Union[str, int]]:
    """
    Returns a random entry of the specified file as a loaded dictionary.

    Parameters:
        file_path (str): The path to the .jsonl file.
        file_length (int): The number of rows of the .jsonl file.

    Returns:
        dict[str, Union[str, int]]: The random entry of the .jsonl file.
    """

    # Choose a random row
    random_row = random.randint(0, file_length - 1)

    # Traverse file and pick randomly chosen row
    with open(file_path, "r", encoding='utf-8') as file:
        for i, jsonl_entry in enumerate(file):
            if i == random_row:
                return json.loads(jsonl_entry)
