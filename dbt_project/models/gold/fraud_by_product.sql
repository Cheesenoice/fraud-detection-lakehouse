-- =============================================================================
-- GOLD: FRAUD BY PRODUCT - DBT MODEL
-- =============================================================================
-- Mô tả: Thống kê gian lận theo loại sản phẩm
-- Source: silver.transactions
-- Target: gold.fraud_by_product
-- =============================================================================

{{ config(
    materialized='table',
    schema='gold',
    description='Thống kê gian lận theo mã sản phẩm'
) }}

WITH transaction_data AS (
    SELECT * FROM {{ ref('silver_transactions') }}
),

product_stats AS (
    SELECT
        product_code,
        
        -- Tổng số giao dịch
        COUNT(*) AS total_transactions,
        
        -- Số giao dịch gian lận
        SUM(is_fraud) AS fraud_count,
        
        -- Tỷ lệ gian lận (%)
        ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
        
        -- Tổng số tiền
        ROUND(SUM(transaction_amount), 2) AS total_amount,
        
        -- Số tiền gian lận
        ROUND(SUM(CASE WHEN is_fraud = 1 THEN transaction_amount ELSE 0 END), 2) AS fraud_amount,
        
        -- Số tiền trung bình
        ROUND(AVG(transaction_amount), 2) AS avg_amount,
        
        -- Min/Max amount
        ROUND(MIN(transaction_amount), 2) AS min_amount,
        ROUND(MAX(transaction_amount), 2) AS max_amount,
        
        -- Số giao dịch giá trị cao
        SUM(is_high_amount) AS high_value_count,
        
        -- Tỷ lệ giao dịch giá trị cao (%)
        ROUND(SUM(is_high_amount) * 100.0 / COUNT(*), 2) AS high_value_pct,
        
        -- Timestamp
        CURRENT_TIMESTAMP() AS report_generated_at,
        '{{ invocation_id }}' AS _dbt_run_id
        
    FROM transaction_data
    GROUP BY product_code
)

SELECT * FROM product_stats
ORDER BY fraud_count DESC
