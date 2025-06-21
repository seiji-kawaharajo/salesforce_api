from pathlib import Path

import pandas as pd

from salesforce_api import Sf, SfBulk

config_file_name = ".secrets.salesforce.json"
config_file_path = Path(__file__).parent / config_file_name
salesforce_config_json_str = config_file_path.read_text(encoding="utf-8")

sf = Sf.from_env(salesforce_config_json_str)

# Query サンプル
print("=== Query サンプル ===")
soql = "select id from Contact"

bulk = SfBulk(sf)
job = bulk.create_job_query(soql)
print(job.info)
job.poll_status()
print(job.info)

print(job.get_results())

# 生のAPIも使用可能
job = bulk.create_job_query_raw(soql)
print(job)
job = bulk.poll_job_query(job["id"])
print(job)
print(bulk.get_job_query_results(job["id"]))

# CRUD サンプル
print("\n=== CRUD サンプル ===")

# Insert サンプル
print("--- Insert サンプル ---")
data = {
    "Name": ["Company A", "Company B", "Company C"],
}
df = pd.DataFrame(data)

# CSVデータに変換
csv_data = df.to_csv(index=False)
print("CSV data:")
print(csv_data)

# Insertジョブを作成
insert_job = bulk.create_job_insert("Account")
print(f"Insert job created: {insert_job.info}")

# データをアップロード
insert_job.upload_data(csv_data)

# ジョブをクローズして処理開始
insert_job.close()

# ステータスをポーリング
insert_job.poll_status()
print(f"Insert job completed: {insert_job.info}")

# 結果を取得
successful_results = insert_job.get_successful_results()
failed_results = insert_job.get_failed_results()
unprocessed_records = insert_job.get_unprocessed_records()

print(f"Successful: {len(successful_results)} records")
print(f"Failed: {len(failed_results)} records")
print(f"Unprocessed: {len(unprocessed_records)} records")

# Update サンプル
print("\n--- Update サンプル ---")
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
print(f"Update job completed: {update_job.info}")

# Upsert サンプル
print("\n--- Upsert サンプル ---")
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
print(f"Upsert job completed: {upsert_job.info}")

# Delete サンプル
print("\n--- Delete サンプル ---")
delete_data = {
    "Id": ["001XXXXXXXXXXXXXXX"],  # 削除するレコードID
}
delete_df = pd.DataFrame(delete_data)
delete_csv = delete_df.to_csv(index=False)

delete_job = bulk.create_job_delete("Account")
delete_job.upload_data(delete_csv)
delete_job.close()
delete_job.poll_status()
print(f"Delete job completed: {delete_job.info}")

# 生のAPIも使用可能
print("\n--- 生のAPI使用例 ---")
raw_insert_job = bulk.create_job_insert_raw("Account")
print(f"Raw insert job: {raw_insert_job}")

raw_update_job = bulk.create_job_update_raw("Account")
print(f"Raw update job: {raw_update_job}")
