"""
occasion_event_generation.py

This module contains the code to generate the occasion entry of a seed.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code.domains.occasion_domain.occasion_infrastructure_generation import generate_infrastructures
from sample_code.domains.occasion_domain.occasion_building_generation import generate_buildings
from sample_code.domains.occasion_domain.occasion_vehicle_generation import generate_vehicles
from sample_code.domains.occasion_domain.occasion_animal_generation import generate_animals
from sample_code.domains.occasion_domain.occasion_object_generation import generate_objects
from sample_code.helpers_event_generation import get_random_csv_entry, count_number_of_humans, get_random_jsonl_entry
from sample_code import config
from typing import Union
import pandas as pd
import datetime
import random
import json


def get_random_location() -> str:
    """
    Returns a random location on earth.

    Returns:
        str: The random location as "city,state_name,country_name".
    """

    # Read .csv header
    cities_header = pd.read_csv(config.E_CITIES_FILE_PATH, nrows=0)
    cities_column_names = cities_header.columns.tolist()

    # Choose random entry in .csv
    random_offset = random.randint(1, config.E_CITIES_FILE_LENGTH)
    cities_full_entry = pd.read_csv(
        config.E_CITIES_FILE_PATH, skiprows=random_offset, nrows=1, header=None)

    # Assign initial .csv header
    cities_full_entry.columns = cities_column_names

    # Construct location
    location = cities_full_entry.at[0, "name"] + "," + \
        cities_full_entry.at[0, "state_name"] + "," + \
        cities_full_entry.at[0, "country_name"]

    return location


def get_random_date() -> str:
    """
    Returns a random date between start_date and end_date.

    Returns:
        str: The random date as "day-month-year".
    """

    # Compute delta between dates and choose random offset
    delta_days = (config.END_DATE - config.START_DATE).days
    random_offset = random.randint(0, delta_days)

    # Construct date
    date_not_formatted = config.START_DATE + \
        datetime.timedelta(days=random_offset)
    date = date_not_formatted.strftime("%d-%m-%Y")

    return date


def get_random_time() -> str:
    """
    Return a random time.

    Returns:
        str: The random time as "hour:min:sec".
    """

    # Choose random hour and minute
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)

    # Construct time
    time = f"{random_hour:02}:{random_minute:02}:{random_second:02}"

    return time


def get_random_scale() -> str:
    """
    Returns a random value between 1 and 10 representing the scale of the event.

    Returns:
        str: The scale of the event.
    """

    return f"{random.randint(1, 10)} out of 10"


def get_random_duration() -> str:
    """
    Returns a random value between 1 and 3 representing the duration of the event in hours.

    Returns:
        str: The duration of the event.
    """

    return f"{random.randint(1, 3)} hours"


def generate_occasion_event(entity_to_count: dict[str, str]) -> dict[str, Union[int, str]]:
    """
    Generates the entry for a single occasion event.

    Parameters:
        entity_to_count (dict[str, str]): Maps entities to the number of occurrences in the current seed.

    Returns:
        dict[str, Union[int, str]]: A dictionary containing the event and the attributes.
    """

    # Create event instance
    location = get_random_location()
    date = get_random_date()
    time = get_random_time()
    content = get_random_csv_entry(
        config.E_ACTIVITIES_FILE_PATH, config.E_ACTIVITIES_FILE_LENGTH, "activity")
    scale = get_random_scale()
    duration = get_random_duration()
    cultural_impact = get_random_csv_entry(
        config.E_CULTURAL_IMPACTS_FILE_PATH, config.E_CULTURAL_IMPACTS_FILE_LENGTH, "e_cultural_impacts")
    societal_impact = get_random_csv_entry(
        config.E_SOCIETAL_IMPACTS_FILE_PATH, config.E_SOCIETAL_IMPACTS_FILE_LENGTH, "e_societal_impacts")
    controversies = get_random_csv_entry(
        config.E_CONTROVERSIES_FILE_PATH, config.E_CONTROVERSIES_FILE_LENGTH, "e_controversies")
    challenges = get_random_csv_entry(
        config.E_CHALLENGES_FILE_PATH, config.E_CHALLENGES_FILE_LENGTH, "e_challenges")
    surprises = get_random_csv_entry(
        config.E_SURPRISES_FILE_PATH, config.E_SURPRISES_FILE_LENGTH, "e_surprises")
    incidents = get_random_csv_entry(
        config.E_INCIDENTS_FILE_PATH, config.E_INCIDENTS_FILE_LENGTH, "e_incidents")
    special_conditions = get_random_csv_entry(
        config.E_SPECIAL_CONDITIONS_FILE_PATH, config.E_SPECIAL_CONDITIONS_FILE_LENGTH, "e_special_conditions")

    # Fetch human, anmial, vehicle, object, building and infrastructure instances
    number_of_humans = count_number_of_humans()
    current_event_year = int(date.split("-")[2])
    humans = []
    while len(humans) < entity_to_count["occasion.humans"]:
        # Sample as long as new human is selected
        human = get_random_jsonl_entry(
            config.HUMAN_INSTANCES_PATH, number_of_humans)

        while json.dumps(human) in config.GLOBAL_HUMAN_SET or (current_event_year - human["birth_year"] > 100) or (current_event_year - human["birth_year"] < 18):
            human = get_random_jsonl_entry(
                config.HUMAN_INSTANCES_PATH, number_of_humans)

        config.GLOBAL_HUMAN_SET.add(json.dumps(human))
        humans.append(human)
    humans = [{f"occasion.humans.{key}": value for key, value in human.items()}
              for human in humans]

    # Remove attributes which are not needed for occasion domain
    for h in humans:
        h.pop("occasion.humans.works_at", None)
        h.pop("occasion.humans.is_ceo_of", None)
        h.pop("occasion.humans.is_employee_at", None)
        h.pop("occasion.humans.is_judge_at", None)
        h.pop("occasion.humans.is_instructor_at", None)
        h.pop("occasion.humans.instructor_email_address", None)
        h.pop("occasion.humans.instructor_id", None)
        h.pop("occasion.humans.is_student_at", None)
        h.pop("occasion.humans.student_email_address", None)
        h.pop("occasion.humans.student_id", None)

    animals = generate_animals(location, entity_to_count["occasion.animals"])
    vehicles = generate_vehicles(
        location, date, entity_to_count["occasion.vehicles"])
    objects = generate_objects(date, entity_to_count["occasion.objects"])
    buildings = generate_buildings(date, entity_to_count["occasion.buildings"])
    infrastructures = generate_infrastructures(
        date, entity_to_count["occasion.infrastructures"])

    # Assemble dictionary
    event = {"occasion.location": location, "occasion.date": date, "occasion.time": time, "occasion.content": content, "occasion.scale": scale, "occasion.duration": duration, "occasion.cultural_impact": cultural_impact,
             "occasion.societal_impact": societal_impact, "occasion.controversies": controversies, "occasion.challenges": challenges, "occasion.surprises": surprises, "occasion.incidents": incidents, "occasion.special_conditions": special_conditions, "occasion.humans": humans, "occasion.animals": animals, "occasion.vehicles": vehicles, "occasion.objects": objects, "occasion.buildings": buildings, "occasion.infrastructures": infrastructures}

    return event
