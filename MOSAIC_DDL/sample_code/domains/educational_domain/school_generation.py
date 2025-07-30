"""
school_generation.py

This module contains the code to generate a pool of school instances.

Author: Benjamin Koch
Date: June 2025
"""

# Imports
from sample_code.helpers_event_generation import extract_formatting_fields
from sample_code import config
import random
import json
import csv


def generate_schools() -> None:
    """
    Generates a pool of school instances for each country.
    """

    # Create artificial naming blocks (naming block content generated with the help of ChatGPT)
    prefixes = ["Royal", "National", "United", "Global", "Central", "Independent", "Progressive", "International", "New",
                "Saint", "Sacred", "Frontier", "Modern", "Colonial", "Republican", "Continental", "Urban", "Grand", "Academic"]
    types = ["University", "College", "Academy", "Institute", "School", "Faculty", "Center",
             "Campus", "Conservatory", "Polytechnic", "Seminary", "Graduate School", "Training Center"]
    regions = ["Northern", "Southern", "Eastern", "Western", "Central", "Urban", "Rural", "Metropolitan",
               "Highland", "Valley", "Capital", "Borderlands", "Continental", "Interstate", "Transnational"]
    modifiers = ["Technical", "Vocational", "Scientific", "Medical", "Liberal Arts", "Business", "Agricultural", "Military", "Pedagogical", "Engineering",
                 "Religious", "Digital", "Environmental", "Classical", "Contemporary", "Multilingual", "Multidisciplinary", "Artistic", "Theological", "Computational", "Civic"]
    descriptors = ["of Technology", "of Sciences", "of Humanities", "of Education", "of the Arts", "of Social Sciences", "of Theology", "of Innovation", "of Modern Languages", "of Advanced Studies",
                   "of Business", "of Law", "of Public Affairs", "of Medicine", "of Environmental Studies", "of Engineering", "of Economics", "of Agriculture", "for Teacher Training", "of Political Science"]
    suffixes = ["of Excellence", "for Advanced Learning", "for Global Impact", "for Future Leaders", "of the Nation",
                "of Innovation", "of the Republic", "for Peace and Development", "of Civic Responsibility", "for Social Transformation"]

    # Define template for schools (template content generated with the help of ChatGPT)
    school_template = ["{prefixes} {types} - {country}", "{regions} {types} - {country}", "{modifiers} {types} - {country}", "{types} of {regions} - {country}", "{types} {descriptors} - {country}", "{types} {suffixes} - {country}", "{prefixes} {modifiers} {types} - {country}", "{regions} {modifiers} {types} - {country}", "{prefixes} {types} {descriptors} - {country}", "{prefixes} {types} {suffixes} - {country}", "{modifiers} {types} {descriptors} - {country}", "{modifiers} {types} {suffixes} - {country}", "{types} of {modifiers} Studies - {country}", "{types} of {modifiers} Education - {country}", "{types} for {modifiers} Innovation - {country}", "{types} for {modifiers} Training - {country}", "{prefixes} {types} for {modifiers} Studies - {country}", "{prefixes} {modifiers} {types} of {regions} - {country}", "{types} of {modifiers} and {modifiers} - {country}", "{types} for {modifiers} and Civic Engagement - {country}",
                       "Faculty of {modifiers} Sciences - {country}", "School of {modifiers} Studies - {country}", "Institute for {modifiers} Leadership - {country}", "College of {modifiers} and {modifiers} - {country}", "University of {regions} {modifiers} Studies - {country}", "{prefixes} {types} of the {regions} - {country}", "{regions} {types} for {modifiers} Research - {country}", "{types} of the {prefixes} Union - {country}", "{types} of Higher {modifiers} Education - {country}", "National {types} of {modifiers} and Innovation - {country}", "Graduate {types} of {modifiers} Development - {country}", "{modifiers} Polytechnic {descriptors} - {country}", "Academy of {modifiers} Leadership - {country}", "Center for {modifiers} Learning - {country}", "{types} for the Study of {modifiers} Society - {country}", "{prefixes} Conservatory of the {regions} - {country}", "Open {types} for {modifiers} Disciplines - {country}"]

    # Iterate through countires and create artificial schools
    with open(config.E_COUNTRIES_FILE_PATH, "r", encoding='utf-8') as countries, open(config.SCHOOL_INSTANCES_PATH, "w", encoding='utf-8', buffering=1) as schools:
        # Reader for csv rows and skip header
        country_reader = csv.reader(countries)
        next(country_reader)

        for country in country_reader:
            # Fetch country name
            country_name = country[1]

            # Compute number of schools
            number_of_schools = random.randint(
                1, config.MAX_NUMBER_OF_SCHOOLS_PER_COUNTRY)

            # Compute schools
            school_names = set()
            while (len(school_names) < number_of_schools):
                # Fetch random template and extract formatting fields
                template = random.choice(school_template)
                formatting_fields = extract_formatting_fields(template)

                # Fetch random values for fields
                formatting_fields_values = {"prefixes": random.choice(prefixes), "types": random.choice(types), "regions": random.choice(
                    regions), "modifiers": random.choice(modifiers), "descriptors": random.choice(descriptors), "suffixes": random.choice(suffixes), "country": country_name}

                school_names.add(template.format(
                    **{v: formatting_fields_values[v] for v in formatting_fields}))

            school_names = list(school_names)

            # Write schools to file
            school_names_dict = {
                "schools": school_names, "country": country_name}

            schools.write(json.dumps(school_names_dict) + "\n")
