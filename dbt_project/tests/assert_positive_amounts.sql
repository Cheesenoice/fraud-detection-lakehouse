-- =============================================================================
-- TEST: Transaction amount phải dương
-- =============================================================================
-- Tất cả giao dịch phải có số tiền > 0
-- =============================================================================

SELECT
    TransactionID,
    transaction_amount
FROM {{ ref('silver_transactions') }}
WHERE transaction_amount <= 0
