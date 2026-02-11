/*■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

	02_02_INSERT_LLAP_CSV_RAW_STUDY.sql

	2026.01.31	Created

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■*/

-- 勉強情報を投入
INSERT INTO llap_raw.raw_study_log (
	file_hash,
	source_file_name,
	study_date,
	category,
	content,
	study_minutes,
	description
) VALUES %s
;
