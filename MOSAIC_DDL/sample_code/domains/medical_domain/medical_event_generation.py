"""
medical_event_generatoin.py

This module contains the code to generate the medical entriy of a seed.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code.helpers_event_generation import get_random_csv_full, get_random_jsonl_entry, count_number_of_humans
from sample_code import config
from typing import Union
import datetime
import random
import json


def get_random_hospital_and_location() -> tuple[str, str]:
    """
    Returns the name of a random hospital and the country it is located in.
    """

    # Choose random row (which represents a country)
    random_row = random.randint(0, config.E_COUNTRIES_FILE_LENGTH - 1)

    # Traverse hospitals file and pick chosen row
    with open(config.HOSPITAL_INSTANCES_PATH, "r", encoding='utf-8') as hospitals:
        for i, hospital_lists in enumerate(hospitals):
            if i == random_row:
                hospital_entry = json.loads(hospital_lists)

    # Choose random hospital type
    random_hospital_type = random.choice(
        ["local_hospitals", "regional_hospitals", "national_hospitals"])

    # Choose random hospital from hospital type
    return random.choice(hospital_entry[random_hospital_type]), hospital_entry["country"]


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


def get_random_doctor(hospital_name: str, hospital_location: str, date_of_visit: str) -> str:
    """
    Returns the name of a doctor from the chosen hospital or some random doctor of the country the hospital is in.

    Parameters:
        hospital_name (str): The name of the hospital selected.
        hospital_location (str): The country the hospital is located in.
        date_of_visit (str): The date of the hospital visit.

    Returns:
        str: The name of a doctor from the corresponding hospital or a random doctor.
    """

    # Storage for all doctors of the hospital
    all_doctors_of_hospital = []

    # Storage for random doctor
    random_doctor = ""

    # Extract year from date
    year_of_visit = int(date_of_visit.split("-")[2])

    # Traverse humans and search for doctor working at the hospital
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
        for human in humans:
            # Fetch content
            human_content = json.loads(human)

            if human_content["occupation"] == "Doctor" and human_content["works_at"] == hospital_name and (18 <= year_of_visit - human_content["birth_year"] <= 100):
                all_doctors_of_hospital.append(human_content["name"])

    if len(all_doctors_of_hospital) == 0:
        # Storage for all doctors of the country
        all_doctors_of_country = []

        with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
            for human in humans:
                # Fetch content
                human_content = json.loads(human)

                if human_content["occupation"] == "Doctor" and human_content["nationality"] == hospital_location and (18 <= year_of_visit - human_content["birth_year"] <= 100):
                    all_doctors_of_country.append(human_content["name"])

        if len(all_doctors_of_country) == 0:
            random_doctor = "Unknown"
        else:
            random_doctor = random.choice(all_doctors_of_country)
    else:
        random_doctor = random.choice(all_doctors_of_hospital)

    return random_doctor


def get_random_patient(date_of_visit: str) -> dict[str, Union[str, int]]:
    """
    Returns the next "free" human in the human instances set.

    Parameters:
        date_of_visit (str): The date of the hospital visit.

    Returns:
        str: The name of the human selected.
    """

    # Storage for random patient
    random_patient = ""

    # Compute number of human instances
    number_of_humans = count_number_of_humans()

    # Extract year from date
    year_of_visit = int(date_of_visit.split("-")[2])

    # Sample until new human is selected
    human = get_random_jsonl_entry(
        config.HUMAN_INSTANCES_PATH, number_of_humans)

    while json.dumps(human) in config.GLOBAL_HUMAN_SET or (year_of_visit - human["birth_year"] > 100) or (year_of_visit - human["birth_year"] < 18):
        human = get_random_jsonl_entry(
            config.HUMAN_INSTANCES_PATH, number_of_humans)

    random_patient = human["name"]
    config.GLOBAL_HUMAN_SET.add(json.dumps(human))

    return random_patient


def generate_medical_event(entity_to_count: dict[str, int]) -> dict[str, Union[int, str]]:
    """
    Generates the entries for a single medical event.

    Parameters:
        entity_to_count (dict[str, str]): Maps entities to the number of occurrences in the current seed.

    Returns:
        dict[str, Union[int, str]]: A dictionary containing the event and the attributes.
    """

    # Create event instance
    hospital_name, hospital_location = get_random_hospital_and_location()
    date_of_visit = get_random_date()
    csm_entry = get_random_csv_full(
        config.CONDITION_SYMPTOMS_MEDICATION_FILE_PATH, config.CONDITION_SYMPTOMS_MEDICATION_FILE_LENGTH)
    doctor_name = get_random_doctor(
        hospital_name, hospital_location, date_of_visit)
    patient_name = get_random_patient(date_of_visit)

    # Extract values from scm entry
    condition = csm_entry["condition"].iloc[0]
    symptoms = csm_entry["symptoms"].iloc[0]
    medication = csm_entry["medication"].iloc[0]

    # Assemble dictionary
    event = {"medical.hospital_name": hospital_name, "medical.date_of_visit": date_of_visit, "medical.doctors_name": doctor_name,
             "medical.symptoms": symptoms, "medical.condition": condition, "medical.medication": medication, "medical.patients_name": patient_name}

    return event
