import csv
import hashlib
import psycopg2 as pc
from psycopg2.extras import execute_values
from pathlib import Path



config = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'llap',
    'user': 'postgres',
    'password': 'postgres'
}



llap_dir = Path(__file__).resolve().parents[1]
input_dir = llap_dir.joinpath("data", "input")
crd_dir = input_dir.joinpath("card")
std_dir = input_dir.joinpath("study")
wgt_dir = input_dir.joinpath("weight")
sql_dir = llap_dir.joinpath("sql")

# 履歴テーブルへのINSERT SQL
SQL_HISTORY = sql_dir.joinpath("01_INSERT_LLAP_HISTORY.sql")

# csvからrawへのロードSQL
SQL_RAW_EXPENSE = sql_dir.joinpath("02_01_INSERT_LLAP_CSV_RAW_EXPENSE.sql")
SQL_RAW_STUDY = sql_dir.joinpath("02_02_INSERT_LLAP_CSV_RAW_STUDY.sql")
SQL_RAW_WEIGHT = sql_dir.joinpath("02_03_INSERT_LLAP_CSV_RAW_WEIGHT.sql")

RAW_JOBS = [
    ("card", SQL_RAW_EXPENSE, crd_dir),
    ("study", SQL_RAW_STUDY,   std_dir),
    ("weight", SQL_RAW_WEIGHT,  wgt_dir),
]

MEISAI_HEADER = ["ご利用者","カテゴリ","ご利用日","ご利用先など","ご利用金額(￥)","支払区分","今回回数","訂正サイン","お支払い金額(￥)","国内／海外","摘要","備考"]

# stg/mart へのINSERT SQL
SQL_MART_EXPENSE = sql_dir.joinpath("03_01_INSERT_LLAP_STG_MART_EXPENSE.sql")
SQL_MART_STUDY = sql_dir.joinpath("03_02_INSERT_LLAP_STG_MART_STUDY.sql")
SQL_MART_WEIGHT = sql_dir.joinpath("03_03_INSERT_LLAP_STG_MART_WEIGHT.sql")

MART_JOBS = [SQL_MART_EXPENSE, SQL_MART_STUDY, SQL_MART_WEIGHT]



def read_sql(sql_path: Path) -> str:
    # SQLファイルを読み込み、文字列で返す。
    return sql_path.read_text(encoding="utf-8")

def replace_values(csv_path: Path, category: str, encoding: str = "utf-8"):
    # csvファイルを読み込み、バインド変数用のタプルリストを返す。
    records = []

    with csv_path.open("r", encoding=encoding, newline="") as f:
        reader = csv.reader(f)

        if category == "card":
            record_flag = False
            cols_cnt = len(MEISAI_HEADER)

            for row in reader:
                if not row:
                    continue
                if row == MEISAI_HEADER:
                    record_flag = True
                    continue
                if not record_flag:
                    continue
                if len(row) != cols_cnt:
                    continue
                records.append(tuple(row))
        else:
            next(reader, None)  # ← ヘッダ1行スキップ
            for row in reader:
                if not row:
                    continue
                records.append(tuple(row))
    
    return records

def sha256_file(csv_path: Path, chunk_size: int = 1024 * 1024) -> str:
    # ファイルの中身からSHA256ハッシュ値を計算して返す。
    h = hashlib.sha256()
    with csv_path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def collect_input_files(raw_jobs) -> list[tuple[str,str,str,str]]:
    method = "import.py"
    rows = []
    for category, _, data_dir in raw_jobs:
        for csv_path in sorted(data_dir.glob("*.csv")):
            rows.append((sha256_file(csv_path), csv_path.name, category, method))
    return rows


def main():
    rows = collect_input_files(RAW_JOBS)

    if not rows:
        print("No csv files found.")
        return

    try:
        with pc.connect(**config) as conn:
            with conn.cursor() as cur:
                # 1) 履歴INSERT
                print("Inserting llap_history...")
                sql_hist = read_sql(SQL_HISTORY)
                execute_values(cur, sql_hist, rows, page_size=500)

                # 2) rawロード
                print("Inserting llap_csv_raw_...")
                for category, sql_path, data_dir in RAW_JOBS:
                    print(f" Processing category: {category} ...")
                    sql_csv_raw = read_sql(sql_path)
                    all_records = []

                    for csv_path in sorted(data_dir.glob("*.csv")):
                        print(f"  Loading file: {csv_path.name} ...")
                        records = replace_values(csv_path, category)
                        if records:
                            print(f"  Inserting {len(records)} records from {csv_path.name} ...")
                            execute_values(cur, sql_csv_raw, records, page_size=500)

                    if all_records:  # 空なら実行しない
                        print(f"  Inserting {len(all_records)} records into raw table...")
                        execute_values(cur, sql_csv_raw, all_records, page_size=500)

                # 3) stg/mart（例）
                for sql_path in MART_JOBS:
                    print(f"Inserting into stg/mart table using {sql_path.name} ...")
                    cur.execute(read_sql(sql_path))

    except pc.Error as e:
        print(f"DB Error: {e}")

    
if __name__ == "__main__":
    main()
