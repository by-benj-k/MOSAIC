"""
medical_modify_human.py

This module contains the code to modify the previously generated pool of human instances.

Author: Benjamin Koch
Date: June 2025
"""

# Imports
from sample_code.helpers_event_generation import count_number_of_humans
from sample_code import config
from tqdm import tqdm
import random
import json
import os


def medical_modify_human() -> None:
    """
    Modifies attributes of humans which are doctors.
    """

    # Count number of humans
    number_of_humans = count_number_of_humans()

    # Iterate through humans
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans, open(config.HUMAN_INSTANCES_TEMPORARY_PATH, "w", encoding='utf-8') as humans_temporary:
        for human in tqdm(humans, total=number_of_humans, desc=f"{'\033[34m'}Applying modifications for medical domain...{'\033[0m'}"):
            # Fetch content
            human_content = json.loads(human)

            if human_content["occupation"] == "Doctor":
                # Search hospitals from his country
                with open(config.HOSPITAL_INSTANCES_PATH, "r", encoding='utf-8') as hospitals:
                    for hospital in hospitals:
                        # Fetch content
                        hospital_content = json.loads(hospital)

                        if hospital_content["country"] == human_content["nationality"]:
                            # Choose a random hospital category
                            hospital_category = random.choice(
                                ["local_hospitals", "regional_hospitals", "national_hospitals"])

                            # Choose a random hospital from the chose category
                            random_hospital = random.choice(
                                hospital_content[hospital_category])

                            # Assign new attribute to human
                            human_content["works_at"] = random_hospital
                            break
                humans_temporary.write(json.dumps(human_content) + "\n")
            else:
                humans_temporary.write(json.dumps(human_content) + "\n")

    # Overwrite old file
    os.replace(config.HUMAN_INSTANCES_TEMPORARY_PATH,
               config.HUMAN_INSTANCES_PATH)
