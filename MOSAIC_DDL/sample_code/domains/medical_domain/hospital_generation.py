"""
hospital_generation.py

This module contains the code to generate a pool of hospital instances.

Author: Benjamin Koch
Date: June 2025
"""

# Imports
from sample_code.helpers_event_generation import extract_formatting_fields
from sample_code import config
import random
import json
import csv


def generate_hospitals() -> None:
    """
    Generates a pool of hospital instances for each country.
    """

    # Create artificial naming blocks (naming block content generated with the help of ChatGPT)
    directions = ["North", "East", "South", "West", "Central", "Upper", "Lower", "Inner", "Outer", "Northeast", "Northwest", "Southeast", "Southwest", "Mid", "Inland", "Rural", "Urban",
                  "Far East", "Far West", "Near North", "Near South", "Greater", "Lesser", "High", "Low", "Trans", "Inter", "Sub", "Cross", "New", "Old", "Remote", "Upland", "Midwest", "Deep South"]
    districts = ["District", "Sector", "Zone", "Division", "Ward", "Canton", "Prefecture", "Borough", "Region", "Enclave", "Cluster", "Corridor",
                 "Province", "BlocK", "Territory", "Union", "Constituency", "Municipality", "Parish", "Section", "Area", "Jurisdiction", "Subdistrict", "Commune"]
    regions = ["Valley", "Ridge", "Highlands", "Lowlands", "River Region", "Forest", "Plains", "Hills",
               "Frontier", "Plateau", "Savannah", "Peninsula", "Basin", "Marsh", "Steppe", "Tundra", "Wetlands"]
    descriptors = ["Clinic", "Health Center", "General Hospital", "Medical Center", "Wellness Facility", "Health Station", "Referral Hospital", "Medical Institute",
                   "Diagnostic Hub", "Emergency Complex", "Primary Care Unit", "Specialty Hospital", "Treament Center", "Medical Pavilion", "Health Hub", "Care Facility", "Surgical Center"]

    # Define template for local, regional and national hospitals (template content generated with the help of ChatGPT)
    local_template = ["{directions} {districts} {descriptors} of {country}", "{districts} {descriptors} of {country}", "{directions} {descriptors} of {country}", "Community Medical Post of {country}",
                      "Primary Health Unit of {country}", "{directions} {regions} {descriptors} of {country}", "Satellite {descriptors} of {country}", "Mobile {descriptors} of {country}"]
    regional_template = ["{directions} Regional Hospital of {country}", "{regions} Medical Center of {country}", "{districts} General Hospital of {country}", "{regions} Healt Authority of {country}", "{directions} {districts} General Hospital of {country}",
                         "{regions} Referral Hospital of {country}", "{regions} Treatment Network of {country}", "Inter-{districts} Medical Facility of {country}", "Central {regions} Health System of {country}", "{directions} Corridor Hospital Group of {country}", "{districts} Specialty Hospital of {country}"]
    national_template = ["National Hospital of {country}", "{country} Central Medical Institute", "{country} University Hospital", "National Referral Center of {country}", "National General Hospital of {country}",
                         "Central Health Complex of {country}", "Ministry of Health - National Hospital of {country}", "{country} Medical Research Institute", "{country} National Medical Authority", "Federated National Hospital of {country}"]

    # Iterate through countries and create artificial hospitals
    with open(config.E_COUNTRIES_FILE_PATH, "r", encoding='utf-8') as countries, open(config.HOSPITAL_INSTANCES_PATH, "w", encoding='utf-8', buffering=1) as hospitals:
        # Reader for csv rows and skip header
        country_reader = csv.reader(countries)
        next(country_reader)

        for country in country_reader:
            # Fetch country name
            country_name = country[1]

            # Compute number of hospitals for each type
            number_of_local_hospitals = random.randint(
                1, config.MAX_NUMBER_OF_LOCAL_HOSPITALS_PER_COUNTRY)
            number_of_regional_hospitals = random.randint(
                1, config.MAX_NUMBER_OF_REGIONAL_HOSPITALS_PER_COUNTRY)
            number_of_national_hospitals = random.randint(
                1, config.MAX_NUMBER_OF_NATIONAL_HOSPITALS_PER_COUNTRY)

            # Compute local hospitals
            local_hospital_names = set()
            while (len(local_hospital_names) < number_of_local_hospitals):
                # Fetch random template and extract formatting fields
                template = random.choice(local_template)
                formatting_fields = extract_formatting_fields(template)

                # Fetch random values for fields
                formatting_fields_values = {"directions": random.choice(directions), "districts": random.choice(
                    districts), "regions": random.choice(regions), "descriptors": random.choice(descriptors), "country": country_name}

                local_hospital_names.add(template.format(
                    **{v: formatting_fields_values[v] for v in formatting_fields}))

            local_hospital_names = list(local_hospital_names)

            # Compute regional hospitals
            regional_hospital_names = set()
            while (len(regional_hospital_names) < number_of_regional_hospitals):
                # Fetch random template and extract formatting fields
                template = random.choice(regional_template)
                formatting_fields = extract_formatting_fields(template)

                # Fetch random values for fields
                formatting_fields_values = {"directions": random.choice(directions), "districts": random.choice(
                    districts), "regions": random.choice(regions), "descriptors": random.choice(descriptors), "country": country_name}

                regional_hospital_names.add(template.format(
                    **{v: formatting_fields_values[v] for v in formatting_fields}))

            regional_hospital_names = list(regional_hospital_names)

            # Compute national hospitals
            national_hospital_names = set()
            while (len(national_hospital_names) < number_of_national_hospitals):
                # Fetch random template and extract formatting fields
                template = random.choice(national_template)
                formatting_fields = extract_formatting_fields(template)

                # Fetch random values for fields
                formatting_fields_values = {"directions": random.choice(directions), "districts": random.choice(
                    districts), "regions": random.choice(regions), "descriptors": random.choice(descriptors), "country": country_name}

                national_hospital_names.add(template.format(
                    **{v: formatting_fields_values[v] for v in formatting_fields}))

            national_hospital_names = list(national_hospital_names)

            # Write local, regional and national hospitals to file
            hospitals_dict = {"local_hospitals": local_hospital_names, "regional_hospitals": regional_hospital_names,
                              "national_hospitals": national_hospital_names, "country": country_name}

            hospitals.write(json.dumps(hospitals_dict) + "\n")
