"""
legal_event_generation.py

This module contains the code to generate the legal entry of a seed.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code.helpers_event_generation import get_random_csv_full, get_random_jsonl_entry, count_number_of_humans
from sample_code import config
from typing import Union
import pandas as pd
import datetime
import random
import json


def get_random_court_and_location() -> tuple[str, str]:
    """
    Returns the name of a random court and the country it is located in.

    Returns:
        tuple[str, str]: A tuple containing the court name and location.
    """

    # Choose a random row (which represents a country)
    random_row = random.randint(0, config.E_COUNTRIES_FILE_LENGTH - 1)

    # Traverse court file and pick chosen row
    with open(config.COURT_INSTANCES_PATH, "r", encoding='utf-8') as courts:
        for i, court in enumerate(courts):
            if i == random_row:
                court_entry = json.loads(court)
                break

    # Choose a random court
    return random.choice(court_entry["courts"]), court_entry["country"]


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


def get_random_lawyer(court_location: str, hearing_date: str) -> str:
    """
    Returns a lawyer from the same country as the court is located in.

    Parameters:
        court_location (str): The location of the court.
        hearing_date (str): The date of the hearing.

    Returns:
        str: The name of a lawyer from that location.
    """

    # Storage for all lawyers of the country
    all_lawyers_of_country = []

    # Extract year from date
    year_of_hearing = int(hearing_date.split("-")[2])

    # Traverse human instances and search for lawyers
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
        for human in humans:
            # Fetch content
            human_content = json.loads(human)

            if human_content["occupation"] == "Lawyer" and human_content["nationality"] == court_location and (18 <= year_of_hearing - human_content["birth_year"] <= 100):
                all_lawyers_of_country.append(human_content["name"])

    if len(all_lawyers_of_country) == 0:
        return "Unknown"

    return random.choice(all_lawyers_of_country)


def get_random_judge(court_name: str, court_location: str, hearing_date: str) -> str:
    """
    Returns a judge from the court or some random judge from the country.

    Parameters:
        court_name (str): The name of the selected court.
        court_location (str): The country the selected court is located in.
        hearing_date (str): The date of the hearing.

    Returns:
        str: The randomly selected judge from the selected court or country.
    """

    # Storage for all judges of the court
    all_judges_of_court = []

    # Storage for random judge
    random_judge = ""

    # Extract year from date
    year_of_hearing = int(hearing_date.split("-")[2])

    # Traverse humans and search for judge working at the court
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
        for human in humans:
            # Fetch content
            human_content = json.loads(human)

            if human_content["occupation"] == "Judge" and human_content["is_judge_at"] == court_name and (18 <= year_of_hearing - human_content["birth_year"] <= 100):
                all_judges_of_court.append(human_content["name"])

    if len(all_judges_of_court) == 0:
        # Storage for all judges of the country
        all_judges_of_country = []

        with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
            for human in humans:
                # Fetch content
                human_content = json.loads(human)

                if human_content["occupation"] == "Judge" and human_content["nationality"] == court_location and (18 <= year_of_hearing - human_content["birth_year"] <= 100):
                    all_judges_of_country.append(human_content["name"])

        if len(all_judges_of_country) == 0:
            random_judge = "Unknown"
        else:
            random_judge = random.choice(all_judges_of_country)
    else:
        random_judge = random.choice(all_judges_of_court)

    return random_judge


def get_random_plaintiff_defendant(hearing_date: str) -> tuple[str, str]:
    """
    Returns the next two "free" humans in the human instances set.

    Parameters:
        hearing_date (str): The date of the hearing.

    Returns:
        tuple[str, str]: A tuple containing the plaintiff and the defendant.
    """

    # Storage for plaintiff and defendant
    plaintiff_and_defendant = []

    # Compute number of human instances
    number_of_humans = count_number_of_humans()

    # Extract year from date
    year_of_hearing = int(hearing_date.split("-")[2])

    # Sample until new humans are selected
    while len(plaintiff_and_defendant) < 2:
        # Sample as long as new human is selected
        human = get_random_jsonl_entry(
            config.HUMAN_INSTANCES_PATH, number_of_humans)

        while json.dumps(human) in config.GLOBAL_HUMAN_SET or (year_of_hearing - human["birth_year"] > 100) or (year_of_hearing - human["birth_year"] < 18):
            human = get_random_jsonl_entry(
                config.HUMAN_INSTANCES_PATH, number_of_humans)

        plaintiff_and_defendant.append(human["name"])
        config.GLOBAL_HUMAN_SET.add(json.dumps(human))

    return plaintiff_and_defendant[0], plaintiff_and_defendant[1]


def generate_legal_event(entity_to_count: dict[str, int]) -> dict[str, Union[int, str]]:
    """
    Generates the entries for a single legal event.

    Parameters:
        entity_to_count (dict[str, str]): Maps entities to the number of occurrences in the current seed.

    Returns:
        dict[str, Union[int, str]]: A dictionary containing the event and the attributes.
    """

    # Create event instance
    court_name, court_location = get_random_court_and_location()
    cs_entry = get_random_csv_full(
        config.CRIMETYPE_SENTENCE_FILE_PATH, config.CRIMETYPE_SENTENCE_FILE_LENGTH)
    hearing_date = get_random_date()
    lawyer_name = get_random_lawyer(court_location, hearing_date)
    judge_name = get_random_judge(court_name, court_location, hearing_date)
    plaintiff, defendant = get_random_plaintiff_defendant(hearing_date)

    # Extract values from cs entry
    sentence = cs_entry["sentence"].iloc[0]
    crime_type = cs_entry["crimetype"].iloc[0]

    # Compute case id
    country_information = pd.read_csv(config.E_COUNTRIES_FILE_PATH)
    country_iso_code = country_information.loc[country_information["name"]
                                               == court_location, "iso3"].values[0]
    court_abbreviation = "".join([c for c in court_name if c.isupper()])
    case_id = f"{court_abbreviation}-{country_iso_code}-{random.randint(1, 1000000000)}"

    # Assemble dictionary
    event = {"legal.court_name": court_name, "legal.hearing_date": hearing_date, "legal.judges_name": judge_name, "legal.lawyers_name": lawyer_name,
             "legal.crime_type": crime_type, "legal.sentence": sentence, "legal.plaintiffs": plaintiff, "legal.defendants": defendant, "legal.case_id": case_id}

    return event
