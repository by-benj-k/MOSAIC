"""
financial_event_generation.py

This module contains the code to generate the financial entry of a seed.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code import config
from typing import Union
import pandas as pd
import datetime
import random
import json


def get_random_company_and_location() -> tuple[str, str]:
    """
    Returns the name of a random company and the country it is located in.

    Returns:
        tuple[str, str]: A tuple containing the company name and location.
    """

    # Choose a random row (which represents a country)
    random_row = random.randint(0, config.E_COUNTRIES_FILE_LENGTH - 1)

    # Traverse companies file and pick chosen row
    with open(config.COMPANY_INSTANCES_PATH, "r", encoding='utf-8') as companies:
        for i, company_list in enumerate(companies):
            if i == random_row:
                company_entry = json.loads(company_list)
                break

    # Choose a random company
    return random.choice(company_entry["companies"]), company_entry["country"]


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


def get_ceo_name(company_name: str, company_location: str, transaction_date: str) -> str:
    """
    Finds the name of the company ceo or returns unknown.

    Parameters:
        company_name (str): The name of the company.
        company_location (str): The country the company is from.
        transaction_date (str): The date of the transaction.

    Returns:
        str: The name of the CEO or unknown.
    """

    # Storage for ceo name
    ceo_name = "Unknown"

    # Extract year from date
    year_of_transaction = int(transaction_date.split("-")[2])

    # Traverse human instances and search for ceo
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
        for human in humans:
            # Fetch content
            human_content = json.loads(human)

            if human_content["occupation"] == "CEO" and human_content["is_ceo_of"] == company_name and human_content["nationality"] == company_location and (18 <= year_of_transaction - human_content["birth_year"] <= 100):
                ceo_name = human_content["name"]
                break

    return ceo_name


def get_employee_name(company_name: str, company_location: str, transaction_date: str) -> str:
    """
    Finds the name of an employee of the company or returns unknown.

    Parameters:
        company_name (str): The name of the company.
        company_location (str): The country the company is from.
        transaction_date (str): The date of the transaction.

    Returns:
        str: The name of an employee or unknown.
    """

    # Storage for all employees of the company
    all_employees_of_company = []

    # Extract year from date
    year_of_transaction = int(transaction_date.split("-")[2])

    # Traverse human instances and search for employees
    with open(config.HUMAN_INSTANCES_PATH, "r", encoding='utf-8') as humans:
        for human in humans:
            # Fetch content
            human_content = json.loads(human)

            if human_content["occupation"] == "Employee" and human_content["is_employee_at"] == company_name and human_content["nationality"] == company_location and (18 <= year_of_transaction - human_content["birth_year"] <= 100):
                all_employees_of_company.append(human_content["name"])

    if len(all_employees_of_company) == 0:
        return "Unknown"

    return random.choice(all_employees_of_company)


def generate_financial_event(entity_to_count: dict[str, int]) -> dict[str, Union[int, str]]:
    """
    Generates the entries for a single financial event.

    Parameters:
        entity_to_count (dict[str, str]): Maps entities to the number of occurrences in the current seed.

    Returns:
        dict[str, Union[int, str]]: A dictionary containing the event and the attributes.
    """

    # Create event instance
    company_name, company_location = get_random_company_and_location()
    quarter = random.randint(1, 4)
    stock_ticker = "".join([c for c in company_name if c.isupper()])
    revenue = random.randint(1, 1000000000)
    transaction_date = get_random_date()
    transaction_amount = random.randint(1, 1000000)
    ceo_name = get_ceo_name(
        company_name, company_location, transaction_date)
    employee_authorized_transaction = get_employee_name(
        company_name, company_location, transaction_date)

    # Compute account id
    country_information = pd.read_csv(config.E_COUNTRIES_FILE_PATH)
    country_iso_code = country_information.loc[country_information["name"]
                                               == company_location, "iso3"].values[0]
    account_id = f"{stock_ticker}-{country_iso_code}-{random.randint(1, 1000000000)}"

    # Assemble dictionary
    event = {"financial.company_name": company_name, "financial.ceos_name": ceo_name, "financial.quarter": quarter, "financial.stock_ticker": stock_ticker, "financial.revenue": revenue,
             "financial.account_id": account_id, "financial.transaction_date": transaction_date, "financial.transaction_amount": transaction_amount, "financial.employees_authorized_transaction": employee_authorized_transaction}

    return event
