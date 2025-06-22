"""Salesforce API package for Python.

This package provides a Python interface for Salesforce API operations,
including bulk operations and data manipulation.
"""

from .salesforce_api import Sf
from .salesforce_bulk import SfBulk

__all__ = ["Sf", "SfBulk"]
