# FULLSTACK OPEN-SOURCE LAKEHOUSE PLATFORM

## Credit Card Fraud Detection - IEEE-CIS Dataset

[Tiếng Việt (Vietnamese)](README.vi.md)

This project builds a complete **Data Lakehouse** system using open-source technologies, implementing the **Medallion** architecture (Bronze → Silver → Gold) to detect credit card fraud.

---

## DEMO VIDEO + REPORT + ACHIEVEMENTS

### YouTube Demo Video

- YouTube video demoing the entire system: https://youtu.be/EgT8e-iyamY

### Documents & Evidence

- Full report: [link report](https://drive.google.com/file/d/18bJnAQuuIVRhmkpPU1UAl8eTy4BETjKW/view?usp=sharing)
- Presentation slides: [link slide](https://drive.google.com/file/d/1hWDCTY-EJjPyTfa0sNK7GCGjlZe3JlpT/view?usp=sharing)
- Facebook (Proof of project reaching Top 10): https://www.facebook.com/share/p/1EdAeNJfm5/

---

## QUICK START - 2 WAYS TO RUN

### Option 1: ONE COMMAND (Recommended - Fully Automated)

```bash
# Run the entire pipeline with a single command
./scripts/run_full_pipeline.sh
```

**Result**: Bronze → Silver → Gold → ClickHouse → Superset Dashboard - **completely automated!**

### 📓 Option 2: Interactive Notebooks (Learning & Exploration)

```bash
# 1. Start the system
./scripts/start_lakehouse.sh

# 2. Open Jupyter: http://localhost:8888
# 3. Run notebooks sequentially:
#    - 01_bronze_layer.ipynb  → Ingest raw data
#    - 02_silver_layer.ipynb  → Clean & transform
#    - 03_gold_layer.ipynb    → Analytics & aggregations
#    - 04_serving_layer.ipynb → Copy to ClickHouse

# 4. Create Dashboard: http://localhost:8088 (admin/admin)

# Bonus: Explore Iceberg Time Travel
# 5. Run 05_time_travel_demo.ipynb
```

**See detailed instructions**: [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## Table of Contents

1. [Demo Video + Report + Achievements](#-demo-video--report--achievements)
2. [System Requirements](#-system-requirements)
3. [System Architecture](#-system-architecture)
4. [Option 1: Full Pipeline Script](#-option-1-full-pipeline-script)
5. [Option 2: Jupyter Notebooks](#-option-2-jupyter-notebooks)
6. [Iceberg Time Travel Demo](#-iceberg-time-travel-demo)
7. [Access Services](#-access-services)
8. [Directory Structure](#-directory-structure)
9. [Troubleshooting](#-troubleshooting)

---

## System Requirements

### Minimum Hardware

| Component | Minimum | Recommended |
| --------- | ------- | ----------- |
| **RAM**   | 8GB     | 16GB        |
| **Disk**  | 15GB    | 25GB        |
| **CPU**   | 4 cores | 8 cores     |

### Software Requirements

- **Docker** & **Docker Compose** v2.x
- **Python 3.x** (for Superset auto-setup)
- **Git** (optional)

### Check Docker

```bash
docker --version        # Docker version 24.x+
docker compose version  # Docker Compose version v2.x+
```

---

## System Architecture

![Lakehouse Architecture](github-assets/images/architecture.png)

_Figure: Overall pipeline architecture from data source to Serving layer and Dashboard._

### Inside Apache Iceberg Table

![Apache Iceberg Table](github-assets/images/apache_iceberg_table.png)

_Figure: Illustration of major Iceberg table components: partitioning, schema evolution, and snapshot timeline (with rollback)._

### Roles and Use Cases

![Use Case Diagram](github-assets/images/usecase_diagram.png)

_Figure: Key roles in the system including Data Engineer, Data Analyst, and Auditor._

### Technologies Used

| Layer              | Technology      | Description                    | Port       |
| ------------------ | --------------- | ------------------------------ | ---------- |
| **Storage**        | MinIO           | S3-compatible object storage   | 9000/9001  |
| **Catalog**        | Iceberg REST    | REST Catalog for Iceberg       | 8181       |
| **Table Format**   | Apache Iceberg  | ACID transactions, Time Travel | -          |
| **Compute**        | Apache Spark    | Distributed data processing    | 8888/10000 |
| **Transformation** | dbt             | Data transformation with tests | -          |
| **Serving**        | ClickHouse      | High-performance OLAP database | 8123       |
| **Visualization**  | Apache Superset | Dashboard & BI                 | 8088       |

---

## Option 1: Full Pipeline Script

### Prerequisites before running

1. **Docker is running**
2. **Data files available** in `notebooks/data/`:
   - 📥 Download dataset from Kaggle: **[IEEE-CIS Fraud Detection](https://www.kaggle.com/competitions/ieee-fraud-detection)**
   - Download the zip, extract and copy these 2 files to `notebooks/data/`:
     - `train_transaction.csv` (590,540 records)
     - `train_identity.csv` (144,233 records)

### Run Pipeline

```bash
cd /path/to/Lakehouse_Project

# Run the entire pipeline
./scripts/run_full_pipeline.sh
```

### Automated Steps

| Step | Name           | Description                                | Time    |
| ---- | -------------- | ------------------------------------------ | ------- |
| 0    | Docker Stack   | Start 7 containers + Thrift Server         | ~2 mins |
| 1    | Bronze Layer   | Ingest CSV → Iceberg tables                | ~2 mins |
| 2    | dbt run        | Transform Silver + Gold (10 models)        | ~1 min  |
| 3    | Serving Layer  | Copy Gold tables → ClickHouse (8 tables)   | ~1 min  |
| 4    | Superset Setup | Create Database + Datasets + Charts + Dash | ~2 mins |

**Total time: ~8-10 minutes**

### Expected Results

```
╔══════════════════════════════════════════════════════════════════════╗
║                       PIPELINE COMPLETED!                            ║
╚══════════════════════════════════════════════════════════════════════╝
 RESULTS:
    Bronze Layer: Raw CSV → Iceberg tables (demo.bronze.*)
    Silver Layer: Cleaned data (demo.silver.*)
    Gold Layer: Analytics tables (demo.gold.*)
    Serving Layer: ClickHouse tables (fraud_detection.*)

 ACCESS:
    Superset Dashboard: http://localhost:8088 (admin/admin)
    MinIO Console:     http://localhost:9001 (admin/password123)
    Jupyter:           http://localhost:8888
    ClickHouse:        http://localhost:8123
```

---

## Option 2: Jupyter Notebooks

This method allows you to **learn and explore** each pipeline step visually.

### Step 1: Start the system

```bash
cd /path/to/Lakehouse_Project

# Start Docker stack + Thrift Server
./scripts/start_lakehouse.sh
```

### Step 2: Open Jupyter Lab

Access: **http://localhost:8888**

### Step 3: Run Notebooks in order

#### Notebook 1: Bronze Layer (`01_bronze_layer.ipynb`)

**Purpose**: Ingest raw data from CSV to Iceberg tables.

**Output**:

- `demo.bronze.transactions` → 590,540 records
- `demo.bronze.identity` → 144,233 records

---

#### Notebook 2: Silver Layer (`02_silver_layer.ipynb`)

**Purpose**: Clean and standardize data.

**Output**:

- `demo.silver.silver_transactions` → Cleaned transaction data
- `demo.silver.silver_identity` → Cleaned identity data

> **Note**: This notebook can be replaced by `dbt run` with models in `dbt_project/models/silver/`.

---

#### Notebook 3: Gold Layer (`03_gold_layer.ipynb`)

**Purpose**: Create analytical tables and aggregations.

**Output**:

- `demo.gold.daily_transaction_summary`
- `demo.gold.fraud_by_card_type`
- `demo.gold.fraud_by_product`
- `demo.gold.hourly_fraud_analysis`
- `demo.gold.high_risk_transactions`
- `demo.gold.kpi_summary`

---

#### Notebook 4: Serving Layer (`04_serving_layer.ipynb`)

**Purpose**: Copy Gold data to ClickHouse for Dashboard serving.

---

### Step 4: Create Dashboard in Superset

1. Open: **http://localhost:8088** (admin/admin)
2. **Settings → Database Connections → + Database**
3. Select **ClickHouse Connect**
4. URI: `clickhousedb://default:clickhouse123@clickhouse:8123/fraud_detection`
5. **Test Connection** → **Connect**

---

## Iceberg Time Travel Demo

### Notebook 5: Time Travel (`05_time_travel_demo.ipynb`)

**Purpose**: Visualize **Time Travel** features of Apache Iceberg.

**Key Use Cases**:

- **Data Recovery**: Restore data after accidental deletion.
- **Audit**: View data at a specific point in time.
- **Testing**: Compare results between versions.

---

## Access Services

| Service           | URL                   | Credentials             | Description        |
| ----------------- | --------------------- | ----------------------- | ------------------ |
| **Superset**      | http://localhost:8088 | admin / admin           | Dashboard & BI     |
| **Jupyter Lab**   | http://localhost:8888 | -                       | Notebooks          |
| **MinIO Console** | http://localhost:9001 | admin / password123     | Object Storage UI  |
| **ClickHouse**    | http://localhost:8123 | default / clickhouse123 | OLAP Database      |
| **Spark UI**      | http://localhost:4040 | -                       | Spark Jobs Monitor |
| **Iceberg REST**  | http://localhost:8181 | -                       | Catalog REST API   |

---

## Directory Structure

Refer to the repository for the full directory structure including Spark notebooks, dbt projects, and automation scripts.

---

## Troubleshooting

1. **Docker not running**: Check `docker info`.
2. **Missing data files**: Ensure `.csv` files are in `notebooks/data/`.
3. **Thrift Server issues**: Check logs via `docker exec spark-iceberg cat /opt/spark/logs/*`.
4. **dbt/ClickHouse connection**: Verify ports and service health.

---

## Author

This project was built to demo a **Data Lakehouse** architecture using entirely **Open Source** technology.

---

## License

MIT License - Free to use for learning and research purposes.
