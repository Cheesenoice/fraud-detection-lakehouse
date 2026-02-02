#!/usr/bin/env python3
"""
Serving Layer - Copy Gold data to ClickHouse
"""

from pyspark.sql import SparkSession
from datetime import datetime
import requests

print("🚀 Khởi tạo Spark Session...")
spark = SparkSession.builder \
    .appName("Serving Layer - ClickHouse Integration") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.demo", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.demo.type", "rest") \
    .config("spark.sql.catalog.demo.uri", "http://iceberg-rest:8181") \
    .config("spark.sql.catalog.demo.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
    .config("spark.sql.catalog.demo.warehouse", "s3://warehouse/") \
    .config("spark.sql.catalog.demo.s3.endpoint", "http://minio:9000") \
    .config("spark.sql.catalog.demo.s3.path-style-access", "true") \
    .config("spark.sql.catalog.demo.s3.access-key-id", "admin") \
    .config("spark.sql.catalog.demo.s3.secret-access-key", "password123") \
    .config("spark.sql.defaultCatalog", "demo") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

print("✅ Spark Session sẵn sàng!")

# ClickHouse Configuration
CLICKHOUSE_HOST = "clickhouse"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = "clickhouse123"

def execute_clickhouse(query):
    """Execute a query on ClickHouse via HTTP interface"""
    url = f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/"
    response = requests.post(
        url, data=query,
        params={"user": CLICKHOUSE_USER, "password": CLICKHOUSE_PASSWORD}
    )
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"ClickHouse Error: {response.text}")

def insert_to_clickhouse(df, table_name, columns):
    """Insert Spark DataFrame to ClickHouse using HTTP interface"""
    rows = df.collect()
    if len(rows) == 0:
        print(f"⚠️ No data to insert into {table_name}")
        return
    
    values_list = []
    for row in rows:
        values = []
        for col in columns:
            val = row[col]
            if val is None:
                values.append("NULL")
            elif isinstance(val, str):
                val = val.replace("'", "\\'")
                values.append(f"'{val}'")
            elif isinstance(val, bool):
                values.append("1" if val else "0")
            elif isinstance(val, datetime):
                values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
            elif hasattr(val, 'strftime'):
                values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
            else:
                values.append(str(val))
        values_list.append(f"({','.join(values)})")
    
    batch_size = 1000
    for i in range(0, len(values_list), batch_size):
        batch = values_list[i:i+batch_size]
        query = f"INSERT INTO fraud_detection.{table_name} ({','.join(columns)}) VALUES {','.join(batch)}"
        execute_clickhouse(query)
    
    print(f"   ✅ Inserted {len(rows)} rows into {table_name}")

# Create Database and Tables
print("\n📁 Tạo database và tables trong ClickHouse...")
execute_clickhouse("CREATE DATABASE IF NOT EXISTS fraud_detection")

# Drop existing tables
for table in ['fraud_by_card_type', 'hourly_fraud_analysis', 'fraud_by_product', 
              'kpi_summary', 'high_risk_transactions', 'daily_transaction_summary',
              'fraud_by_day_of_week', 'fraud_by_amount_category']:
    execute_clickhouse(f"DROP TABLE IF EXISTS fraud_detection.{table}")

# Create tables
execute_clickhouse("""
CREATE TABLE fraud_detection.fraud_by_card_type (
    card_brand String, card_category String, total_transactions UInt64,
    fraud_count UInt64, legitimate_count UInt64, fraud_rate_pct Float64,
    total_amount Float64, fraud_amount Float64, avg_transaction_amount Float64,
    avg_fraud_amount Float64, report_generated_at DateTime, _dbt_run_id String
) ENGINE = MergeTree() ORDER BY (card_brand, card_category)
""")

execute_clickhouse("""
CREATE TABLE fraud_detection.hourly_fraud_analysis (
    hour_of_day UInt8, total_transactions UInt64, fraud_count UInt64,
    fraud_rate_pct Float64, total_amount Float64, fraud_amount Float64,
    avg_amount Float64, high_value_transactions UInt64, time_period String,
    report_generated_at DateTime, _dbt_run_id String
) ENGINE = MergeTree() ORDER BY hour_of_day
""")

execute_clickhouse("""
CREATE TABLE fraud_detection.fraud_by_product (
    product_code String, total_transactions UInt64, fraud_count UInt64,
    fraud_rate_pct Float64, total_amount Float64, fraud_amount Float64,
    avg_amount Float64, min_amount Float64, max_amount Float64,
    high_value_count UInt64, high_value_pct Float64,
    report_generated_at DateTime, _dbt_run_id String
) ENGINE = MergeTree() ORDER BY product_code
""")

execute_clickhouse("""
CREATE TABLE fraud_detection.kpi_summary (
    metric_category String, total_transactions UInt64, total_fraud_count UInt64,
    total_legitimate_count UInt64, fraud_rate_pct Float64,
    total_transaction_amount Float64, total_fraud_amount Float64,
    avg_transaction_amount Float64, avg_fraud_amount Float64,
    avg_legitimate_amount Float64, max_transaction_amount Float64,
    high_value_transactions UInt64, unique_card_brands UInt64,
    unique_products UInt64, active_days UInt64,
    report_generated_at DateTime, _dbt_run_id String
) ENGINE = MergeTree() ORDER BY metric_category
""")

execute_clickhouse("""
CREATE TABLE fraud_detection.high_risk_transactions (
    TransactionID Int32, is_fraud Int32, transaction_amount Float64,
    transaction_hour Int32, transaction_day Int32, product_code String,
    card_brand String, card_category String,
    purchaser_email_domain Nullable(String), device_type Nullable(String),
    device_category Nullable(String), operating_system Nullable(String),
    risk_score Int32, risk_level String,
    report_generated_at DateTime, _dbt_run_id String
) ENGINE = MergeTree() ORDER BY (risk_score, TransactionID)
""")

execute_clickhouse("""
CREATE TABLE fraud_detection.daily_transaction_summary (
    transaction_day Int32, total_transactions UInt64, fraud_count UInt64,
    legitimate_count UInt64, fraud_rate_pct Float64, total_amount Float64,
    fraud_amount Float64, avg_amount Float64, high_value_count UInt64,
    unique_cards UInt64, unique_products UInt64,
    report_generated_at DateTime, _dbt_run_id String
) ENGINE = MergeTree() ORDER BY transaction_day
""")

execute_clickhouse("""
CREATE TABLE fraud_detection.fraud_by_day_of_week (
    day_of_week UInt8, day_of_week_name String, total_transactions UInt64,
    fraud_count UInt64, legitimate_count UInt64, fraud_rate_pct Float64,
    total_amount Float64, fraud_amount Float64, avg_amount Float64,
    high_value_transactions UInt64, report_generated_at DateTime, _dbt_run_id String
) ENGINE = MergeTree() ORDER BY day_of_week
""")

execute_clickhouse("""
CREATE TABLE fraud_detection.fraud_by_amount_category (
    amount_category String, category_order UInt8, total_transactions UInt64,
    fraud_count UInt64, legitimate_count UInt64, fraud_rate_pct Float64,
    total_amount Float64, fraud_amount Float64, avg_amount Float64,
    min_amount Float64, max_amount Float64,
    report_generated_at DateTime, _dbt_run_id String
) ENGINE = MergeTree() ORDER BY category_order
""")

print("✅ Đã tạo tất cả tables trong ClickHouse!")

# Copy data from Gold Layer to ClickHouse
print("\n📤 Copy dữ liệu từ Gold Layer sang ClickHouse...")

# fraud_by_card_type
df = spark.sql("SELECT * FROM bronze_gold.fraud_by_card_type")
insert_to_clickhouse(df, "fraud_by_card_type", 
    ["card_brand", "card_category", "total_transactions", "fraud_count", "legitimate_count",
     "fraud_rate_pct", "total_amount", "fraud_amount", "avg_transaction_amount", "avg_fraud_amount",
     "report_generated_at", "_dbt_run_id"])

# hourly_fraud_analysis
df = spark.sql("SELECT * FROM bronze_gold.hourly_fraud_analysis")
insert_to_clickhouse(df, "hourly_fraud_analysis",
    ["hour_of_day", "total_transactions", "fraud_count", "fraud_rate_pct", 
     "total_amount", "fraud_amount", "avg_amount", "high_value_transactions", 
     "time_period", "report_generated_at", "_dbt_run_id"])

# fraud_by_product
df = spark.sql("SELECT * FROM bronze_gold.fraud_by_product")
insert_to_clickhouse(df, "fraud_by_product",
    ["product_code", "total_transactions", "fraud_count", "fraud_rate_pct",
     "total_amount", "fraud_amount", "avg_amount", "min_amount", "max_amount",
     "high_value_count", "high_value_pct", "report_generated_at", "_dbt_run_id"])

# kpi_summary
df = spark.sql("SELECT * FROM bronze_gold.kpi_summary")
insert_to_clickhouse(df, "kpi_summary",
    ["metric_category", "total_transactions", "total_fraud_count", "total_legitimate_count",
     "fraud_rate_pct", "total_transaction_amount", "total_fraud_amount", 
     "avg_transaction_amount", "avg_fraud_amount", "avg_legitimate_amount",
     "max_transaction_amount", "high_value_transactions", "unique_card_brands",
     "unique_products", "active_days", "report_generated_at", "_dbt_run_id"])

# daily_transaction_summary
df = spark.sql("SELECT * FROM bronze_gold.daily_transaction_summary")
insert_to_clickhouse(df, "daily_transaction_summary",
    ["transaction_day", "total_transactions", "fraud_count", "legitimate_count",
     "fraud_rate_pct", "total_amount", "fraud_amount", "avg_amount",
     "high_value_count", "unique_cards", "unique_products", "report_generated_at", "_dbt_run_id"])

# high_risk_transactions (limit 10000)
df = spark.sql("SELECT * FROM bronze_gold.high_risk_transactions LIMIT 10000")
insert_to_clickhouse(df, "high_risk_transactions",
    ["TransactionID", "is_fraud", "transaction_amount", "transaction_hour", "transaction_day",
     "product_code", "card_brand", "card_category", "purchaser_email_domain",
     "device_type", "device_category", "operating_system", "risk_score", "risk_level",
     "report_generated_at", "_dbt_run_id"])

# fraud_by_day_of_week
try:
    df = spark.sql("SELECT * FROM bronze_gold.fraud_by_day_of_week")
    insert_to_clickhouse(df, "fraud_by_day_of_week",
        ["day_of_week", "day_of_week_name", "total_transactions", "fraud_count", "legitimate_count",
         "fraud_rate_pct", "total_amount", "fraud_amount", "avg_amount", "high_value_transactions",
         "report_generated_at", "_dbt_run_id"])
except Exception as e:
    print(f"   ⚠️ fraud_by_day_of_week: Bảng chưa có trong dbt")

# fraud_by_amount_category
try:
    df = spark.sql("SELECT * FROM bronze_gold.fraud_by_amount_category")
    insert_to_clickhouse(df, "fraud_by_amount_category",
        ["amount_category", "category_order", "total_transactions", "fraud_count", "legitimate_count",
         "fraud_rate_pct", "total_amount", "fraud_amount", "avg_amount", "min_amount", "max_amount",
         "report_generated_at", "_dbt_run_id"])
except Exception as e:
    print(f"   ⚠️ fraud_by_amount_category: Bảng chưa có trong dbt")

# Summary
print("\n" + "="*60)
print("📊 SERVING LAYER SUMMARY")
print("="*60)
for table in ['fraud_by_card_type', 'hourly_fraud_analysis', 'fraud_by_product', 
              'kpi_summary', 'high_risk_transactions', 'daily_transaction_summary',
              'fraud_by_day_of_week', 'fraud_by_amount_category']:
    try:
        count = execute_clickhouse(f"SELECT count() FROM fraud_detection.{table}")
        print(f"   {table}: {count.strip()} rows")
    except:
        print(f"   {table}: ⚠️ No data")
print("="*60)
print("✅ Serving Layer hoàn tất!")

spark.stop()
