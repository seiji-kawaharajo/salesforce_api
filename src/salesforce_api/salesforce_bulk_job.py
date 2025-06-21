from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from .salesforce_bulk import SfBulk


class SfBulkJobQuery:
    def __init__(self, sf_bulk: "SfBulk", job_info: dict):
        self._sf_bulk = sf_bulk
        self.id = job_info["id"]
        self.info = job_info

    def poll_status(self) -> dict:
        self.info = self._sf_bulk.poll_job_query(self.id)
        return self.info

    def get_results(self) -> pd.DataFrame:
        return self._sf_bulk.get_job_query_results(self.id)


class SfBulkJob:
    def __init__(self, sf_bulk: "SfBulk", job_info: dict):
        self._sf_bulk = sf_bulk
        self.id = job_info["id"]
        self.info = job_info

    def upload_data(self, csv_data: str) -> None:
        self._sf_bulk.upload_job_data(job_id=self.id, csv_data=csv_data)

    def close(self) -> None:
        self._sf_bulk.uploaded_job(job_id=self.id)

    def poll_status(self) -> dict:
        self.info = self._sf_bulk.poll_job(job_id=self.id)
        return self.info

    def get_successful_results(self) -> pd.DataFrame:
        return self._sf_bulk.get_ingest_successful_results(job_id=self.id)

    def get_failed_results(self) -> pd.DataFrame:
        return self._sf_bulk.get_ingest_failed_results(job_id=self.id)

    def get_unprocessed_records(self) -> pd.DataFrame:
        return self._sf_bulk.get_ingest_unprocessed_records(job_id=self.id)
