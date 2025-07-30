"""
educational_event_generation.py

This module contains the code to generate the educational entry of a seeds.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code.helpers_event_generation import get_random_csv_entry
from sample_code import config
from typing import Union
import random
import json


def get_random_school_and_location() -> tuple[str, str]:
    """
    Returns the name of a random school and the country it is located in.

    Returns:
        tuple[str, str]: A tuple containing the school name and location.
    """

    # Choose a random row (which represent a country)
    random_row = random.randint(0, config.E_COUNTRIES_FILE_LENGTH - 1)

    # Traverse school file and pick chosen row
    with open(config.SCHOOL_INSTANCES_PATH, "r", encoding='utf-8') as schools:
        for i, school in enumerate(schools):
            if i == random_row:
                school_entry = json.loads(school)
                break

    # Choose a random school
    return random.choice(school_entry["schools"]), school_entry["country"]


def get_random_instructor(school_name: str, school_location: str, school_year: int) -> str:
    """
    Returns an instructor from the school or some random instructor from the country.

    Parameters:
        school_name (str): The name of the selected school.
        school_location (str): The country the selected school is located in.
        school_year (int): The current school year.

    Returns:
        str: The randomly selected instructor from the selected school or country, together with his email address and id.
    """

    # Storage for all instructors of the school
    all_instructors_of_school = []

    # Storage for random instructor
    random_instructor = ""

    # Traverse humans and search for instructor working at the school
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
        for human in humans:
            # Fetch content
            human_content = json.loads(human)

            if human_content["occupation"] == "Instructor" and human_content["is_instructor_at"] == school_name and (18 <= school_year - human_content["birth_year"] <= 100):
                all_instructors_of_school.append(human_content)

    if len(all_instructors_of_school) == 0:
        # Storage for all instructors of the country
        all_instructors_of_country = []

        with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
            for human in humans:
                # Fetch content
                human_content = json.loads(human)

                if human_content["occupation"] == "Instructor" and human_content["nationality"] == school_location and (18 <= school_year - human_content["birth_year"] <= 100):
                    all_instructors_of_country.append(human_content)

        if len(all_instructors_of_country) == 0:
            random_instructor = "Unknown"
            random_instructor_email_address = "Unknown"
            random_instructor_id = "Unknown"
        else:
            random_instructor_content = random.choice(
                all_instructors_of_country)
            random_instructor = random_instructor_content["name"]
            random_instructor_email_address = random_instructor_content["instructor_email_address"]
            random_instructor_id = random_instructor_content["instructor_id"]
    else:
        random_instructor_content = random.choice(all_instructors_of_school)
        random_instructor = random_instructor_content["name"]
        random_instructor_email_address = random_instructor_content["instructor_email_address"]
        random_instructor_id = random_instructor_content["instructor_id"]

    return random_instructor, random_instructor_email_address, random_instructor_id


def get_random_student(school_name: str, school_location: str, school_year: int) -> str:
    """
    Returns a student from the school or some random student from the country.

    Parameters:
        school_name (str): The name of the selected school.
        school_location (str): The country the selected school is located in.
        school_year (int): The current school year.

    Returns:
        str: The randomly selected student from the selected school or country, together with his email address and id.
    """

    # Storage for all students of the school
    all_students_of_school = []

    # Storage for random student
    random_student = ""

    # Traverse humans and search for student studying at the school
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
        for human in humans:
            # Fetch content
            human_content = json.loads(human)

            if human_content["occupation"] == "Student" and human_content["is_student_at"] == school_name and (5 <= school_year - human_content["birth_year"] <= 100):
                all_students_of_school.append(human_content)

    if len(all_students_of_school) == 0:
        # Storage for all students of the country
        all_students_of_country = []

        with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
            for human in humans:
                # Fetch content
                human_content = json.loads(human)

                if human_content["occupation"] == "Student" and human_content["nationality"] == school_location and (5 <= school_year - human_content["birth_year"] <= 100):
                    all_students_of_country.append(human_content)

        if len(all_students_of_country) == 0:
            random_student = "Unknown"
            random_student_email_address = "Unknown"
            random_student_id = "Unknown"
        else:
            random_student_content = random.choice(all_students_of_country)
            random_student = random_student_content["name"]
            random_student_email_address = random_student_content["student_email_address"]
            random_student_id = random_student_content["student_id"]
    else:
        random_student_content = random.choice(all_students_of_school)
        random_student = random_student_content["name"]
        random_student_email_address = random_student_content["student_email_address"]
        random_student_id = random_student_content["student_id"]

    return random_student, random_student_email_address, random_student_id


def generate_educational_event(entity_to_count: dict[str, int]) -> dict[str, Union[int, str]]:
    """
    Generates the entry for a single educational events.

    Parameters:
        entity_to_count (dict[str, str]): Maps entities to the number of occurrences in the current seed.

    Returns:
        dict[str, Union[int, str]]: A dictionary containing the event and the attributes.
    """

    # Create event instance
    course_name = get_random_csv_entry(
        config.A_COURSE_NAMES_FILE_PATH, config.A_COURSE_NAMES_FILE_LENGTH, "course_name")
    semester = random.randint(1, 10)
    school_name, school_location = get_random_school_and_location()
    school_year = random.randint(
        config.START_DATE.year, config.END_DATE.year)
    instructor_name, instructor_email_address, instructor_id = get_random_instructor(
        school_name, school_location, school_year)
    student_name, student_email_address, student_id = get_random_student(
        school_name, school_location, school_year)

    # Compute grade and gpa based on probabilities
    grades = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25,
              3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0, 5.25, 5.5, 5.75, 6.0]
    grades_distribution = [0.005, 0.005, 0.005, 0.005, 0.001, 0.015, 0.02, 0.025,
                           0.03, 0.04, 0.05, 0.06, 0.10, 0.12, 0.13, 0.11, 0.08, 0.05, 0.03, 0.015, 0.005]

    grade = random.choices(grades, grades_distribution, k=1)[0]
    gpa = random.choices(grades, grades_distribution, k=1)[0]

    # Assemble dictionary
    event = {"educational.course_name": course_name, "educational.instructors_name": instructor_name, "educational.instructors_email_address": instructor_email_address, "educational.instructors_id": instructor_id, "educational.semester": semester,
             "educational.grade": grade, "educational.gpa": gpa, "educational.school_name": school_name, "educational.school_year": school_year, "educational.students_name": student_name, "educational.students_email_address": student_email_address, "educational.students_id": student_id}

    return event
