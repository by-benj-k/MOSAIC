"""
errors.py

This module contains some custom errors of MOSAIC_DDL.

Author: Benjamin Koch
Date: July 2025
"""


class SamplingProcedureNotFoundError(Exception):
    """
    A custom error being rased if a sampling procedure has not been registered.
    """

    def __init__(self, attribute_id: str):
        """
        Initializes the custom error.
        """

        self.attribute_id = attribute_id

    def __str__(self):
        """
        Provides some custom formatting for the error.
        """

        return f"No sampling procedure was registered for the domain \"{self.attribute_id}\". Please implement this missing sampling procedure and restart the framework."


class CyclicDependencyBetweenRelationsFound(Exception):
    """
    A custom error being rased if a cycle is found in the graph after processing the xml configuration file.
    """

    def __init__(self, cycle):
        """
        Initializes the custom error.
        """

        self.cycle = cycle

    def __str__(self):
        """
        Provides some custom formatting for the error.
        """

        return f"A cyclic dependency between relations has been found (e.g.{self.cycle}). Please resolve this cyclic dependency and restart the framework."
