-- =============================================================================
-- GOLD: DAILY TRANSACTION SUMMARY - DBT MODEL
-- =============================================================================
-- Mô tả: Tổng hợp giao dịch theo ngày
-- Source: silver.transactions
-- Target: gold.daily_transaction_summary
-- =============================================================================

{{ config(
    materialized='table',
    schema='gold',
    description='Tổng hợp giao dịch theo ngày - Time Series Analysis'
) }}

WITH transaction_data AS (
    SELECT * FROM {{ ref('silver_transactions') }}
),

daily_stats AS (
    SELECT
        transaction_day,
        
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
        
        -- Số giao dịch giá trị cao
        SUM(is_high_amount) AS high_value_count,
        
        -- Số loại thẻ duy nhất
        COUNT(DISTINCT card_brand) AS unique_cards,
        
        -- Số loại sản phẩm
        COUNT(DISTINCT product_code) AS unique_products,
        
        -- Timestamp
        CURRENT_TIMESTAMP() AS report_generated_at,
        '{{ invocation_id }}' AS _dbt_run_id
        
    FROM transaction_data
    GROUP BY transaction_day
)

SELECT * FROM daily_stats
ORDER BY transaction_day
