-- =============================================================================
-- CUSTOM SCHEMA NAME GENERATOR
-- =============================================================================
-- Mục đích: Override hành vi mặc định của dbt để tạo schema riêng biệt
-- 
-- Mặc định dbt ghép: {{ target_schema }}_{{ custom_schema_name }}
-- Ví dụ: bronze + silver = bronze_silver (SAI)
-- 
-- Macro này sửa lại: Nếu có custom_schema_name, dùng đúng tên đó
-- Ví dụ: schema='silver' → tạo namespace "silver" (ĐÚNG)
-- =============================================================================

{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
