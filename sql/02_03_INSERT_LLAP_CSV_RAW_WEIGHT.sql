/*■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

	02_03_INSERT_LLAP_CSV_RAW_WEIGHT.sql

	2026.01.31	Created

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■*/

-- 体重情報を投入
INSERT INTO llap_raw.raw_weight (
	file_hash,
	source_file_name,
	measure_date,
	weight_kg,
	description
) VALUES %s
;
