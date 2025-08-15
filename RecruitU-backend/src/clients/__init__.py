"""
Clients Module

Contains HTTP client functionality for interacting with external APIs,
specifically the people search and profile APIs.
"""

from .people_api import PeopleAPI, people_api

__all__ = ['PeopleAPI', 'people_api']
