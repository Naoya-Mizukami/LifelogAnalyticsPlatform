/*■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

	03_03_INSERT_LLAP_STG_MART_WEIGHT.sql

	2026.02.02	Created

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■*/
-- Daily
INSERT INTO llap_mart.mart_weight_daily (
	ymd,
	avg_weight_kg,
	rows_count,
	refreshed_at
)
SELECT
	p1.measure_date AS ymd,
	AVG(p1.weight_kg) AS avg_weight_kg,
	COUNT(p1.weight_kg) AS rows_count,
	CURRENT_TIMESTAMP AS refreshed_at
FROM llap_stg.stg_weight p1
GROUP BY p1.measure_date
ON CONFLICT (ymd) DO UPDATE
SET
	avg_weight_kg = EXCLUDED.avg_weight_kg,
	rows_count    = EXCLUDED.rows_count,
	refreshed_at  = CURRENT_TIMESTAMP;


-- Weekly
INSERT INTO llap_mart.mart_weight_weekly (
	week_start,
	avg_weight_kg,
	rows_count,
	refreshed_at
)
SELECT
	p1.measure_week_start AS week_start,
	AVG(p1.weight_kg) AS avg_weight_kg,
	COUNT(p1.weight_kg) AS rows_count,
	CURRENT_TIMESTAMP AS refreshed_at
FROM llap_stg.stg_weight p1
GROUP BY p1.measure_week_start
ON CONFLICT (week_start) DO UPDATE
SET
	avg_weight_kg = EXCLUDED.avg_weight_kg,
	rows_count    = EXCLUDED.rows_count,
	refreshed_at  = CURRENT_TIMESTAMP;


-- Monthly
INSERT INTO llap_mart.mart_weight_monthly (
	month_start,
	avg_weight_kg,
	rows_count,
	refreshed_at
)
SELECT
	p1.measure_month_start AS month_start,
	AVG(p1.weight_kg) AS avg_weight_kg,
	COUNT(p1.weight_kg) AS rows_count,
	CURRENT_TIMESTAMP AS refreshed_at
FROM llap_stg.stg_weight p1
GROUP BY p1.measure_month_start
ON CONFLICT (month_start) DO UPDATE
SET
	avg_weight_kg = EXCLUDED.avg_weight_kg,
	rows_count    = EXCLUDED.rows_count,
	refreshed_at  = CURRENT_TIMESTAMP;
