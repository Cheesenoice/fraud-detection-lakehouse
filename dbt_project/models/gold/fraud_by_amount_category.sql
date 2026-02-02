-- =============================================================================
-- GOLD: FRAUD BY AMOUNT CATEGORY - DBT MODEL
-- =============================================================================
-- Mô tả: Phân tích gian lận theo quy mô số tiền giao dịch
-- Source: silver.transactions
-- Target: gold.fraud_by_amount_category
-- Business Question: "Fraud tập trung ở giao dịch nhỏ (thử thẻ) hay lớn (rút ruột)?"
-- =============================================================================

{{ config(
    materialized='table',
    schema='gold',
    description='Phân tích gian lận theo phân khúc giá trị giao dịch'
) }}

WITH transaction_data AS (
    SELECT * FROM {{ ref('silver_transactions') }}
),

amount_stats AS (
    SELECT
        amount_category,
        
        -- Thứ tự sắp xếp
        CASE amount_category
            WHEN 'Micro (<=$50)' THEN 1
            WHEN 'Very Small ($50-100)' THEN 2
            WHEN 'Small ($100-500)' THEN 3
            WHEN 'Medium ($500-1K)' THEN 4
            WHEN 'Large ($1K-5K)' THEN 5
            ELSE 6
        END AS category_order,
        
        -- Tổng số giao dịch
        COUNT(*) AS total_transactions,
        
        -- Số giao dịch gian lận
        SUM(is_fraud) AS fraud_count,
        
        -- Số giao dịch hợp lệ
        COUNT(*) - SUM(is_fraud) AS legitimate_count,
        
        -- Tỷ lệ gian lận (%)
        ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
        
        -- Tổng số tiền
        ROUND(SUM(transaction_amount), 2) AS total_amount,
        
        -- Số tiền gian lận
        ROUND(SUM(CASE WHEN is_fraud = 1 THEN transaction_amount ELSE 0 END), 2) AS fraud_amount,
        
        -- Số tiền trung bình
        ROUND(AVG(transaction_amount), 2) AS avg_amount,
        
        -- Min/Max amount trong category
        ROUND(MIN(transaction_amount), 2) AS min_amount,
        ROUND(MAX(transaction_amount), 2) AS max_amount,
        
        -- Timestamp tạo báo cáo
        CURRENT_TIMESTAMP() AS report_generated_at,
        '{{ invocation_id }}' AS _dbt_run_id
        
    FROM transaction_data
    GROUP BY amount_category
)

SELECT * FROM amount_stats
ORDER BY category_order
