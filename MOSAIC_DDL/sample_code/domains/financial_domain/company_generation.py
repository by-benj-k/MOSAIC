"""
company_generation.py

This module contains the code to generate a pool of company instances.

Author: Benjamin Koch
Date: June 2025
"""

# Imports
from sample_code.helpers_event_generation import extract_formatting_fields
from sample_code import config
import random
import json
import csv


def generate_companies() -> None:
    """
    Generates a pool of company instances for each country.
    """

    # Create artificial naming blocks (naming block content generated with the help of ChatGPT)
    prefixes = ["Meta", "Neo", "Omni", "Alpha", "Nova", "Hyper", "Aero", "Quantum", "Opti",
                "Global", "Cyber", "Blue", "Green", "Next", "Eco", "Smart", "Bright", "Open", "Core"]
    sectors = ["Tech", "Solutions", "Industries", "Systems", "Holdings", "Enterprises", "Dynamics", "Analytics", "Logistics", "Consulting", "Biotech",
               "Digital", "Capital", "Ventures", "Networks", "Foods", "Energy", "Media", "Security", "Mobility", "Robotics", "Finance", "Retail", "Cloud"]
    types = ["Inc", "Ltd", "LLC", "Corp", "GmbH", "PLC", "S.A.", "S.p.A.", "LLP",
             "Co.", "Group", "Consortium", "Agency", "Partners", "Company", "Labs", "Sutdio"]
    regions = ["North", "South", "East", "West", "Central", "Pacific", "Atlantic", "European", "Global",
               "Transnational", "Continental", "PanAmerican", "Nordic", "Asian", "Mediterranean", "Euro-Asian"]
    modifiers = ["Advanced", "Integrated", "Premier", "Unified", "NextGen", "Smart", "Elite", "Secure", "Innovative", "Eco", "Agile", "Strategic", "Trusted", "Dynamic", "Accelerated", "Future", "Efficient",
                 "Modular", "Virtual", "Scalable", "Robust", "Open", "Seamless", "Sustainable", "Decentralized", "Collaborative", "Automated", "Green", "Responsive", "Mobile", "Cross-Border", "High-Performance", "Adaptive"]
    descriptors = ["Network", "Labs", "Collective", "Initiative", "Alliance", "Team", "Firm", "Bureau", "Nexus", "Platofrm",
                   "Exchanged", "Guild", "Circle", "Union", "Node", "Matrix", "Engine", "Stack", "Sphere", "Grid", "Bridge", "Forge", "Space", "Flow"]

    # Define template for companies (template content generated with the help of ChatGPT)
    company_template = ["{prefixes}{sectors} {types} based in {country}", "{modifiers} {sectors} {types} based in {country}", "{prefixes} {sectors} based in {country}", "{prefixes}-{sectors} {types} based in {country}", "{sectors} & {sectors} {types} based in {country}", "{regions} {sectors} {types} based in {country}", "{regions} {modifiers} {sectors} {types} based in {country}", "{regions} {prefixes} {sectors} based in {country}", "{prefixes} {regions} {sectors} based in {country}", "{regions} {prefixes}-{sectors} {types} based in {country}",
                        "{prefixes} {modifiers} {sectors} {types} based in {country}", "{modifiers} {prefixes} {sectors} based in {country}", "{sectors} {descriptors} {types} based in {country}", "{prefixes} {sectors} & {descriptors} based in {country}", "{prefixes}.{sectors} based in {country}", "{prefixes}{sectors}.{types} based in {country}", "{modifiers}-{sectors} {types} based in {country}", "{sectors}-{prefixes} {types} based in {country}", "{prefixes}{modifiers}{sectors} {types} based in {country}"]

    # Iterate through countries and create artificial companies
    with open(config.E_COUNTRIES_FILE_PATH, "r", encoding='utf-8') as countries, open(config.COMPANY_INSTANCES_PATH, "w", encoding='utf-8', buffering=1) as companies:
        # Reader for csv rows and skip header
        country_reader = csv.reader(countries)
        next(country_reader)

        for country in country_reader:
            # Fetch country name
            country_name = country[1]

            # Compute number of companies
            number_of_companies = random.randint(
                1, config.MAX_NUMBER_OF_COMPANIES_PER_COUNTRY)

            # Compute companies
            company_names = set()
            while (len(company_names) < number_of_companies):
                # Fetch random template and extract formatting fields
                template = random.choice(company_template)
                formatting_fields = extract_formatting_fields(template)

                # Fetch random values for fields
                formatting_fields_values = {"prefixes": random.choice(prefixes), "sectors": random.choice(sectors), "types": random.choice(
                    types), "regions": random.choice(regions), "modifiers": random.choice(modifiers), "descriptors": random.choice(descriptors), "country": country_name}

                company_names.add(template.format(
                    **{v: formatting_fields_values[v] for v in formatting_fields}))

            company_names = list(company_names)

            # Write companies to file
            company_names_dict = {
                "companies": company_names, "country": country_name}

            companies.write(json.dumps(company_names_dict) + "\n")
