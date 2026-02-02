-- =============================================================================
-- GOLD: HOURLY FRAUD ANALYSIS - DBT MODEL
-- =============================================================================
-- Mô tả: Phân tích xu hướng gian lận theo giờ trong ngày
-- Source: silver.transactions
-- Target: gold.hourly_fraud_analysis
-- =============================================================================

{{ config(
    materialized='table',
    schema='gold',
    description='Phân tích gian lận theo giờ - phát hiện pattern thời gian'
) }}

WITH transaction_data AS (
    SELECT * FROM {{ ref('silver_transactions') }}
),

hourly_stats AS (
    SELECT
        transaction_hour AS hour_of_day,
        
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
        
        -- Số giao dịch giá trị cao
        SUM(is_high_amount) AS high_value_transactions,
        
        -- Phân loại khung giờ
        CASE 
            WHEN transaction_hour BETWEEN 0 AND 5 THEN 'Night (00-05)'
            WHEN transaction_hour BETWEEN 6 AND 11 THEN 'Morning (06-11)'
            WHEN transaction_hour BETWEEN 12 AND 17 THEN 'Afternoon (12-17)'
            ELSE 'Evening (18-23)'
        END AS time_period,
        
        -- Timestamp
        CURRENT_TIMESTAMP() AS report_generated_at,
        '{{ invocation_id }}' AS _dbt_run_id
        
    FROM transaction_data
    GROUP BY transaction_hour
)

SELECT * FROM hourly_stats
ORDER BY hour_of_day
