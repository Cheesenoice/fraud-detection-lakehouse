-- =============================================================================
-- TEST: Fraud Rate không vượt quá 50%
-- =============================================================================
-- Đây là sanity check - nếu fraud rate > 50% thì có vấn đề với data
-- =============================================================================

SELECT
    card_brand,
    card_category,
    fraud_rate_pct
FROM {{ ref('fraud_by_card_type') }}
WHERE fraud_rate_pct > 50
