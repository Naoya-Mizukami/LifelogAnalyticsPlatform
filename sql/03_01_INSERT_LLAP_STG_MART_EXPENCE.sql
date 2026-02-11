/*■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

	03_01_INSERT_LLAP_STG_MART_EXPENSE.sql

	2026.02.02	Created

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■*/
-- Daily
INSERT INTO llap_mart.mart_expense_daily (
	ymd,
	total_amount_yen,
	rows_count,
	refreshed_at
)
SELECT
	p1.usage_date AS ymd,
	SUM(p1.amount_yen) AS total_amount_yen,
	COUNT(p1.amount_yen) AS rows_count,
	CURRENT_TIMESTAMP AS refreshed_at
FROM llap_stg.stg_expense p1
GROUP BY p1.usage_date
ON CONFLICT (ymd) DO UPDATE
SET
	total_amount_yen = EXCLUDED.total_amount_yen,
	rows_count    = EXCLUDED.rows_count,
	refreshed_at  = CURRENT_TIMESTAMP;


-- Weekly
INSERT INTO llap_mart.mart_expense_weekly (
	week_start,
	total_amount_yen,
	rows_count,
	refreshed_at
)
SELECT
	p1.usage_week_start AS week_start,
	SUM(p1.amount_yen) AS total_amount_yen,
	COUNT(p1.amount_yen) AS rows_count,
	CURRENT_TIMESTAMP AS refreshed_at
FROM llap_stg.stg_expense p1
GROUP BY p1.usage_week_start
ON CONFLICT (week_start) DO UPDATE
SET
	total_amount_yen = EXCLUDED.total_amount_yen,
	rows_count    = EXCLUDED.rows_count,
	refreshed_at  = CURRENT_TIMESTAMP;


-- Monthly
INSERT INTO llap_mart.mart_expense_monthly (
	month_start,
	total_amount_yen,
	rows_count,
	refreshed_at
)
SELECT
	p1.usage_month_start AS month_start,
	SUM(p1.amount_yen) AS total_amount_yen,
	COUNT(p1.amount_yen) AS rows_count,
	CURRENT_TIMESTAMP AS refreshed_at
FROM llap_stg.stg_expense p1
GROUP BY p1.usage_month_start
ON CONFLICT (month_start) DO UPDATE
SET
	total_amount_yen = EXCLUDED.total_amount_yen,
	rows_count    = EXCLUDED.rows_count,
	refreshed_at  = CURRENT_TIMESTAMP;
