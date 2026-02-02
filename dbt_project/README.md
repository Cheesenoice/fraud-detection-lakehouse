# Fraud Detection Lakehouse - DBT Project

Dự án dbt (data build tool) cho hệ thống Lakehouse phát hiện gian lận thẻ tín dụng.

## Cấu trúc thư mục

```
dbt_project/
├── dbt_project.yml          # Cấu hình dự án
├── profiles.yml             # Cấu hình kết nối
├── models/
│   ├── silver/              # Silver Layer - Dữ liệu đã làm sạch
│   │   ├── sources.yml      # Định nghĩa Bronze sources
│   │   ├── schema.yml       # Tests & documentation
│   │   ├── silver_transactions.sql
│   │   └── silver_identity.sql
│   └── gold/                # Gold Layer - Dữ liệu tổng hợp
│       ├── schema.yml       # Tests & documentation
│       ├── fraud_by_card_type.sql
│       ├── hourly_fraud_analysis.sql
│       ├── fraud_by_product.sql
│       ├── kpi_summary.sql
│       ├── high_risk_transactions.sql
│       └── daily_transaction_summary.sql
└── tests/                   # Custom tests
    ├── assert_fraud_rate_reasonable.sql
    └── assert_positive_amounts.sql
```

## Medallion Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   BRONZE        │───▶│   SILVER        │───▶│   GOLD          │
│   (Raw Data)    │    │   (Cleaned)     │    │   (Aggregated)  │
│                 │    │                 │    │                 │
│ • transactions  │    │ • silver_trans  │    │ • fraud_by_card │
│ • identity      │    │ • silver_ident  │    │ • hourly_fraud  │
│                 │    │                 │    │ • kpi_summary   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Cách sử dụng

### Kiểm tra cấu hình

```bash
docker exec dbt dbt debug
```

### Chạy tất cả models

```bash
docker exec dbt dbt run
```

### Chạy chỉ Silver Layer

```bash
docker exec dbt dbt run --select silver
```

### Chạy chỉ Gold Layer

```bash
docker exec dbt dbt run --select gold
```

### Chạy tests

```bash
docker exec dbt dbt test
```

### Tạo documentation

```bash
docker exec dbt dbt docs generate
docker exec dbt dbt docs serve --port 8000
```

## DAG (Directed Acyclic Graph)

```
bronze.transactions ──┬──▶ silver_transactions ──┬──▶ fraud_by_card_type
                      │                          ├──▶ hourly_fraud_analysis
                      │                          ├──▶ fraud_by_product
                      │                          ├──▶ kpi_summary
                      │                          ├──▶ daily_transaction_summary
                      │                          └──┬──▶ high_risk_transactions
                      │                             │
bronze.identity ──────┴──▶ silver_identity ────────┘
```

## Tags

- `silver`: Models thuộc Silver Layer
- `gold`: Models thuộc Gold Layer
- `cleaned`: Dữ liệu đã được làm sạch
- `aggregated`: Dữ liệu đã được tổng hợp
- `reporting`: Phục vụ báo cáo
