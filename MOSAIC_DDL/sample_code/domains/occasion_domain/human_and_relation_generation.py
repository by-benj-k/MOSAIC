"""
human_and_relation_generation.py

This module contains the code to generate a network of humans and also their relationships.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code.helpers_event_generation import get_random_csv_entry, get_unique_values_from_function
from sample_code import config
from typing import Self
from tqdm import tqdm
import pandas as pd
import secrets
import random
import string
import json
import csv
import ast
import os


class Human:
    def __init__(self, name: str, first_name: str, last_name: str, gender: str, birth_year: int, occupation: str, nationality: str, political_affiliation: str, religious_affiliation: str, passport_number: str, phone_number: str, email_address: str, social_media_platforms: list[str], social_media_usernames: list[str], mother: Self = None, father: Self = None, spouse: Self = None):
        """
        Initializes a human instance with the provided attributes.

        Parameters:
            name (str): The full name of the human.
            first_name (str): The first name of the human.
            last_name (str): The last name of the human.
            gender (str): The gender of the human.
            birth_year (int): The year of birth of the human.
            occupation (str): The job of the human.
            nationality (str): The country of origin of the human.
            political_affiliation (str): The political party the human associates with.
            religious_affiliation (str): The religious party the human associates with.
            passport_number (str): The passport number of the human.
            phone_number (str): The phone number of the human.
            email_address (str): The email address of the human.
            social_media_platforms (list[str]): The social media platforms that the human uses.
            social_media_usernames (list[str]): The usernames of the human on the social media platforms he uses.
        """

        # Attributes which are provided during the instantiation of a human instance
        self.name = name
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.birth_year = birth_year
        self.occupation = occupation
        self.nationality = nationality
        self.political_affiliation = political_affiliation
        self.religious_affiliation = religious_affiliation
        self.passport_number = passport_number
        self.phone_number = phone_number
        self.email_address = email_address
        self.social_media_platforms = social_media_platforms
        self.social_media_usernames = social_media_usernames

        # Attributes which are computed on the fly
        self.mother = mother
        self.father = father
        self.spouse = spouse
        self.children = []

    def add_child(self, child: Self):
        """
        Adds a human as a child to another human.

        Parameters:
            child (Self): The human instance which should be added as a child.
        """

        self.children.append(child)


def form_marriage(spouse1: Human, spouse2: Human, last_name_from_husband: float = 0.85) -> tuple[Human, Human]:
    """
    Assigns a common last name to the married humans using the husbands name 85% of the time and the wifes name 15% of the time.

    Parameters:
        spouse1 (Human): Spouse number 1 in the marriage.
        spouse2 (Human): Spouse number 2 in the marriage.
        last_name_from_husband (float): The probability of choosing the husbands last name.

    Returns:
        tuple[Human, Human]: A tuple containing the original human instances but with adapted last names.
    """

    # Compute who is the husband and who is the wife
    if spouse1.gender == "male":
        husband, wife = spouse1, spouse2
    else:
        husband, wife = spouse2, spouse1

    # Sample random value between 0 and 1 and check whether it is below the threshold provided as a parameter
    if random.random() < last_name_from_husband:
        common_last_name = husband.last_name
    else:
        common_last_name = wife.last_name

    # Assign common last name
    husband.last_name = common_last_name
    wife.last_name = common_last_name

    # Update name
    husband.name = " ".join(husband.name.strip().split()[
                            :-1] + [common_last_name])
    wife.name = " ".join(wife.name.strip().split()[:-1] + [common_last_name])

    return husband, wife


def get_random_first_name_and_gender() -> tuple[str, str]:
    """
    Returns a random first name.

    Returns:
        [str, str]: The randomly selected first name and its gender.
    """

    # Get .txt files which store the first names.
    txt_files = [file for file in os.listdir(
        config.H_FIRST_NAMES_FOLDER_PATH) if file.endswith('.txt')]

    # Choose a random .txt file and generate the path to it
    random_txt_file = random.choice(txt_files)
    random_txt_file_path = os.path.join(
        config.H_FIRST_NAMES_FOLDER_PATH, random_txt_file)

    # Read all entries and select a random entry
    with open(random_txt_file_path, 'r', encoding='utf-8') as file:
        entries = file.readlines()
    random_entry = random.choice(entries).strip().split(',')

    # Create first name and gender
    first_name = random_entry[0]
    gender = "male" if random_entry[1] == 'M' else "female"

    return first_name, gender


def get_random_name_and_gender() -> tuple[str, str]:
    """
    Fetches first and last name and returns full name as well as its gender.

    Returns:
        tuple[str, str]: The random name and the gender
    """

    # Fetch values
    first_name, gender = get_random_first_name_and_gender()
    last_name = str(get_random_csv_entry(
        config.H_SURNAMES_FILE_PATH, config.H_SURNAMES_FILE_LENGTH, "name")).capitalize()

    # Create name
    name = first_name + " " + last_name

    return name, gender


def get_random_politics_religion_given_nationality(nationality: str) -> tuple[str, str, str]:
    """
    Takes in the nationality and fetches a random political affiliation and religous affiliation in correspondence to the metrices stored for each country.

    Parameters:
        nationality (str): The nationality to fetch from.

    Returns:
        tuple[str, str, str]: A tuple containing the nationality, the political and religous affiliation.
    """

    # Storage for full csv row
    crrp_entry = dict()

    # Fetch line corresponding to nationality
    with open(config.COUNTRY_REGION_RELIGION_POLITICS_FILE_PATH, "r", encoding='utf-8') as crrps:
        # Instantiate reader for csv
        crrp_reader = csv.reader(crrps)

        for crrp in crrp_reader:
            if crrp[0].strip() == nationality:
                crrp_entry = crrp
                break

    # Collect religion dictionary
    religions = json.loads(crrp_entry[2])

    # Sample random religion
    random_religion = random.choices(
        list(religions.keys()), list(religions.values()), k=1)[0]

    # Collect politics list
    politics = ast.literal_eval(crrp_entry[3])

    # Sample random politics
    random_politics = random.choice(politics)

    return random_politics, random_religion


def get_random_phone_number(nationality: str) -> str:
    """
    Takes in the nationality of the human and returns a random phone number with the correct phone code.

    Parameters:
        country (str): The nationality of the human.

    Returns:
        str: The random phone number.
    """

    # Look up nationality in countries dataset and extract phone code
    country_information = pd.read_csv(config.E_COUNTRIES_FILE_PATH)
    phone_code = ""
    phone_code = country_information.loc[country_information["name"]
                                         == nationality, "phone_code"].values[0]

    # Generate random digits
    random_digits = f"{random.randint(0, 999999999):09d}"

    # Construct phone number as "phone_code-xx-xxx-xx-xx"
    random_phone_number = str(
        phone_code) + f"-{random_digits[:2]}-{random_digits[2:5]}-{random_digits[5:7]}-{random_digits[7:]}"

    return random_phone_number


def get_random_email_address() -> str:
    """
    Returns a random email address.

    Returns:
        str: The random email address.
    """

    # Compute set of possible characters
    character = string.ascii_letters + string.digits

    # One or two "prefixes" of local part
    multiple_prefixes = random.choice([True, False])

    # Compute local part
    if multiple_prefixes:
        local_part = ''.join(secrets.choice(character) for _ in range(
            6)) + "." + ''.join(secrets.choice(character) for _ in range(10))
    else:
        local_part = ''.join(secrets.choice(character) for _ in range(10))

    # Compute domain
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "aol.com", "protonmail.com", "zoho.com", "mail.com", "yandex.com", "msn.com", "mail.ru", "fastmail.com", "tutanota.com", "gmx.com", "inbox.com", "lavabit.com", "gmane.org", "usa.com", "hushmail.com", "126.com", "163.com", "qq.com", "sina.com", "live.com", "rediffmail.com", "rakuten.com", "bol.com", "rocketmail.com", "juno.com", "lycos.com", "aim.com", "zoho.eu", "cox.net", "charter.net", "comcast.net", "sbcglobal.net", "frontier.com", "netzero.com", "bellsouth.net", "earthlink.net", "pacbell.net", "videotron.ca", "shaw.ca", "rogers.com", "tiscali.it", "telstra.com.au", "optusnet.com.au", "kpnmail.nl", "t-online.de", "mailchimp.com", "icloud.co.uk", "fastmail.fm", "neomailbox.com", "posteo.de", "zoho.in", "ymail.com", "bigpond.com", "btinternet.com", "alibaba.com"
                            ])

    # Assemble email address
    email_address = local_part + "@" + domain

    return email_address


def create_human(nationality: str, birth_year: int, gender_provided: str, last_name_provided: str = None) -> Human:
    """
    Creates a human with all the attributes of the specified nationality.

    Parameters:
        nationality (str): The nationality the human should have.
        birth_year (int): The year of birth of the human.
        gender_provided (str): The gender of the human.
        last_name (str): The last name of possible parents.

    Returns:
        Human: The created human instance.
    """

    # Fetch values
    name, gender = get_random_name_and_gender()

    while gender != gender_provided:
        name, gender = get_random_name_and_gender()

    birth_year = birth_year
    occupation = get_random_csv_entry(
        config.H_OCCUPATIONS_FILE_PATH, config.H_OCCUPATIONS_FILE_LENGTH, "Occupation")
    political_affiliation, religious_affiliation = get_random_politics_religion_given_nationality(
        nationality)
    phone_number = get_random_phone_number(nationality)
    email_address = get_random_email_address()

    # Compute first and last name
    name_parts = name.strip().split()
    first_name = " ".join(name_parts[:-1])
    last_name = name_parts[-1]

    if last_name_provided:
        last_name = last_name_provided
        name = " ".join(name.strip().split()[:-1] + [last_name])

    # Compute passport number
    country_information = pd.read_csv(config.E_COUNTRIES_FILE_PATH)
    country_iso_code = country_information.loc[country_information["name"]
                                               == nationality, "iso3"].values[0]
    passport_number = f"PN-{country_iso_code}-{random.randint(1, 8000000000)}"

    # Compute social media platforms
    number_of_platforms = random.randint(
        1, config.MAX_NUMBER_OF_SOCIAL_MEDIA_PLATFORMS_PER_HUMAN)
    social_media_platforms = get_unique_values_from_function(
        get_random_csv_entry, number_of_platforms, config.A_PLATFORM_FILE_PATH, config.A_PLATFORM_FILE_LENGTH, "platform")

    # Compute social media usernames
    name_concatenation = "".join(word.lower() for word in name.split())
    social_media_usernames = [
        f"{name_concatenation}-{str(random.randint(1, 8000000000))}-{platform.lower()}" for platform in social_media_platforms]

    return Human(name, first_name, last_name, gender, birth_year, occupation, nationality, political_affiliation, religious_affiliation, passport_number, phone_number, email_address, social_media_platforms, social_media_usernames)


def generate_family_tree(nationality: str, founding_year: int, depth: int) -> list[Human]:
    """
    Recursively generates a family tree found in founding_year in the country of nationality, with depth generations.

    Parameters:
        nationality (str): The nationality of the family.
        founding_year (int): The year the family was founded (root of the family tree).
        depth (int): Number of family generations to compute.

    Returns:
        list[Humans]: The list of all humans in the family tree.
    """

    # Storage for all humans
    all_humans = []

    def generate_generation(parents: tuple[Human, Human], generation: int) -> None:
        """
        Recursively computes the generations of the family tree.

        Parameters:
            parents (tuple[Human, Human]): The parents of the current human.
            generation (int): The current depth of the generation process.
        """

        # Basecase of recursion
        if generation > depth:
            return

        # Compute number of children the married couple has
        number_of_children = random.randint(
            0, config.MAX_NUMBER_OF_CHILDREN_PER_COUPLE)

        for _ in range(number_of_children):
            # Create child with approximated random birth year and the same nationality as the whole family
            child_birth_year = founding_year + \
                (generation * 28) + random.randint(-7, 7)

            parents_last_name = parents[0].last_name
            if parents[0].last_name != parents[1].last_name:
                parents_last_name = random.choice(
                    [parents[0].last_name, parents[1].last_name])

            child = create_human(nationality, child_birth_year, random.choice(
                ["male", "female"]), parents_last_name)

            # Assign parents
            child.father = parents[0] if parents[0].gender == "male" else parents[1]
            child.mother = parents[1] if parents[1].gender == "female" else parents[0]
            child.father.add_child(child)
            child.mother.add_child(child)

            # Add created human to family tree
            all_humans.append(child)

            # Recurse by generating a spouse of the newly generated child or stay single with 40% chance
            if generation + 1 < depth and random.random() > 0.4:
                spouse_gender = "male" if child.gender == "female" else "female"
                spouse_birth_year = child_birth_year + random.randint(-3, 3)
                spouse = create_human(
                    nationality, spouse_birth_year, spouse_gender)

                # Form couple/marriage out of them
                form_marriage(child, spouse)

                # Add create spouse to family tree
                all_humans.append(spouse)

                # Assign spouses to each other
                child.spouse = spouse
                spouse.spouse = child

                # Start recursion
                generate_generation([child, spouse], generation + 1)
            else:
                child.spouse = None

    # Create root of family tree
    root_human1 = create_human(nationality, founding_year, "male")
    root_human2 = create_human(nationality, founding_year, "female")
    root_human1.spouse = root_human2
    root_human2.spouse = root_human1

    # Form marriage of root
    form_marriage(root_human1, root_human2)

    # Add root to family tree and start recursion
    all_humans.extend([root_human1, root_human2])
    generate_generation([root_human1, root_human2], 0)

    return all_humans


def generate_multiple_family_trees_for_country(nationality: str, number_of_family_trees: int) -> list[list[Human]]:
    """
    Creates multiple family trees for a single country.

    Parameters:
        nationality (str): The country for which the family trees should be generated.
        number_of_family_trees (int): The number of family trees that should be generated.

    Returns:
        list[list[Human]]: A list of lists where each list in the list is a family tree.
    """

    # Storage for family trees
    family_trees = []

    for _ in range(number_of_family_trees):
        family_tree = generate_family_tree(nationality, random.randint(
            1800, 2025), random.randint(1, config.MAXIMUM_DEPTH_OF_FAMILY_TREES))
        family_trees.append(family_tree)

    return family_trees


def connect_singles_across_family_trees(all_humans: list[list[Human]]) -> list[list[Human]]:
    """
    Connect single humans across family trees, marries them and potentially generated children for them.

    Parameters:
        all_humans (list[list[Human]]): All family trees consisting of humans generated so far (for each seperate country).

    Returns:
        list[list[Human]]: The new and extended list of humans with marriages across family trees.
    """

    # Storage for intermediate trees
    all_humans_in_tree = []

    def generate_generation(parents: tuple[Human, Human], generation: int, depth: int) -> None:
        """
        Recursively computes the generations of the family tree.

        Parameters:
            parents (tuple[Human, Human]): The parents of the current human.
            generation (int): The current depth of the generation process.
            depth (int): The maximum depth of the generation process.
        """

        # Select nationality randomly between parents
        nationality = random.choice(
            [parents[0].nationality, parents[1].nationality])

        # Select founding year randomly between birth year of parents
        founding_year = random.choice(
            [parents[0].birth_year, parents[1].birth_year])

        # Basecase of recursion
        if generation > depth:
            return

        # Compute number of children the married couple has
        number_of_children = random.randint(
            0, config.MAX_NUMBER_OF_CHILDREN_PER_COUPLE)

        for _ in range(number_of_children):
            # Create child with approximated random birth year and the same nationality as the whole family
            child_birth_year = founding_year + \
                (generation * 28) + random.randint(-7, 7)

            parents_last_name = parents[0].last_name
            if parents[0].last_name != parents[1].last_name:
                parents_last_name = random.choice(
                    [parents[0].last_name, parents[1].last_name])

            child = create_human(nationality, child_birth_year, random.choice(
                ["male", "female"]), parents_last_name)

            # Assign parents
            child.father = parents[0] if parents[0].gender == "male" else parents[1]
            child.mother = parents[1] if parents[1].gender == "female" else parents[0]
            child.father.add_child(child)
            child.mother.add_child(child)

            # Add created human to family tree
            all_humans_in_tree.append(child)

            # Recurse by generating a spouse of the newly generated child or stay single with 40% chance
            if generation + 1 < depth and random.random() > 0.4:
                spouse_gender = "male" if child.gender == "female" else "female"
                spouse_birth_year = child_birth_year + random.randint(-3, 3)
                spouse = create_human(
                    nationality, spouse_birth_year, spouse_gender)

                # Form couple/marriage out of them
                form_marriage(child, spouse)

                # Add create spouse to family tree
                all_humans_in_tree.append(spouse)

                # Assign spouses to each other
                child.spouse = spouse
                spouse.spouse = child

                # Start recursion
                generate_generation([child, spouse], generation + 1, depth)
            else:
                child.spouse = None

    # Try at most specified number of tries for across family tree marriages
    current_attempt = 0
    possible_marriage_found = False
    while current_attempt < config.MAXIMUM_ATTEMPTS_FOR_ACROSS_TREE_MARRIAGES:
        # Choose two random family trees
        family_tree1, family_tree2 = random.sample(all_humans, 2)

        for h1 in family_tree1:
            for h2 in family_tree2:
                if h1.gender != h2.gender and h1.spouse is None and h2.spouse is None and abs(h1.birth_year - h2.birth_year) <= 15:
                    human1 = h1
                    human2 = h2
                    possible_marriage_found = True
                    break
            if possible_marriage_found:
                break

        # Update attempt counter
        current_attempt += 1

        if possible_marriage_found:
            # Form marriage
            form_marriage(human1, human2)
            human1.spouse = human2
            human2.spouse = human1

            # Start recursion
            generate_generation([human1, human2], 0, random.randint(
                1, config.MAXIMUM_DEPTH_OF_FAMILY_TREES))
            all_humans.append(all_humans_in_tree)
            all_humans_in_tree = []
            possible_marriage_found = False

    return all_humans


def generate_humans() -> None:
    """
    Generates a pool of human instances with attributes defined by the EII level.
    """

    # Storage for all humans
    all_humans = []

    # Traverse countries and create family trees for each country.
    with open(config.E_COUNTRIES_FILE_PATH, "r", encoding='utf-8') as countries:
        # Reader for csv rows and skip header
        country_reader = csv.reader(countries)
        next(country_reader)
        country_idx = 1

        for country in country_reader:
            for _ in tqdm(range(config.NUMBER_OF_FAMILY_TREES_PER_COUNTRY), desc=f"{'\033[34m'}Generating humans for {country[1]} ({country_idx}/{config.E_COUNTRIES_FILE_LENGTH})...{'\033[0m'}"):
                all_humans.extend(
                    generate_multiple_family_trees_for_country(country[1], 1))

            country_idx += 1

    # Connect some singles across family trees
    print(f"{'\033[34m'}Connecting singles across family trees...{'\033[0m'}")
    all_humans = connect_singles_across_family_trees(all_humans)

    # Flatten list of family trees into list of humans
    all_humans_flat = [
        human for family_tree in all_humans for human in family_tree]

    # Traverse flattened list, compute linked fields, create correct dictionary according to EII level and write to file
    with open(config.HUMAN_INSTANCES_PATH, "w", encoding='utf-8', buffering=1) as human_instances:
        for h in all_humans_flat:
            # Construct dictionary
            human = {"name": h.name, "occupation": h.occupation, "social_media_platforms": h.social_media_platforms, "social_media_usernames": h.social_media_usernames, "gender": h.gender, "birth_year": h.birth_year, "political_affiliation": h.political_affiliation, "nationality": h.nationality,
                     "religious_affiliation": h.religious_affiliation, "father": h.father.name if h.father else "Unknown", "mother": h.mother.name if h.mother else "Unknown", "spouse": h.spouse.name if isinstance(h.spouse, Human) else "Single", "passport_number": h.passport_number, "phone_number": h.phone_number, "email_address": h.email_address}

            human_instances.write(json.dumps(human) + "\n")
