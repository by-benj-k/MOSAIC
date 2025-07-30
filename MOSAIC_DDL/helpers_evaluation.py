"""
helpers_evaluations.py

This module contains some helper functions which are used by the evaluation functions.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from typing import Generator


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
