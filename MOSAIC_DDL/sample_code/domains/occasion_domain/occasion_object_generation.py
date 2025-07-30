"""
occasion_object_generation.py

This module contains the code to generate the object entries of a seed.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code.helpers_event_generation import get_random_csv_entry
import matplotlib.colors as colors
from sample_code import config
from typing import Union
import pandas as pd
import random


def get_random_name_size_production_value(date: str) -> tuple[str, str, str, str]:
    """
    Takes in the event date and samples a random object name, its size, its production year and its value.

    Parameters:
        date (str): The event date.

    Returns:
        tuple[str, str, str, str]: A tuple containing the object name, size, production year and value.
    """

    # Extract year from date
    event_year = date.split("-")[2]

    # Find all objects with production year before event date
    object_information = pd.read_csv(
        config.NAME_SIZE_PRODUCTION_VALUE_FILE_PATH)
    objects_matching_date = object_information.loc[object_information["production"] <= int(
        event_year)]

    # Sample random object and extract fields
    random_object = objects_matching_date.sample(n=1)
    name = random_object.iloc[0]["name"]
    size = random_object.iloc[0]["size"]
    first_production_year = random_object.iloc[0]["production"]
    production_year = random.randint(
        int(first_production_year), int(event_year))
    value = random_object.iloc[0]["value"]

    return name, size, str(production_year), str(value)


def get_random_color() -> str:
    """
    Returns a random color name.

    Returns:
        str: The random color.
    """

    return random.choice(list(colors.CSS4_COLORS.keys()))


def generate_objects(date: str, count: int) -> list[dict[str, Union[int, str]]]:
    """
    Generate the object entries object=o for all event=e.

    Parameters:
        date (list[str]): The dates of the events.
        count (int): The number of objects of the event.

    Returns:
        list[dict[str, Union[int, str]]]: A list containing multiple object instances.
    """

    # Storage for all objects
    all_objects = []

    # Prepare unique attributes for all objects
    all_serial_numbers = random.sample(
        range(1, 8000000000), k=count)

    # Create object instances
    object_index = 0
    for _ in range(count):
        # Fetch values
        name, size, manufacturing_year, value = get_random_name_size_production_value(
            date)
        condition = get_random_csv_entry(
            config.O_CONDITIONS_FILE_PATH, config.O_CONDITIONS_FILE_LENGTH, "o_conditions")
        color = get_random_color()

        # Compute serial number
        name_abbreviation = "".join([letters[0]
                                    for letters in name.split(" ")])
        serial_number = f"SN-{name_abbreviation}-{all_serial_numbers[object_index]}"

        # Assemble dictionary
        single_object = {"occasion.objects.name": name, "occasion.objects.size": size, "occasion.objects.condition": condition, "occasion.objects.color": color,
                         "occasion.objects.manufacturing_year": manufacturing_year, "occasion.objects.value": value, "occasion.objects.serial_number": serial_number}

        all_objects.append(single_object)
        object_index += 1

    return all_objects
