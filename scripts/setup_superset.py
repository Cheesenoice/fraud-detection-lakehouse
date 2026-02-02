#!/usr/bin/env python3
"""
Superset Auto Setup Script
Tự động tạo database connection, datasets, charts và dashboard trong Superset
"""

import requests
import json
import time

# Superset Configuration
SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"

# ClickHouse Configuration  
CLICKHOUSE_CONNECTION = {
    "database_name": "ClickHouse Fraud Detection",
    "sqlalchemy_uri": "clickhousedb://default:clickhouse123@clickhouse:8123/fraud_detection",
    "expose_in_sqllab": True,
    "allow_ctas": True,
    "allow_cvas": True,
    "allow_dml": True,
}

# Tables to create datasets
TABLES = [
    "fraud_by_card_type",
    "hourly_fraud_analysis", 
    "fraud_by_product",
    "kpi_summary",
    "high_risk_transactions",
    "daily_transaction_summary",
    "fraud_by_day_of_week",
    "fraud_by_amount_category",
]

class SupersetSetup:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.csrf_token = None
        self.database_id = None
        self.dataset_ids = {}
        self.chart_ids = []
        
    def login(self):
        """Login và lấy access token"""
        print("🔐 Đang đăng nhập Superset...")
        
        # Get CSRF token first
        resp = self.session.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")
        if resp.status_code == 200:
            self.csrf_token = resp.json().get("result")
            self.session.headers.update({"X-CSRFToken": self.csrf_token})
        
        # Login to get access token
        login_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "provider": "db",
            "refresh": True
        }
        
        resp = self.session.post(
            f"{SUPERSET_URL}/api/v1/security/login",
            json=login_data
        )
        
        if resp.status_code == 200:
            self.access_token = resp.json().get("access_token")
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            })
            
            # Refresh CSRF after login
            resp = self.session.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")
            if resp.status_code == 200:
                self.csrf_token = resp.json().get("result")
                self.session.headers.update({"X-CSRFToken": self.csrf_token})
            
            print("   ✅ Đăng nhập thành công!")
            return True
        else:
            print(f"   ❌ Đăng nhập thất bại: {resp.text}")
            return False
    
    def create_database_connection(self):
        """Tạo database connection tới ClickHouse"""
        print("🗄️  Đang tạo Database Connection...")
        
        # Check if database already exists
        resp = self.session.get(f"{SUPERSET_URL}/api/v1/database/")
        if resp.status_code == 200:
            databases = resp.json().get("result", [])
            for db in databases:
                if db.get("database_name") == CLICKHOUSE_CONNECTION["database_name"]:
                    self.database_id = db.get("id")
                    print(f"   ⚠️  Database đã tồn tại (ID: {self.database_id})")
                    return True
        
        # Create new database connection
        resp = self.session.post(
            f"{SUPERSET_URL}/api/v1/database/",
            json=CLICKHOUSE_CONNECTION
        )
        
        if resp.status_code in [200, 201]:
            self.database_id = resp.json().get("id")
            print(f"   ✅ Đã tạo Database Connection (ID: {self.database_id})")
            return True
        else:
            print(f"   ❌ Lỗi tạo database: {resp.status_code} - {resp.text}")
            return False
    
    def create_datasets(self):
        """Tạo datasets từ các tables"""
        print("📊 Đang tạo Datasets...")
        
        if not self.database_id:
            print("   ❌ Chưa có database_id")
            return False
        
        for table in TABLES:
            # Check if dataset exists
            resp = self.session.get(
                f"{SUPERSET_URL}/api/v1/dataset/",
                params={"q": json.dumps({"filters": [{"col": "table_name", "opr": "eq", "value": table}]})}
            )
            
            if resp.status_code == 200:
                existing = resp.json().get("result", [])
                if existing:
                    self.dataset_ids[table] = existing[0].get("id")
                    print(f"   ⚠️  Dataset '{table}' đã tồn tại (ID: {self.dataset_ids[table]})")
                    continue
            
            # Create dataset
            dataset_data = {
                "database": self.database_id,
                "table_name": table,
                "schema": "fraud_detection"
            }
            
            resp = self.session.post(
                f"{SUPERSET_URL}/api/v1/dataset/",
                json=dataset_data
            )
            
            if resp.status_code in [200, 201]:
                self.dataset_ids[table] = resp.json().get("id")
                print(f"   ✅ Đã tạo dataset: {table} (ID: {self.dataset_ids[table]})")
            else:
                print(f"   ⚠️  Lỗi tạo dataset {table}: {resp.status_code}")
        
        return True
    
    def create_charts(self):
        """Tạo các charts"""
        print("📈 Đang tạo Charts...")
        
        charts_config = [
            # ============================================================
            # KPI SUMMARY CHARTS (6 charts)
            # ============================================================
            # 1. KPI Summary - Big Number Total Transactions
            {
                "slice_name": "Tổng Giao Dịch",
                "viz_type": "big_number_total",
                "datasource_id": self.dataset_ids.get("kpi_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "metric": {"label": "total_transactions", "expressionType": "SIMPLE", "column": {"column_name": "total_transactions"}, "aggregate": "MAX"},
                    "subheader": "Total Transactions",
                    "y_axis_format": ",d"
                })
            },
            # 2. Fraud Rate - Big Number
            {
                "slice_name": "Tỷ Lệ Gian Lận",
                "viz_type": "big_number_total", 
                "datasource_id": self.dataset_ids.get("kpi_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "metric": {"label": "fraud_rate_pct", "expressionType": "SIMPLE", "column": {"column_name": "fraud_rate_pct"}, "aggregate": "MAX"},
                    "subheader": "Fraud Rate %",
                    "y_axis_format": ".2f"
                })
            },
            # 3. Total Fraud Count - Big Number
            {
                "slice_name": "Tổng Số Gian Lận",
                "viz_type": "big_number_total",
                "datasource_id": self.dataset_ids.get("kpi_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "metric": {"label": "total_fraud_count", "expressionType": "SIMPLE", "column": {"column_name": "total_fraud_count"}, "aggregate": "MAX"},
                    "subheader": "Fraud Cases Detected",
                    "y_axis_format": ",d"
                })
            },
            # 4. Total Transaction Amount - Big Number
            {
                "slice_name": "Tổng Giá Trị Giao Dịch",
                "viz_type": "big_number_total",
                "datasource_id": self.dataset_ids.get("kpi_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "metric": {"label": "total_transaction_amount", "expressionType": "SIMPLE", "column": {"column_name": "total_transaction_amount"}, "aggregate": "MAX"},
                    "subheader": "Total Amount ($)",
                    "y_axis_format": "$,.2f"
                })
            },
            # 5. Total Fraud Amount - Big Number
            {
                "slice_name": "Tổng Giá Trị Gian Lận",
                "viz_type": "big_number_total",
                "datasource_id": self.dataset_ids.get("kpi_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "metric": {"label": "total_fraud_amount", "expressionType": "SIMPLE", "column": {"column_name": "total_fraud_amount"}, "aggregate": "MAX"},
                    "subheader": "Fraud Amount ($)",
                    "y_axis_format": "$,.2f"
                })
            },
            # 6. KPI Summary Table
            {
                "slice_name": "Bảng Tổng Hợp KPI",
                "viz_type": "table",
                "datasource_id": self.dataset_ids.get("kpi_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "all_columns": ["metric_category", "total_transactions", "total_fraud_count", "fraud_rate_pct", "total_transaction_amount", "total_fraud_amount", "avg_transaction_amount"],
                    "page_length": 10
                })
            },
            
            # ============================================================
            # FRAUD BY CARD TYPE CHARTS (7 charts)
            # ============================================================
            # 7. Fraud by Card Type - Pie Chart
            {
                "slice_name": "Gian Lận theo Loại Thẻ",
                "viz_type": "pie",
                "datasource_id": self.dataset_ids.get("fraud_by_card_type"),
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["card_brand"],
                    "metric": {"label": "fraud_count", "expressionType": "SIMPLE", "column": {"column_name": "fraud_count"}, "aggregate": "SUM"},
                    "show_legend": True,
                    "show_labels": True,
                    "label_type": "key_percent"
                })
            },
            # 8. Fraud Rate by Card Brand - Bar Chart
            {
                "slice_name": "Tỷ Lệ Gian Lận theo Thương Hiệu Thẻ",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("fraud_by_card_type"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "card_brand",
                    "metrics": [{"label": "fraud_rate_pct", "expressionType": "SIMPLE", "column": {"column_name": "fraud_rate_pct"}, "aggregate": "AVG"}],
                    "show_legend": True,
                    "order_desc": True
                })
            },
            # 9. Fraud Rate by Card Category - Bar Chart
            {
                "slice_name": "Tỷ Lệ Gian Lận theo Danh Mục Thẻ",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("fraud_by_card_type"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "card_category",
                    "metrics": [{"label": "fraud_rate_pct", "expressionType": "SIMPLE", "column": {"column_name": "fraud_rate_pct"}, "aggregate": "AVG"}],
                    "show_legend": True,
                    "order_desc": True
                })
            },
            # 10. Fraud Amount by Card Brand - Treemap
            {
                "slice_name": "Giá Trị Gian Lận theo Thương Hiệu Thẻ",
                "viz_type": "treemap_v2",
                "datasource_id": self.dataset_ids.get("fraud_by_card_type"),
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["card_brand"],
                    "metric": {"label": "fraud_amount", "expressionType": "SIMPLE", "column": {"column_name": "fraud_amount"}, "aggregate": "SUM"},
                    "show_labels": True,
                    "number_format": "$,.0f"
                })
            },
            # 11. Card Type Fraud Distribution - Donut
            {
                "slice_name": "Phân Phối Gian Lận theo Danh Mục Thẻ",
                "viz_type": "pie",
                "datasource_id": self.dataset_ids.get("fraud_by_card_type"),
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["card_category"],
                    "metric": {"label": "fraud_count", "expressionType": "SIMPLE", "column": {"column_name": "fraud_count"}, "aggregate": "SUM"},
                    "show_legend": True,
                    "show_labels": True,
                    "donut": True,
                    "innerRadius": 40
                })
            },
            # 12. Total Transactions by Card Brand - Bar
            {
                "slice_name": "Tổng Giao Dịch theo Thương Hiệu Thẻ",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("fraud_by_card_type"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "card_brand",
                    "metrics": [{"label": "total_transactions", "expressionType": "SIMPLE", "column": {"column_name": "total_transactions"}, "aggregate": "SUM"}],
                    "show_legend": True
                })
            },
            # 13. Card Type Details Table
            {
                "slice_name": "Chi Tiết Loại Thẻ",
                "viz_type": "table",
                "datasource_id": self.dataset_ids.get("fraud_by_card_type"),
                "datasource_type": "table",
                "params": json.dumps({
                    "all_columns": ["card_brand", "card_category", "total_transactions", "fraud_count", "legitimate_count", "fraud_rate_pct", "total_amount", "fraud_amount"],
                    "page_length": 15,
                    "order_desc": True
                })
            },
            
            # ============================================================
            # HOURLY FRAUD ANALYSIS CHARTS (6 charts)
            # ============================================================
            # 14. Hourly Analysis - Bar Chart (Fraud Count)
            {
                "slice_name": "Phân Tích Theo Giờ",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("hourly_fraud_analysis"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "hour_of_day",
                    "metrics": [{"label": "fraud_count", "expressionType": "SIMPLE", "column": {"column_name": "fraud_count"}, "aggregate": "SUM"}],
                    "show_legend": True
                })
            },
            # 15. Hourly Fraud Rate - Line Chart
            {
                "slice_name": "Tỷ Lệ Gian Lận Theo Giờ",
                "viz_type": "echarts_timeseries_line",
                "datasource_id": self.dataset_ids.get("hourly_fraud_analysis"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "hour_of_day",
                    "metrics": [{"label": "fraud_rate_pct", "expressionType": "SIMPLE", "column": {"column_name": "fraud_rate_pct"}, "aggregate": "MAX"}],
                    "show_legend": True,
                    "show_markers": True
                })
            },
            # 16. Hourly Transactions - Bar Chart
            {
                "slice_name": "Số Giao Dịch Theo Giờ",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("hourly_fraud_analysis"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "hour_of_day",
                    "metrics": [{"label": "total_transactions", "expressionType": "SIMPLE", "column": {"column_name": "total_transactions"}, "aggregate": "SUM"}],
                    "show_legend": True,
                    "color_scheme": "blue"
                })
            },
            # 17. Hourly Fraud Amount - Area Chart
            {
                "slice_name": "Giá Trị Gian Lận Theo Giờ",
                "viz_type": "echarts_area",
                "datasource_id": self.dataset_ids.get("hourly_fraud_analysis"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "hour_of_day",
                    "metrics": [{"label": "fraud_amount", "expressionType": "SIMPLE", "column": {"column_name": "fraud_amount"}, "aggregate": "SUM"}],
                    "show_legend": True,
                    "opacity": 0.7
                })
            },
            # 18. Time Period Fraud Distribution - Pie
            {
                "slice_name": "Phân Phối Gian Lận theo Thời Điểm",
                "viz_type": "pie",
                "datasource_id": self.dataset_ids.get("hourly_fraud_analysis"),
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["time_period"],
                    "metric": {"label": "fraud_count", "expressionType": "SIMPLE", "column": {"column_name": "fraud_count"}, "aggregate": "SUM"},
                    "show_legend": True,
                    "show_labels": True
                })
            },
            # 19. Hourly Analysis Table
            {
                "slice_name": "Bảng Phân Tích Theo Giờ",
                "viz_type": "table",
                "datasource_id": self.dataset_ids.get("hourly_fraud_analysis"),
                "datasource_type": "table",
                "params": json.dumps({
                    "all_columns": ["hour_of_day", "time_period", "total_transactions", "fraud_count", "fraud_rate_pct", "total_amount", "fraud_amount"],
                    "page_length": 24
                })
            },
            
            # ============================================================
            # DAILY TRANSACTION SUMMARY CHARTS (5 charts)
            # ============================================================
            # 20. Daily Trend - Line Chart
            {
                "slice_name": "Xu Hướng Hàng Ngày",
                "viz_type": "echarts_timeseries_line",
                "datasource_id": self.dataset_ids.get("daily_transaction_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "transaction_day",
                    "metrics": [
                        {"label": "fraud_count", "expressionType": "SIMPLE", "column": {"column_name": "fraud_count"}, "aggregate": "SUM"},
                        {"label": "legitimate_count", "expressionType": "SIMPLE", "column": {"column_name": "legitimate_count"}, "aggregate": "SUM"}
                    ],
                    "show_legend": True
                })
            },
            # 21. Daily Transactions - Bar Chart
            {
                "slice_name": "Số Giao Dịch Hàng Ngày",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("daily_transaction_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "transaction_day",
                    "metrics": [{"label": "total_transactions", "expressionType": "SIMPLE", "column": {"column_name": "total_transactions"}, "aggregate": "SUM"}],
                    "show_legend": True
                })
            },
            # 22. Daily Fraud Rate Trend - Line
            {
                "slice_name": "Xu Hướng Tỷ Lệ Gian Lận Hàng Ngày",
                "viz_type": "echarts_timeseries_line",
                "datasource_id": self.dataset_ids.get("daily_transaction_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "transaction_day",
                    "metrics": [{"label": "fraud_rate_pct", "expressionType": "SIMPLE", "column": {"column_name": "fraud_rate_pct"}, "aggregate": "AVG"}],
                    "show_legend": True,
                    "show_markers": True,
                    "color_scheme": "red"
                })
            },
            # 23. Daily Amount - Area Chart
            {
                "slice_name": "Giá Trị Giao Dịch Hàng Ngày",
                "viz_type": "echarts_area",
                "datasource_id": self.dataset_ids.get("daily_transaction_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "transaction_day",
                    "metrics": [{"label": "total_amount", "expressionType": "SIMPLE", "column": {"column_name": "total_amount"}, "aggregate": "SUM"}],
                    "show_legend": True
                })
            },
            # 24. Daily Summary Table
            {
                "slice_name": "Bảng Tổng Hợp Hàng Ngày",
                "viz_type": "table",
                "datasource_id": self.dataset_ids.get("daily_transaction_summary"),
                "datasource_type": "table",
                "params": json.dumps({
                    "all_columns": ["transaction_day", "total_transactions", "fraud_count", "legitimate_count", "fraud_rate_pct", "total_amount", "fraud_amount"],
                    "page_length": 30
                })
            },
            
            # ============================================================
            # FRAUD BY DAY OF WEEK CHARTS (4 charts)
            # ============================================================
            # 25. Fraud by Day of Week - Bar Chart
            {
                "slice_name": "Gian Lận theo Ngày trong Tuần",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("fraud_by_day_of_week"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "day_of_week_name",
                    "metrics": [{"label": "fraud_rate_pct", "expressionType": "SIMPLE", "column": {"column_name": "fraud_rate_pct"}, "aggregate": "MAX"}],
                    "show_legend": True
                })
            },
            # 26. Fraud Count by Day of Week - Bar
            {
                "slice_name": "Số Gian Lận theo Ngày trong Tuần",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("fraud_by_day_of_week"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "day_of_week_name",
                    "metrics": [{"label": "fraud_count", "expressionType": "SIMPLE", "column": {"column_name": "fraud_count"}, "aggregate": "SUM"}],
                    "show_legend": True,
                    "color_scheme": "red"
                })
            },
            # 27. Day of Week Distribution - Pie
            {
                "slice_name": "Phân Phối Gian Lận theo Ngày trong Tuần",
                "viz_type": "pie",
                "datasource_id": self.dataset_ids.get("fraud_by_day_of_week"),
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["day_of_week_name"],
                    "metric": {"label": "fraud_count", "expressionType": "SIMPLE", "column": {"column_name": "fraud_count"}, "aggregate": "SUM"},
                    "show_legend": True,
                    "show_labels": True
                })
            },
            # 28. Day of Week Table
            {
                "slice_name": "Bảng Phân Tích Ngày trong Tuần",
                "viz_type": "table",
                "datasource_id": self.dataset_ids.get("fraud_by_day_of_week"),
                "datasource_type": "table",
                "params": json.dumps({
                    "all_columns": ["day_of_week", "day_of_week_name", "total_transactions", "fraud_count", "legitimate_count", "fraud_rate_pct", "total_amount", "fraud_amount"],
                    "page_length": 7
                })
            },
            
            # ============================================================
            # FRAUD BY AMOUNT CATEGORY CHARTS (4 charts)
            # ============================================================
            # 29. Amount Category Analysis - Pie
            {
                "slice_name": "Phân Tích theo Mức Tiền",
                "viz_type": "pie",
                "datasource_id": self.dataset_ids.get("fraud_by_amount_category"),
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["amount_category"],
                    "metric": {"label": "fraud_count", "expressionType": "SIMPLE", "column": {"column_name": "fraud_count"}, "aggregate": "SUM"},
                    "show_legend": True
                })
            },
            # 30. Fraud Rate by Amount Category - Bar
            {
                "slice_name": "Tỷ Lệ Gian Lận theo Mức Tiền",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("fraud_by_amount_category"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "amount_category",
                    "metrics": [{"label": "fraud_rate_pct", "expressionType": "SIMPLE", "column": {"column_name": "fraud_rate_pct"}, "aggregate": "MAX"}],
                    "show_legend": True,
                    "order_desc": True
                })
            },
            # 31. Transaction Volume by Amount - Treemap
            {
                "slice_name": "Khối Lượng Giao Dịch theo Mức Tiền",
                "viz_type": "treemap_v2",
                "datasource_id": self.dataset_ids.get("fraud_by_amount_category"),
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["amount_category"],
                    "metric": {"label": "total_transactions", "expressionType": "SIMPLE", "column": {"column_name": "total_transactions"}, "aggregate": "SUM"},
                    "show_labels": True
                })
            },
            # 32. Amount Category Table
            {
                "slice_name": "Bảng Phân Tích Mức Tiền",
                "viz_type": "table",
                "datasource_id": self.dataset_ids.get("fraud_by_amount_category"),
                "datasource_type": "table",
                "params": json.dumps({
                    "all_columns": ["amount_category", "category_order", "total_transactions", "fraud_count", "legitimate_count", "fraud_rate_pct", "total_amount", "fraud_amount", "avg_amount", "min_amount", "max_amount"],
                    "page_length": 10
                })
            },
            
            # ============================================================
            # FRAUD BY PRODUCT CHARTS (5 charts)
            # ============================================================
            # 33. Product Analysis - Table
            {
                "slice_name": "Gian Lận theo Sản Phẩm",
                "viz_type": "table",
                "datasource_id": self.dataset_ids.get("fraud_by_product"),
                "datasource_type": "table",
                "params": json.dumps({
                    "all_columns": ["product_code", "total_transactions", "fraud_count", "fraud_rate_pct"],
                    "page_length": 10
                })
            },
            # 34. Fraud Rate by Product - Bar Chart
            {
                "slice_name": "Tỷ Lệ Gian Lận theo Sản Phẩm",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("fraud_by_product"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "product_code",
                    "metrics": [{"label": "fraud_rate_pct", "expressionType": "SIMPLE", "column": {"column_name": "fraud_rate_pct"}, "aggregate": "MAX"}],
                    "show_legend": True,
                    "order_desc": True
                })
            },
            # 35. Transaction Volume by Product - Pie
            {
                "slice_name": "Khối Lượng Giao Dịch theo Sản Phẩm",
                "viz_type": "pie",
                "datasource_id": self.dataset_ids.get("fraud_by_product"),
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["product_code"],
                    "metric": {"label": "total_transactions", "expressionType": "SIMPLE", "column": {"column_name": "total_transactions"}, "aggregate": "SUM"},
                    "show_legend": True,
                    "show_labels": True
                })
            },
            # 36. Fraud Amount by Product - Donut
            {
                "slice_name": "Giá Trị Gian Lận theo Sản Phẩm",
                "viz_type": "pie",
                "datasource_id": self.dataset_ids.get("fraud_by_product"),
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["product_code"],
                    "metric": {"label": "fraud_amount", "expressionType": "SIMPLE", "column": {"column_name": "fraud_amount"}, "aggregate": "SUM"},
                    "show_legend": True,
                    "donut": True,
                    "innerRadius": 40
                })
            },
            # 37. Product Full Details Table
            {
                "slice_name": "Chi Tiết Đầy Đủ Sản Phẩm",
                "viz_type": "table",
                "datasource_id": self.dataset_ids.get("fraud_by_product"),
                "datasource_type": "table",
                "params": json.dumps({
                    "all_columns": ["product_code", "total_transactions", "fraud_count", "fraud_rate_pct", "total_amount", "fraud_amount", "avg_amount", "min_amount", "max_amount", "high_value_count", "high_value_pct"],
                    "page_length": 10
                })
            },
            
            # ============================================================
            # HIGH RISK TRANSACTIONS CHARTS (5 charts)
            # ============================================================
            # 38. High Risk Transactions Table
            {
                "slice_name": "Giao Dịch Rủi Ro Cao",
                "viz_type": "table",
                "datasource_id": self.dataset_ids.get("high_risk_transactions"),
                "datasource_type": "table",
                "params": json.dumps({
                    "all_columns": ["TransactionID", "is_fraud", "transaction_amount", "transaction_hour", "product_code", "card_brand", "risk_score", "risk_level"],
                    "page_length": 100,
                    "order_desc": True
                })
            },
            # 39. Risk Level Distribution - Pie
            {
                "slice_name": "Phân Phối Mức Độ Rủi Ro",
                "viz_type": "pie",
                "datasource_id": self.dataset_ids.get("high_risk_transactions"),
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["risk_level"],
                    "metric": {"label": "count", "expressionType": "SQL", "sqlExpression": "COUNT(*)"},
                    "show_legend": True,
                    "show_labels": True
                })
            },
            # 40. High Risk by Product - Bar
            {
                "slice_name": "Rủi Ro Cao theo Sản Phẩm",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("high_risk_transactions"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "product_code",
                    "metrics": [{"label": "count", "expressionType": "SQL", "sqlExpression": "COUNT(*)"}],
                    "show_legend": True
                })
            },
            # 41. High Risk by Card Brand - Bar
            {
                "slice_name": "Rủi Ro Cao theo Thương Hiệu Thẻ",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": self.dataset_ids.get("high_risk_transactions"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "card_brand",
                    "metrics": [{"label": "count", "expressionType": "SQL", "sqlExpression": "COUNT(*)"}],
                    "show_legend": True
                })
            },
            # 42. High Risk by Hour - Line
            {
                "slice_name": "Rủi Ro Cao theo Giờ",
                "viz_type": "echarts_timeseries_line",
                "datasource_id": self.dataset_ids.get("high_risk_transactions"),
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "transaction_hour",
                    "metrics": [{"label": "count", "expressionType": "SQL", "sqlExpression": "COUNT(*)"}],
                    "show_legend": True,
                    "show_markers": True
                })
            },
        ]
        
        for chart_config in charts_config:
            if not chart_config.get("datasource_id"):
                print(f"   ⚠️  Bỏ qua chart '{chart_config['slice_name']}' - thiếu dataset")
                continue
            
            # Check if chart already exists
            resp = self.session.get(
                f"{SUPERSET_URL}/api/v1/chart/",
                params={"q": json.dumps({"filters": [{"col": "slice_name", "opr": "eq", "value": chart_config["slice_name"]}]})}
            )
            
            if resp.status_code == 200:
                existing = resp.json().get("result", [])
                if existing:
                    chart_id = existing[0].get("id")
                    self.chart_ids.append(chart_id)
                    print(f"   ⚠️  Chart '{chart_config['slice_name']}' đã tồn tại (ID: {chart_id})")
                    continue
                
            resp = self.session.post(
                f"{SUPERSET_URL}/api/v1/chart/",
                json=chart_config
            )
            
            if resp.status_code in [200, 201]:
                chart_id = resp.json().get("id")
                self.chart_ids.append(chart_id)
                print(f"   ✅ Đã tạo chart: {chart_config['slice_name']} (ID: {chart_id})")
            else:
                print(f"   ⚠️  Lỗi tạo chart {chart_config['slice_name']}: {resp.status_code}")
        
        return True
    
    def create_dashboard(self):
        """Tạo dashboard với các charts và layout"""
        print("🎨 Đang tạo Dashboard...")
        
        if not self.chart_ids:
            print("   ⚠️  Không có charts để thêm vào dashboard")
            return False
        
        # Check if dashboard exists
        resp = self.session.get(
            f"{SUPERSET_URL}/api/v1/dashboard/",
            params={"q": json.dumps({"filters": [{"col": "dashboard_title", "opr": "eq", "value": "Fraud Detection Dashboard"}]})}
        )
        
        dashboard_id = None
        if resp.status_code == 200:
            existing = resp.json().get("result", [])
            if existing:
                dashboard_id = existing[0].get("id")
                print(f"   ⚠️  Dashboard đã tồn tại (ID: {dashboard_id})")
        
        if not dashboard_id:
            # Create new dashboard
            dashboard_data = {
                "dashboard_title": "Fraud Detection Dashboard",
                "published": True,
                "slug": "fraud-detection",
            }
            
            resp = self.session.post(
                f"{SUPERSET_URL}/api/v1/dashboard/",
                json=dashboard_data
            )
            
            if resp.status_code in [200, 201]:
                dashboard_id = resp.json().get("id")
                print(f"   ✅ Đã tạo Dashboard (ID: {dashboard_id})")
            else:
                print(f"   ❌ Lỗi tạo dashboard: {resp.status_code} - {resp.text}")
                return False
        
        # Link charts to dashboard via direct database manipulation
        # This is required because Superset API doesn't auto-link charts
        self._link_charts_to_dashboard(dashboard_id)
        
        print(f"   🌐 Truy cập: {SUPERSET_URL}/superset/dashboard/{dashboard_id}/")
        return True
    
    def _link_charts_to_dashboard(self, dashboard_id):
        """Link charts to dashboard via Superset CLI inside container"""
        import subprocess
        
        print("   🔗 Đang liên kết charts vào dashboard...")
        
        # Build Python script to run inside Superset container
        python_script = f'''
import sqlite3
conn = sqlite3.connect("/app/superset_home/superset.db")
cursor = conn.cursor()

dashboard_id = {dashboard_id}
chart_ids = {self.chart_ids}

# Clear existing links for this dashboard
cursor.execute("DELETE FROM dashboard_slices WHERE dashboard_id = ?", (dashboard_id,))

# Insert new links
for chart_id in chart_ids:
    cursor.execute("INSERT INTO dashboard_slices (dashboard_id, slice_id) VALUES (?, ?)", (dashboard_id, chart_id))

conn.commit()
conn.close()
print("OK")
'''
        
        try:
            result = subprocess.run(
                ["docker", "exec", "superset", "python3", "-c", python_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and "OK" in result.stdout:
                print(f"   ✅ Đã liên kết {len(self.chart_ids)} charts vào dashboard")
            else:
                print(f"   ⚠️  Lỗi liên kết: {result.stderr}")
        except Exception as e:
            print(f"   ⚠️  Không thể liên kết tự động: {e}")
            print(f"   📌 Chạy thủ công: docker exec superset python3 -c '...'")
    
    def run(self):
        """Chạy toàn bộ setup"""
        print("=" * 60)
        print("🚀 SUPERSET AUTO SETUP")
        print("=" * 60)
        
        if not self.login():
            return False
        
        time.sleep(1)
        
        if not self.create_database_connection():
            return False
        
        time.sleep(1)
        
        if not self.create_datasets():
            return False
        
        time.sleep(1)
        
        self.create_charts()
        
        time.sleep(1)
        
        self.create_dashboard()
        
        print("=" * 60)
        print("✅ SETUP HOÀN TẤT!")
        print("=" * 60)
        print(f"\n🌐 Mở Dashboard: {SUPERSET_URL}/dashboard/list/")
        print(f"📊 SQL Lab: {SUPERSET_URL}/sqllab/")
        print(f"📈 Charts: {SUPERSET_URL}/chart/list/")
        
        return True


if __name__ == "__main__":
    setup = SupersetSetup()
    setup.run()
