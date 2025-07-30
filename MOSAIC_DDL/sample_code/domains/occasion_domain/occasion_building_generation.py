"""
occasion_building_generation.py

This module contains the code to generate the building entries of a seed.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code import config
from typing import Union
import pandas as pd
import random


def get_random_type_construction_floors(date: str) -> tuple[str, str, str]:
    """
    Takes in the event date and samples a random building type, its construction year and the number of floors.

    Parameters:
        date (str): The event date.

    Returns:
        tuple[str, str, str]: A tuple containing the building type, its construction year and the number of floors.
    """

    # Extract year from date
    event_year = date.split("-")[2]

    # Find all buildings with construction year before event date
    building_information = pd.read_csv(
        config.TYPE_CONSTRUCTION_FLOORS_FILE_PATH)
    buildings_matching_date = building_information.loc[building_information["construction"] <= int(
        event_year)]

    # Sample random building and extract fields
    random_building = buildings_matching_date.sample(n=1)
    btype = random_building.iloc[0]["type"]
    first_construction_year = random_building.iloc[0]["construction"]
    construction_year = random.randint(
        int(first_construction_year), int(event_year))
    floors = random_building.iloc[0]["floors"]

    return btype, construction_year, str(floors)


def get_renovation_status(date: str, construction_year: str) -> str:
    """
    Takes in the event date and the construction year and returns one out of five renovation status.

    Parameters:
        date (str): The event date.
        construction_year (str): The year of construction of the building.

    Returns:
        str: The renovation status.
    """

    # Extract year-range
    event_year = event_year = date.split("-")[2]
    year_range = int(event_year) - int(construction_year)

    # Compute renovation status
    if year_range < 10:
        renovation_status = "No Renovation Needed"
    elif year_range < 20:
        renovation_status = "Minor Repairs Needed"
    elif year_range < 30:
        renovation_status = "Renovation Recommended"
    elif year_range < 40:
        renovation_status = "Minor Renovation Required"
    else:
        renovation_status = "Major Renovation Required"

    return renovation_status


def get_random_damage_status() -> str:
    """
    Samples a random damage status from 0 to 3.

    Returns:
        str: The damage status.
    """

    return f"{random.choices([0, 1, 2, 3], [0.4, 0.3, 0.2, 0.1], k=1)[0]} out of 3"


def generate_buildings(date: str, count: int) -> list[dict[str, Union[int, str]]]:
    """
    Generate the building entries for a single event.

    Parameters:
        date (str): The date of the event.
        count (int): The number of buildings of the event.

    Returns:
        list[dict[str, Union[int, str]]]: A list containing multiple building instances.
    """

    # Storage for all buildings
    all_buildings = []

    # Prepare unique attributes for all buildings
    all_blueprint_ids = random.sample(
        range(1, 8000000000), k=count)

    # Create building instances
    building_index = 0
    for _ in range(count):
        # Fetch values
        type, construction_year, floors = get_random_type_construction_floors(
            date)
        renovation_status = get_renovation_status(date, construction_year)
        damage_status = get_random_damage_status()

        # Compute blueprint id
        type_abbreviation = "".join([letters[0]
                                    for letters in type.split(" ")])
        blueprint_id = f"BPID-{type_abbreviation}-{all_blueprint_ids[building_index]}"

        # Assemble dictionary
        building = {"occasion.buildings.type": type, "occasion.buildings.construction_year": construction_year, "occasion.buildings.floors": floors,
                    "occasion.buildings.renovation_status": renovation_status, "occasion.buildings.damage_status": damage_status, "occasion.buildings.blueprint_id": blueprint_id}

        all_buildings.append(building)
        building_index += 1

    return all_buildings
