"""Salesforce Bulk Job module for Python.

This module provides classes for managing Salesforce bulk job operations,
including query jobs and CRUD operation jobs.
"""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from .salesforce_bulk import SfBulk


class SfBulkJobQuery:
    """Salesforce Bulk Query Job."""

    def __init__(self: "SfBulkJobQuery", sf_bulk: "SfBulk", job_info: dict) -> None:
        """Initialize query job with bulk client and job info."""
        self._sf_bulk = sf_bulk
        self.id = job_info["id"]
        self.info = job_info

    def poll_status(self: "SfBulkJobQuery") -> dict:
        """Poll job status until completion."""
        self.info = self._sf_bulk.poll_job_query(self.id)
        return self.info

    def get_results(self: "SfBulkJobQuery") -> pd.DataFrame:
        """Get job results as DataFrame."""
        return self._sf_bulk.get_job_query_results(self.id)


class SfBulkJob:
    """Salesforce Bulk CRUD Job."""

    def __init__(self: "SfBulkJob", sf_bulk: "SfBulk", job_info: dict) -> None:
        """Initialize CRUD job with bulk client and job info."""
        self._sf_bulk = sf_bulk
        self.id = job_info["id"]
        self.info = job_info

    def upload_data(self: "SfBulkJob", csv_data: str) -> None:
        """Upload CSV data to the job."""
        self._sf_bulk.upload_job_data(job_id=self.id, csv_data=csv_data)

    def close(self: "SfBulkJob") -> None:
        """Close the job and mark as uploaded."""
        self._sf_bulk.uploaded_job(job_id=self.id)

    def poll_status(self: "SfBulkJob") -> dict:
        """Poll job status until completion."""
        self.info = self._sf_bulk.poll_job(job_id=self.id)
        return self.info

    def get_successful_results(self: "SfBulkJob") -> pd.DataFrame:
        """Get successful results as DataFrame."""
        return self._sf_bulk.get_ingest_successful_results(job_id=self.id)

    def get_failed_results(self: "SfBulkJob") -> pd.DataFrame:
        """Get failed results as DataFrame."""
        return self._sf_bulk.get_ingest_failed_results(job_id=self.id)

    def get_unprocessed_records(self: "SfBulkJob") -> pd.DataFrame:
        """Get unprocessed records as DataFrame."""
        return self._sf_bulk.get_ingest_unprocessed_records(job_id=self.id)
