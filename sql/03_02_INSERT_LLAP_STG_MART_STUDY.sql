/*■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

	03_02_INSERT_LLAP_STG_MART_STUDY.sql

	2026.02.02	Created

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■*/
-- Daily
INSERT INTO llap_mart.mart_study_daily (
	ymd,
	total_minutes,
	rows_count,
	refreshed_at
)
SELECT
	p1.study_date AS ymd,
	SUM(p1.study_minutes) AS total_minutes,
	COUNT(p1.study_minutes) AS rows_count,
	CURRENT_TIMESTAMP AS refreshed_at
FROM llap_stg.stg_study p1
GROUP BY p1.study_date
ON CONFLICT (ymd) DO UPDATE
SET
	total_minutes = EXCLUDED.total_minutes,
	rows_count    = EXCLUDED.rows_count,
	refreshed_at  = CURRENT_TIMESTAMP;


-- Weekly
INSERT INTO llap_mart.mart_study_weekly (
	week_start,
	total_minutes,
	rows_count,
	refreshed_at
)
SELECT
	p1.study_week_start AS week_start,
	SUM(p1.study_minutes) AS total_minutes,
	COUNT(p1.study_minutes) AS rows_count,
	CURRENT_TIMESTAMP AS refreshed_at
FROM llap_stg.stg_study p1
GROUP BY p1.study_week_start
ON CONFLICT (week_start) DO UPDATE
SET
	total_minutes = EXCLUDED.total_minutes,
	rows_count    = EXCLUDED.rows_count,
	refreshed_at  = CURRENT_TIMESTAMP;


-- Monthly
INSERT INTO llap_mart.mart_study_monthly (
	month_start,
	total_minutes,
	rows_count,
	refreshed_at
)
SELECT
	p1.study_month_start AS month_start,
	SUM(p1.study_minutes) AS total_minutes,
	COUNT(p1.study_minutes) AS rows_count,
	CURRENT_TIMESTAMP AS refreshed_at
FROM llap_stg.stg_study p1
GROUP BY p1.study_month_start
ON CONFLICT (month_start) DO UPDATE
SET
	total_minutes = EXCLUDED.total_minutes,
	rows_count    = EXCLUDED.rows_count,
	refreshed_at  = CURRENT_TIMESTAMP;
