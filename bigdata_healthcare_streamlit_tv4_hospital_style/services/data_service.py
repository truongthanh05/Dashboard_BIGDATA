from __future__ import annotations

from pathlib import Path
import os
import pandas as pd
import json


CONDITION_MAP_PATH = Path(__file__).resolve().parent.parent / "condition_vi.json"

if CONDITION_MAP_PATH.exists():
    with open(CONDITION_MAP_PATH, "r", encoding="utf-8") as f:
        CONDITION_VI = json.load(f)
else:
    CONDITION_VI = {}
    
DISPLAY_MAPS = {
    "gender": {
        "M": "Nam",
        "F": "Nữ",
    },

    "race": {
        "white": "Da trắng",
        "black": "Da đen",
        "asian": "Châu Á",
        "hawaiian": "Người Hawaii",
        "native": "Người bản địa",
        "other": "Khác",
    },

    "ethnicity": {
        "nonhispanic": "Không phải Hispanic",
        "hispanic": "Hispanic",
    },

    "encounter_class": {
        "ambulatory": "Khám lưu động",
        "emergency": "Cấp cứu",
        "home": "Chăm sóc tại nhà",
        "hospice": "Chăm sóc cuối đời",
        "inpatient": "Nội trú",
        "outpatient": "Ngoại trú",
        "snf": "Cơ sở điều dưỡng",
        "urgentcare": "Chăm sóc khẩn cấp",
        "virtual": "Khám trực tuyến",
        "wellness": "Khám định kỳ",
    },

    "payer": {
        "Aetna": "Aetna",
        "Anthem": "Anthem",
        "Blue Cross Blue Shield": "Blue Cross Blue Shield",
        "Cigna Health": "Cigna Health",
        "Dual Eligible": "Đủ điều kiện kép Medicare và Medicaid",
        "Humana": "Humana",
        "Medicaid": "Medicaid",
        "Medicare": "Medicare",
        "NO_INSURANCE": "Không có bảo hiểm",
        "UnitedHealthcare": "UnitedHealthcare",
    },

    "condition": CONDITION_VI,
}
FILTER_LABELS = {"encounter_class": "Loại lượt khám", "age_group": "Nhóm tuổi", "payer": "Bảo hiểm / đơn vị chi trả"}

def age_group(age: int | float) -> str:
    age = int(age)
    if age <= 17: return "0–17"
    if age <= 34: return "18–34"
    if age <= 49: return "35–49"
    if age <= 64: return "50–64"
    return "65+"

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={c: str(c).strip().lower() for c in df.columns})
    aliases = {"id": "encounter_id", "encounterclass": "encounter_class", "reasondescription": "condition"}
    for src, dst in aliases.items():
        if src in df.columns and dst not in df.columns: df = df.rename(columns={src: dst})
    required = ["encounter_id", "age", "gender", "race", "ethnicity", "encounter_class", "payer", "condition", "total_claim_cost"]
    missing = [x for x in required if x not in df.columns]
    if missing: raise ValueError(f"Thiếu cột dashboard: {missing}")
    df = df[required].copy()
    df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(0).astype(int)
    df["total_claim_cost"] = pd.to_numeric(df["total_claim_cost"], errors="coerce").fillna(0.0)
    for c in ["gender", "race", "ethnicity", "encounter_class", "payer", "condition"]: df[c] = df[c].fillna("UNKNOWN").astype(str)
    return df

# def _find_real_gold(base_dir: Path):
#     configured = os.getenv("GOLD_DATA_DIR")
#     candidates = [Path(configured)] if configured else []
#     candidates += [base_dir / "artifacts" / "handoff" / "encounter_features", base_dir.parent / "artifacts" / "handoff" / "encounter_features", Path(r"C:\Users\truon\OneDrive\Documents\bigdata\model\handoff\encounter_features")]
#     for folder in candidates:
#         if folder.is_dir():
#             files = sorted(folder.glob("part-*.parquet"))
#             if files: return folder, files
#     return None, []
def _find_real_gold(base_dir: Path):
    folder = base_dir.parent.parent / "model" / "encounter_features_v2"

    if not folder.exists():
        raise FileNotFoundError(
            f"Không tìm thấy Gold V2 tại: {folder}"
        )

    parquet_files = sorted(folder.glob("*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(
            f"Không tìm thấy file Parquet trong: {folder}"
        )

    return folder

# def load_dashboard_data(base_dir: Path):
#     folder, parquet_files = _find_real_gold(base_dir)
#     if parquet_files:
#         try: return _normalize_columns(pd.concat([pd.read_parquet(file) for file in parquet_files], ignore_index=True)), "real", str(folder)
#         except Exception as exc: raise RuntimeError(f"Không thể đọc dữ liệu Gold encounter_features tại {folder}: {exc}") from exc
#     if os.getenv("ALLOW_DEMO_DATA", "false").lower() == "true":
#         demo_path = base_dir / "mock_data" / "encounter_features_demo.csv"
#         return _normalize_columns(pd.read_csv(demo_path)), "demo", "Dữ liệu demo tích hợp trong dashboard"
#     raise FileNotFoundError("Không tìm thấy dữ liệu Gold encounter_features.")
def load_dashboard_data(base_dir: Path):
    real_folder = _find_real_gold(base_dir)

    parquet_files = sorted(real_folder.glob("*.parquet"))

    df = pd.concat(
        [pd.read_parquet(file) for file in parquet_files],
        ignore_index=True
    )

    return _normalize_columns(df), "real", str(real_folder)

def apply_filters(df: pd.DataFrame, encounter_class=None, selected_age_group=None, payer=None):
    out = df
    if encounter_class: out = out[out["encounter_class"] == encounter_class]
    if selected_age_group and selected_age_group != "Tất cả": out = out[out["age"].apply(age_group) == selected_age_group]
    if payer: out = out[out["payer"] == payer]
    return out
