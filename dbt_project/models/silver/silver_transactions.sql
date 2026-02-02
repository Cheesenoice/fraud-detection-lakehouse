-- =============================================================================
-- SILVER TRANSACTIONS - DBT MODEL
-- =============================================================================
-- Mô tả: Làm sạch và chuẩn hóa dữ liệu giao dịch từ Bronze Layer
-- Source: demo.bronze.transactions
-- Target: demo.silver.transactions
-- =============================================================================

{{ config(
    materialized='table',
    schema='silver',
    description='Bảng giao dịch đã làm sạch từ Bronze Layer'
) }}

WITH source_data AS (
    -- Đọc dữ liệu từ Bronze Layer
    SELECT * FROM {{ source('bronze', 'transactions') }}
),

cleaned_data AS (
    SELECT
        -- ===== ID và Target =====
        TransactionID,
        CAST(isFraud AS INT) AS is_fraud,
        
        -- ===== Thông tin giao dịch =====
        CAST(TransactionAmt AS DOUBLE) AS transaction_amount,
        CAST(TransactionDT AS INT) AS transaction_dt,
        ProductCD AS product_code,
        
        -- ===== Thông tin thẻ =====
        CAST(card1 AS INT) AS card1,
        CAST(card2 AS DOUBLE) AS card2,
        CAST(card3 AS DOUBLE) AS card3,
        COALESCE(card4, 'unknown') AS card_brand,      -- visa, mastercard, etc
        CAST(card5 AS DOUBLE) AS card5,
        COALESCE(card6, 'unknown') AS card_category,   -- credit, debit
        
        -- ===== Địa chỉ =====
        CAST(addr1 AS DOUBLE) AS billing_region,
        CAST(addr2 AS DOUBLE) AS billing_country,
        
        -- ===== Email domains =====
        COALESCE(P_emaildomain, 'unknown') AS purchaser_email_domain,
        COALESCE(R_emaildomain, 'unknown') AS recipient_email_domain,
        
        -- ===== Device info (C1-C14) =====
        CAST(C1 AS DOUBLE) AS c1,
        CAST(C2 AS DOUBLE) AS c2,
        CAST(C3 AS DOUBLE) AS c3,
        CAST(C4 AS DOUBLE) AS c4,
        CAST(C5 AS DOUBLE) AS c5,
        CAST(C6 AS DOUBLE) AS c6,
        CAST(C7 AS DOUBLE) AS c7,
        CAST(C8 AS DOUBLE) AS c8,
        CAST(C9 AS DOUBLE) AS c9,
        CAST(C10 AS DOUBLE) AS c10,
        CAST(C11 AS DOUBLE) AS c11,
        CAST(C12 AS DOUBLE) AS c12,
        CAST(C13 AS DOUBLE) AS c13,
        CAST(C14 AS DOUBLE) AS c14,
        
        -- ===== Metadata từ Bronze =====
        _ingestion_time,
        _source_file
        
    FROM source_data
    WHERE TransactionID IS NOT NULL
),

enriched_data AS (
    SELECT
        *,
        -- ===== FEATURE ENGINEERING =====
        -- Giờ trong ngày (0-23)
        CAST((transaction_dt % 86400) / 3600 AS INT) AS transaction_hour,
        
        -- Ngày (số ngày từ epoch)
        CAST(transaction_dt / 86400 AS INT) AS transaction_day,
        
        -- ===== MỚI: Ngày trong tuần (0=Mon, 6=Sun) - Theo yêu cầu BA =====
        CAST((transaction_dt / 86400) % 7 AS INT) AS day_of_week,
        
        -- ===== MỚI: Tên ngày trong tuần (cho Dashboard dễ đọc) =====
        CASE CAST((transaction_dt / 86400) % 7 AS INT)
            WHEN 0 THEN 'Mon'
            WHEN 1 THEN 'Tue'
            WHEN 2 THEN 'Wed'
            WHEN 3 THEN 'Thu'
            WHEN 4 THEN 'Fri'
            WHEN 5 THEN 'Sat'
            WHEN 6 THEN 'Sun'
        END AS day_of_week_name,
        
        -- Log của số tiền (xử lý skewness)
        LN(transaction_amount + 1) AS amount_log,
        
        -- Cờ giao dịch giá trị cao
        CASE 
            WHEN transaction_amount > {{ var('high_amount_threshold') }} THEN 1 
            ELSE 0 
        END AS is_high_amount,
        
        -- ===== MỚI: Phân loại quy mô số tiền giao dịch - Theo yêu cầu BA =====
        CASE 
            WHEN transaction_amount <= 50 THEN 'Micro (<=$50)'
            WHEN transaction_amount <= 100 THEN 'Very Small ($50-100)'
            WHEN transaction_amount <= 500 THEN 'Small ($100-500)'
            WHEN transaction_amount <= 1000 THEN 'Medium ($500-1K)'
            WHEN transaction_amount <= 5000 THEN 'Large ($1K-5K)'
            ELSE 'Very Large (>$5K)'
        END AS amount_category,
        
        -- ===== MỚI: Khung giờ cho Heatmap =====
        CASE 
            WHEN CAST((transaction_dt % 86400) / 3600 AS INT) BETWEEN 0 AND 5 THEN 'Night (00-05)'
            WHEN CAST((transaction_dt % 86400) / 3600 AS INT) BETWEEN 6 AND 11 THEN 'Morning (06-11)'
            WHEN CAST((transaction_dt % 86400) / 3600 AS INT) BETWEEN 12 AND 17 THEN 'Afternoon (12-17)'
            ELSE 'Evening (18-23)'
        END AS time_period,
        
        -- Email domain có khớp không
        CASE 
            WHEN purchaser_email_domain = recipient_email_domain THEN 1 
            ELSE 0 
        END AS email_domain_match,
        
        -- Timestamp xử lý dbt
        CURRENT_TIMESTAMP() AS _dbt_transformed_at,
        '{{ invocation_id }}' AS _dbt_run_id
        
    FROM cleaned_data
)

SELECT * FROM enriched_data
