import csv
import hashlib
from pathlib import Path
import psycopg2 as pc
from psycopg2.extras import execute_values


# =========================
# DB Config
# =========================
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "llap",
    "user": "postgres",
    "password": "postgres",
}

# =========================
# CONSTANTS
# =========================
LLAP_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = LLAP_DIR / "data" / "input"
SQL_DIR = LLAP_DIR / "sql"
CATEGORIES = ["card", "study", "weight"]

DIR_BY_CAT = [INPUT_DIR / category for category in CATEGORIES]

SQL_HISTORY = SQL_DIR / "01_INSERT_LLAP_HISTORY.sql"

SQL_RAW_BY_CAT = {
    "card": SQL_DIR / "02_01_INSERT_LLAP_CSV_RAW_EXPENSE.sql",
    "study": SQL_DIR / "02_02_INSERT_LLAP_CSV_RAW_STUDY.sql",
    "weight": SQL_DIR / "02_03_INSERT_LLAP_CSV_RAW_WEIGHT.sql"
}

MEISAI_HEADER = [
    "ご利用者", "カテゴリ", "ご利用日", "ご利用先など", "ご利用金額(￥)",
    "支払区分", "今回回数", "訂正サイン", "お支払い金額(￥)",
    "国内／海外", "摘要", "備考"
]

IMPORT_METHOD = "import.py"

# =========================
# Helpers
# =========================
def read_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def collect_unique_files_by_hash() -> list[dict]:
    by_hash: dict[str, dict] = {}

    for data_dir in DIR_BY_CAT:
        if not data_dir.exists():
            continue

        for csv_path in sorted(data_dir.glob("*.csv")):
            file_hash = sha256_file(csv_path)
            by_hash.setdefault(
                file_hash,
                {
                    "category": data_dir.name,
                    "path": csv_path,
                    "file_hash": file_hash,
                    "file_name": csv_path.name
                },
            )

    return list(by_hash.values())


def build_raw_records(file_info: dict) -> list[tuple]:
    rows: list[tuple] = []
    category_name = file_info["category"]
    csv_path: Path = file_info["path"]
    file_hash = file_info["file_hash"]
    file_name = file_info["file_name"]

    with csv_path.open("r", encoding="utf-8", newline="") as file_obj:
        reader = csv.reader(file_obj)

        if category_name == "card":
            record_flag = False
            column_count = len(MEISAI_HEADER)

            for row_values in reader:
                if not row_values:
                    continue
                if row_values == MEISAI_HEADER:
                    record_flag = True
                    continue
                if not record_flag:
                    continue
                if len(row_values) != column_count:
                    continue

                rows.append((file_hash, file_name, *row_values))

        else:
            next(reader, None)
            for row_values in reader:
                if not row_values:
                    continue
                rows.append((file_hash, file_name, *row_values))

    return rows


# =========================
# Main
# =========================
def main() -> None:
    files = collect_unique_files_by_hash()
    if not files:
        print("No csv files found.")
        return

    # SQLファイルのロード
    sql_history = read_sql(SQL_HISTORY)
    sql_raw_by_cat = {category_name: read_sql(sql_path) for category_name, sql_path in SQL_RAW_BY_CAT.items()}

    # DB接続と処理
    with pc.connect(**DB_CONFIG) as conn:
        try:
            with conn.cursor() as cursor:
                print(f"Importing {len(files)} files...")
                history_rows = [
                    (file_info["file_hash"], file_info["file_name"], file_info["category"], IMPORT_METHOD)
                    for file_info in files
                ]
                execute_values(cursor, sql_history, history_rows, page_size=500)

                inserted_hashes = {row[0] for row in cursor.fetchall()}

                if not inserted_hashes:
                    print("No new files (by file_hash). Nothing to do.")
                    conn.commit()
                    return

                print(f"Inserting raw data for {len(inserted_hashes)} new files...")
                for file_info in files:
                    if not file_info["file_hash"] in inserted_hashes:
                        print(f"  Skipping (already imported): {file_info['path'].name}")
                        continue

                    category_name = file_info["category"]
                    records: list[tuple] = []
                    records.extend(build_raw_records(file_info))

                    if records:
                        print(f"  Inserting raw data from: {file_info['path'].name} ({len(records)} rows)")
                        execute_values(cursor, sql_raw_by_cat[category_name], records, page_size=500)

            conn.commit()
            print(f"Done. new file_hash count = {len(inserted_hashes)}")

        except Exception:
            print("Error occurred. Rolling back...")
            conn.rollback()
            raise


if __name__ == "__main__":
    main()
