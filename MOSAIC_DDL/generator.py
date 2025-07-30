"""
generator.py

This module contains the generation pipeline of MOSAIC_DDL.

Author: Benjamin Koch
Date: July 2025
"""

# Imports
from errors import SamplingProcedureNotFoundError, CyclicDependencyBetweenRelationsFound
from helpers_document_generation import generate_document_file
import xml.etree.ElementTree as ET
from typing import Union
import config_framework
from tqdm import tqdm
import networkx as nx
import random
import asyncio
import json
import sys


class Generator:
    def __init__(self, config_file: str) -> None:
        """
        Initializes the generator.

        Parameters:
            confi_file (str): The path to the xml configuration file.
        """
        self.config_file = config_file
        self.graph = nx.DiGraph()
        self.sampling_procedures = {}
        self.entity_to_count = {}
        self.load_config()

    def load_config(self) -> None:
        """
        Loads the configuration stored in the xml file and create a graph of its entities/attributes.
        """

        # Load config tree and its root
        config_tree = ET.parse(self.config_file)
        config_root = config_tree.getroot()

        # Traverse and collect domains
        for domain in config_root.find("domains").findall("domain"):
            # Fetch domain id (name)
            domain_id = domain.get("id")

            # Add node for domain
            self.graph.add_node(domain_id, type="domain",
                                eii=domain.get("eii"))

            # Traverse and collect domain attributes
            for domain_attribute in domain.findall("domainAttribute"):
                # Fetch domain attributes (their names)
                domain_attribute_id = domain_attribute.get("id")

                # Create a node for each domain attribute of type domain (the scope of the node) and the domain as the parent node
                self.graph.add_node(domain_attribute_id, key=domain_attribute.get("key"), value=domain_attribute.get(
                    "value"), type="domain_attribute", parent=domain_id, frequency=domain_attribute.get("frequency"), eii=domain_attribute.get("eii"))

            # Traverse and collect entities
            for entity in domain.find("entities").findall("entity"):
                # Fetch entity id (name)
                entity_id = entity.get("id")

                # Add node for entity
                self.graph.add_node(entity_id, type="entity", parent=domain_id)

                # Traverse and collect entity attributes
                for entity_attribute in entity.findall("entityAttribute"):
                    # Fetch entity attributes (their names)
                    entity_attribute_id = entity_attribute.get("id")

                    # Create a node for each entity attribute of type entity (the scope of the node) and the entity as the parent node
                    self.graph.add_node(entity_attribute_id, key=entity_attribute.get("key"), value=entity_attribute.get(
                        "value"), type="entity_attribute", parent=entity_id, frequency=entity_attribute.get("frequency"), eii=entity_attribute.get("eii"))

            # Traverse and collect relations
            for relation in domain.find("relations").findall("relation"):
                # Fetch values defining the relation
                relation_type = relation.get("type")

                if relation_type == "cooccurrence":
                    relation_scope = relation.get("scope")
                    relation_probability = float(relation.get("probability"))
                    relation_from = relation.find("from").get("ref")
                    relation_to = relation.find("to").get("ref")

                    # Add edge for relation to graph
                    self.graph.add_edge(relation_from, relation_to, type="_".join(
                        [relation_type, relation_scope]), probability=relation_probability)
                else:
                    pass

        # Check whether graph is acyclic such that there are no acyclic co-occurrence relations
        try:
            cycle = nx.find_cycle(self.graph)

            if cycle:
                raise CyclicDependencyBetweenRelationsFound(cycle)
        except nx.NetworkXNoCycle:
            pass

    def register_sampling_procedure(self, attribute_id: str) -> None:
        """
        Used for creating the actual sampling procedure function for the individual attributes (domain and entity attributes).

        Parameters:
            attribute_id (str): The name (id) of the attribute.
        """

        def wrapper(function):
            """
            Sets the provided function for the corrsponding attribute by updating the sampling procedures dictionary.

            Parameters:
                function: The sampling function for the attribute corresponding to attribute_id.
            """

            self.sampling_procedures[attribute_id] = function
            return function

        return wrapper

    def generate_sampling_procedure_stubs(self) -> None:
        """
        Generates a python file with stub functions for the sampling procedures required by the specified configuration file.
        """

        with open(config_framework.SAMPLING_PROCEDURES, "w", encoding='utf-8') as sampling_procedures_file:
            # Set up file
            sampling_procedures_file.write(
                "\"\"\"\nsampling_procedures.py\n\nThis file contains automatically generated function stubs for the sampling procedures required by the structure provided from the configuration file.\n\"\"\"\n\n")
            sampling_procedures_file.write(
                "# Imports\nfrom generator import Generator\n\n\n")
            sampling_procedures_file.write(
                "def register_all_sampling_procedures(framework: Generator) -> None:\n")
            sampling_procedures_file.write(
                "\t\"\"\"\n\tContains all registrations for the sampling procedures.\n\n\tUsage Instructions:\n\t- There is one sampling function for each domain.\n\t- Each sampling function must return a dictionary containing the following:\n\t\t- For each domain attribute there must be a field with the domain attribute id as the key and your generated value as the value.\n\t\t- For each entity there must be a field with the entity id as the key and a list of dictionaries, containing all entity attributes, as the value. The entity attributes in each dictionary of the list must again have the entity attribute id as the key and your generated value as the value.\n\t\t- You have access to framework.entity_to_count which is a dictionary holding the number of entities which must be generated for the respective list as defined by your configuration.\n\t- Not following these instructions will result in a warning and the abortion of the framework execution.\n\t\"\"\"\n\n")

            # Filter out domain nodes (exclude entity and attribute nodes)
            only_domain_nodes = [node for node, node_attributes in self.graph.nodes(
                data=True) if node_attributes.get("type") == "domain"]
            only_domain_graph = self.graph.subgraph(only_domain_nodes)

            # Compute topological ordering of nodes in the graph
            topological_order = list(nx.topological_sort(only_domain_graph))

            # Traverse attributes in topological order and sample
            for domain_id in topological_order:
                sampling_procedures_file.write(
                    f"\t@framework.register_sampling_procedure(\"{domain_id}\")\n")
                sampling_procedures_file.write(
                    f"\tdef sample_{domain_id.replace(".", "_")}():\n")
                sampling_procedures_file.write("\t\treturn None\n\n")

    def get_entities_and_count_of_domain(self, domain_id: str) -> dict[str, int]:
        """
        Returns the entity names and their count of a specified domain.

        Parameters:
            domain_id (str): The name of the domain to search entities in.

        Returns:
            dict[str, int]: A dictionary containing the name of the entities and their respective number of occurrences.
        """

        # Load config tree and its root
        config_tree = ET.parse(self.config_file)
        config_root = config_tree.getroot()

        # Traverse domains and only check for the domain_id
        for domain in config_root.find("domains").findall("domain"):
            if domain.get("id") == domain_id:
                return {entity.get("id"): int(entity.get("count")) for entity in domain.find("entities").findall("entity")}

        return {}

    def dictionary_key_structure(self, dictionary: dict) -> dict:
        """
        Returns a new dictionary which only contains the sorted key structure, without any values.

        Parameters:
            dictionary (dict): The input dictionary:

        Returns:
            dict: The output dictionary containing only the keys, sorted lexicographically.
        """

        # Differentiate between list, dict, and entry
        if isinstance(dictionary, dict):
            # Consider items of dictionary
            return {key: self.dictionary_key_structure(value) for key, value in dictionary.items()}
        elif isinstance(dictionary, list):
            # Consider dictionaries in the list and sort resulting list
            key_structures = [
                self.dictionary_key_structure(d) for d in dictionary if isinstance(d, (dict, list))]
            if key_structures:
                return sorted(key_structures, key=repr)
            else:
                return None
        else:
            # Replace value by None
            return None

    def compare_dictionary_key_structure(self, dict1: dict, dict2: dict) -> bool:
        """
        Compares the key structures of two provided dictionaries.

        Parameters:
            dict1 (dict): The first input dictionary.
            dict2 (dict): The second input dictionary.

        Returns:
            bool: Whether the key structures are the same or not.
        """

        return self.dictionary_key_structure(dict1) == self.dictionary_key_structure(dict2)

    def filter_dictionary_keys(self, dictionary: dict, allowed_attributes: set[str], allowed_entities: set[str], domain_id: str) -> dict:
        """
        Filters out all key value pairs in the dictionary which do not have their key occurring in the allowed attributes set.

        Parameters:
            dictionary (dict): The dictionary to filter.
            allowed_attributes (set[str]): A set of keys which should be kept in the dictionary.
            allowed_entities (set[str]): A set of keys which should be kept in the dictionary.
            domain_id (str): The domain we are currently in.

        Returns:
            dict: The filtered dictionary.
        """

        # Storage for filtered dictionary
        filtered_dictionary = {}

        for key, value in dictionary.items():
            if isinstance(value, list):
                # If entity not in occurring entities just skip
                if key not in allowed_entities:
                    continue

                # Filter list of dictionaries
                filtered_dictionary_list = []
                for sub_dictionary in value:
                    if isinstance(sub_dictionary, dict):
                        filtered_sub_dictionary = {
                            key: value for key, value in sub_dictionary.items() if key in allowed_attributes and config_framework.EII_LEVEL_MAPPING[self.graph.nodes[key]["eii"]] <= config_framework.EII_LEVEL_MAPPING[self.graph.nodes[domain_id]["eii"]]}

                        # If this dictionary is not empty, add it to filtered list
                        if filtered_sub_dictionary:
                            filtered_dictionary_list.append(
                                filtered_sub_dictionary)

                # If this filtered list is not empty, add it to filtered dictionary
                if filtered_dictionary_list:
                    filtered_dictionary[key] = filtered_dictionary_list
            else:
                # Filter singular key value pair
                if key in allowed_attributes and config_framework.EII_LEVEL_MAPPING[self.graph.nodes[key]["eii"]] <= config_framework.EII_LEVEL_MAPPING[self.graph.nodes[domain_id]["eii"]]:
                    filtered_dictionary[key] = value

        return filtered_dictionary

    def generate_seed(self, domain_id: str) -> dict[str, Union[str, int, list[str], list[int]]]:
        """
        Generates a singular seed by sampling according to the registered sampling procedures and the constraints specified in the configuration file.

        Parameters:
            domain_id (str): The name (id) of the domain.

        Returns:
            dict[str, Union[str, int, list[str], list[int]]]: The sampled seed returned as a dictionary of its attributes and the corresponding values.
        """

        # Update entity_to_count dictionary such that its values are accessible in the sampling procedure functions
        self.entity_to_count = self.get_entities_and_count_of_domain(domain_id)

        # Create a verification seed to later verify that the seed returned by the sampling function contains all fields necessary
        verification_seed = {entity: [{} for _ in range(
            self.entity_to_count[entity])] for entity in self.entity_to_count.keys()}
        verification_seed["domain"] = domain_id

        # Compute subgraph of only entity nodes
        only_entity_nodes = [node for node, node_attributes in self.graph.nodes(
            data=True) if node_attributes.get("type") == "entity"]
        only_entity_graph = self.graph.subgraph(only_entity_nodes)

        # Traverse entity-only subgraph in topological order to compute co-occurrence relations specified
        only_entity_graph_order = list(nx.topological_sort(only_entity_graph))
        occurring_entities = set()
        for entity in [entity for entity in only_entity_graph_order if entity.split(".")[0] == domain_id]:
            # Check whether all predecessors were sampled
            entity_predecessors = list(only_entity_graph.predecessors(entity))
            if any(predecessor not in occurring_entities for predecessor in entity_predecessors):
                continue

            # If no predecessors then sample always
            if not entity_predecessors:
                occurring_entities.add(entity)
                continue

            # If all predecessors were sampled, compute occurrence probabilistically
            entity_occurrs = True
            for predecessor in entity_predecessors:
                # Fetch data for edge connecting entity to predecessor
                edge_data = only_entity_graph.edges[predecessor, entity]

                # Probabilistically keep node or discard it
                if random.random() > edge_data.get("probability"):
                    entity_occurrs = False
                    break

            if entity_occurrs:
                occurring_entities.add(entity)

        # Compute subgraph of only attribute nodes
        only_attribute_nodes = [node for node, node_attributes in self.graph.nodes(data=True) if node_attributes.get(
            "type") == "domain_attribute" or node_attributes.get("type") == "entity_attribute"]
        only_attribute_graph = self.graph.subgraph(only_attribute_nodes)

        # Traverse attribute-only subgraph in topological order to sample and compute co-occurrence relations specified
        only_attribute_graph_order = list(
            nx.topological_sort(only_attribute_graph))
        occurring_attributes = set()
        for attribute in [attribute for attribute in only_attribute_graph_order if attribute.split(".")[0] == domain_id]:
            # Update verification seed
            if self.graph.nodes[attribute]["type"] == "domain_attribute":
                verification_seed[attribute] = None
            elif self.graph.nodes[attribute]["type"] == "entity_attribute":
                key = ".".join(attribute.split(".")[:2])
                for d in verification_seed[key]:
                    d[attribute] = None

            if self.graph.nodes[attribute]["parent"] in occurring_entities or self.graph.nodes[attribute]["type"] == "domain_attribute":
                # Check whether all predecessors were sampled
                attribute_predecessors = list(
                    only_attribute_graph.predecessors(attribute))
                if any(predecessor not in occurring_attributes for predecessor in attribute_predecessors):
                    continue

                # If no predecessor then sample always
                if not attribute_predecessors:
                    occurring_attributes.add(attribute)

                # If all predecessors were sampled, compute occurrence probabilistically
                attribute_occurs = True
                for predecessor in attribute_predecessors:
                    # Fetch data for edge connecting attribute to predecessor
                    edge_data = only_attribute_graph.edges[predecessor, attribute]

                    # Probabilistically keep node or discard it
                    if random.random() > edge_data.get("probability"):
                        attribute_occurs = False
                        break

                if attribute_occurs:
                    occurring_attributes.add(attribute)

        # Fetch sampling procedure
        sampling_procedure = self.sampling_procedures.get(domain_id)
        if not sampling_procedure:
            raise SamplingProcedureNotFoundError(self.graph.nodes[domain_id])

        # Fetch sample and add domain id (name) to sample
        sample = sampling_procedure()
        sample["domain"] = domain_id

        # Validate sample
        same_key_structure = self.compare_dictionary_key_structure(
            verification_seed, sample)

        if not same_key_structure:
            print(
                f"WARNING: The provided sampling procedure for the domain {domain_id} does not output a correct sample.\n\nExpected:\n{verification_seed}\n\nGot:\n{sample}\n\nFix the issue and restart the framework.")
            sys.exit("FRAMEWORK EXECUTION ABORTED")

        # Storage for seed
        seed = {}

        # Add domain id (name) to seed
        seed["domain"] = domain_id

        # Filter sample to only contain attributes which occur in the occurring attributes set and only contain entities which occur in the occurring entities set; also checks the eii level and includes/excludes from sample based on that
        seed.update(self.filter_dictionary_keys(
            sample, occurring_attributes, occurring_entities, domain_id))

        # Sort seed lexicographically and lists (entities) at the end
        domain_keys = [key for key,
                       value in seed.items() if not isinstance(value, list)]
        entity_keys = [key for key,
                       value in seed.items() if isinstance(value, list)]

        domain_keys = sorted(domain_keys)
        entity_keys = sorted(entity_keys)

        seed = {key: seed[key] for key in domain_keys + entity_keys}

        return seed

    def compute_domain_to_text_types_to_number_of_seeds_and_documents(self, domain_ids: list[str]) -> dict:
        """
        Computes a dictionary mapping domain id to a dictionary mapping text types to tuple (number of seed, number of documents per seed)

        Parameters:
            domain_ids (list[str]): The domains we are generating.

        Returns:
            dict: The computed dictionary.
        """

        # Compute dictionary mapping domain id to dictionary mapping texttypes to tuple (number of seed, number of documents per seed)
        domain_to_text_types_to_number_of_seeds_and_documents = {}
        config_tree = ET.parse(self.config_file)
        config_root = config_tree.getroot()

        for domain in config_root.find("domains").findall("domain"):
            if domain.get("id") in domain_ids:
                text_types = [texttype.get("id") for texttype in domain.find(
                    "texttypes").findall("texttype")]
                text_types_number_of_seeds = [texttype.get(
                    "number_of_seeds") for texttype in domain.find("texttypes").findall("texttype")]
                text_types_documents_per_seed = [texttype.get(
                    "documents_per_seed") for texttype in domain.find("texttypes").findall("texttype")]

                domain_to_text_types_to_number_of_seeds_and_documents[domain.get("id")] = {
                    key: (int(value1), int(value2)) for key, value1, value2 in zip(text_types, text_types_number_of_seeds, text_types_documents_per_seed) if int(value1) > 0}

        return domain_to_text_types_to_number_of_seeds_and_documents

    def generate_seeds(self, domain_ids: list[str]) -> None:
        """
        Generates as many seeds for the specified domain as configured in the config file.

        Parameters:
            domain_ids (list[str]): The names (ids) of the domains.
        """

        domain_to_text_types_to_number_of_seeds_and_documents = self.compute_domain_to_text_types_to_number_of_seeds_and_documents(
            domain_ids)

        # Compute number of seeds to be generated for progress bar
        number_of_seeds = 0
        for domain_id in domain_ids:
            for texttype in domain_to_text_types_to_number_of_seeds_and_documents[domain_id]:
                for _ in range(domain_to_text_types_to_number_of_seeds_and_documents[domain_id][texttype][0]):
                    number_of_seeds += 1

        # Open seeds file, sample seeds and write them to jsonl file
        with open(config_framework.SEEDS, "w", encoding='utf-8', buffering=1) as seeds:
            progress_bar = tqdm(
                total=number_of_seeds, desc=f"{'\033[34m'}Generating Seeds...{'\033[0m'}")

            for domain_id in domain_ids:
                for texttype in domain_to_text_types_to_number_of_seeds_and_documents[domain_id]:
                    for _ in range(domain_to_text_types_to_number_of_seeds_and_documents[domain_id][texttype][0]):
                        seed = self.generate_seed(domain_id)
                        seed["text_type"] = texttype
                        seeds.write(json.dumps(seed) + "\n")
                        progress_bar.update(1)

    def generate_documents(self, domain_ids: list[str]) -> None:
        """
        Generates as many documents per text type per seed as specified in the config file.

        Parameters:
            domain_ids (list[str]): The names (ids) of the domains.
        """

        # Load configuration file
        config_tree = ET.parse(self.config_file)
        config_root = config_tree.getroot()

        # Compute dictionary with text types and the respective number of seeds and documents
        domain_to_text_types_to_number_of_seeds_and_documents = self.compute_domain_to_text_types_to_number_of_seeds_and_documents(
            domain_ids)

        # Fetch system prompts and occurring attributes for each domain
        system_prompts = {}
        for domain in config_root.find("domains").findall("domain"):
            prompts_for_domain = {}
            for texttype in domain.find("texttypes").findall("texttype"):
                prompts_for_domain[texttype.get("id")] = (
                    texttype.find("texttypePrompt").get("value"), texttype.find("occurringAttributes").get("value"))
            system_prompts[domain.get("id")] = prompts_for_domain

        # Assemble system prompts for model inference
        system_prompts_for_model_inference = []
        for domain in domain_ids:
            for texttype in system_prompts[domain]:
                if texttype in domain_to_text_types_to_number_of_seeds_and_documents[domain].keys():
                    for _ in range(int(domain_to_text_types_to_number_of_seeds_and_documents[domain][texttype][0]) * (domain_to_text_types_to_number_of_seeds_and_documents[domain][texttype][1])):
                        system_prompts_for_model_inference.extend(
                            [system_prompts[domain][texttype]])

        # Fetch frequency probabilities for all attributes
        probabilities = {}
        for domain in config_root.find("domains").findall("domain"):
            for domain_attribute in domain.findall("domainAttribute"):
                probabilities[domain_attribute.get(
                    "id")] = float(domain_attribute.get("frequency"))
            for entity in domain.find("entities").findall("entity"):
                for entity_attribute in entity.findall("entityAttribute"):
                    probabilities[entity_attribute.get(
                        "id")] = float(entity_attribute.get("frequency"))

        # Compute number of seeds
        number_of_text_types = sum(1 for texttypes in domain_to_text_types_to_number_of_seeds_and_documents.values()
                                   for _, _ in texttypes.values())

        # Execute document generation
        asyncio.run(generate_document_file(system_prompts_for_model_inference, config_framework.SEEDS, config_framework.DOCUMENTS,
                                           config_framework.BLANK_SEEDS, number_of_text_types, domain_to_text_types_to_number_of_seeds_and_documents, probabilities))
