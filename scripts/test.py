from pathlib import Path

path = Path(__file__).resolve().parents[1].joinpath("data", "input", "card", "202602meisai.csv")

text = path.read_text(encoding="utf-8")

text_replace = text.replace("2025", "9999")

print(text_replace)