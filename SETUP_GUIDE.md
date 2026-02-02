# 📖 HƯỚNG DẪN THIẾT LẬP CHI TIẾT

## Lakehouse Project - Credit Card Fraud Detection

Tài liệu này hướng dẫn chi tiết **2 cách chạy** dự án Lakehouse:

1. **Cách 1**: Full Pipeline Script (Tự động hóa hoàn toàn)
2. **Cách 2**: Interactive Jupyter Notebooks (Học tập & Khám phá)

---

## 📋 Mục Lục

1. [Yêu Cầu Hệ Thống](#1-yêu-cầu-hệ-thống)
2. [Chuẩn Bị Data](#2-chuẩn-bị-data)
3. [Cách 1: Full Pipeline Script](#3-cách-1-full-pipeline-script)
4. [Cách 2: Jupyter Notebooks](#4-cách-2-jupyter-notebooks)
5. [Iceberg Time Travel Demo](#5-iceberg-time-travel-demo)
6. [Tạo Dashboard Trong Superset](#6-tạo-dashboard-trong-superset)
7. [Dừng Hệ Thống](#7-dừng-hệ-thống)
8. [Xử Lý Sự Cố](#8-xử-lý-sự-cố)

---

## 1. Yêu Cầu Hệ Thống

### 1.1 Phần cứng

| Thành phần | Tối thiểu  | Khuyến nghị |
| ---------- | ---------- | ----------- |
| **RAM**    | 8GB        | 16GB        |
| **Disk**   | 15GB trống | 25GB trống  |
| **CPU**    | 4 cores    | 8 cores     |

### 1.2 Phần mềm

- **Docker Desktop** (bao gồm Docker Compose v2)
- **Python 3.8+** với `requests` library
- **Git** (tùy chọn - để clone repo)

### 1.3 Kiểm tra cài đặt

```bash
# Kiểm tra Docker
docker --version
# Output: Docker version 24.x.x hoặc cao hơn

docker compose version
# Output: Docker Compose version v2.x.x

# Kiểm tra Python
python3 --version
# Output: Python 3.8+ hoặc cao hơn

# Cài requests nếu chưa có
pip3 install requests
```

---

## 2. Chuẩn Bị Data

### 2.1 Vị trí data files

Đặt các file CSV trong thư mục `notebooks/data/`:

```
Lakehouse_Project/
└── notebooks/
    └── data/
        ├── train_transaction.csv   ← 590,540 records (bắt buộc)
        ├── train_identity.csv      ← 144,233 records (bắt buộc)
        ├── test_transaction.csv    ← (tùy chọn)
        └── test_identity.csv       ← (tùy chọn)
```

### 2.2 Kiểm tra data

```bash
cd /path/to/Lakehouse_Project

# Kiểm tra files tồn tại
ls -la notebooks/data/*.csv

# Kiểm tra số dòng
wc -l notebooks/data/train_transaction.csv
# Output: ~590,541 (bao gồm header)

wc -l notebooks/data/train_identity.csv
# Output: ~144,234 (bao gồm header)
```

### 2.3 Nguồn data

Data từ cuộc thi **IEEE-CIS Fraud Detection** trên Kaggle:

- https://www.kaggle.com/c/ieee-fraud-detection/data

---

## 3. Cách 1: Full Pipeline Script

### ⭐ Đây là cách nhanh nhất - chỉ cần 1 lệnh!

### 3.1 Chạy Pipeline

```bash
cd /path/to/Lakehouse_Project

# Chạy toàn bộ pipeline
./scripts/run_full_pipeline.sh
```

### 3.2 Các bước tự động thực hiện

Script sẽ tự động thực hiện **5 bước** sau:

#### Step 0: Khởi động Docker Stack (~2 phút)

- Khởi động 7 Docker containers
- Đợi tất cả services sẵn sàng
- Khởi động Spark Thrift Server (port 10000)

```
Containers khởi động:
├── minio          → S3-compatible storage (port 9000, 9001)
├── minio-init     → Tạo bucket warehouse
├── iceberg-rest   → Iceberg REST Catalog (port 8181)
├── spark-iceberg  → Spark + Jupyter (port 8888, 10000)
├── clickhouse     → OLAP Database (port 8123)
├── superset       → Visualization (port 8088)
└── dbt            → Data transformation
```

#### Step 1: Bronze Layer (~2 phút)

- Tạo namespaces: `demo.bronze`, `bronze_silver`, `bronze_gold`
- Đọc CSV files từ `notebooks/data/`
- Ingest vào Iceberg tables với metadata columns

```
Output:
├── demo.bronze.transactions  → 590,540 records
└── demo.bronze.identity      → 144,233 records
```

#### Step 2: dbt run (~1 phút)

- Chạy Silver models (2 models)
- Chạy Gold models (8 models)
- Tổng cộng 10 models

```
Output:
├── Silver Layer:
│   ├── bronze_silver.silver_transactions
│   └── bronze_silver.silver_identity
│
└── Gold Layer:
    ├── bronze_gold.daily_transaction_summary
    ├── bronze_gold.fraud_by_card_type
    ├── bronze_gold.fraud_by_product
    ├── bronze_gold.hourly_fraud_analysis
    ├── bronze_gold.high_risk_transactions
    ├── bronze_gold.kpi_summary
    ├── bronze_gold.fraud_by_day_of_week
    └── bronze_gold.fraud_by_amount_category
```

#### Step 3: Serving Layer (~1 phút)

- Tạo database `fraud_detection` trong ClickHouse
- Copy 8 Gold tables sang ClickHouse

```
Output:
├── fraud_detection.fraud_by_card_type        → 15 rows
├── fraud_detection.hourly_fraud_analysis     → 24 rows
├── fraud_detection.fraud_by_product          → 5 rows
├── fraud_detection.kpi_summary               → 1 row
├── fraud_detection.daily_transaction_summary → 182 rows
├── fraud_detection.high_risk_transactions    → 10,000 rows
├── fraud_detection.fraud_by_day_of_week      → 7 rows
└── fraud_detection.fraud_by_amount_category  → 6 rows
```

#### Step 4: Superset Auto-Setup (~2 phút)

- Cài đặt clickhouse-connect driver
- Tạo Database connection
- Tạo 8 Datasets
- Tạo 8 Charts
- Tạo 1 Dashboard với layout

```
Output:
├── Database: ClickHouse Fraud Detection
├── Datasets: 8 datasets
├── Charts: 8 charts
└── Dashboard: Fraud Detection Dashboard
```

### 3.3 Kết quả mong đợi

```
╔══════════════════════════════════════════════════════════════════════╗
║                    🎉 PIPELINE HOÀN TẤT!                             ║
╚══════════════════════════════════════════════════════════════════════╝
📊 KẾT QUẢ:
   ✅ Bronze Layer: Raw CSV → Iceberg tables (demo.bronze.*)
   ✅ Silver Layer: Cleaned data (bronze_silver.*)
   ✅ Gold Layer: Analytics tables (bronze_gold.*)
   ✅ Serving Layer: ClickHouse tables (fraud_detection.*)

🌐 TRUY CẬP:
   📊 Superset Dashboard: http://localhost:8088 (admin/admin)
   📁 MinIO Console:     http://localhost:9001 (admin/password123)
   💻 Jupyter:           http://localhost:8888
   🗄️  ClickHouse:        http://localhost:8123
```

### 3.4 Truy cập Dashboard

1. Mở browser: **http://localhost:8088**
2. Đăng nhập: `admin` / `admin`
3. Vào **Dashboards** → **Fraud Detection Dashboard**

---

## 4. Cách 2: Jupyter Notebooks

### ⭐ Cách này phù hợp để học và khám phá từng bước

### 4.1 Khởi động hệ thống

```bash
cd /path/to/Lakehouse_Project

# Khởi động Docker + Thrift Server
./scripts/start_lakehouse.sh
```

**Đợi ~2 phút** để tất cả services khởi động.

### 4.2 Mở Jupyter Lab

Truy cập: **http://localhost:8888**

### 4.3 Notebook 1: Bronze Layer

**File**: `01_bronze_layer.ipynb`

**Mục đích**: Ingest dữ liệu thô từ CSV vào Iceberg tables

**Các bước trong notebook**:

```python
# Cell 1: Import libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit

# Cell 2: Khởi tạo Spark Session với Iceberg
spark = SparkSession.builder \
    .appName("Bronze Layer") \
    .config("spark.sql.catalog.demo", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.demo.type", "rest") \
    .config("spark.sql.catalog.demo.uri", "http://iceberg-rest:8181") \
    .config("spark.sql.catalog.demo.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
    .config("spark.sql.catalog.demo.warehouse", "s3://warehouse/") \
    .config("spark.sql.catalog.demo.s3.endpoint", "http://minio:9000") \
    .getOrCreate()

# Cell 3: Đọc CSV
transactions_df = spark.read.option("header", True).csv("/home/spark/notebooks/data/train_transaction.csv")
identity_df = spark.read.option("header", True).csv("/home/spark/notebooks/data/train_identity.csv")

# Cell 4: Thêm metadata columns
transactions_df = transactions_df \
    .withColumn("_ingestion_time", current_timestamp()) \
    .withColumn("_source_file", lit("train_transaction.csv"))

# Cell 5: Tạo Iceberg tables
transactions_df.writeTo("demo.bronze.transactions").createOrReplace()
identity_df.writeTo("demo.bronze.identity").createOrReplace()

# Cell 6: Kiểm tra kết quả
spark.sql("SELECT COUNT(*) FROM demo.bronze.transactions").show()
spark.sql("SELECT COUNT(*) FROM demo.bronze.identity").show()
```

**Output**:

```
demo.bronze.transactions → 590,540 records
demo.bronze.identity     → 144,233 records
```

---

### 4.4 Notebook 2: Silver Layer

**File**: `02_silver_layer.ipynb`

**Mục đích**: Làm sạch và chuẩn hóa dữ liệu

**Các bước trong notebook**:

```python
# Cell 1: Đọc Bronze tables
transactions_df = spark.table("demo.bronze.transactions")
identity_df = spark.table("demo.bronze.identity")

# Cell 2: Data cleaning
# - Xử lý null values
# - Standardize data types
# - Remove duplicates

# Cell 3: Feature engineering
# - Tạo các derived columns
# - Categorization

# Cell 4: Ghi vào Silver layer
cleaned_transactions.writeTo("demo.silver.silver_transactions").createOrReplace()
cleaned_identity.writeTo("demo.silver.silver_identity").createOrReplace()
```

**Output**:

```
demo.silver.silver_transactions → Cleaned transaction data
demo.silver.silver_identity     → Cleaned identity data
```

> 💡 **Thay thế**: Có thể dùng `dbt run` thay cho notebook này

---

### 4.5 Notebook 3: Gold Layer

**File**: `03_gold_layer.ipynb`

**Mục đích**: Tạo các bảng phân tích và aggregations

**Các bước trong notebook**:

```python
# Cell 1: Đọc Silver tables
silver_trans = spark.table("demo.silver.silver_transactions")
silver_identity = spark.table("demo.silver.silver_identity")

# Cell 2: Join tables
enriched_df = silver_trans.join(silver_identity, "TransactionID", "left")

# Cell 3: Tạo aggregations
# - Daily summary
# - Fraud by card type
# - Fraud by product
# - Hourly analysis
# - KPI summary

# Cell 4: Ghi vào Gold layer
daily_summary.writeTo("demo.gold.daily_transaction_summary").createOrReplace()
fraud_by_card.writeTo("demo.gold.fraud_by_card_type").createOrReplace()
# ... các tables khác
```

**Output**:

```
demo.gold.daily_transaction_summary → Tổng hợp theo ngày
demo.gold.fraud_by_card_type        → Phân tích theo loại thẻ
demo.gold.fraud_by_product          → Phân tích theo sản phẩm
demo.gold.hourly_fraud_analysis     → Phân tích theo giờ
demo.gold.high_risk_transactions    → Giao dịch rủi ro cao
demo.gold.kpi_summary               → Tổng hợp KPIs
```

> 💡 **Thay thế**: Có thể dùng `dbt run` thay cho notebook này

---

### 4.6 Notebook 4: Serving Layer

**File**: `04_serving_layer.ipynb`

**Mục đích**: Copy dữ liệu Gold sang ClickHouse

**Các bước trong notebook**:

```python
# Cell 1: Import clickhouse-driver
import clickhouse_driver

# Cell 2: Kết nối ClickHouse
client = clickhouse_driver.Client(
    host='clickhouse',
    port=9000,
    user='default',
    password='clickhouse123'
)

# Cell 3: Tạo database
client.execute("CREATE DATABASE IF NOT EXISTS fraud_detection")

# Cell 4: Đọc Gold tables và copy sang ClickHouse
gold_tables = [
    "fraud_by_card_type",
    "hourly_fraud_analysis",
    "fraud_by_product",
    "kpi_summary",
    "daily_transaction_summary",
    "high_risk_transactions"
]

for table in gold_tables:
    # Đọc từ Iceberg
    df = spark.table(f"demo.gold.{table}")

    # Copy sang ClickHouse
    # (implementation chi tiết trong notebook)
```

**Output**:

```
fraud_detection.fraud_by_card_type        → 15 rows
fraud_detection.hourly_fraud_analysis     → 24 rows
fraud_detection.fraud_by_product          → 5 rows
fraud_detection.kpi_summary               → 1 row
fraud_detection.daily_transaction_summary → 182 rows
fraud_detection.high_risk_transactions    → 10,000 rows
```

---

## 5. Iceberg Time Travel Demo

### 📓 Notebook 5: Time Travel (`05_time_travel_demo.ipynb`)

**Mục đích**: Trực quan hóa tính năng **Time Travel** độc đáo của Apache Iceberg

### 5.1 Xem lịch sử thay đổi

```python
# Xem history của table
spark.sql("""
    SELECT * FROM demo.bronze.transactions.history
    ORDER BY made_current_at DESC
""").show()
```

**Output**:

```
+--------------------+-------------------+-------------------+
|made_current_at     |snapshot_id        |parent_id          |
+--------------------+-------------------+-------------------+
|2026-02-02 13:40:10 |8940796255292973358|null               |
+--------------------+-------------------+-------------------+
```

### 5.2 Xem danh sách Snapshots

```python
# Xem tất cả snapshots
spark.sql("""
    SELECT
        snapshot_id,
        committed_at,
        operation,
        summary
    FROM demo.bronze.transactions.snapshots
""").show(truncate=False)
```

### 5.3 Query dữ liệu tại thời điểm cụ thể

```python
# Query dữ liệu tại snapshot cụ thể
snapshot_id = 8940796255292973358

df_old = spark.read \
    .option("snapshot-id", snapshot_id) \
    .table("demo.bronze.transactions")

df_old.count()
```

### 5.4 Query theo timestamp

```python
# Query dữ liệu tại thời điểm cụ thể
df_at_time = spark.read \
    .option("as-of-timestamp", "2026-02-02 13:00:00") \
    .table("demo.bronze.transactions")
```

### 5.5 So sánh 2 versions

```python
# Đọc 2 versions khác nhau
old_snapshot = 8940796255292973350
new_snapshot = 8940796255292973358

df_old = spark.read.option("snapshot-id", old_snapshot).table("demo.bronze.transactions")
df_new = spark.read.option("snapshot-id", new_snapshot).table("demo.bronze.transactions")

# So sánh số lượng records
print(f"Old snapshot: {df_old.count()} records")
print(f"New snapshot: {df_new.count()} records")
print(f"Difference: {df_new.count() - df_old.count()} records")
```

### 5.6 Rollback về version trước

```python
# Rollback table về snapshot cụ thể
spark.sql(f"""
    CALL demo.system.rollback_to_snapshot(
        'demo.bronze.transactions',
        {old_snapshot_id}
    )
""")
```

### 5.7 Các use cases của Time Travel

| Use Case            | Mô tả                             | Ví dụ                      |
| ------------------- | --------------------------------- | -------------------------- |
| **Data Recovery**   | Khôi phục sau khi xóa/update nhầm | Rollback về snapshot trước |
| **Audit**           | Xem dữ liệu tại thời điểm cụ thể  | Query as-of timestamp      |
| **Debugging**       | Tìm khi nào data bị thay đổi      | So sánh snapshots          |
| **Reproducibility** | Chạy lại analysis với data cũ     | Query specific snapshot    |
| **Testing**         | Test với production data snapshot | Tạo test từ snapshot       |

---

## 6. Tạo Dashboard Trong Superset

### 6.1 Đăng nhập Superset

1. Mở browser: **http://localhost:8088**
2. Đăng nhập: `admin` / `admin`

### 6.2 Tạo Database Connection (nếu chưa có)

1. Vào **Settings** (⚙️) → **Database Connections**
2. Click **+ Database**
3. Chọn **ClickHouse Connect**
4. Nhập connection string:
   ```
   clickhousedb://default:clickhouse123@clickhouse:8123/fraud_detection
   ```
5. Click **Test Connection**
6. Click **Connect**

### 6.3 Tạo Dataset

1. Vào **SQL Lab** → **SQL Editor**
2. Chọn Database: `ClickHouse Fraud Detection`
3. Chọn Schema: `fraud_detection`
4. Thấy các tables:
   - `fraud_by_card_type`
   - `hourly_fraud_analysis`
   - `daily_transaction_summary`
   - ... và các tables khác

5. Click **+ Dataset** để tạo dataset từ table

### 6.4 Tạo Charts

**Chart 1: Tổng số giao dịch (Big Number)**

- Dataset: `kpi_summary`
- Metric: `total_transactions`
- Chart type: Big Number

**Chart 2: Tỷ lệ gian lận (Gauge)**

- Dataset: `kpi_summary`
- Metric: `fraud_rate_pct`
- Chart type: Gauge Chart

**Chart 3: Gian lận theo loại thẻ (Bar Chart)**

- Dataset: `fraud_by_card_type`
- Dimension: `card_brand`
- Metrics: `fraud_count`, `legitimate_count`
- Chart type: Bar Chart

**Chart 4: Xu hướng theo ngày (Line Chart)**

- Dataset: `daily_transaction_summary`
- Dimension: `transaction_day`
- Metrics: `fraud_count`, `total_transactions`
- Chart type: Time-series Line Chart

### 6.5 Tạo Dashboard

1. Vào **Dashboards** → **+ Dashboard**
2. Đặt tên: "Fraud Detection Dashboard"
3. Kéo thả các Charts vào Dashboard
4. Sắp xếp layout
5. **Save**

---

## 7. Dừng Hệ Thống

### 7.1 Dừng tạm thời (giữ data)

```bash
./scripts/stop_lakehouse.sh
```

Hoặc:

```bash
docker compose stop
```

### 7.2 Dừng và xóa containers (giữ data trong volumes)

```bash
docker compose down
```

### 7.3 Dừng và xóa toàn bộ (bao gồm data)

⚠️ **Cảnh báo**: Lệnh này sẽ xóa tất cả dữ liệu!

```bash
docker compose down -v
```

### 7.4 Khởi động lại

```bash
# Nếu muốn giữ data cũ
./scripts/start_lakehouse.sh

# Nếu muốn chạy lại từ đầu
docker compose down -v
./scripts/run_full_pipeline.sh
```

---

## 8. Xử Lý Sự Cố

### 8.1 Docker không chạy

**Triệu chứng**: `Cannot connect to the Docker daemon`

**Giải pháp**:

```bash
# Linux
sudo systemctl start docker

# Mac/Windows
# Mở Docker Desktop
```

### 8.2 Container không khởi động

**Triệu chứng**: Container exit với error

**Giải pháp**:

```bash
# Xem logs
docker logs spark-iceberg
docker logs clickhouse
docker logs superset

# Restart container cụ thể
docker restart spark-iceberg
```

### 8.3 Thrift Server không khởi động

**Triệu chứng**: dbt connection failed, port 10000 không mở

**Giải pháp**:

```bash
# Xem logs Thrift Server
docker exec spark-iceberg cat /opt/spark/logs/*HiveThriftServer2*.out | tail -50

# Stop và restart
docker exec spark-iceberg /opt/spark/sbin/stop-thriftserver.sh
./scripts/start_lakehouse.sh
```

### 8.4 dbt run failed

**Triệu chứng**: `dbt run` báo lỗi

**Giải pháp**:

```bash
# Test connection
docker exec dbt dbt debug

# Xem chi tiết lỗi
docker exec dbt dbt run --debug

# Chạy lại model cụ thể
docker exec dbt dbt run --select silver_transactions
```

### 8.5 ClickHouse connection failed

**Triệu chứng**: Không query được ClickHouse

**Giải pháp**:

```bash
# Kiểm tra ClickHouse
curl "http://localhost:8123/?query=SELECT%201"

# Restart ClickHouse
docker restart clickhouse

# Chờ 10 giây và thử lại
sleep 10
curl "http://localhost:8123/?query=SELECT%201"
```

### 8.6 Superset không load được charts

**Triệu chứng**: Dashboard trống, charts không hiển thị

**Giải pháp**:

1. Kiểm tra Database connection trong Superset
2. Vào **Settings → Database Connections**
3. Click vào database → **Test Connection**
4. Nếu fail, kiểm tra ClickHouse đang chạy

### 8.7 Thiếu data

**Triệu chứng**: Tables trống, không có records

**Giải pháp**:

```bash
# Kiểm tra Bronze tables có data
docker exec spark-iceberg /opt/spark/bin/spark-sql \
    -e "SELECT COUNT(*) FROM demo.bronze.transactions"

# Nếu trống, chạy lại Bronze layer
./scripts/run_full_pipeline.sh
```

### 8.8 Reset hoàn toàn

**Khi tất cả cách khác không được**:

```bash
# Dừng và xóa tất cả
docker compose down -v

# Xóa cache Docker (tùy chọn)
docker system prune -a

# Chạy lại từ đầu
./scripts/run_full_pipeline.sh
```

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề không giải quyết được, hãy:

1. Kiểm tra logs: `docker logs <container_name>`
2. Xem lại các bước trong hướng dẫn
3. Reset và chạy lại từ đầu

---

## ✅ Checklist Hoàn Thành

- [ ] Docker đang chạy
- [ ] Data files có trong `notebooks/data/`
- [ ] Pipeline hoàn thành (Cách 1 hoặc Cách 2)
- [ ] Truy cập Superset Dashboard thành công
- [ ] Thử nghiệm Time Travel với Notebook 5

**🎉 Chúc mừng! Bạn đã thiết lập thành công Lakehouse Platform!**
