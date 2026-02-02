-- =============================================================================
-- GOLD: FRAUD BY CARD TYPE - DBT MODEL
-- =============================================================================
-- Mô tả: Thống kê gian lận theo loại thẻ và thương hiệu
-- Source: silver.transactions
-- Target: gold.fraud_by_card_type
-- =============================================================================

{{ config(
    materialized='table',
    schema='gold',
    description='Thống kê gian lận theo loại thẻ - phục vụ báo cáo'
) }}

WITH transaction_data AS (
    SELECT * FROM {{ ref('silver_transactions') }}
),

aggregated AS (
    SELECT
        card_brand,
        card_category,
        
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
        
        -- Số tiền trung bình mỗi giao dịch
        ROUND(AVG(transaction_amount), 2) AS avg_transaction_amount,
        
        -- Số tiền trung bình giao dịch gian lận
        ROUND(AVG(CASE WHEN is_fraud = 1 THEN transaction_amount END), 2) AS avg_fraud_amount,
        
        -- Timestamp tạo báo cáo
        CURRENT_TIMESTAMP() AS report_generated_at,
        '{{ invocation_id }}' AS _dbt_run_id
        
    FROM transaction_data
    GROUP BY card_brand, card_category
)

SELECT * FROM aggregated
ORDER BY fraud_count DESC
