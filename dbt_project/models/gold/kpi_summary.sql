-- =============================================================================
-- GOLD: KPI SUMMARY - DBT MODEL
-- =============================================================================
-- Mô tả: Tổng hợp các chỉ số KPI chính cho Dashboard
-- Source: silver.transactions
-- Target: gold.kpi_summary
-- =============================================================================

{{ config(
    materialized='table',
    schema='gold',
    description='Bảng tổng hợp KPI chính cho Fraud Detection Dashboard'
) }}

WITH transaction_data AS (
    SELECT * FROM {{ ref('silver_transactions') }}
),

overall_stats AS (
    SELECT
        'overall' AS metric_category,
        
        -- Tổng số giao dịch
        COUNT(*) AS total_transactions,
        
        -- Số giao dịch gian lận
        SUM(is_fraud) AS total_fraud_count,
        
        -- Số giao dịch hợp lệ
        COUNT(*) - SUM(is_fraud) AS total_legitimate_count,
        
        -- Tỷ lệ gian lận (%)
        ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
        
        -- Tổng số tiền giao dịch
        ROUND(SUM(transaction_amount), 2) AS total_transaction_amount,
        
        -- Tổng số tiền bị gian lận
        ROUND(SUM(CASE WHEN is_fraud = 1 THEN transaction_amount ELSE 0 END), 2) AS total_fraud_amount,
        
        -- Số tiền trung bình mỗi giao dịch
        ROUND(AVG(transaction_amount), 2) AS avg_transaction_amount,
        
        -- Số tiền trung bình giao dịch gian lận
        ROUND(AVG(CASE WHEN is_fraud = 1 THEN transaction_amount END), 2) AS avg_fraud_amount,
        
        -- Số tiền trung bình giao dịch hợp lệ
        ROUND(AVG(CASE WHEN is_fraud = 0 THEN transaction_amount END), 2) AS avg_legitimate_amount,
        
        -- Giao dịch lớn nhất
        ROUND(MAX(transaction_amount), 2) AS max_transaction_amount,
        
        -- Số giao dịch giá trị cao
        SUM(is_high_amount) AS high_value_transactions,
        
        -- Số loại thẻ duy nhất
        COUNT(DISTINCT card_brand) AS unique_card_brands,
        
        -- Số loại sản phẩm duy nhất
        COUNT(DISTINCT product_code) AS unique_products,
        
        -- Số ngày có giao dịch
        COUNT(DISTINCT transaction_day) AS active_days,
        
        -- Timestamp tạo báo cáo
        CURRENT_TIMESTAMP() AS report_generated_at,
        '{{ invocation_id }}' AS _dbt_run_id
        
    FROM transaction_data
)

SELECT * FROM overall_stats
