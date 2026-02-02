-- =============================================================================
-- SILVER IDENTITY - DBT MODEL  
-- =============================================================================
-- Mô tả: Làm sạch và chuẩn hóa dữ liệu định danh từ Bronze Layer
-- Source: demo.bronze.identity
-- Target: demo.silver.identity
-- =============================================================================

{{ config(
    materialized='table',
    schema='silver',
    description='Bảng định danh đã làm sạch từ Bronze Layer'
) }}

WITH source_data AS (
    -- Đọc dữ liệu từ Bronze Layer
    SELECT * FROM {{ source('bronze', 'identity') }}
),

cleaned_data AS (
    SELECT
        -- ===== ID =====
        TransactionID,
        
        -- ===== Device Info =====
        COALESCE(DeviceType, 'unknown') AS device_type,
        COALESCE(DeviceInfo, 'unknown') AS device_info,
        
        -- ===== Identity columns (id_01 - id_38) =====
        CAST(id_01 AS DOUBLE) AS id_01,
        CAST(id_02 AS DOUBLE) AS id_02,
        CAST(id_03 AS DOUBLE) AS id_03,
        CAST(id_04 AS DOUBLE) AS id_04,
        CAST(id_05 AS DOUBLE) AS id_05,
        CAST(id_06 AS DOUBLE) AS id_06,
        CAST(id_07 AS STRING) AS id_07,
        CAST(id_08 AS STRING) AS id_08,
        CAST(id_09 AS STRING) AS id_09,
        CAST(id_10 AS STRING) AS id_10,
        CAST(id_11 AS DOUBLE) AS id_11,
        CAST(id_12 AS STRING) AS id_12,
        CAST(id_13 AS DOUBLE) AS id_13,
        CAST(id_14 AS DOUBLE) AS id_14,
        CAST(id_15 AS STRING) AS id_15,
        CAST(id_16 AS STRING) AS id_16,
        CAST(id_17 AS DOUBLE) AS id_17,
        CAST(id_18 AS DOUBLE) AS id_18,
        CAST(id_19 AS DOUBLE) AS id_19,
        CAST(id_20 AS DOUBLE) AS id_20,
        
        -- ===== Metadata từ Bronze =====
        _ingestion_time,
        _source_file
        
    FROM source_data
    WHERE TransactionID IS NOT NULL
),

enriched_data AS (
    SELECT
        *,
        -- ===== Phân loại thiết bị =====
        CASE 
            WHEN LOWER(device_type) LIKE '%mobile%' THEN 'mobile'
            WHEN LOWER(device_type) LIKE '%desktop%' THEN 'desktop'
            WHEN LOWER(device_type) LIKE '%tablet%' THEN 'tablet'
            ELSE 'other'
        END AS device_category,
        
        -- ===== Trích xuất hệ điều hành từ DeviceInfo =====
        CASE
            WHEN LOWER(device_info) LIKE '%windows%' THEN 'windows'
            WHEN LOWER(device_info) LIKE '%ios%' OR LOWER(device_info) LIKE '%iphone%' THEN 'ios'
            WHEN LOWER(device_info) LIKE '%android%' THEN 'android'
            WHEN LOWER(device_info) LIKE '%mac%' THEN 'macos'
            WHEN LOWER(device_info) LIKE '%linux%' THEN 'linux'
            ELSE 'other'
        END AS operating_system,
        
        -- Timestamp xử lý dbt
        CURRENT_TIMESTAMP() AS _dbt_transformed_at,
        '{{ invocation_id }}' AS _dbt_run_id
        
    FROM cleaned_data
)

SELECT * FROM enriched_data
