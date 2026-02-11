/*■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

	02_01_INSERT_LLAP_CSV_RAW_EXPENSE.sql

	2026.01.31	Created

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■*/

-- カード明細情報を投入
INSERT INTO llap_raw.raw_card_statement (
	file_hash,
	source_file_name,
	user_name,
	category,
	usage_date,
	merchant,
	usage_amount,
	payment_type,
	payment_times,
	correction_sign,
	payment_amount,
	domestic_overseas,
	summary,
	note
) VALUES %s
;
