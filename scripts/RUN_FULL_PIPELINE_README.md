# 🚀 Hướng dẫn chạy Full Pipeline tự động

## Dành cho người mới bắt đầu

Script `run_full_pipeline.sh` sẽ tự động chạy **toàn bộ quy trình** từ dữ liệu thô đến Dashboard hiển thị. Bạn chỉ cần chạy **một lệnh duy nhất**!

---

## 📋 Yêu cầu trước khi chạy

1. **Docker** đã được cài đặt và đang chạy
2. **Dữ liệu** đã có trong thư mục `notebooks/data/`:
   - `train_transaction.csv`
   - `train_identity.csv`
3. **Docker stack đã khởi động** (nếu chưa, chạy `./start_lakehouse.sh` trước)

---

## 🎯 Cách chạy

### Bước 1: Khởi động Docker stack (nếu chưa chạy)

```bash
cd /path/to/Lakehouse_Project/scripts
./start_lakehouse.sh
```

Đợi khoảng 2-3 phút cho tất cả containers khởi động.

### Bước 2: Chạy Full Pipeline

```bash
./run_full_pipeline.sh
```

**Thời gian chạy:** ~10-15 phút (tùy cấu hình máy)

---

## 📊 Pipeline sẽ thực hiện gì?

| Step       | Mô tả                                     | Thời gian |
| ---------- | ----------------------------------------- | --------- |
| **Step 1** | Bronze Layer - Ingest CSV vào Iceberg     | ~3-5 phút |
| **Step 2** | dbt run - Tạo Silver & Gold layers        | ~3-5 phút |
| **Step 3** | Serving Layer - Copy Gold sang ClickHouse | ~2-3 phút |
| **Step 4** | Superset - Tạo Dashboard tự động          | ~1 phút   |

---

## 🌐 Truy cập sau khi chạy xong

| Service                  | URL                   | Credentials             |
| ------------------------ | --------------------- | ----------------------- |
| **Superset** (Dashboard) | http://localhost:8088 | admin / admin           |
| **MinIO** (Storage)      | http://localhost:9001 | admin / password123     |
| **Spark UI**             | http://localhost:8888 | -                       |
| **ClickHouse**           | http://localhost:8123 | default / clickhouse123 |

---

## 📈 Xem Dashboard

1. Mở browser: **http://localhost:8088**
2. Đăng nhập: `admin` / `admin`
3. Click **Dashboards** → **Fraud Detection Dashboard**
4. Hoặc vào **SQL Lab** để query trực tiếp

---

## 🗄️ Cấu trúc dữ liệu được tạo

### Bronze Layer (Raw Data)

- `demo.bronze.transactions` - 590,540 records
- `demo.bronze.identity` - 144,233 records

### Silver Layer (Cleaned)

- `bronze_silver.silver_transactions` - Transactions đã làm sạch
- `bronze_silver.silver_identity` - Identity đã làm sạch

### Gold Layer (Analytics)

- `bronze_gold.fraud_by_card_type`
- `bronze_gold.hourly_fraud_analysis`
- `bronze_gold.fraud_by_product`
- `bronze_gold.kpi_summary`
- `bronze_gold.high_risk_transactions`
- `bronze_gold.daily_transaction_summary`
- `bronze_gold.fraud_by_day_of_week`
- `bronze_gold.fraud_by_amount_category`

### ClickHouse (Serving)

- `fraud_detection.*` - Tất cả tables từ Gold layer

---

## ❓ Troubleshooting

### Lỗi "Container chưa chạy"

```bash
# Khởi động lại stack
./stop_lakehouse.sh
./start_lakehouse.sh
# Đợi 2-3 phút rồi chạy lại
./run_full_pipeline.sh
```

### Lỗi "Không tìm thấy data files"

- Đảm bảo các file CSV đã được đặt trong `notebooks/data/`
- Kiểm tra tên file chính xác: `train_transaction.csv`, `train_identity.csv`

### Superset dashboard trống

- Login vào Superset
- Vào SQL Lab → Chọn database "ClickHouse Fraud Detection"
- Chạy query test: `SELECT * FROM fraud_detection.kpi_summary`
- Nếu có data, tạo chart thủ công theo hướng dẫn trong `SUPERSET_CHARTS_GUIDE.md`

---

## 📚 Tài liệu bổ sung

- [SUPERSET_CHARTS_GUIDE.md](../markdown/SUPERSET_CHARTS_GUIDE.md) - Hướng dẫn tạo 40+ charts
- [SETUP_GUIDE.md](../SETUP_GUIDE.md) - Hướng dẫn cài đặt chi tiết
- [README.md](../README.md) - Tổng quan dự án

---

## 🎉 Done!

Sau khi chạy xong, bạn có một Lakehouse hoàn chỉnh với:

- ✅ Data Pipeline tự động (Medallion Architecture)
- ✅ Analytics Dashboard (Superset)
- ✅ Real-time Query (ClickHouse)
- ✅ Time Travel Support (Iceberg)
