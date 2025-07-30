"""
occasion_infrastructure_generation.py

This module contains the code to generate the infrastructure entries of a seed.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code import config
from typing import Union
import pandas as pd
import random


def get_random_type_construction_capacity_safety(date: str) -> tuple[str, str, str, str]:
    """
    Takes in the event date and samples a random infrastructure, its construction year, the capacity and a safety rating.

    Parameters:
        date (str): The event date.

    Returns:
        tuple[str, str, str, str]: A tuple cointaining the infrastructure type, its construction year, its capacity and the safety rating.
    """

    # Extract year from date
    event_year = date.split("-")[2]

    # Find all infrastructure with construction year before event date
    infrastructure_information = pd.read_csv(
        config.TYPE_CONSTRUCTION_CAPACITY_SAFETY_FILE_PATH)
    infrastructure_matching_date = infrastructure_information.loc[infrastructure_information["construction"] <= int(
        event_year)]

    # Sample random infrastructure and extract fields
    random_infrastructure = infrastructure_matching_date.sample(n=1)
    itype = random_infrastructure.iloc[0]["type"]
    first_construction_year = random_infrastructure.iloc[0]["construction"]
    construction_year = random.randint(
        int(first_construction_year), int(event_year))
    capacity = random_infrastructure.iloc[0]["capacity"]
    safety = random_infrastructure.iloc[0]["safety"]

    return itype, str(construction_year), str(capacity), safety


def get_random_utilization_level() -> str:
    """
    Returns a random utilization level between 0 and 3.

    Returns:
        str: The utilization level.
    """

    return f"{random.randint(0, 3)} out of 3"


def get_random_damage_status() -> str:
    """
    Samples a random damage status from 0 to 3.

    Returns:
        str: The damage status.
    """

    return f"{random.choices([0, 1, 2, 3], [0.4, 0.3, 0.2, 0.1], k=1)[0]} out of 3"


def generate_infrastructures(date: str, count: int) -> list[dict[str, Union[int, str]]]:
    """
    Generate the infrastructure entries for a single event.

    Parameters:
        date (str): The date of the event.
        count (int): The number of infrastructures of the event.

    Returns:
        list[dict[str, Union[int, str]]]: A list containing multiple building instances.
    """

    # Storage for all infrastructure
    all_infrastructures = []

    # Prepare unique attributes for all infrastructure
    all_regulatory_ids = random.sample(
        range(1, 8000000000), k=count)

    # Create infrastructure instances
    infrastructure_index = 0
    for _ in range(count):
        # Fetch values
        type, construction_year, capacity, safety_rating = get_random_type_construction_capacity_safety(
            date)
        utilization_level = get_random_utilization_level()
        damage_status = get_random_damage_status()

        # Compute regulatory id
        type_abbreviation = "".join([letters[0]
                                    for letters in type.split(" ")])
        o_regulatory_id = f"RID-{type_abbreviation}-{all_regulatory_ids[infrastructure_index]}"

        # Compute last inspection date
        event_year = date.split("-")[2]
        last_inspection_year = random.randint(
            int(construction_year), int(event_year))

        # Assemble dictionary
        infrastructure = {"occasion.infrastructures.type": type, "occasion.infrastructures.construction_year": construction_year, "occasion.infrastructures.capacity": capacity, "occasion.infrastructures.utilization_level": utilization_level,
                          "occasion.infrastructures.damage_status": damage_status, "occasion.infrastructures.safety_rating": f"{safety_rating} (from A=best to D=worst)", "occasion.infrastructures.regulatory_id": o_regulatory_id, "occasion.infrastructures.last_inspection_year": last_inspection_year}

        all_infrastructures.append(infrastructure)
        infrastructure_index += 1

    return all_infrastructures
