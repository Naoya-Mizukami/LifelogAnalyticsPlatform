/*■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

	01_INSERT_LLAP_HISTORY.sql

	2026.02.02	Created

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■*/

-- 履歴テーブルへの登録
INSERT INTO llap_history.input_files_history (
	file_hash,
	source_file_name,
	category,
	method
) VALUES %s
ON CONFLICT (file_hash) DO NOTHING;
