#!/usr/bin/env python3
"""
Script tạo các namespaces cần thiết cho dbt
"""
from pyspark.sql import SparkSession

print("=" * 60)
print("Creating Iceberg Namespaces")
print("=" * 60)

spark = SparkSession.builder \
    .appName("CreateNamespaces") \
    .config("spark.sql.catalog.demo", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.demo.type", "rest") \
    .config("spark.sql.catalog.demo.uri", "http://iceberg-rest:8181") \
    .config("spark.sql.catalog.demo.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
    .config("spark.sql.catalog.demo.s3.endpoint", "http://minio:9000") \
    .config("spark.sql.catalog.demo.warehouse", "s3://warehouse/") \
    .config("spark.sql.defaultCatalog", "demo") \
    .getOrCreate()

# Create namespaces
namespaces = ["default", "bronze", "bronze_silver", "bronze_gold"]
for ns in namespaces:
    try:
        spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {ns}")
        print(f"✅ Created namespace: {ns}")
    except Exception as e:
        print(f"⚠️ Namespace {ns}: {e}")

print("\n📋 All Namespaces:")
spark.sql("SHOW NAMESPACES").show()

print("\n✅ Done!")
spark.stop()
