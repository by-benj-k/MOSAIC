"""
financial_modify_human.py

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


def financial_modify_human() -> None:
    """
    Modifies attributes of humans which are ceos or employees.
    """

    # Count number of humans
    number_of_humans = count_number_of_humans()

    # Iterate through humans
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans, open(config.HUMAN_INSTANCES_TEMPORARY_PATH, "w", encoding='utf-8') as humans_temporary:
        for human in tqdm(humans, total=number_of_humans, desc=f"{'\033[34m'}Applying modifications for financial domain...{'\033[0m'}"):
            # Fetch content
            human_content = json.loads(human)

            if human_content["occupation"] == "CEO":
                # Search companies from his country
                with open(config.COMPANY_INSTANCES_PATH, "r", encoding='utf-8') as companies:
                    for company in companies:
                        # Fetch content
                        company_content = json.loads(company)

                        if company_content["country"] == human_content["nationality"]:
                            # Choose a random company
                            random_company = random.choice(
                                company_content["companies"])

                            # Assign new attribute to human
                            human_content["is_ceo_of"] = random_company
                            break
                humans_temporary.write(json.dumps(human_content) + "\n")
            elif human_content["occupation"] == "Employee":
                # Search companies from his country
                with open(config.COMPANY_INSTANCES_PATH, "r", encoding='utf-8') as companies:
                    for company in companies:
                        # Fetch content
                        company_content = json.loads(company)

                        if company_content["country"] == human_content["nationality"]:
                            # Choose a random company
                            random_company = random.choice(
                                company_content["companies"])

                            # Assign new attribute to human
                            human_content["is_employee_at"] = random_company
                            break
                humans_temporary.write(json.dumps(human_content) + "\n")
            else:
                humans_temporary.write(json.dumps(human_content) + "\n")

    # Overwrite old file
    os.replace(config.HUMAN_INSTANCES_TEMPORARY_PATH,
               config.HUMAN_INSTANCES_PATH)
