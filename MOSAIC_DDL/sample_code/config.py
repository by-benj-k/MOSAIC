"""
config.py

This module contains the parameters of the example MOSAIC_DDL that can be adjusted.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
import datetime

# Dataset folder paths
EDUCATIONAL_DATASETS_FOLDER_PATH = "MOSAIC_DDL/sample_code/datasets/educationaL_dataset/"
FINANCIAL_DATASETS_FOLDER_PATH = "MOSAIC_DDL/sample_code/datasets/financial_dataset/"
LEGAL_DATASETS_FOLDER_PATH = "MOSAIC_DDL/sample_code/datasets/legal_dataset/"
MEDICAL_DATASETS_FOLDER_PATH = "MOSAIC_DDL/sample_code/datasets/medical_dataset/"
OCCASION_DATASETS_FOLDER_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/"
SOCIAL_DATASETS_FOLDER_PATH = "MOSAIC_DDL/sample_code/datasets/social_dataset/"

# Educational dataset files
A_COURSE_NAMES_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/educational_dataset/a_course_names.csv"
A_COURSE_NAMES_FILE_LENGTH = 402

# Financial dataset files

# Legal dataset files
CRIMETYPE_SENTENCE_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/legal_dataset/crimetype_sentence.csv"
CRIMETYPE_SENTENCE_FILE_LENGTH = 338

# Medical dataset files
CONDITION_SYMPTOMS_MEDICATION_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/medical_dataset/condition_symptoms_medication.csv"
CONDITION_SYMPTOMS_MEDICATION_FILE_LENGTH = 326

# Occasion dataset files
H_FIRST_NAMES_FOLDER_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/h_first_names/"
COUNTRY_REGION_RELIGION_POLITICS_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/country_region_religion_politics.csv"
COUNTRY_REGION_RELIGION_POLITICS_FILE_LENGTH = 247
E_ACTIVITIES_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/e_activities.csv"
E_ACTIVITIES_FILE_LENGTH = 10000
E_CHALLENGES_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/e_challenges.csv"
E_CHALLENGES_FILE_LENGTH = 100
E_CITIES_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/e_cities.csv"
E_CITIES_FILE_LENGTH = 148061
E_CONTROVERSIES_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/e_controversies.csv"
E_CONTROVERSIES_FILE_LENGTH = 100
E_COUNTRIES_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/e_countries.csv"
E_COUNTRIES_FILE_LENGTH = 247
E_CULTURAL_IMPACTS_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/e_cultural_impacts.csv"
E_CULTURAL_IMPACTS_FILE_LENGTH = 100
E_INCIDENTS_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/e_incidents.csv"
E_INCIDENTS_FILE_LENGTH = 100
E_SOCIETAL_IMPACTS_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/e_societal_impacts.csv"
E_SOCIETAL_IMPACTS_FILE_LENGTH = 100
E_SPECIAL_CONDITIONS_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/e_special_conditions.csv"
E_SPECIAL_CONDITIONS_FILE_LENGTH = 100
E_SURPRISES_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/e_surprises.csv"
E_SURPRISES_FILE_LENGTH = 100
H_OCCUPATIONS_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/h_occupations.csv"
H_OCCUPATIONS_FILE_LENGTH = 1158
H_SURNAMES_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/h_surnames.csv"
H_SURNAMES_FILE_LENGTH = 162252
NAME_SIZE_PRODUCTION_VALUE_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/name_size_production_value.csv"
NAME_SIZE_PRODUCTION_VALUE_FILE_LENGTH = 313
O_CONDITIONS_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/o_conditions.csv"
O_CONDITIONS_FILE_LENGTH = 100
SPECIES_REGION_LIFETIME_ENDANGERED_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/species_region_lifetime_endangered.csv"
SPECIES_REGION_LIFETIME_ENDANGERED_FILE_LENGTH = 320
TYPE_CONSTRUCTION_CAPACITY_SAFETY_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/type_construction_capacity_safety.csv"
TYPE_CONSTRUCTION_CAPACITY_SAFETY_FILE_LENGTH = 310
TYPE_CONSTRUCTION_FLOORS_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/type_construction_floors.csv"
TYPE_CONSTRUCTION_FLOORS_FILE_LENGTH = 356
TYPE_MANUFACTURER_PRODUCTION_FUEL_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/type_manufacturer_production_fuel.csv"
TYPE_MANUFACTURER_PRODUCTION_FUEL_FILE_LENGTH = 360
V_CONDITIONS_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/occasion_dataset/v_conditions.csv"
V_CONDITIONS_FILE_LENGTH = 100

# Social dataset files
A_PLATFORM_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/social_dataset/a_platform.csv"
A_PLATFORM_FILE_LENGTH = 48
A_TOPICS_FILE_PATH = "MOSAIC_DDL/sample_code/datasets/social_dataset/a_topics.csv"
A_TOPICS_FILE_LENGTH = 378

# Path to store generated files
HOSPITAL_INSTANCES_PATH = "MOSAIC_DDL/sample_code/generations/hospitals.jsonl"
COMPANY_INSTANCES_PATH = "MOSAIC_DDL/sample_code/generations/companies.jsonl"
COURT_INSTANCES_PATH = "MOSAIC_DDL/sample_code/generations/courts.jsonl"
SCHOOL_INSTANCES_PATH = "MOSAIC_DDL/sample_code/generations/schools.jsonl"

GENERATIONS_FOLDER_PATH = "MOSAIC_DDL/sample_code/generations/"

HUMAN_INSTANCES_PATH = "MOSAIC_DDL/sample_code/generations/humans.jsonl"
HUMAN_INSTANCES_TEMPORARY_PATH = "MOSAIC_DDL/sample_code/generations/humans_temporary.jsonl"

# Parameters for seed generations
MAX_NUMBER_OF_LOCAL_HOSPITALS_PER_COUNTRY = 8
MAX_NUMBER_OF_REGIONAL_HOSPITALS_PER_COUNTRY = 5
MAX_NUMBER_OF_NATIONAL_HOSPITALS_PER_COUNTRY = 2
NUMBER_OF_HOSPITAL_TYPES = 3

MAX_NUMBER_OF_COMPANIES_PER_COUNTRY = 15
MAX_NUMBER_OF_COURTS_PER_COUNTRY = 15
MAX_NUMBER_OF_SCHOOLS_PER_COUNTRY = 15

MAX_NUMBER_OF_SOCIAL_MEDIA_PLATFORMS_PER_HUMAN = 5

MAX_NUMBER_OF_CHILDREN_PER_COUPLE = 3
NUMBER_OF_FAMILY_TREES_PER_COUNTRY = 25
MAXIMUM_ATTEMPTS_FOR_ACROSS_TREE_MARRIAGES = int(
    0.35 * E_COUNTRIES_FILE_LENGTH * NUMBER_OF_FAMILY_TREES_PER_COUNTRY)
MAXIMUM_DEPTH_OF_FAMILY_TREES = 7

# All domains generation parameters/variables
GLOBAL_HUMAN_SET = set()
START_DATE = datetime.date(1850, 1, 1)
END_DATE = datetime.date(2025, 8, 1)
