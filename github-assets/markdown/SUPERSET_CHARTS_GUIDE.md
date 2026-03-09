# 📊 HƯỚNG DẪN TẠO CHARTS & DASHBOARD TRÊN SUPERSET

## Credit Card Fraud Detection - IEEE-CIS Dataset

---

## 📋 MỤC LỤC

1. [Chuẩn bị](#1-chuẩn-bị)
2. [Tạo Datasets](#2-tạo-datasets)
3. [Charts từ KPI Summary](#3-charts-từ-kpi-summary)
4. [Charts từ Fraud by Card Type](#4-charts-từ-fraud-by-card-type)
5. [Charts từ Hourly Fraud Analysis](#5-charts-từ-hourly-fraud-analysis)
6. [Charts từ Fraud by Product](#6-charts-từ-fraud-by-product)
7. [Charts từ Daily Transaction Summary](#7-charts-từ-daily-transaction-summary)
8. [Charts từ High Risk Transactions](#8-charts-từ-high-risk-transactions)
9. [Charts từ Fraud by Email Domain](#9-charts-từ-fraud-by-email-domain)
10. [Charts từ Fraud by Device](#10-charts-từ-fraud-by-device)
11. [Tạo Dashboard](#11-tạo-dashboard)
12. [Gợi ý Dashboard Layout](#12-gợi-ý-dashboard-layout)

---

## 1. CHUẨN BỊ

### 1.1 Truy cập Superset

- **URL**: http://localhost:8088
- **Username**: `admin`
- **Password**: `admin`

### 1.2 Kết nối Database ClickHouse

1. Vào **Settings** (⚙️ góc phải) → **Database Connections**
2. Click **+ DATABASE**
3. Chọn **Other** hoặc **ClickHouse Connect**
4. Điền **SQLAlchemy URI**:

```
clickhousedb://default:clickhouse123@clickhouse:8123/fraud_detection
```

5. **Display Name**: `ClickHouse Fraud Detection`
6. Click **TEST CONNECTION** → Nếu OK → **CONNECT**

---

## 2. TẠO DATASETS

### 2.1 Thêm tất cả các bảng

Vào **Datasets** → **+ DATASET** → Lần lượt thêm các bảng:

| #   | Table Name                  | Mô tả                   |
| --- | --------------------------- | ----------------------- |
| 1   | `kpi_summary`               | Tổng hợp KPIs chính     |
| 2   | `fraud_by_card_type`        | Fraud theo loại thẻ     |
| 3   | `hourly_fraud_analysis`     | Fraud theo giờ          |
| 4   | `fraud_by_product`          | Fraud theo sản phẩm     |
| 5   | `daily_transaction_summary` | Thống kê theo ngày      |
| 6   | `high_risk_transactions`    | Giao dịch rủi ro cao    |
| 7   | `fraud_by_email_domain`     | Fraud theo email domain |
| 8   | `fraud_by_device`           | Fraud theo thiết bị     |

**Cách thêm**:

1. Database: `ClickHouse Fraud Detection`
2. Schema: `fraud_detection`
3. Table: Chọn table từ danh sách
4. Click **ADD**

---

## 3. CHARTS TỪ KPI SUMMARY

### 📊 Chart 3.1: Big Number - Total Transactions

| Thuộc tính     | Giá trị              |
| -------------- | -------------------- |
| **Chart Type** | Big Number           |
| **Dataset**    | `kpi_summary`        |
| **Metric**     | `total_transactions` |
| **Subheader**  | `Total Transactions` |

**Cách tạo**:

1. Vào **Charts** → **+ CHART**
2. Chọn dataset `kpi_summary`
3. Chọn chart type: **Big Number**
4. Kéo `total_transactions` vào **METRIC**
5. Subheader: `Total Transactions`
6. **UPDATE CHART** → **SAVE**

---

### 📊 Chart 3.2: Big Number - Total Fraud Count

| Thuộc tính           | Giá trị                |
| -------------------- | ---------------------- |
| **Chart Type**       | Big Number             |
| **Dataset**          | `kpi_summary`          |
| **Metric**           | `total_fraud`          |
| **Subheader**        | `Fraud Cases Detected` |
| **Header Font Size** | 0.5 (to show in red)   |

---

### 📊 Chart 3.3: Big Number - Fraud Rate (%)

| Thuộc tính     | Giá trị                |
| -------------- | ---------------------- |
| **Chart Type** | Big Number             |
| **Dataset**    | `kpi_summary`          |
| **Metric**     | `fraud_rate_pct`       |
| **Subheader**  | `Overall Fraud Rate %` |

---

### 📊 Chart 3.4: Big Number - Total Amount ($)

| Thuộc tính     | Giá trị                        |
| -------------- | ------------------------------ |
| **Chart Type** | Big Number                     |
| **Dataset**    | `kpi_summary`                  |
| **Metric**     | `total_amount`                 |
| **Subheader**  | `Total Transaction Amount ($)` |
| **D3 Format**  | `$,.2f`                        |

---

### 📊 Chart 3.5: Big Number - Fraud Amount ($)

| Thuộc tính     | Giá trị                  |
| -------------- | ------------------------ |
| **Chart Type** | Big Number               |
| **Dataset**    | `kpi_summary`            |
| **Metric**     | `fraud_amount`           |
| **Subheader**  | `Total Fraud Amount ($)` |
| **D3 Format**  | `$,.2f`                  |

---

### 📊 Chart 3.6: Big Number - Unique Cards

| Thuộc tính     | Giá trị             |
| -------------- | ------------------- |
| **Chart Type** | Big Number          |
| **Dataset**    | `kpi_summary`       |
| **Metric**     | `unique_cards`      |
| **Subheader**  | `Unique Cards Used` |

---

### 📊 Chart 3.7: Big Number - Avg Risk Score

| Thuộc tính     | Giá trị              |
| -------------- | -------------------- |
| **Chart Type** | Big Number           |
| **Dataset**    | `kpi_summary`        |
| **Metric**     | `avg_risk_score`     |
| **Subheader**  | `Average Risk Score` |
| **D3 Format**  | `.4f`                |

---

### 📊 Chart 3.8: Table - Full KPI Summary

| Thuộc tính      | Giá trị        |
| --------------- | -------------- |
| **Chart Type**  | Table          |
| **Dataset**     | `kpi_summary`  |
| **Columns**     | Tất cả columns |
| **Page Length** | 10             |

---

## 4. CHARTS TỪ FRAUD BY CARD TYPE

### 📊 Chart 4.1: Pie Chart - Fraud Distribution by Card Brand

| Thuộc tính      | Giá trị              |
| --------------- | -------------------- |
| **Chart Type**  | Pie Chart            |
| **Dataset**     | `fraud_by_card_type` |
| **Dimension**   | `card_brand`         |
| **Metric**      | `SUM(fraud_count)`   |
| **Show Labels** | Yes                  |
| **Label Type**  | Key and Percent      |

**Cách tạo**:

1. Chart type: **Pie Chart**
2. Dimension: `card_brand`
3. Metric: `SUM(fraud_count)`
4. Bật **Show Labels**
5. Label Type: `Key and Percent`

---

### 📊 Chart 4.2: Bar Chart - Fraud Rate by Card Brand

| Thuộc tính     | Giá trị               |
| -------------- | --------------------- |
| **Chart Type** | Bar Chart             |
| **Dataset**    | `fraud_by_card_type`  |
| **X-Axis**     | `card_brand`          |
| **Metric**     | `AVG(fraud_rate_pct)` |
| **Sort**       | Descending by metric  |
| **Color**      | Red gradient          |

---

### 📊 Chart 4.3: Bar Chart - Fraud Rate by Card Category

| Thuộc tính     | Giá trị               |
| -------------- | --------------------- |
| **Chart Type** | Bar Chart             |
| **Dataset**    | `fraud_by_card_type`  |
| **X-Axis**     | `card_category`       |
| **Metric**     | `AVG(fraud_rate_pct)` |
| **Sort**       | Descending            |

---

### 📊 Chart 4.4: Grouped Bar - Card Brand vs Category

| Thuộc tính     | Giá trị              |
| -------------- | -------------------- |
| **Chart Type** | Bar Chart            |
| **Dataset**    | `fraud_by_card_type` |
| **X-Axis**     | `card_brand`         |
| **Breakdowns** | `card_category`      |
| **Metric**     | `SUM(fraud_count)`   |

---

### 📊 Chart 4.5: Treemap - Fraud Amount by Card Brand

| Thuộc tính        | Giá trị              |
| ----------------- | -------------------- |
| **Chart Type**    | Treemap              |
| **Dataset**       | `fraud_by_card_type` |
| **Dimension**     | `card_brand`         |
| **Metric**        | `SUM(fraud_amount)`  |
| **Number Format** | `$,.0f`              |

---

### 📊 Chart 4.6: Scatter Plot - Transaction Amount vs Fraud Rate

| Thuộc tính      | Giá trị               |
| --------------- | --------------------- |
| **Chart Type**  | Scatter Plot          |
| **Dataset**     | `fraud_by_card_type`  |
| **X-Axis**      | `avg_transaction_amt` |
| **Y-Axis**      | `fraud_rate_pct`      |
| **Series**      | `card_brand`          |
| **Bubble Size** | `total_transactions`  |

---

### 📊 Chart 4.7: Table - Card Type Details

| Thuộc tính                 | Giá trị                                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Chart Type**             | Table                                                                                                |
| **Dataset**                | `fraud_by_card_type`                                                                                 |
| **Columns**                | `card_brand`, `card_category`, `total_transactions`, `fraud_count`, `fraud_rate_pct`, `fraud_amount` |
| **Sort**                   | `fraud_rate_pct` DESC                                                                                |
| **Conditional Formatting** | `fraud_rate_pct` > 5 → Red                                                                           |

---

## 5. CHARTS TỪ HOURLY FRAUD ANALYSIS

### 📊 Chart 5.1: Line Chart - Fraud Rate by Hour

| Thuộc tính     | Giá trị                 |
| -------------- | ----------------------- |
| **Chart Type** | Line Chart              |
| **Dataset**    | `hourly_fraud_analysis` |
| **X-Axis**     | `hour_of_day`           |
| **Metric**     | `fraud_rate_pct`        |
| **Sort**       | `hour_of_day` ASC       |
| **Markers**    | Show markers            |

**Cách tạo**:

1. Chart type: **Line Chart**
2. X-Axis: `hour_of_day`
3. Metric: `fraud_rate_pct`
4. Sort by: `hour_of_day` ascending
5. Bật **Show Markers**

---

### 📊 Chart 5.2: Bar Chart - Transactions by Hour

| Thuộc tính     | Giá trị                 |
| -------------- | ----------------------- |
| **Chart Type** | Bar Chart               |
| **Dataset**    | `hourly_fraud_analysis` |
| **X-Axis**     | `hour_of_day`           |
| **Metric**     | `total_transactions`    |
| **Color**      | Blue                    |

---

### 📊 Chart 5.3: Mixed Chart - Transactions vs Fraud Rate

| Thuộc tính      | Giá trị                  |
| --------------- | ------------------------ |
| **Chart Type**  | Mixed Chart (Bar + Line) |
| **Dataset**     | `hourly_fraud_analysis`  |
| **X-Axis**      | `hour_of_day`            |
| **Bar Metric**  | `total_transactions`     |
| **Line Metric** | `fraud_rate_pct`         |

**Cách tạo** (dùng Echarts hoặc Bar Chart với dual axis):

1. Chọn **Bar Chart**
2. Thêm 2 metrics: `total_transactions`, `fraud_rate_pct`
3. Bật **Secondary Y-Axis** cho `fraud_rate_pct`

---

### 📊 Chart 5.4: Area Chart - Fraud Amount by Hour

| Thuộc tính     | Giá trị                 |
| -------------- | ----------------------- |
| **Chart Type** | Area Chart              |
| **Dataset**    | `hourly_fraud_analysis` |
| **X-Axis**     | `hour_of_day`           |
| **Metric**     | `fraud_amount`          |
| **Color**      | Red with opacity        |

---

### 📊 Chart 5.5: Heatmap - Hour Analysis

| Thuộc tính       | Giá trị                     |
| ---------------- | --------------------------- |
| **Chart Type**   | Heatmap                     |
| **Dataset**      | `hourly_fraud_analysis`     |
| **X-Axis**       | `hour_of_day`               |
| **Y-Axis**       | Constant (1 row)            |
| **Metric**       | `fraud_rate_pct`            |
| **Color Scheme** | Red-Yellow-Green (reversed) |

---

### 📊 Chart 5.6: Big Number - Peak Fraud Hour

Tạo custom SQL query:

```sql
SELECT hour_of_day, fraud_rate_pct
FROM fraud_detection.hourly_fraud_analysis
ORDER BY fraud_rate_pct DESC
LIMIT 1
```

| Thuộc tính     | Giá trị                        |
| -------------- | ------------------------------ |
| **Chart Type** | Big Number                     |
| **Subheader**  | `Hour with Highest Fraud Rate` |

---

## 6. CHARTS TỪ FRAUD BY PRODUCT

### 📊 Chart 6.1: Bar Chart - Fraud Rate by Product

| Thuộc tính     | Giá trị                |
| -------------- | ---------------------- |
| **Chart Type** | Bar Chart (Horizontal) |
| **Dataset**    | `fraud_by_product`     |
| **Y-Axis**     | `product_category`     |
| **Metric**     | `fraud_rate_pct`       |
| **Sort**       | Descending             |
| **Bar Colors** | Gradient Red           |

---

### 📊 Chart 6.2: Pie Chart - Transaction Volume by Product

| Thuộc tính      | Giá trị                   |
| --------------- | ------------------------- |
| **Chart Type**  | Pie Chart                 |
| **Dataset**     | `fraud_by_product`        |
| **Dimension**   | `product_category`        |
| **Metric**      | `SUM(total_transactions)` |
| **Show Legend** | Yes                       |

---

### 📊 Chart 6.3: Donut Chart - Fraud Amount Distribution

| Thuộc tính       | Giá trị             |
| ---------------- | ------------------- |
| **Chart Type**   | Pie Chart (Donut)   |
| **Dataset**      | `fraud_by_product`  |
| **Dimension**    | `product_category`  |
| **Metric**       | `SUM(fraud_amount)` |
| **Donut**        | Yes                 |
| **Inner Radius** | 40%                 |

---

### 📊 Chart 6.4: Bubble Chart - Product Risk Analysis

| Thuộc tính      | Giá trị            |
| --------------- | ------------------ |
| **Chart Type**  | Bubble Chart       |
| **Dataset**     | `fraud_by_product` |
| **X-Axis**      | `avg_amount`       |
| **Y-Axis**      | `fraud_rate_pct`   |
| **Bubble Size** | `fraud_count`      |
| **Series**      | `product_category` |

---

### 📊 Chart 6.5: Funnel Chart - Fraud Funnel by Product

| Thuộc tính     | Giá trị            |
| -------------- | ------------------ |
| **Chart Type** | Funnel Chart       |
| **Dataset**    | `fraud_by_product` |
| **Dimension**  | `product_category` |
| **Metric**     | `fraud_count`      |
| **Sort**       | Descending         |

---

### 📊 Chart 6.6: Table - Product Summary

| Thuộc tính                 | Giá trị                                                                                                                   |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **Chart Type**             | Table                                                                                                                     |
| **Dataset**                | `fraud_by_product`                                                                                                        |
| **Columns**                | `product_category`, `total_transactions`, `fraud_count`, `fraud_rate_pct`, `total_amount`, `fraud_amount`, `unique_cards` |
| **Conditional Formatting** | `fraud_rate_pct` gradient                                                                                                 |

---

## 7. CHARTS TỪ DAILY TRANSACTION SUMMARY

### 📊 Chart 7.1: Time Series - Daily Transactions

| Thuộc tính      | Giá trị                     |
| --------------- | --------------------------- |
| **Chart Type**  | Time-series Line Chart      |
| **Dataset**     | `daily_transaction_summary` |
| **Time Column** | `transaction_day`           |
| **Metric**      | `SUM(total_transactions)`   |
| **Time Grain**  | Day                         |

---

### 📊 Chart 7.2: Stacked Area - Daily Transactions by Product

| Thuộc tính     | Giá trị                     |
| -------------- | --------------------------- |
| **Chart Type** | Area Chart                  |
| **Dataset**    | `daily_transaction_summary` |
| **X-Axis**     | `transaction_day`           |
| **Metric**     | `total_transactions`        |
| **Breakdowns** | `ProductCD`                 |
| **Stacked**    | Yes                         |

---

### 📊 Chart 7.3: Line Chart - Daily Fraud Rate Trend

| Thuộc tính          | Giá trị                     |
| ------------------- | --------------------------- |
| **Chart Type**      | Line Chart                  |
| **Dataset**         | `daily_transaction_summary` |
| **X-Axis**          | `transaction_day`           |
| **Metric**          | `AVG(fraud_rate_pct)`       |
| **Rolling Average** | 7 days (optional)           |

---

### 📊 Chart 7.4: Calendar Heatmap - Fraud Activity

| Thuộc tính      | Giá trị                     |
| --------------- | --------------------------- |
| **Chart Type**  | Calendar Heatmap            |
| **Dataset**     | `daily_transaction_summary` |
| **Time Column** | `transaction_day`           |
| **Metric**      | `SUM(fraud_count)`          |

---

### 📊 Chart 7.5: Bar Chart - Daily Volume Comparison

| Thuộc tính     | Giá trị                             |
| -------------- | ----------------------------------- |
| **Chart Type** | Bar Chart                           |
| **Dataset**    | `daily_transaction_summary`         |
| **X-Axis**     | `transaction_day`                   |
| **Metrics**    | `total_transactions`, `fraud_count` |
| **Group Mode** | Stacked                             |

---

## 8. CHARTS TỪ HIGH RISK TRANSACTIONS

### 📊 Chart 8.1: Table - High Risk Transaction Details

| Thuộc tính                 | Giá trị                                                                                                  |
| -------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Chart Type**             | Table                                                                                                    |
| **Dataset**                | `high_risk_transactions`                                                                                 |
| **Columns**                | `TransactionID`, `TransactionAmt`, `ProductCD`, `card_type`, `risk_score`, `isFraud`, `transaction_hour` |
| **Row Limit**              | 100                                                                                                      |
| **Sort**                   | `risk_score` DESC                                                                                        |
| **Conditional Formatting** | `isFraud = 1` → Red background                                                                           |

---

### 📊 Chart 8.2: Histogram - Risk Score Distribution

| Thuộc tính     | Giá trị                  |
| -------------- | ------------------------ |
| **Chart Type** | Histogram                |
| **Dataset**    | `high_risk_transactions` |
| **Column**     | `risk_score`             |
| **Bins**       | 20                       |
| **Cumulative** | Optional                 |

---

### 📊 Chart 8.3: Scatter Plot - Amount vs Risk Score

| Thuộc tính     | Giá trị                  |
| -------------- | ------------------------ |
| **Chart Type** | Scatter Plot             |
| **Dataset**    | `high_risk_transactions` |
| **X-Axis**     | `TransactionAmt`         |
| **Y-Axis**     | `risk_score`             |
| **Color**      | `isFraud`                |
| **Row Limit**  | 5000                     |

---

### 📊 Chart 8.4: Box Plot - Transaction Amount by Fraud Status

| Thuộc tính       | Giá trị                  |
| ---------------- | ------------------------ |
| **Chart Type**   | Box Plot                 |
| **Dataset**      | `high_risk_transactions` |
| **X-Axis**       | `isFraud`                |
| **Columns**      | `TransactionAmt`         |
| **Whisker Type** | Min/Max                  |

---

### 📊 Chart 8.5: Pie Chart - High Risk by Product

| Thuộc tính     | Giá trị                  |
| -------------- | ------------------------ |
| **Chart Type** | Pie Chart                |
| **Dataset**    | `high_risk_transactions` |
| **Dimension**  | `ProductCD`              |
| **Metric**     | `COUNT(*)`               |
| **Filters**    | `risk_score >= 0.7`      |

---

### 📊 Chart 8.6: Big Number - Count of High Risk

| Thuộc tính     | Giá trị                  |
| -------------- | ------------------------ |
| **Chart Type** | Big Number               |
| **Dataset**    | `high_risk_transactions` |
| **Metric**     | `COUNT(*)`               |
| **Subheader**  | `High Risk Transactions` |
| **Filters**    | `risk_score >= 0.7`      |

---

## 9. CHARTS TỪ FRAUD BY EMAIL DOMAIN

### 📊 Chart 9.1: Bar Chart - Top 10 Risky Email Domains

| Thuộc tính     | Giá trị                 |
| -------------- | ----------------------- |
| **Chart Type** | Bar Chart (Horizontal)  |
| **Dataset**    | `fraud_by_email_domain` |
| **Y-Axis**     | `email_domain`          |
| **Metric**     | `fraud_rate_pct`        |
| **Row Limit**  | 10                      |
| **Sort**       | Descending              |

---

### 📊 Chart 9.2: Treemap - Email Domain by Fraud Amount

| Thuộc tính     | Giá trị                 |
| -------------- | ----------------------- |
| **Chart Type** | Treemap                 |
| **Dataset**    | `fraud_by_email_domain` |
| **Dimension**  | `email_domain`          |
| **Metric**     | `SUM(fraud_count)`      |
| **Row Limit**  | 15                      |

---

### 📊 Chart 9.3: Word Cloud - Email Domains

| Thuộc tính     | Giá trị                 |
| -------------- | ----------------------- |
| **Chart Type** | Word Cloud              |
| **Dataset**    | `fraud_by_email_domain` |
| **Series**     | `email_domain`          |
| **Metric**     | `fraud_count`           |
| **Rotation**   | Random                  |

---

### 📊 Chart 9.4: Table - Email Domain Analysis

| Thuộc tính     | Giá trị                                                                               |
| -------------- | ------------------------------------------------------------------------------------- |
| **Chart Type** | Table                                                                                 |
| **Dataset**    | `fraud_by_email_domain`                                                               |
| **Columns**    | `email_domain`, `total_transactions`, `fraud_count`, `fraud_rate_pct`, `total_amount` |
| **Sort**       | `fraud_rate_pct` DESC                                                                 |
| **Row Limit**  | 20                                                                                    |

---

## 10. CHARTS TỪ FRAUD BY DEVICE

### 📊 Chart 10.1: Bar Chart - Fraud by Device Type

| Thuộc tính     | Giá trị           |
| -------------- | ----------------- |
| **Chart Type** | Bar Chart         |
| **Dataset**    | `fraud_by_device` |
| **X-Axis**     | `device_type`     |
| **Metric**     | `fraud_rate_pct`  |
| **Color**      | By `device_type`  |

---

### 📊 Chart 10.2: Grouped Bar - Device Type & Browser

| Thuộc tính     | Giá trị           |
| -------------- | ----------------- |
| **Chart Type** | Bar Chart         |
| **Dataset**    | `fraud_by_device` |
| **X-Axis**     | `device_type`     |
| **Breakdowns** | `browser`         |
| **Metric**     | `fraud_rate_pct`  |
| **Row Limit**  | 20                |

---

### 📊 Chart 10.3: Sunburst - Device Hierarchy

| Thuộc tính     | Giá trị                   |
| -------------- | ------------------------- |
| **Chart Type** | Sunburst                  |
| **Dataset**    | `fraud_by_device`         |
| **Hierarchy**  | `device_type` → `browser` |
| **Metric**     | `fraud_count`             |

---

### 📊 Chart 10.4: Table - Device Details

| Thuộc tính                 | Giá trị                                                                         |
| -------------------------- | ------------------------------------------------------------------------------- |
| **Chart Type**             | Table                                                                           |
| **Dataset**                | `fraud_by_device`                                                               |
| **Columns**                | `device_type`, `browser`, `total_transactions`, `fraud_count`, `fraud_rate_pct` |
| **Conditional Formatting** | `fraud_rate_pct` gradient                                                       |

---

## 11. TẠO DASHBOARD

### 11.1 Tạo Dashboard mới

1. Vào **Dashboards** → **+ DASHBOARD**
2. Đặt tên: `🛡️ Fraud Detection Dashboard`
3. Click **SAVE**

### 11.2 Thêm Charts vào Dashboard

1. Click **EDIT DASHBOARD** (✏️)
2. Kéo thả charts từ panel bên phải
3. Resize và sắp xếp theo ý muốn
4. Click **SAVE**

### 11.3 Thêm Filters

1. Trong Edit mode, click **+ FILTER**
2. Thêm các filters:
   - **Card Brand**: Filter by `card_brand`
   - **Product**: Filter by `ProductCD`
   - **Time Range**: Filter by `transaction_day`
   - **Fraud Status**: Filter by `isFraud`

---

## 12. GỢI Ý DASHBOARD LAYOUT

### 🎯 Dashboard 1: Executive Summary (Cho Ban lãnh đạo)

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 FRAUD DETECTION EXECUTIVE DASHBOARD                         │
├─────────────┬─────────────┬─────────────┬─────────────┬────────┤
│ Total Trans │ Fraud Cases │ Fraud Rate  │ Total $     │ Fraud $│
│   590,540   │   20,663    │   3.50%     │  $53.4B     │ $1.8B  │
├─────────────┴─────────────┴─────────────┴─────────────┴────────┤
│                                                                 │
│  [Pie: Fraud by Card]     [Bar: Fraud by Product]              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Line: Hourly Fraud Trend with Transactions]                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [Table: Top 10 Risky Card Types]                              │
└─────────────────────────────────────────────────────────────────┘
```

**Charts cần có**:

- 5x Big Number (Total Trans, Fraud Cases, Fraud Rate, Total $, Fraud $)
- 1x Pie Chart (Fraud by Card Brand)
- 1x Bar Chart (Fraud by Product)
- 1x Mixed Chart (Hourly: Transactions + Fraud Rate)
- 1x Table (Top Risky Card Types)

---

### 🔍 Dashboard 2: Analyst Deep Dive (Cho Data Analyst)

```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 FRAUD ANALYSIS DEEP DIVE                                    │
├─────────────────────────────────┬───────────────────────────────┤
│ [Scatter: Amount vs Risk Score] │ [Histogram: Risk Distribution]│
│                                 │                               │
├─────────────────────────────────┴───────────────────────────────┤
│ [Heatmap: Hourly Fraud Pattern]                                 │
├─────────────────────────────────────────────────────────────────┤
│ [Bar: Top Email Domains]  │ [Bar: Device Type Analysis]        │
├─────────────────────────────────────────────────────────────────┤
│ [Table: High Risk Transactions - Top 100]                       │
└─────────────────────────────────────────────────────────────────┘
```

**Charts cần có**:

- 1x Scatter Plot (Amount vs Risk)
- 1x Histogram (Risk Score)
- 1x Heatmap (Hourly Pattern)
- 1x Bar Chart (Email Domains)
- 1x Bar Chart (Device Types)
- 1x Table (High Risk Transactions)

---

### 📈 Dashboard 3: Trend Monitoring (Cho Operations)

```
┌─────────────────────────────────────────────────────────────────┐
│  📈 FRAUD TREND MONITORING                                      │
├─────────────────────────────────────────────────────────────────┤
│ [Time Series: Daily Fraud Rate Trend - 30 days]                 │
├─────────────────────────────────────────────────────────────────┤
│ [Stacked Area: Daily Transactions by Product]                   │
├─────────────────────────────────────────────────────────────────┤
│ [Line: Hourly Pattern] │ [Bar: Peak Hours Analysis]             │
├─────────────────────────────────────────────────────────────────┤
│ [Calendar Heatmap: Monthly Fraud Activity]                      │
└─────────────────────────────────────────────────────────────────┘
```

---

### 💳 Dashboard 4: Card Analysis (Cho Risk Team)

```
┌─────────────────────────────────────────────────────────────────┐
│  💳 CARD TYPE FRAUD ANALYSIS                                    │
├─────────────────────────────────────────────────────────────────┤
│ [Treemap: Fraud Amount by Card Brand]                           │
├───────────────────────────────┬─────────────────────────────────┤
│ [Donut: Card Category]        │ [Bar: Card Brand Fraud Rate]   │
├───────────────────────────────┴─────────────────────────────────┤
│ [Bubble: Transaction Amount vs Fraud Rate by Card]              │
├─────────────────────────────────────────────────────────────────┤
│ [Table: Detailed Card Type Statistics]                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 CHECKLIST TẠO DASHBOARD

### Minimum Charts (Yêu cầu tối thiểu - 3 charts)

- [ ] Chart 1: Fraud by Card Type (Pie hoặc Bar)
- [ ] Chart 2: Hourly Fraud Analysis (Line hoặc Bar)
- [ ] Chart 3: KPI Summary (Table hoặc Big Numbers)

### Recommended Charts (Khuyến nghị - 7-10 charts)

- [ ] Big Number: Total Transactions
- [ ] Big Number: Fraud Rate %
- [ ] Big Number: Fraud Amount
- [ ] Pie Chart: Fraud by Card Brand
- [ ] Bar Chart: Fraud by Product
- [ ] Line Chart: Hourly Fraud Trend
- [ ] Mixed Chart: Transactions vs Fraud Rate
- [ ] Table: Card Type Details
- [ ] Scatter: Risk Analysis
- [ ] Table: High Risk Transactions

### Full Dashboard (Đầy đủ - 15+ charts)

Thêm tất cả charts từ các sections 3-10 ở trên.

---

## 🎨 TIPS TỐI ƯU DASHBOARD

### Color Scheme

- **Red**: Fraud, High Risk, Danger
- **Green**: Safe, Low Risk, Normal
- **Blue**: Neutral data, Transactions
- **Orange/Yellow**: Warning, Medium Risk

### D3 Format Reference

| Format  | Example   | Mô tả                 |
| ------- | --------- | --------------------- |
| `,.0f`  | 1,234,567 | Số nguyên có dấu phẩy |
| `$,.2f` | $1,234.56 | Tiền USD              |
| `.2%`   | 3.50%     | Phần trăm             |
| `.4f`   | 0.0350    | 4 chữ số thập phân    |

### Conditional Formatting

- `fraud_rate_pct > 5%` → Red
- `fraud_rate_pct 3-5%` → Orange
- `fraud_rate_pct < 3%` → Green
- `isFraud = 1` → Red background

---

## 🔗 QUICK REFERENCE

| Dataset                  | Key Metrics                                                           |
| ------------------------ | --------------------------------------------------------------------- |
| `kpi_summary`            | `total_transactions`, `total_fraud`, `fraud_rate_pct`, `fraud_amount` |
| `fraud_by_card_type`     | `card_brand`, `fraud_rate_pct`, `fraud_count`, `fraud_amount`         |
| `hourly_fraud_analysis`  | `hour_of_day`, `fraud_rate_pct`, `total_transactions`                 |
| `fraud_by_product`       | `product_category`, `fraud_rate_pct`, `fraud_amount`                  |
| `high_risk_transactions` | `risk_score`, `TransactionAmt`, `isFraud`                             |

---

**Chúc bạn tạo Dashboard thành công! 🚀**
