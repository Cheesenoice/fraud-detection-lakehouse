-- =============================================================================
-- GOLD: HIGH RISK TRANSACTIONS - DBT MODEL
-- =============================================================================
-- Mô tả: Danh sách các giao dịch có nguy cơ gian lận cao
-- Source: silver.transactions, silver.identity
-- Target: gold.high_risk_transactions
-- =============================================================================

{{ config(
    materialized='table',
    schema='gold',
    description='Danh sách giao dịch có nguy cơ gian lận cao để giám sát'
) }}

WITH transactions AS (
    SELECT * FROM {{ ref('silver_transactions') }}
),

identity AS (
    SELECT * FROM {{ ref('silver_identity') }}
),

-- Join Transaction với Identity
joined_data AS (
    SELECT
        t.TransactionID,
        t.is_fraud,
        t.transaction_amount,
        t.transaction_hour,
        t.transaction_day,
        t.product_code,
        t.card_brand,
        t.card_category,
        t.purchaser_email_domain,
        t.recipient_email_domain,
        t.email_domain_match,
        t.is_high_amount,
        t.amount_log,
        
        -- Identity info
        COALESCE(i.device_type, 'unknown') AS device_type,
        COALESCE(i.device_category, 'unknown') AS device_category,
        COALESCE(i.operating_system, 'unknown') AS operating_system
        
    FROM transactions t
    LEFT JOIN identity i ON t.TransactionID = i.TransactionID
),

-- Tính điểm rủi ro
risk_scored AS (
    SELECT
        *,
        -- Tính risk score dựa trên nhiều yếu tố
        (
            -- Giao dịch giá trị cao: +2 điểm
            (CASE WHEN is_high_amount = 1 THEN 2 ELSE 0 END) +
            
            -- Giao dịch ban đêm (0-5h): +1 điểm
            (CASE WHEN transaction_hour BETWEEN 0 AND 5 THEN 1 ELSE 0 END) +
            
            -- Email domain không khớp: +1 điểm
            (CASE WHEN email_domain_match = 0 THEN 1 ELSE 0 END) +
            
            -- Sản phẩm có risk cao (W, C): +1 điểm
            (CASE WHEN product_code IN ('W', 'C') THEN 1 ELSE 0 END) +
            
            -- Số tiền rất cao (>1000): +2 điểm
            (CASE WHEN transaction_amount > 1000 THEN 2 ELSE 0 END)
        ) AS risk_score
        
    FROM joined_data
),

-- Lọc giao dịch high risk
high_risk AS (
    SELECT
        TransactionID,
        is_fraud,
        transaction_amount,
        transaction_hour,
        transaction_day,
        product_code,
        card_brand,
        card_category,
        purchaser_email_domain,
        device_type,
        device_category,
        operating_system,
        risk_score,
        
        -- Phân loại mức độ rủi ro
        CASE 
            WHEN risk_score >= 5 THEN 'Critical'
            WHEN risk_score >= 3 THEN 'High'
            WHEN risk_score >= 2 THEN 'Medium'
            ELSE 'Low'
        END AS risk_level,
        
        -- Timestamp
        CURRENT_TIMESTAMP() AS report_generated_at,
        '{{ invocation_id }}' AS _dbt_run_id
        
    FROM risk_scored
    WHERE risk_score >= 2  -- Chỉ lấy các giao dịch có risk từ Medium trở lên
)

SELECT * FROM high_risk
ORDER BY risk_score DESC, transaction_amount DESC
LIMIT 10000
