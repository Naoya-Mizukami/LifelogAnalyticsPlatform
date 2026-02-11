## リポジトリ構成
```graphql
lifelog-analytics-platform/
├ README.md
├ design.md
├ diagrams.md
├ docker-compose.yml
├ .env.example
├ .gitignore
│
├ scripts/
│  ├ run_all.py
│  ├ load_raw.py
│  └ run_sql.py
│
├ sql/
│  ├ 00_core_tables.sql
│  ├ 10_stg.sql
│  └ 20_mart.sql
│
└ data/
   ├ input/
   │  ├ card/      # クレカCSVを置く
   │  ├ study/     # 学習CSVを置く
   │  └ weight/    # 体重CSVを置く
   └ output/       # （任意）集計結果をCSVで出したい時用
```

---

## 2.1 アーキテクチャ設計
### 全体処理フロー
```mermaid
 flowchart TD
  %% LifeLog Analytics Platform - Architecture

  U[利用者] -->|CSVを配置| IN[入力フォルダ<br/>data/input/]

  subgraph BATCH[Pythonバッチ（コマンド1つで一括実行）]
    LOAD[① 取り込み（Load）<br/>CSV読込・検証]
    TRANSFORM[② 変換（Transform）<br/>SQL実行（stg/mart作成）]
  end

  IN --> LOAD

  subgraph DB[PostgreSQL]
    subgraph RAW[raw層（生データ保管）]
      R_CARD[(raw_card_statement)]
      R_STUDY[(raw_study_log)]
      R_WEIGHT[(raw_weight)]
    end

    subgraph STG[stg層（正規化・中間テーブル）]
      S_EXP[(stg_expense)]
      S_STUDY[(stg_study)]
      S_WEIGHT[(stg_weight)]
    end

    subgraph MART[mart層（分析用データマート）]
      M_DAILY[(mart_life_daily)]
      M_WK[(mart_life_weekly)]
      M_MO[(mart_life_monthly)]
      M_CAT[(mart_category_summary<br/>※拡張：余裕があれば)]
    end
  end

  LOAD -->|INSERT| R_CARD
  LOAD -->|INSERT| R_STUDY
  LOAD -->|INSERT| R_WEIGHT

  LOAD -->|成功時のみ| TRANSFORM

  TRANSFORM -->|raw→stg| S_EXP
  TRANSFORM -->|raw→stg| S_STUDY
  TRANSFORM -->|raw→stg| S_WEIGHT

  TRANSFORM -->|stg→mart| M_DAILY
  TRANSFORM -->|stg→mart| M_WK
  TRANSFORM -->|stg→mart| M_MO
  TRANSFORM -.->|カテゴリマスタ導入時| M_CAT

  %% Non-functional behavior annotations
  LOAD -.->|不正データ検知| RB[ロールバック<br/>（処理中断・修正を促す）]
  LOAD --> LOG[ログ出力<br/>ファイル名・読み込み行数・登録件数・エラー内容]
  TRANSFORM --> LOG
```

### 依存関係図
```mermaid
  flowchart LR
  %% =========================
  %% Schemas
  %% =========================
  subgraph RAW["llap_raw (raw schema)"]
    RAW_CARD["raw_card_statement<br/>(PK: id)"]
    RAW_STUDY["raw_study_log<br/>(PK: id)"]
    RAW_WEIGHT["raw_weight<br/>(PK: id)"]
  end

  subgraph STG["llap_stg (stg schema) : views"]
    STG_EXP["stg_expense (VIEW)<br/>from raw_card_statement"]
    STG_STUDY["stg_study (VIEW)<br/>from raw_study_log"]
    STG_WEIGHT["stg_weight (VIEW)<br/>from raw_weight"]
  end

  subgraph MART["llap_mart (mart schema) : tables"]
    %% Expense marts
    M_E_D["mart_expense_daily<br/>(PK: ymd)"]
    M_E_W["mart_expense_weekly<br/>(PK: week_start)"]
    M_E_M["mart_expense_monthly<br/>(PK: month_start)"]

    %% Study marts
    M_S_D["mart_study_daily<br/>(PK: ymd)"]
    M_S_W["mart_study_weekly<br/>(PK: week_start)"]
    M_S_M["mart_study_monthly<br/>(PK: month_start)"]

    %% Weight marts
    M_W_D["mart_weight_daily<br/>(PK: ymd)"]
    M_W_W["mart_weight_weekly<br/>(PK: week_start)"]
    M_W_M["mart_weight_monthly<br/>(PK: month_start)"]
  end

  subgraph HIST["llap_history (history schema)"]
    HIST_FILES["input_files_history<br/>(PK: id)<br/>UQ: (file_hash, source_file_name)"]
  end

  %% =========================
  %% Dependencies (Lineage)
  %% =========================
  RAW_CARD --> STG_EXP
  RAW_STUDY --> STG_STUDY
  RAW_WEIGHT --> STG_WEIGHT

  STG_EXP --> M_E_D
  STG_EXP --> M_E_W
  STG_EXP --> M_E_M

  STG_STUDY --> M_S_D
  STG_STUDY --> M_S_W
  STG_STUDY --> M_S_M

  STG_WEIGHT --> M_W_D
  STG_WEIGHT --> M_W_W
  STG_WEIGHT --> M_W_M

  %% History (logical relationship)
  HIST_FILES -. "tracks ingested files<br/>(logical link via file_hash / source_file_name)" .-> RAW_CARD
  HIST_FILES -. "tracks ingested files<br/>(logical link via file_hash / source_file_name)" .-> RAW_STUDY
  HIST_FILES -. "tracks ingested files<br/>(logical link via file_hash / source_file_name)" .-> RAW_WEIGHT
```

---


## 2.3 バッチ設計（処理構成・実行フロー）
```mermaid
  flowchart TD
  %% Batch Execution Flow (run_all)

  A[run_all 開始] --> B[入力フォルダ走査<br/>card / study / weight]
  B --> C{対象CSVはある？}

  C -- ない --> Z[終了<br/>処理対象なしをログ出力]

  C -- ある --> D[raw取り込み開始ログ<br/>（処理対象ファイル一覧）]
  D --> E[DBトランザクション開始]

  E --> F[ファイルごとに処理（ループ）]
  F --> G[CSV読み込み]
  G --> H[行ごとに検証<br/>（日付形式・金額形式など）]

  H --> I{不正データあり？}

  I -- はい --> J[エラーログ出力<br/>（ファイル名・行番号・不正内容）]
  J --> K[ロールバック]
  K --> L[処理中断<br/>stg/martは実行しない]
  L --> END_FAIL[run_all 終了（失敗）]

  I -- いいえ --> M[rawへ登録（INSERT/UPSERT）]
  M --> N[件数ログ出力<br/>（読み込み行数・登録件数）]
  N --> O{次のファイルはある？}
  O -- はい --> F
  O -- いいえ --> P[コミット]
  P --> Q[stg作成SQL実行<br/>（raw → stg）]
  Q --> R{stgでエラー？}

  R -- はい --> R1[エラーログ出力]
  R1 --> END_FAIL2[run_all 終了（失敗）]

  R -- いいえ --> S[mart作成SQL実行<br/>（stg → mart）]
  S --> T{martでエラー？}

  T -- はい --> T1[エラーログ出力]
  T1 --> END_FAIL3[run_all 終了（失敗）]

  T -- いいえ --> U[完了ログ出力]
  U --> END_OK[run_all 終了（成功）]
```

