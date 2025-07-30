"""
educational_modify_human.py

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


def educational_modify_human() -> None:
    """
    Modifies attributes of humans which are instructors or students.
    """

    # Count number of humans
    number_of_humans = count_number_of_humans()

    # Iterate through humans
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans, open(config.HUMAN_INSTANCES_TEMPORARY_PATH, "w", encoding='utf-8') as humans_temporary:
        for human in tqdm(humans, total=number_of_humans, desc=f"{'\033[34m'}Applying modifications for educational domain...{'\033[0m'}"):
            # Fetch content
            human_content = json.loads(human)

            if human_content["occupation"] == "Instructor":
                # Search schools from his country
                with open(config.SCHOOL_INSTANCES_PATH, "r", encoding='utf-8') as schools:
                    for school in schools:
                        # Fetch content
                        school_content = json.loads(school)

                        if school_content["country"] == human_content["nationality"]:
                            # Choose a random school
                            random_school = random.choice(
                                school_content["schools"])

                            # Assign new attribute to human
                            human_content["is_instructor_at"] = random_school
                            break

                # Compute name school abbreviation
                name_concatenation = ".".join(
                    word.lower() for word in human_content["name"].split())
                school_abbreviation = "".join(word[0].upper(
                ) for word in human_content["is_instructor_at"].split())

                # Create school instructor email and id
                instructor_email_address = f"{name_concatenation}@instructor.{school_abbreviation}"
                instructor_id = f"{name_concatenation}-{school_abbreviation}-{str(random.randint(1, 8000000000))}"

                # Assign new attributes to human
                human_content["instructor_email_address"] = instructor_email_address
                human_content["instructor_id"] = instructor_id

                humans_temporary.write(json.dumps(human_content) + "\n")
            elif human_content["occupation"] == "Student":
                # Search schools from his country
                with open(config.SCHOOL_INSTANCES_PATH, "r", encoding='utf-8') as schools:
                    for school in schools:
                        # Fetch content
                        school_content = json.loads(school)

                        if school_content["country"] == human_content["nationality"]:
                            # Choose a random school
                            random_school = random.choice(
                                school_content["schools"])

                            # Assign new attribute to human
                            human_content["is_student_at"] = random_school
                            break

                # Compute name school abbreviation
                name_concatenation = ".".join(
                    word.lower() for word in human_content["name"].split())
                school_abbreviation = "".join(
                    word[0].upper() for word in human_content["is_student_at"].split())

                # Create school instructor email and id
                student_email_address = f"{name_concatenation}@student.{school_abbreviation}"
                student_id = f"{name_concatenation}-{school_abbreviation}-{str(random.randint(1, 8000000000))}"

                # Assign new attributes to human
                human_content["student_email_address"] = student_email_address
                human_content["student_id"] = student_id

                humans_temporary.write(json.dumps(human_content) + "\n")
            else:
                humans_temporary.write(json.dumps(human_content) + "\n")

    # Overwrite old file
    os.replace(config.HUMAN_INSTANCES_TEMPORARY_PATH,
               config.HUMAN_INSTANCES_PATH)
