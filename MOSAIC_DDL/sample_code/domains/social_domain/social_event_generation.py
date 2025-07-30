"""
social_event_generation.py

This module contains the code to generate the social entry of a seed.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from sample_code.helpers_event_generation import extract_formatting_fields, count_number_of_humans, get_random_jsonl_entry
from sample_code import config
from typing import Union
import random
import json
import csv


def get_random_time() -> str:
    """
    Return a random time.

    Returns:
        str: The random time as "hour:min:sec".
    """

    # Choose random hour and minute
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)

    # Construct time
    time = f"{random_hour:02}:{random_minute:02}:{random_second:02}"

    return time


def get_random_topic() -> str:
    """
    Returns a randomly created topic one could post about on social media.

    Returns:
        str: The social media topic.
    """

    # Create artificial naming blocks (naming blocks content generated with the helpf of ChatGPT)
    topics = [row[0] for row in csv.reader(open(config.A_TOPICS_FILE_PATH))]
    modifiers = ["honest", "real", "raw", "vulernable", "controversial", "lighthearted", "data-driven", "inspiring", "actionable", "emotional", "relatable", "snarky", "educational", "uplifting",
                 "reflective", "quick", "detailed", "minimalist", "pragmatic", "visual", "funny", "sarcastic", "experimental", "underrated", "overrated", "evidence-based", "well-researched", "personal", "provocative"]
    audiences = ["for beginners", "for professionals", "for students", "for creators", "for parents",
                 "for overthinkers", "for designers", "for remote workers", "for developers", "for introverts"]
    angles = ["from experience", "from research", "from a beginner's view", "with a twist", "in real life", "without the fluff",
              "from a therapist's view", "a case study", "based on my journey", "from interviews", "after a year of trying", "with results"]

    # Define template for topics (template content generated with the help of ChatGPT)
    social_template = ["{modifiers} takes on {topics}", "{topics} {audiences}", "{topics} {angles}", "{modifiers} guide to {topics}", "{modifiers} breakdown of {topics}", "{modifiers} content about {topics}", "{modifiers} + {topics}",
                       "{topics} with a {modifiers} spin", "{modifiers} thought on {topics}", "{topics}: {modifiers}, {angles}", "How I approach {topics} {angles}", "{topics} {audiences} - {modifiers} and useful", "Exploring {topics} {angles}", "{topics} in a {modifiers} way"]

    # Fetch random template and extract formatting fields
    template = random.choice(social_template)
    formatting_fields = extract_formatting_fields(template)

    # Fetch random values for fields
    formatting_fields_values = {"topics": random.choice(topics), "modifiers": random.choice(
        modifiers), "audiences": random.choice(audiences), "angles": random.choice(angles)}

    return template.format(**{v: formatting_fields_values[v] for v in formatting_fields})


def get_random_platform_and_username_and_location() -> tuple[str, str, str]:
    """
    Returns a random platform, username and location (nationality of the user).

    Returns:
        tuple[str, str, str]: A tuple containing the platform, username and location.
    """

    # Compute number of human instances
    number_of_humans = count_number_of_humans()

    # Sample until new human is selected
    human = get_random_jsonl_entry(
        config.HUMAN_INSTANCES_PATH, number_of_humans)

    while json.dumps(human) in config.GLOBAL_HUMAN_SET or human["birth_year"] < 1935:
        human = get_random_jsonl_entry(
            config.HUMAN_INSTANCES_PATH, number_of_humans)

    config.GLOBAL_HUMAN_SET.add(json.dumps(human))

    # Random index for platform/username
    random_index = random.randint(0, len(human["social_media_platforms"]) - 1)
    return human["social_media_platforms"][random_index], human["social_media_usernames"][random_index], human["nationality"]


def generate_social_event(entity_to_count: dict[str, int]) -> dict[str, Union[int, str]]:
    """
    Generates the entry for a single social event.

    Parameters:
        entity_to_count (dict[str, str]): Maps entities to the number of occurrences in the current seed.

    Returns:
        dict[str, Union[int, str]]: A dictionary containing the event and the attributes.
    """

    # Create event instance
    post_time = get_random_time()
    topic = get_random_topic()
    platform, username, location = get_random_platform_and_username_and_location()

    # Assemble dictionary
    event = {"social.post_time": post_time, "social.topic": topic,
             "social.platform": platform, "social.location": location, "social.username": username}

    return event
