-- =============================================================================
-- GOLD: FRAUD BY DAY OF WEEK - DBT MODEL
-- =============================================================================
-- Mô tả: Phân tích xu hướng gian lận theo ngày trong tuần
-- Source: silver.transactions
-- Target: gold.fraud_by_day_of_week
-- Business Question: "Kẻ gian thường hoạt động vào ngày nào trong tuần?"
-- =============================================================================

{{ config(
    materialized='table',
    schema='gold',
    description='Phân tích gian lận theo ngày trong tuần - phát hiện pattern tuần'
) }}

WITH transaction_data AS (
    SELECT * FROM {{ ref('silver_transactions') }}
),

daily_stats AS (
    SELECT
        day_of_week,
        day_of_week_name,
        
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
        SUM(is_high_amount) AS high_value_transactions,
        
        -- Timestamp tạo báo cáo
        CURRENT_TIMESTAMP() AS report_generated_at,
        '{{ invocation_id }}' AS _dbt_run_id
        
    FROM transaction_data
    GROUP BY day_of_week, day_of_week_name
)

SELECT * FROM daily_stats
ORDER BY day_of_week
