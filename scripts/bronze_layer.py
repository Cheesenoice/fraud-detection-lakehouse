#!/usr/bin/env python3
"""
Bronze Layer - Ingest CSV to Iceberg
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit

print("🚀 Khởi tạo Spark Session...")
spark = SparkSession.builder \
    .appName("Bronze Layer - Data Ingestion") \
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

# Create Bronze namespace
print("\n📁 Tạo Bronze namespace...")
spark.sql("CREATE NAMESPACE IF NOT EXISTS demo.bronze")
print("✅ Namespace demo.bronze đã tạo!")

# Ingest Transactions
print("\n📥 Đang ingest train_transaction.csv...")
df_transaction = spark.read.option("header", "true").csv("/home/spark/notebooks/data/train_transaction.csv")
tx_count = df_transaction.count()
print(f"   → Đọc được {tx_count:,} transactions")

df_transaction_bronze = df_transaction \
    .withColumn("_ingestion_time", current_timestamp()) \
    .withColumn("_source_file", lit("train_transaction.csv"))

df_transaction_bronze.writeTo("demo.bronze.transactions") \
    .tableProperty("format-version", "2") \
    .createOrReplace()
print(f"✅ Đã tạo bảng demo.bronze.transactions ({tx_count:,} records)")

# Ingest Identity
print("\n📥 Đang ingest train_identity.csv...")
df_identity = spark.read.option("header", "true").csv("/home/spark/notebooks/data/train_identity.csv")
id_count = df_identity.count()
print(f"   → Đọc được {id_count:,} identity records")

df_identity_bronze = df_identity \
    .withColumn("_ingestion_time", current_timestamp()) \
    .withColumn("_source_file", lit("train_identity.csv"))

df_identity_bronze.writeTo("demo.bronze.identity") \
    .tableProperty("format-version", "2") \
    .createOrReplace()
print(f"✅ Đã tạo bảng demo.bronze.identity ({id_count:,} records)")

# Summary
print("\n" + "="*60)
print("📊 BRONZE LAYER SUMMARY")
print("="*60)
print(f"   Transactions: {tx_count:,} records")
print(f"   Identity:     {id_count:,} records")
print(f"   Metadata:     _ingestion_time, _source_file")
print(f"   Format:       Apache Iceberg v2")
print(f"   Storage:      MinIO (S3-compatible)")
print("="*60)
print("✅ Bronze Layer hoàn tất!")

spark.stop()
