"""Salesforce API usage examples.

This module demonstrates how to use the Salesforce API package
for various operations including queries and CRUD operations.
"""

import logging
from pathlib import Path

import pandas as pd
from salesforce_api import Sf, SfBulk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_file_name = ".secrets.salesforce.json"
config_file_path = Path(__file__).parent / config_file_name
salesforce_config_json_str = config_file_path.read_text(encoding="utf-8")

sf = Sf.from_env(salesforce_config_json_str)

# Query サンプル
logger.info("=== Query サンプル ===")
soql = "select id from Contact"

bulk = SfBulk(sf)

# クラス型の利用例
job = bulk.create_job_query(soql)
logger.info(job.info)
job.poll_status()
logger.info(job.info)
logger.info(job.get_results())

# 生のAPIも使用可能
job_dict = bulk.create_job_query_raw(soql)
logger.info(job_dict)
job_info = bulk.poll_job_query(job_dict["id"])
logger.info(job_info)
logger.info(bulk.get_job_query_results(job_dict["id"]))

# CRUD サンプル
logger.info("\n=== CRUD サンプル ===")

# Insert サンプル
logger.info("--- Insert サンプル ---")
data = {
    "Name": ["Company A", "Company B", "Company C"],
}
accounts_df = pd.DataFrame(data)

# CSVデータに変換
csv_data = accounts_df.to_csv(index=False)
logger.info("CSV data:")
logger.info(csv_data)

# Insertジョブを作成
insert_job = bulk.create_job_insert("Account")
logger.info("Insert job created: %s", insert_job.info)

# データをアップロード
insert_job.upload_data(csv_data)

# ジョブをクローズして処理開始
insert_job.close()

# ステータスをポーリング
insert_job.poll_status()
logger.info("Insert job completed: %s", insert_job.info)

# 結果を取得
successful_results = insert_job.get_successful_results()
failed_results = insert_job.get_failed_results()
unprocessed_records = insert_job.get_unprocessed_records()

logger.info("Successful: %d records", len(successful_results))
logger.info("Failed: %d records", len(failed_results))
logger.info("Unprocessed: %d records", len(unprocessed_records))

# Update サンプル
logger.info("\n--- Update サンプル ---")
update_data = {
    "Id": ["001XXXXXXXXXXXXXXX"],  # 実際のレコードIDを指定
    "Name": ["Updated Company Name"],
}
update_df = pd.DataFrame(update_data)
update_csv = update_df.to_csv(index=False)

update_job = bulk.create_job_update("Account")
update_job.upload_data(update_csv)
update_job.close()
update_job.poll_status()
logger.info("Update job completed: %s", update_job.info)

# Upsert サンプル
logger.info("\n--- Upsert サンプル ---")
upsert_data = {
    "External_Id__c": ["EXT001", "EXT002"],  # 外部IDフィールド
    "Name": ["Upsert Company A", "Upsert Company B"],
}
upsert_df = pd.DataFrame(upsert_data)
upsert_csv = upsert_df.to_csv(index=False)

upsert_job = bulk.create_job_upsert("Account", "External_Id__c")
upsert_job.upload_data(upsert_csv)
upsert_job.close()
upsert_job.poll_status()
logger.info("Upsert job completed: %s", upsert_job.info)

# Delete サンプル
logger.info("\n--- Delete サンプル ---")
delete_data = {
    "Id": ["001XXXXXXXXXXXXXXX"],  # 削除するレコードID
}
delete_df = pd.DataFrame(delete_data)
delete_csv = delete_df.to_csv(index=False)

delete_job = bulk.create_job_delete("Account")
delete_job.upload_data(delete_csv)
delete_job.close()
delete_job.poll_status()
logger.info("Delete job completed: %s", delete_job.info)

# 生のAPIも使用可能
logger.info("\n--- 生のAPI使用例 ---")
raw_insert_job = bulk.create_job_insert_raw("Account")
logger.info("Raw insert job: %s", raw_insert_job)

raw_update_job = bulk.create_job_update_raw("Account")
logger.info("Raw update job: %s", raw_update_job)
