import io
from copy import deepcopy
from time import sleep
from typing import Any

import pandas as pd
import requests

from .salesforce_api import Sf
from .salesforce_bulk_job import SfBulkJob, SfBulkJobQuery


class SfBulk:
    def __init__(self, sf: Sf):
        self.bulk2_url = sf.bulk2_url
        self.headers = sf.headers

    # query
    def create_job_query_raw(
        self,
        query: str,
        all: bool = False,
    ) -> Any:
        _operation = "query"
        if all:
            _operation += "All"

        _response = requests.post(
            f"{self.bulk2_url}query",
            headers=self.headers,
            json={"operation": _operation, "query": query},
        )
        _response.raise_for_status()

        return _response.json()

    def create_job_query(
        self,
        query: str,
        all: bool = False,
    ) -> SfBulkJobQuery:
        return SfBulkJobQuery(self, self.create_job_query_raw(query, all))

    def get_job_query_info(self, job_id: str) -> Any:
        _response = requests.get(
            f"{self.bulk2_url}query/{job_id}",
            headers=self.headers,
        )
        _response.raise_for_status()
        return _response.json()

    def poll_job_query(self, job_id: str) -> Any:
        while True:
            _job_info = self.get_job_query_info(job_id)

            if _job_info["state"] in ["Aborted", "JobComplete", "Failed"]:
                break

            sleep(5)

        return _job_info

    def get_job_query_results(self, job_id: str) -> pd.DataFrame:
        _response = requests.get(
            f"{self.bulk2_url}query/{job_id}/results",
            headers=self.headers,
        )
        _response.raise_for_status()
        _response.encoding = "utf-8"
        return pd.read_csv(io.StringIO(_response.text))

    # CRUD
    def create_job_insert_raw(self, object: str) -> Any:
        return self.create_job_raw(object, "insert")

    def create_job_insert(self, object: str) -> SfBulkJob:
        return self.create_job(object, "insert")

    def create_job_delete_raw(self, object: str) -> Any:
        return self.create_job_raw(object, "delete")

    def create_job_delete(self, object: str) -> SfBulkJob:
        return self.create_job(object, "delete")

    def create_job_hardDelete_raw(self, object: str) -> Any:
        return self.create_job_raw(object, "hardDelete")

    def create_job_hardDelete(self, object: str) -> SfBulkJob:
        return self.create_job(object, "hardDelete")

    def create_job_update_raw(self, object: str) -> Any:
        return self.create_job_raw(object, "update")

    def create_job_update(self, object: str) -> SfBulkJob:
        return self.create_job(object, "update")

    def create_job_upsert_raw(self, object: str, external_id_field: str) -> Any:
        return self.create_job_raw(object, "upsert", external_id_field)

    def create_job_upsert(self, object: str, external_id_field: str) -> SfBulkJob:
        return self.create_job(object, "upsert", external_id_field)

    def create_job_raw(
        self,
        object: str,
        operation: str,
        external_id_field: str | None = None,
    ) -> Any:
        if operation == "upsert" and not external_id_field:
            raise ValueError(
                "operation が 'upsert' の場合、external_id_field は必須です。"
            )

        _payload = {
            "object": object,
            "operation": operation,
        }

        if operation == "upsert" and external_id_field is not None:
            _payload["externalIdFieldName"] = external_id_field

        _response = requests.post(
            f"{self.bulk2_url}ingest",
            headers=self.headers,
            json=_payload,
        )
        _response.raise_for_status()

        return _response.json()

    def create_job(
        self,
        object: str,
        operation: str,
        external_id_field: str | None = None,
    ) -> SfBulkJob:
        return SfBulkJob(
            self, self.create_job_raw(object, operation, external_id_field)
        )

    def upload_job_data(self, job_id: str, csv_data: str) -> None:
        _headers_csv = deepcopy(self.headers)
        _headers_csv["Content-Type"] = "text/csv"

        _response = requests.put(
            f"{self.bulk2_url}ingest/{job_id}/batches",
            data=csv_data.encode("utf-8"),
            headers=_headers_csv,
        )
        _response.raise_for_status()

    def uploaded_job(self, job_id: str) -> None:
        _response = requests.patch(
            f"{self.bulk2_url}ingest/{job_id}",
            headers=self.headers,
            json={"state": "UploadComplete"},
        )
        _response.raise_for_status()

    def get_job_info(self, job_id: str) -> Any:
        _response = requests.get(
            f"{self.bulk2_url}ingest/{job_id}",
            headers=self.headers,
        )
        _response.raise_for_status()
        return _response.json()

    def poll_job(self, job_id: str) -> Any:
        while True:
            _job_info = self.get_job_info(job_id)

            if _job_info["state"] in ["Aborted", "JobComplete", "Failed"]:
                break

            sleep(5)

        return _job_info

    def get_ingest_successful_results(self, job_id: str) -> pd.DataFrame:
        _response = requests.get(
            f"{self.bulk2_url}ingest/{job_id}/successfulResults",
            headers=self.headers,
        )
        _response.raise_for_status()
        _response.encoding = "utf-8"
        return pd.read_csv(io.StringIO(_response.text))

    def get_ingest_failed_results(self, job_id: str) -> pd.DataFrame:
        _response = requests.get(
            f"{self.bulk2_url}ingest/{job_id}/failedResults",
            headers=self.headers,
        )
        _response.raise_for_status()
        _response.encoding = "utf-8"
        return pd.read_csv(io.StringIO(_response.text))

    def get_ingest_unprocessed_records(self, job_id: str) -> pd.DataFrame:
        _response = requests.get(
            f"{self.bulk2_url}ingest/{job_id}/unprocessedrecords",
            headers=self.headers,
        )
        _response.raise_for_status()
        _response.encoding = "utf-8"
        return pd.read_csv(io.StringIO(_response.text))
