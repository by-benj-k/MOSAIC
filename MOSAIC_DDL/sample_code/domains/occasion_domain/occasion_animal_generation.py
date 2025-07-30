"""
occasion_animal_generation.py

This module contains the code to generate the animal entries of a seed.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code import config
from typing import Union
import pandas as pd
import random


def get_random_species_age_endangered_origin(location: str) -> tuple[str, int, str, str]:
    """
    Takes in the location of the event and samples a random species from that broad region together with its age sampled from its approximate age-range, its endangered status and its region.

    Parameters:
        location (str): The location of the event.

    Returns:
        tuple[str, int, str, str]: A tuple containing the species, its age, its endangered status and its origin.
    """

    # Extract country from location
    country = location.split(",")[2]

    # Extract region from country
    country_information = pd.read_csv(
        config.COUNTRY_REGION_RELIGION_POLITICS_FILE_PATH)
    region = country_information.loc[country_information["country"]
                                     == country, "region"].values[0]

    # Find all animals from said region
    animal_information = pd.read_csv(
        config.SPECIES_REGION_LIFETIME_ENDANGERED_FILE_PATH)
    animals_matching_region = animal_information.loc[animal_information["region"] == region]

    # Sample random animal and extract fields
    random_animal = animals_matching_region.sample(n=1)
    species = random_animal.iloc[0]["species"]
    age_range = random_animal.iloc[0]["lifetime"].split("-")
    age = random.randint(int(age_range[0]), int(age_range[1]))
    endangered = random_animal.iloc[0]["endangered"]

    return species, age, endangered, region


def generate_animals(location: str, count: int) -> list[dict[str, Union[int, str]]]:
    """
    Generates the animal entries for a single event.

    Parameters:
        location (list[str]): The location of the event.
        count (int): The number of animals of the event.

    Returns:
        list[dict[str, Union[int, str]]]: A list containing multiple animal instances.
    """

    # Storage for all animals
    all_animals = []

    # Prepare unique attributes for all animals of event
    all_microchip_ids = random.sample(
        range(1, 8000000000), k=count)

    # Create animal instances
    animal_index = 0
    for _ in range(count):
        # Fetch values
        species, age, endangered_status, region = get_random_species_age_endangered_origin(
            location)

        # Compute microchip id
        region_abbrevation = "".join([letters[0]
                                      for letters in region.split(" ")])
        microchip_id = f"MCID-{region_abbrevation}-{all_microchip_ids[animal_index]}"

        # Assemble dictionary
        animal = {"occasion.animals.species": species, "occasion.animals.age": age, "occasion.animals.endangered_status":
                  endangered_status, "occasion.animals.region": region, "occasion.animals.microchip_id": microchip_id}

        all_animals.append(animal)
        animal_index += 1

    return all_animals
