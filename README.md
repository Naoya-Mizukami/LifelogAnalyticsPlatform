# LifeLog Analytics Platform

## 概要
生活ログを対象としたデータ分析基盤です。

## 構成
CSV → Python → PostgreSQL（raw / stg / mart）

## 使い方（運用手順）

1. DB起動
   docker compose up -d

2. CSVを配置
   data/input/card/   にクレカ明細CSVを置く
   data/input/study/  に学習ログCSVを置く
   data/input/weight/ に体重ログCSVを置く

3. 一括実行
   python scripts/run_all.py
