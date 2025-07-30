"""
occasion_vehicle_generation.py

This module contains the code to generate the vehicle entries of a seed.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code.helpers_event_generation import get_random_csv_entry, get_unique_values_from_function
import matplotlib.colors as colors
from sample_code import config
from typing import Union
from faker import Faker
import pandas as pd
import random

# Initialize handlers for packages
fake = Faker()


def get_random_type_manufacturer_production_fuel(date: str) -> tuple[str, str, str, str]:
    """
    Takes in the event date and samples a random vehicle type, manufacturer with production date before the event data and its fuel type.

    Parameters:
        date (str): The date of the event.

    Returns:
        tuple[str, str, str, str]: A tuple containing the vehicle type, manufacturer, production year and fuel type.
    """

    # Extract year from date
    event_year = date.split("-")[2]

    # Find all vehicles with production year before event date
    vehicle_information = pd.read_csv(
        config.TYPE_MANUFACTURER_PRODUCTION_FUEL_FILE_PATH)
    vehicles_matching_date = vehicle_information.loc[vehicle_information["production"] <= int(
        event_year)]

    # Sample random vehicle and extract fields
    random_vehicle = vehicles_matching_date.sample(n=1)
    vtype = random_vehicle.iloc[0]["type"]
    manufacturer = random_vehicle.iloc[0]["manufacturer"]
    first_production_year = random_vehicle.iloc[0]["production"]
    production_year = random.randint(
        int(first_production_year), int(event_year))
    fuel_type = random_vehicle.iloc[0]["fuel"]

    return vtype, manufacturer, str(production_year), fuel_type


def get_random_color() -> str:
    """
    Returns a random color name.

    Returns:
        str: The random color.
    """

    return random.choice(list(colors.CSS4_COLORS.keys()))


def get_random_license_plate(location: str) -> str:
    """
    Takes in the event location and returns a random license plate.

    Parameters:
        location (str): The location of the event.

    Returns:
        str: The random license plate.
    """

    # Extract country from event location
    country = location.split(",")[2]

    # Get country code
    country_information = pd.read_csv(config.E_COUNTRIES_FILE_PATH)
    country_iso_code = country_information.loc[country_information["name"]
                                               == country, "iso3"].values[0]

    # Construct license plate
    license_plate = f"LP-{country_iso_code}-{random.randint(0, 999999999):09d}"

    return license_plate


def get_random_vin() -> str:
    """
    Returns a random vin using the Faker package.

    Returns:
        str: The random vin.
    """

    return fake.vin()


def generate_vehicles(location: str, date: str, count: int) -> list[dict[str, Union[int, str]]]:
    """
    Generates the vehicle entries vehicle=v for all event=e.

    Parameters:
        location (str): The location of the event.
        date (str): The date of the event.
        count (int): The number of objects of the event.

    Returns:
        list[dict[str, Union[int, str]]]: A list containing multiple vehicle instances.
    """

    # Storage for all vehicles
    all_vehicles = []

    # Prepare unique attribtues for all vehicles
    all_license_plate_numbers = random.sample(range(0, 999999999), k=count)
    all_vins = get_unique_values_from_function(get_random_vin, count)

    # Create vehicle instances
    vehicle_index = 0
    for _ in range(count):
        # Fetch values
        type, manufacturer, production_year, fuel_type = get_random_type_manufacturer_production_fuel(
            date)
        color = get_random_color()
        condition = get_random_csv_entry(
            config.V_CONDITIONS_FILE_PATH, config.V_CONDITIONS_FILE_LENGTH, "v_conditions")

        # Compute license plate number
        country = location.split(",")[2]
        country_information = pd.read_csv(config.E_COUNTRIES_FILE_PATH)
        country_iso_code = country_information.loc[country_information["name"]
                                                   == country, "iso3"].values[0]
        license_plate_number = f"LP-{country_iso_code}-{all_license_plate_numbers[vehicle_index]:09d}"

        vin = all_vins[vehicle_index]

        # Assemble dictionary
        vehicle = {"occasion.vehicles.type": type, "occasion.vehicles.manufacturer": manufacturer, "occasion.vehicles.color": color, "occasion.vehicles.production_year": production_year,
                   "occasion.vehicles.condition": condition, "occasion.vehicles.fuel_type": fuel_type, "occasion.vehicles.license_plate_number": license_plate_number, "occasion.vehicles.vin": vin}

        all_vehicles.append(vehicle)
        vehicle_index += 1

    return all_vehicles
