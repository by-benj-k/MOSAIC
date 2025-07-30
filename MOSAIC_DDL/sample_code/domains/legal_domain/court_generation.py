"""
court_generation.py

This module contains the code to generate a pool of court instances.

Author: Benjamin Koch
Date: June 2025
"""

# Imports
from sample_code.helpers_event_generation import extract_formatting_fields
from sample_code import config
import random
import json
import csv


def generate_courts() -> None:
    """
    Generates a pool of court instances for each country.
    """

    # Create artificial naming blocks (naming block content generated with the help of ChatGPT)
    prefixes = ["National", "Federal", "High", "Supreme", "Central", "State", "Regional", "Provincial", "Local", "Unified",
                "Metropolitan", "Municipal", "District", "Continental", "International", "Superior", "Royal", "Constitutional"]
    types = ["Court", "Tribunal", "Bench", "Judiciary", "Chamber",
             "Division", "panel", "Jurisdiction", "Circuit", "Commission", "Board"]
    regions = ["Northern", "Southern", "Eastern", "Western", "Central", "Metropolitan",
               "Urban", "Rural", "Pacific", "Atlantic", "Continental", "Mountain", "Capital", "National"]
    modifiers = ["Criminal", "Civil", "Commercial", "Appeals", "Family", "Administrative", "Constitutional", "Labor", "Tax", "Juvenile",
                 "Military", "Antitrust", "Environmental", "Human Rights", "Religious", "Small Claims", "Trade", "Bankruptcy", "Patent", "Election"]
    descriptors = ["Authority", "Body", "Council", "Commission", "Office", "Section", "Service",
                   "Jurisdiction", "Administration", "Forum", "House", "Registry", "Aribtration Centre", "Mediation Panel"]
    suffixes = ["of Justic", "of Appeal", "for Civil Matters", "for Criminal Affairs", "of Commerce", "for Public Law",
                "of Equity", "of the Realm", "for Constitutional Review", "for Human Rights", "for National Security", "of Final Instance"]

    # Define template for courts (template content generated with the help of ChatGPT)
    court_template = ["{prefixes} {types} of {country}", "{prefixes} {modifiers} {types} of {country}", "{modifiers} {types} of {country}", "{types} of {regions} Jurisdiction of {country}", "{regions} {modifiers} {types} of {country}", "{regions} {types} of {modifiers} of {country}", "{prefixes} {types} for {modifiers} Matters of {country}", "{prefixes} {types} for {modifiers} Affairs of {country}", "{types} for {modifiers} Cases of {country}", "{modifiers} Division of the {prefixes} {types} of {country}", "{modifiers} Tribunal of the {regions} of {country}", "{prefixes} Tribunal for {modifiers} Cases of {country}", "{modifiers} Bench of {regions} Justic of {country}", "The {types} of {regions} of {country}", "{prefixes} {types} of {modifiers} of {country}", "{prefixes} {descriptors} for {modifiers} Law of {country}", "{regions} {descriptors} of {modifiers} Justice of {country}",
                      "{prefixes} {descriptors} on {modifiers} Matters of {country}", "{types} of the {prefixes} {descriptors} of {country}", "{prefixes} {modifiers} {types} {suffixes} of {country}", "{regions} {types} {suffixes} of {country}", "{types} {suffixes} of {country}", "{modifiers} {types} {suffixes} of {country}", "Office of the {modifiers} {types} of {country}", "Judicial {descriptors} of {regions} of {country}", "Council for {modifiers} Justice of {country}", "Department of {modifiers} Jurisdiction of {country}", "Commission on {modifiers} Law of {country}", "{prefixes} Chamber for {modifiers} Review of {country}", "{modifiers} Adjudication Panel of {country}", "{prefixes} Aribtration Board of {country}", "{regions} Mediation Centre of {country}", "Unified {modifiers} Court System of {country}", "{prefixes} Court of Final Appeal of {country}"]

    # Iterate through countries and create artificial courts
    with open(config.E_COUNTRIES_FILE_PATH, "r", encoding='utf-8') as countries, open(config.COURT_INSTANCES_PATH, "w", encoding='utf-8', buffering=1) as courts:
        # Reader for csv rows and skip header
        country_reader = csv.reader(countries)
        next(country_reader)

        for country in country_reader:
            # Fetch country name
            country_name = country[1]

            # Compute number of courts
            number_of_courts = random.randint(
                1, config.MAX_NUMBER_OF_COURTS_PER_COUNTRY)

            # Compute courts
            court_names = set()
            while (len(court_names) < number_of_courts):
                # Fetch random template and extract formatting fields
                template = random.choice(court_template)
                formatting_fields = extract_formatting_fields(template)

                # Fetch random values for fields
                formatting_fields_values = {"prefixes": random.choice(prefixes), "types": random.choice(types), "regions": random.choice(
                    regions), "modifiers": random.choice(modifiers), "descriptors": random.choice(descriptors), "suffixes": random.choice(suffixes), "country": country_name}

                court_names.add(template.format(
                    **{v: formatting_fields_values[v] for v in formatting_fields}))

            court_names = list(court_names)

            # Write courts to file
            court_names_dict = {"courts": court_names, "country": country_name}

            courts.write(json.dumps(court_names_dict) + "\n")
