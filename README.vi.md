# FULLSTACK OPEN-SOURCE LAKEHOUSE PLATFORM

## Credit Card Fraud Detection - IEEE-CIS Dataset

[English Version (Tiếng Anh)](README.md)

Dự án xây dựng hệ thống **Data Lakehouse** hoàn chỉnh sử dụng các công nghệ mã nguồn mở, triển khai kiến trúc **Medallion** (Bronze → Silver → Gold) để phát hiện gian lận thẻ tín dụng.

---

## DEMO VIDEO + REPORT + THÀNH TÍCH

### Video Demo YouTube

- Video Youtube demo toàn bộ hệ thống: https://youtu.be/EgT8e-iyamY

### Tài liệu & minh chứng

- Full report: [link report](https://drive.google.com/file/d/18bJnAQuuIVRhmkpPU1UAl8eTy4BETjKW/view?usp=sharing)
- Slide thuyết trình: [link slide](https://drive.google.com/file/d/1hWDCTY-EJjPyTfa0sNK7GCGjlZe3JlpT/view?usp=sharing)
- Facebook (minh chứng dự án đạt Top 10): https://www.facebook.com/share/p/1EdAeNJfm5/

---

## QUICK START - 2 CÁCH CHẠY

### Cách 1: ONE COMMAND (Khuyến nghị - Tự động hóa hoàn toàn)

```bash
# Chạy toàn bộ pipeline chỉ với 1 lệnh
./scripts/run_full_pipeline.sh
```

**Kết quả**: Bronze → Silver → Gold → ClickHouse → Superset Dashboard - **hoàn toàn tự động!**

### 📓 Cách 2: Interactive Notebooks (Học tập & Khám phá)

```bash
# 1. Khởi động hệ thống
./scripts/start_lakehouse.sh

# 2. Mở Jupyter: http://localhost:8888
# 3. Chạy lần lượt các notebook:
#    - 01_bronze_layer.ipynb  → Ingest raw data
#    - 02_silver_layer.ipynb  → Clean & transform
#    - 03_gold_layer.ipynb    → Analytics & aggregations
#    - 04_serving_layer.ipynb → Copy to ClickHouse

# 4. Tạo Dashboard: http://localhost:8088 (admin/admin)

# Bonus: Khám phá Iceberg Time Travel
# 5. Chạy 05_time_travel_demo.ipynb
```

**Xem hướng dẫn chi tiết**: [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## Mục Lục

1. [Demo Video + Report + Thành Tích](#-demo-video--report--thành-tích)
2. [Yêu Cầu Hệ Thống](#-yêu-cầu-hệ-thống)
3. [Kiến Trúc Hệ Thống](#-kiến-trúc-hệ-thống)
4. [Cách 1: Full Pipeline Script](#-cách-1-full-pipeline-script)
5. [Cách 2: Jupyter Notebooks](#-cách-2-jupyter-notebooks)
6. [Iceberg Time Travel Demo](#-iceberg-time-travel-demo)
7. [Truy Cập Services](#-truy-cập-services)
8. [Cấu Trúc Thư Mục](#-cấu-trúc-thư-mục)
9. [Xử Lý Lỗi](#-xử-lý-lỗi-thường-gặp)

---

## Yêu Cầu Hệ Thống

### Phần cứng tối thiểu

| Thành phần | Tối thiểu | Khuyến nghị |
| ---------- | --------- | ----------- |
| **RAM**    | 8GB       | 16GB        |
| **Disk**   | 15GB      | 25GB        |
| **CPU**    | 4 cores   | 8 cores     |

### Phần mềm cần cài

- **Docker** & **Docker Compose** v2.x
- **Python 3.x** (cho Superset auto-setup)
- **Git** (tùy chọn)

### Kiểm tra Docker

```bash
docker --version        # Docker version 24.x+
docker compose version  # Docker Compose version v2.x+
```

---

## Kiến Trúc Hệ Thống

![Lakehouse Architecture](github-assets/images/architecture.png)

_Hình: Kiến trúc tổng thể pipeline từ nguồn dữ liệu đến tầng Serving và Dashboard._

### Bên trong Apache Iceberg Table

![Apache Iceberg Table](github-assets/images/apache_iceberg_table.png)

_Hình: Minh họa các thành phần chính của table Iceberg: partitioning, schema evolution và snapshot timeline (kèm rollback)._

### Vai trò và Use Cases

![Use Case Diagram](github-assets/images/usecase_diagram.png)

_Hình: Các vai trò chính trong hệ thống gồm Data Engineer, Data Analyst và Auditor._

### Công nghệ sử dụng

| Tầng               | Công nghệ       | Mô tả                          | Port       |
| ------------------ | --------------- | ------------------------------ | ---------- |
| **Storage**        | MinIO           | Object storage tương thích S3  | 9000/9001  |
| **Catalog**        | Iceberg REST    | REST Catalog cho Iceberg       | 8181       |
| **Table Format**   | Apache Iceberg  | ACID transactions, Time Travel | -          |
| **Compute**        | Apache Spark    | Distributed data processing    | 8888/10000 |
| **Transformation** | dbt             | Data transformation với tests  | -          |
| **Serving**        | ClickHouse      | OLAP database hiệu năng cao    | 8123       |
| **Visualization**  | Apache Superset | Dashboard & BI                 | 8088       |

---

## Cách 1: Full Pipeline Script

### Yêu cầu trước khi chạy

1. **Docker đang chạy**
2. **Data files có sẵn** trong `notebooks/data/`:
   - 📥 Tải bộ dữ liệu từ Kaggle: **[IEEE-CIS Fraud Detection](https://www.kaggle.com/competitions/ieee-fraud-detection)**
   - Tải file zip, giải nén và copy 2 file sau vào thư mục `notebooks/data/`:
     - `train_transaction.csv` (590,540 records)
     - `train_identity.csv` (144,233 records)

### Chạy Pipeline

```bash
cd /path/to/Lakehouse_Project

# Chạy toàn bộ pipeline
./scripts/run_full_pipeline.sh
```

### Các bước tự động thực hiện

| Step | Tên            | Mô tả                                        | Thời gian |
| ---- | -------------- | -------------------------------------------- | --------- |
| 0    | Docker Stack   | Khởi động 7 containers + Thrift Server       | ~2 phút   |
| 1    | Bronze Layer   | Ingest CSV → Iceberg tables                  | ~2 phút   |
| 2    | dbt run        | Transform Silver + Gold (10 models)          | ~1 phút   |
| 3    | Serving Layer  | Copy Gold tables → ClickHouse (8 tables)     | ~1 phút   |
| 4    | Superset Setup | Tạo Database + Datasets + Charts + Dashboard | ~2 phút   |

**Tổng thời gian: ~8-10 phút**

### Kết quả mong đợi

```
╔══════════════════════════════════════════════════════════════════════╗
║                       PIPELINE HOÀN TẤT!                             ║
╚══════════════════════════════════════════════════════════════════════╝
 KẾT QUẢ:
    Bronze Layer: Raw CSV → Iceberg tables (demo.bronze.*)
    Silver Layer: Cleaned data (demo.silver.*)
    Gold Layer: Analytics tables (demo.gold.*)
    Serving Layer: ClickHouse tables (fraud_detection.*)

 TRUY CẬP:
    Superset Dashboard: http://localhost:8088 (admin/admin)
    MinIO Console:     http://localhost:9001 (admin/password123)
    Jupyter:           http://localhost:8888
     ClickHouse:        http://localhost:8123
```

---

## Cách 2: Jupyter Notebooks

Phương pháp này cho phép bạn **học và khám phá** từng bước của pipeline một cách trực quan.

### Bước 1: Khởi động hệ thống

```bash
cd /path/to/Lakehouse_Project

# Khởi động Docker stack + Thrift Server
./scripts/start_lakehouse.sh
```

### Bước 2: Mở Jupyter Lab

Truy cập: **http://localhost:8888**

### Bước 3: Chạy các Notebooks theo thứ tự

#### Notebook 1: Bronze Layer (`01_bronze_layer.ipynb`)

**Mục đích**: Ingest dữ liệu thô từ CSV vào Iceberg tables

![Bronze Notebook Mapping](github-assets/images/bronze_layer.png)

_Sơ đồ này tương ứng trực tiếp với logic trong notebook `01_bronze_layer.ipynb`._

**Nội dung**:

- Khởi tạo Spark Session với Iceberg
- Đọc file CSV (transactions + identity)
- Thêm metadata columns (`_ingestion_time`, `_source_file`)
- Tạo Iceberg tables trong namespace `demo.bronze`

**Output**:

```
demo.bronze.transactions → 590,540 records
demo.bronze.identity     → 144,233 records
```

---

#### Notebook 2: Silver Layer (`02_silver_layer.ipynb`)

**Mục đích**: Làm sạch và chuẩn hóa dữ liệu

![Silver Layer Flow](github-assets/images/silver_layer.png)

_Sơ đồ thể hiện mapping từ nguồn Bronze (`bronze_transactions`, `bronze_identity`) sang hai model Silver tương ứng._

**Nội dung**:

- Data cleaning (xử lý null values)
- Data type standardization
- Feature engineering cơ bản
- Tạo tables trong namespace `demo.silver`

**Output**:

```
demo.silver.silver_transactions → Cleaned transaction data
demo.silver.silver_identity     → Cleaned identity data
```

> **Lưu ý**: Notebook này có thể được thay thế bằng `dbt run` với models trong `dbt_project/models/silver/`

---

#### Notebook 3: Gold Layer (`03_gold_layer.ipynb`)

**Mục đích**: Tạo các bảng phân tích và aggregations

![dbt Dependency Graph](github-assets/images/dbt_dependency.png)

_Sơ đồ phụ thuộc dbt: nguồn Bronze -> model Silver -> các model Gold dùng cho reporting._

**Nội dung**:

- Join Silver transactions + identity
- Tính toán KPIs và metrics
- Tạo các aggregation tables cho reporting
- Tạo tables trong namespace `demo.gold`

**Output**:

```
demo.gold.daily_transaction_summary → Tổng hợp theo ngày
demo.gold.fraud_by_card_type        → Phân tích theo loại thẻ
demo.gold.fraud_by_product          → Phân tích theo sản phẩm
demo.gold.hourly_fraud_analysis     → Phân tích theo giờ
demo.gold.high_risk_transactions    → Giao dịch rủi ro cao
demo.gold.kpi_summary               → Tổng hợp KPIs
```

> **Lưu ý**: Notebook này có thể được thay thế bằng `dbt run` với models trong `dbt_project/models/gold/`

---

#### Notebook 4: Serving Layer (`04_serving_layer.ipynb`)

**Mục đích**: Copy dữ liệu Gold sang ClickHouse để phục vụ Dashboard

**Nội dung**:

- Kết nối ClickHouse qua clickhouse-driver
- Tạo database `fraud_detection` trong ClickHouse
- Copy toàn bộ Gold tables sang ClickHouse
- Tối ưu cấu trúc tables cho OLAP queries

**Output**:

```
fraud_detection.fraud_by_card_type        → 15 rows
fraud_detection.hourly_fraud_analysis     → 24 rows
fraud_detection.fraud_by_product          → 5 rows
fraud_detection.kpi_summary               → 1 row
fraud_detection.daily_transaction_summary → 182 rows
fraud_detection.high_risk_transactions    → 10,000 rows
fraud_detection.fraud_by_day_of_week      → 7 rows
fraud_detection.fraud_by_amount_category  → 6 rows
```

---

### Bước 4: Tạo Dashboard trong Superset

1. Mở: **http://localhost:8088**
2. Đăng nhập: `admin` / `admin`
3. Vào **Settings → Database Connections → + Database**
4. Chọn **ClickHouse Connect**
5. Nhập connection string:
   ```
   clickhousedb://default:clickhouse123@clickhouse:8123/fraud_detection
   ```
6. **Test Connection** → **Connect**
7. Tạo Datasets và Charts

---

## Iceberg Time Travel Demo

### Notebook 5: Time Travel (`05_time_travel_demo.ipynb`)

**Mục đích**: Trực quan hóa tính năng **Time Travel** của Apache Iceberg

![Iceberg Time Travel Flow](github-assets/images/time_travel.png)

_Flow Time Travel phục vụ audit: truy vấn theo timestamp hoặc version ID, đọc metadata snapshot cũ, sau đó trả về dữ liệu lịch sử chính xác._

**Các thao tác chính trong notebook**:

- Query dữ liệu theo thời điểm: `TIMESTAMP AS OF`
- Query dữ liệu theo version/snapshot: `VERSION AS OF`
- Xem lịch sử snapshots và metadata để audit
- Rollback table về snapshot mong muốn khi cần khôi phục

**Các trường hợp sử dụng Time Travel**:

- **Data Recovery**: Khôi phục dữ liệu sau khi xóa nhầm
- **Audit**: Xem dữ liệu tại thời điểm cụ thể
- **Testing**: So sánh kết quả giữa các versions
- **Analytics**: Phân tích xu hướng thay đổi theo thời gian

---

## Truy Cập Services

| Service           | URL                   | Credentials             | Mô tả              |
| ----------------- | --------------------- | ----------------------- | ------------------ |
| **Superset**      | http://localhost:8088 | admin / admin           | Dashboard & BI     |
| **Jupyter Lab**   | http://localhost:8888 | -                       | Notebooks          |
| **MinIO Console** | http://localhost:9001 | admin / password123     | Object Storage UI  |
| **ClickHouse**    | http://localhost:8123 | default / clickhouse123 | OLAP Database      |
| **Spark UI**      | http://localhost:4040 | -                       | Spark Jobs Monitor |
| **Iceberg REST**  | http://localhost:8181 | -                       | Catalog REST API   |

---

## Cấu Trúc Thư Mục

```
Lakehouse_Project/
├──  docker-compose.yml       # Docker services configuration
├──  README.md                # Tài liệu chính (file này)
├──  SETUP_GUIDE.md           # Hướng dẫn chi tiết
│
├──  notebooks/               # Jupyter Notebooks
│   ├── 01_bronze_layer.ipynb   # Ingestion raw data
│   ├── 02_silver_layer.ipynb   # Data cleaning
│   ├── 03_gold_layer.ipynb     # Aggregations
│   ├── 04_serving_layer.ipynb  # Copy to ClickHouse
│   ├── 05_time_travel_demo.ipynb # Iceberg Time Travel
│   └──  data/                # CSV data files
│       ├── train_transaction.csv
│       └── train_identity.csv
│
├──  dbt_project/             # dbt transformation
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └──  models/
│       ├──  silver/          # Silver layer models
│       │   ├── silver_transactions.sql
│       │   ├── silver_identity.sql
│       │   └── schema.yml
│       └──  gold/            # Gold layer models
│           ├── daily_transaction_summary.sql
│           ├── fraud_by_card_type.sql
│           ├── fraud_by_product.sql
│           ├── hourly_fraud_analysis.sql
│           ├── high_risk_transactions.sql
│           ├── kpi_summary.sql
│           └── schema.yml
│
└──  scripts/                 # Utility scripts
    ├── run_full_pipeline.sh    #  Full automation script
    ├── start_lakehouse.sh      # Start Docker + Thrift Server
    ├── stop_lakehouse.sh       # Stop all services
    ├── run_dbt.sh              # Run dbt commands
    ├── bronze_layer.py         # Bronze ingestion script
    ├── serving_layer.py        # Serving layer script
    ├── setup_superset.py       # Superset auto-setup
    └── create_namespaces.py    # Create Iceberg namespaces
```

---

## Xử Lý Lỗi Thường Gặp

### 1. Docker không chạy

```bash
# Kiểm tra Docker daemon
docker info

# Nếu lỗi, khởi động Docker Desktop hoặc service
sudo systemctl start docker
```

### 2. Thiếu data files

```bash
# Kiểm tra data files
ls -la notebooks/data/*.csv

# Cần có:
# - train_transaction.csv
# - train_identity.csv
```

### 3. Thrift Server không khởi động

```bash
# Xem logs
docker exec spark-iceberg cat /opt/spark/logs/*HiveThriftServer2*.out | tail -50

# Restart Thrift Server
docker exec spark-iceberg /opt/spark/sbin/stop-thriftserver.sh
./scripts/start_lakehouse.sh
```

### 4. dbt connection failed

```bash
# Kiểm tra Thrift Server port
docker exec dbt python3 -c "import socket; s=socket.socket(); s.settimeout(2); print('OK' if s.connect_ex(('spark-iceberg', 10000))==0 else 'FAIL')"

# Test dbt connection
docker exec dbt dbt debug
```

### 5. ClickHouse connection failed

```bash
# Kiểm tra ClickHouse
curl "http://localhost:8123/?query=SELECT%201"

# Restart ClickHouse
docker restart clickhouse
```

### 6. Reset toàn bộ hệ thống

```bash
# Dừng và xóa tất cả volumes
docker compose down -v

# Khởi động lại từ đầu
./scripts/run_full_pipeline.sh
```

---

## Tài Liệu Bổ Sung

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Hướng dẫn chi tiết từng bước
- [dbt_project/README.md](dbt_project/README.md) - dbt documentation
- [github-assets/markdown/](github-assets/markdown/) - Các tài liệu khác

---

## Author

Dự án được xây dựng để demo kiến trúc **Data Lakehouse** sử dụng hoàn toàn công nghệ **Open Source**.

---

## License

MIT License - Sử dụng tự do cho mục đích học tập và nghiên cứu.
