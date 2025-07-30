"""
sampling_procedures.py

This file contains automatically generated function stubs for the sampling procedures required by the structure provided from the configuration file.
"""

# Imports
from sample_code.domains.occasion_domain import human_and_relation_generation, occasion_event_generation
from sample_code.domains.medical_domain import hospital_generation, medical_modify_human, medical_event_generation
from sample_code.domains.financial_domain import company_generation, financial_modify_human, financial_event_generation
from sample_code.domains.legal_domain import court_generation, legal_modify_human, legal_event_generation
from sample_code.domains.educational_domain import school_generation, educational_modify_human, educational_event_generation
from sample_code.domains.social_domain import social_event_generation
from generator import Generator
from sample_code import config
import os


def register_all_sampling_procedures(framework: Generator) -> None:
    """
    Contains all registrations for the sampling procedures.

    Usage Instructions:
    - There is one sampling function for each domain.
    - Each sampling function must return a dictionary containing the following:
        - For each domain attribute there must be a field with the domain attribute id as the key and your generated value as the value.
        - For each entity there must be a field with the entity id as the key and a list of dictionaries, containing all entity attributes, as the value. The entity attributes in each dictionary of the list must again have the entity attribute id as the key and your generated value as the value.
        - You have access to framework.entity_to_count which is a dictionary holding the number of entities which must be generated for the respective list as defined by your configuration.
    - Not following these instructions will result in a warning and the abortion of the framework execution.
    """

    # Run hospital, company, court, school and human generation
    print(f"{'\033[31m'}Running Preparation Procedures (Might take a while due to the complexity of the family tree computation)...{'\033[0m'}")
    if not os.path.exists(config.HOSPITAL_INSTANCES_PATH):
        hospital_generation.generate_hospitals()
    if not os.path.exists(config.COMPANY_INSTANCES_PATH):
        company_generation.generate_companies()
    if not os.path.exists(config.COURT_INSTANCES_PATH):
        court_generation.generate_courts()
    if not os.path.exists(config.SCHOOL_INSTANCES_PATH):
        school_generation.generate_schools()
    if not os.path.exists(config.HUMAN_INSTANCES_PATH):
        human_and_relation_generation.generate_humans()
        medical_modify_human.medical_modify_human()
        financial_modify_human.financial_modify_human()
        legal_modify_human.legal_modify_human()
        educational_modify_human.educational_modify_human()

    @framework.register_sampling_procedure("medical")
    def sample_medical():
        return medical_event_generation.generate_medical_event(framework.entity_to_count)

    @framework.register_sampling_procedure("legal")
    def sample_legal():
        return legal_event_generation.generate_legal_event(framework.entity_to_count)

    @framework.register_sampling_procedure("social")
    def sample_social():
        return social_event_generation.generate_social_event(framework.entity_to_count)

    @framework.register_sampling_procedure("financial")
    def sample_financial():
        return financial_event_generation.generate_financial_event(framework.entity_to_count)

    @framework.register_sampling_procedure("occasion")
    def sample_occasion():
        return occasion_event_generation.generate_occasion_event(framework.entity_to_count)

    @framework.register_sampling_procedure("educational")
    def sample_educational():
        return educational_event_generation.generate_educational_event(framework.entity_to_count)
