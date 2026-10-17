from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

from services.data_service import (
    DISPLAY_MAPS,
    FILTER_LABELS,
    load_dashboard_data,
    apply_filters,
    age_group,
)
from services.api_service import check_api_health, predict_cost

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Bảng điều khiển y tế",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# CSS — bám sát dashboard mẫu người dùng cung cấp
# -----------------------------
st.markdown(
    """
<style>
:root {
    --bg: #f6f7f8;
    --surface: #ffffff;
    --border: #e5e8eb;
    --text: #3f4347;
    --muted: #7d848b;
    --blue: #3d8fd1;
    --teal: #2fb0a1;
    --danger: #d85c5c;
    --success: #29956d;
    --table-head: #dcecf7;
}

html, body, [class*="css"] {
    font-family: "Segoe UI", Inter, Arial, sans-serif;
    color: var(--text);
}

.stApp { background: var(--bg); }

.block-container {
    max-width: 1480px;
    padding-top: 0.6rem;
    padding-bottom: 2rem;
    padding-left: 0.7rem;
    padding-right: 0.7rem;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* Header */
.app-header {
    background: #fff;
    border: 1px solid #d9dde1;
    border-bottom: 0;
    border-radius: 6px 6px 0 0;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}
.app-title {
    font-size: 24px;
    font-weight: 500;
    line-height: 1.2;
    color: #404448;
}
.header-meta {
    color: #969ba0;
    font-size: 12px;
    display: flex;
    gap: 12px;
    align-items: center;
    white-space: nowrap;
}
.demo-badge {
    border: 1px solid #78c9be;
    color: #278f83;
    background: #effaf8;
    border-radius: 999px;
    padding: 4px 9px;
    font-size: 11px;
    font-weight: 600;
}
.online-dot, .offline-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
}
.online-dot { background: #2fb0a1; }
.offline-dot { background: #d9a544; }

/* Main dashboard shell */
.dashboard-shell {
    border-left: 1px solid #d9dde1;
    border-right: 1px solid #d9dde1;
    border-bottom: 1px solid #d9dde1;
    background: #f7f8f9;
    padding: 10px;
}

/* Card helpers */
.panel {
    background: var(--surface);
    border: 1px solid #eef0f2;
    border-radius: 3px;
    box-shadow: 0 1px 4px rgba(20, 36, 50, 0.025);
    padding: 13px 16px;
    height: 100%;
}
.panel-title {
    font-size: 15px;
    font-weight: 600;
    color: #43474b;
    margin-bottom: 8px;
}
.metric-card {
    background: #fff;
    border: 1px solid #eef0f2;
    min-height: 98px;
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}
.metric-label {
    font-size: 14px;
    color: #60656a;
    margin-bottom: 5px;
}
.metric-value {
    font-size: 28px;
    line-height: 1.15;
    color: #2f3337;
    font-weight: 500;
}
.metric-sub {
    font-size: 12px;
    color: #7d848b;
    margin-top: 4px;
}
.split-metric {
    background: #fff;
    border: 1px solid #eef0f2;
    min-height: 122px;
    padding: 13px 14px;
}
.split-label {
    font-size: 14px;
    color: #60656a;
    margin-bottom: 8px;
}
.split-row { display: flex; align-items: stretch; }
.split-item { flex: 1; text-align: center; }
.split-item + .split-item { border-left: 1px solid #e2e5e8; }
.split-value { font-size: 24px; font-weight: 500; color: #303438; }
.split-caption { font-size: 12px; color: #72787e; margin-top: 2px; }

/* Streamlit controls */
.stSelectbox label, .stNumberInput label {
    color: #3f4347 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}
[data-baseweb="select"] > div,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    border-radius: 2px !important;
    border-color: #d3d8dc !important;
    min-height: 34px !important;
    background: white !important;
}
[data-baseweb="select"] > div:focus-within,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #58a9df !important;
    box-shadow: 0 0 0 1px #58a9df !important;
}

.stButton > button {
    border-radius: 3px;
    border: 1px solid #2f8bc7;
    background: #3d8fd1;
    color: #fff;
    font-weight: 600;
    min-height: 38px;
}
.stButton > button:hover {
    background: #347fbb;
    border-color: #347fbb;
    color: #fff;
}

/* Prediction section */
.section-card {
    margin-top: 12px;
    background: #fff;
    border: 1px solid #dfe3e6;
    border-radius: 4px;
    padding: 18px 20px;
}
.section-title {
    font-size: 17px;
    font-weight: 600;
    margin-bottom: 2px;
}
.section-subtitle {
    font-size: 12px;
    color: #8b9298;
    margin-bottom: 10px;
}
.prediction-result {
    min-height: 150px;
    border: 1px solid #e3e7ea;
    background: #fbfcfc;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 20px;
}
.prediction-result .label { font-size: 13px; color: #747b81; }
.prediction-result .value { font-size: 34px; font-weight: 500; color: #2f3337; margin-top: 6px; }
.prediction-result .mode { font-size: 11px; color: #9aa0a5; margin-top: 4px; }

/* Table */
[data-testid="stDataFrame"] {
    border: 1px solid #e1e5e8;
    border-radius: 0;
}

/* Plotly */
[data-testid="stPlotlyChart"] { background: #fff; }

/* Tighten vertical spacing */
div[data-testid="stVerticalBlock"] { gap: 0.55rem; }
hr { border-color: #e7eaed !important; }

@media (max-width: 900px) {
    .app-header { align-items: flex-start; flex-direction: column; }
    .header-meta { white-space: normal; }
    .metric-value { font-size: 23px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
BLUE = "#3d8fd1"
TEAL = "#2fb0a1"
GRID = "#e7eaed"
TEXT = "#555b60"
FONT = "Segoe UI, Arial, sans-serif"


def plot_layout(height: int = 270, margin=None):
    return dict(
        height=height,
        margin=margin or dict(l=10, r=10, t=10, b=28),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=12, color=TEXT),
        showlegend=False,
        uniformtext=dict(minsize=10, mode="hide"),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family=FONT),
    )


def money(v: float) -> str:
    return f"${v:,.0f}"


def vi_encounter(value: str) -> str:
    return DISPLAY_MAPS["encounter_class"].get(value, value)


def vi_gender(value: str) -> str:
    return DISPLAY_MAPS["gender"].get(value, value)


def vi_payer(value: str) -> str:
    return DISPLAY_MAPS["payer"].get(value, value)

def vi_condition(value: str) -> str:
    vi = DISPLAY_MAPS["condition"].get(value)

    if vi:
        return f"{vi} | {value}"

    return value


# -----------------------------
# Data
# -----------------------------
@st.cache_data(show_spinner="Đang tải dữ liệu Gold...")
def load_cached_data(base_dir: str):
    return load_dashboard_data(Path(base_dir))


df, data_mode, source_label = load_cached_data(str(BASE_DIR))
api_base_url = os.getenv("API_BASE_URL", "http://localhost:5005")
api_online, api_health = check_api_health(api_base_url)
# model_name = "Linear Regression" if isinstance(api_health, dict) and api_health.get("best_model") == "linear_regression" else ""
if isinstance(api_health, dict):
    best_model = api_health.get("best_model", "")

    if best_model == "random_forest_log1p_deep":
        model_name = "Random Forest (log1p)"
    elif best_model == "linear_regression":
        model_name = "Linear Regression"
    else:
        model_name = best_model
else:
    model_name = ""

# Header
stamp = datetime.now().strftime("%d/%m/%Y %H:%M")
status_dot = "online-dot" if api_online else "offline-dot"
mode_badge = "Dữ liệu thật" if data_mode == "real" else "Dữ liệu demo"
st.markdown(
    f"""
    <div class="app-header">
      <div class="app-title">Bảng điều khiển phân tích y tế</div>
      <div class="header-meta">
        <span>Cập nhật: {stamp}</span>
        <span class="{status_dot}"></span>
        <span>{'API sẵn sàng' if api_online else 'API chưa kết nối'}</span>
        <span>{model_name}</span>
        <span class="demo-badge">{mode_badge}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Top filter row (visual proportions similar to reference)
filter_c1, filter_c2, filter_c3, filter_c4 = st.columns([1.15, 1.15, 1.15, 1.05], gap="small")

encounter_options = ["Tất cả"] + [vi_encounter(x) for x in sorted(df["encounter_class"].dropna().unique())]
reverse_encounter = {v: k for k, v in DISPLAY_MAPS["encounter_class"].items()}
with filter_c1:
    selected_encounter_vi = st.selectbox("Loại lượt khám", encounter_options, index=0)

age_options = ["Tất cả", "0–17", "18–34", "35–49", "50–64", "65+"]
with filter_c2:
    selected_age_group = st.selectbox("Nhóm tuổi", age_options, index=0)

payer_values = sorted(df["payer"].dropna().unique())
payer_options = ["Tất cả"] + [vi_payer(x) for x in payer_values]
reverse_payer = {vi_payer(x): x for x in payer_values}
with filter_c3:
    selected_payer_vi = st.selectbox("Bảo hiểm / đơn vị chi trả", payer_options, index=0)

selected_encounter = None if selected_encounter_vi == "Tất cả" else reverse_encounter.get(selected_encounter_vi, selected_encounter_vi)
selected_payer = None if selected_payer_vi == "Tất cả" else reverse_payer.get(selected_payer_vi, selected_payer_vi)
filtered = apply_filters(df, selected_encounter, selected_age_group, selected_payer)

with filter_c4:
    patient_count = int(filtered["condition"].nunique())
    st.markdown(
        f"""
        <div class="metric-card" style="min-height:89px;margin-top:27px;">
          <div class="metric-label">Số tình trạng bệnh</div>
          <div class="metric-value">{patient_count:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Main grid row 1
# left metrics / center bar / right stacked bar
# -----------------------------
left, center, right = st.columns([1.0, 1.05, 1.25], gap="small")

with left:
    m1, m2 = st.columns(2, gap="small")
    avg_cost = float(filtered["total_claim_cost"].mean()) if len(filtered) else 0.0
    total_encounters = int(len(filtered))
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Tổng lượt khám</div>
              <div class="metric-value">{total_encounters:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Chi phí trung bình</div>
              <div class="metric-value">{money(avg_cost)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    m3, m4 = st.columns(2, gap="small")
    inpatient = int((filtered["encounter_class"] == "inpatient").sum()) if len(filtered) else 0
    emergency = int((filtered["encounter_class"] == "emergency").sum()) if len(filtered) else 0
    insured = int((filtered["payer"] != "NO_INSURANCE").sum()) if len(filtered) else 0
    uninsured = int((filtered["payer"] == "NO_INSURANCE").sum()) if len(filtered) else 0
    insured_rate = (insured / len(filtered) * 100) if len(filtered) else 0
    with m3:
        st.markdown(
            f"""
            <div class="split-metric">
              <div class="split-label">Nội trú và cấp cứu</div>
              <div class="split-row">
                <div class="split-item"><div class="split-value">{inpatient:,}</div><div class="split-caption">Nội trú</div></div>
                <div class="split-item"><div class="split-value">{emergency:,}</div><div class="split-caption">Cấp cứu</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="split-metric">
              <div class="split-label">Tỷ lệ có bảo hiểm</div>
              <div style="text-align:center;font-size:24px;font-weight:500;margin-bottom:3px;">{insured_rate:.0f}%</div>
              <div class="split-row">
                <div class="split-item"><div class="split-value" style="font-size:19px">{insured:,}</div><div class="split-caption">Có BH</div></div>
                <div class="split-item"><div class="split-value" style="font-size:19px">{uninsured:,}</div><div class="split-caption">Không BH</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with center:
    st.markdown('<div class="panel-title">Chi phí trung bình theo loại lượt khám</div>', unsafe_allow_html=True)
    cost_by_class = (
        filtered.groupby("encounter_class", dropna=False)["total_claim_cost"]
        .mean()
        .sort_values(ascending=False)
        .head(6)
    )
    fig = go.Figure(
        go.Bar(
            x=[vi_encounter(x) for x in cost_by_class.index],
            y=cost_by_class.values,
            marker_color=TEAL,
            text=[money(v) for v in cost_by_class.values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}<br>Chi phí TB: $%{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(**plot_layout(285, margin=dict(l=48, r=12, t=10, b=68)))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, title="USD", automargin=True)
    fig.update_xaxes(showgrid=False, tickangle=-25, tickfont=dict(size=11), automargin=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with right:
    st.markdown('<div class="panel-title">Lượt khám theo tình trạng bệnh</div>', unsafe_allow_html=True)
    top_cond = filtered["condition"].value_counts().head(6).index.tolist()
    cond_gender = (
        filtered[filtered["condition"].isin(top_cond)]
        .groupby(["condition", "gender"]).size().unstack(fill_value=0)
        .reindex(top_cond)
    )
    fig = go.Figure()
    for gender, color in [("M", BLUE), ("F", TEAL)]:
        vals = cond_gender[gender] if gender in cond_gender.columns else pd.Series(0, index=cond_gender.index)
        fig.add_trace(
            go.Bar(
                y=[vi_condition(x) for x in cond_gender.index],
                x=vals.values,
                name=vi_gender(gender),
                orientation="h",
                marker_color=color,
                text=vals.values,
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="white"),
                hovertemplate=f"{vi_gender(gender)}: %{{x}}<extra></extra>",
            )
        )
    fig.update_layout(
        **plot_layout(285, margin=dict(l=92, r=12, t=32, b=30)),
        barmode="stack",
        legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, automargin=True)
    fig.update_yaxes(showgrid=False, autorange="reversed", automargin=True, tickfont=dict(size=11))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# -----------------------------
# Main grid row 2
# age cost + high-cost encounter table
# -----------------------------
bottom_left, bottom_right = st.columns([1.0, 2.0], gap="small")

with bottom_left:
    st.markdown('<div class="panel-title">Chi phí trung bình theo nhóm tuổi</div>', unsafe_allow_html=True)
    tmp = filtered.copy()
    tmp["age_group"] = tmp["age"].apply(age_group)
    ordered_groups = ["0–17", "18–34", "35–49", "50–64", "65+"]
    by_age = tmp.groupby("age_group")["total_claim_cost"].mean().reindex(ordered_groups).dropna()
    fig = go.Figure(
        go.Bar(
            y=by_age.index,
            x=by_age.values,
            orientation="h",
            marker_color=BLUE,
            text=[money(v) for v in by_age.values],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=12),
            hovertemplate="%{y}<br>Chi phí TB: $%{x:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(**plot_layout(285, margin=dict(l=92, r=12, t=10, b=32)))
    fig.update_xaxes(gridcolor=GRID, zeroline=False, title="USD", automargin=True)
    fig.update_yaxes(showgrid=False, autorange="reversed", automargin=True, tickfont=dict(size=11))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with bottom_right:
    st.markdown('<div class="panel-title">Các lượt khám có chi phí cao</div>', unsafe_allow_html=True)
    cols = ["encounter_id", "age", "gender", "encounter_class", "payer", "condition", "total_claim_cost"]
    high = filtered.sort_values("total_claim_cost", ascending=False).head(7)[cols].copy()
    high.columns = ["Mã lượt khám", "Tuổi", "Giới tính", "Loại lượt khám", "Bảo hiểm", "Tình trạng bệnh", "Chi phí"]
    high["Giới tính"] = high["Giới tính"].map(lambda x: vi_gender(str(x)))
    high["Loại lượt khám"] = high["Loại lượt khám"].map(lambda x: vi_encounter(str(x)))
    high["Bảo hiểm"] = high["Bảo hiểm"].map(lambda x: vi_payer(str(x)))
    high["Tình trạng bệnh"] = high["Tình trạng bệnh"].map(lambda x: vi_condition(str(x)))
    high["Chi phí"] = high["Chi phí"].map(lambda x: money(float(x)))
    st.dataframe(high, use_container_width=True, hide_index=True, height=285)

# -----------------------------
# Prediction section below the reference dashboard viewport
# -----------------------------
st.markdown('<div class="section-card"><div class="section-title">Dự đoán chi phí điều trị</div><div class="section-subtitle">Nhập thông tin lượt khám để ước tính tổng chi phí claim.</div></div>', unsafe_allow_html=True)

form_col, result_col = st.columns([2.6, 1.0], gap="medium")

with form_col:
    with st.form("prediction_form", clear_on_submit=False):

        # =========================
        # NHÓM 1: Thông tin cơ bản
        # =========================
        st.markdown("#### Thông tin lượt khám")

        r1c1, r1c2, r1c3 = st.columns(3, gap="small")

        with r1c1:
            pred_age = st.number_input(
                "Tuổi",
                min_value=0,
                max_value=120,
                value=45,
                step=1
            )

        with r1c2:
            gender_values = sorted(
                df["gender"].dropna().astype(str).unique()
            )

            pred_gender = st.selectbox(
                "Giới tính",
                gender_values,
                format_func=vi_gender,
                key="pred_gender"
            )

        with r1c3:
            race_values = sorted(
                df["race"].dropna().astype(str).unique()
            )

            pred_race = st.selectbox(
                "Chủng tộc",
                race_values,
                format_func=lambda x:
                    DISPLAY_MAPS.get("race", {}).get(x, x),
                key="pred_race"
            )


        r2c1, r2c2, r2c3 = st.columns(3, gap="small")

        with r2c1:
            ethnicity_values = sorted(
                df["ethnicity"].dropna().astype(str).unique()
            )

            pred_ethnicity = st.selectbox(
                "Nhóm dân tộc",
                ethnicity_values,
                format_func=lambda x:
                    DISPLAY_MAPS.get("ethnicity", {}).get(x, x),
                key="pred_eth"
            )

        with r2c2:
            encounter_values = sorted(
                df["encounter_class"].dropna().astype(str).unique()
            )

            pred_encounter = st.selectbox(
                "Loại lượt khám",
                encounter_values,
                format_func=vi_encounter,
                key="pred_enc"
            )

        with r2c3:
            payer_values_pred = sorted(
                df["payer"].dropna().astype(str).unique()
            )

            pred_payer = st.selectbox(
                "Bảo hiểm / đơn vị chi trả",
                payer_values_pred,
                format_func=vi_payer,
                key="pred_payer"
            )


        condition_values = sorted(
            df["condition"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        pred_condition = st.selectbox(
            "Tình trạng bệnh",
            condition_values,
            format_func=vi_condition,
            key="pred_condition"
        )


        # =========================
        # NHÓM 2: Hoạt động y tế
        # =========================
        st.markdown("#### Hoạt động y tế")

        r3c1, r3c2, r3c3 = st.columns(3, gap="small")

        with r3c1:
            pred_condition_count = st.number_input(
                "Số tình trạng bệnh",
                min_value=0,
                value=1,
                step=1
            )

        with r3c2:
            pred_procedure_count = st.number_input(
                "Số thủ thuật",
                min_value=0,
                value=0,
                step=1
            )

        with r3c3:
            pred_distinct_procedure_count = st.number_input(
                "Số loại thủ thuật khác nhau",
                min_value=0,
                value=0,
                step=1
            )


        r4c1, r4c2, r4c3 = st.columns(3, gap="small")

        with r4c1:
            pred_medication_count = st.number_input(
                "Số thuốc",
                min_value=0,
                value=0,
                step=1
            )

        with r4c2:
            pred_distinct_medication_count = st.number_input(
                "Số loại thuốc khác nhau",
                min_value=0,
                value=0,
                step=1
            )

        with r4c3:
            pred_observation_count = st.number_input(
                "Số quan sát / xét nghiệm",
                min_value=0,
                value=0,
                step=1
            )


        pred_encounter_duration_hours = st.number_input(
            "Thời lượng lượt khám (giờ)",
            min_value=0.0,
            value=1.0,
            step=0.5
        )


        # =========================
        # NHÓM 3: Lịch sử khám
        # =========================
        st.markdown("#### Lịch sử khám")

        r5c1, r5c2, r5c3 = st.columns(3, gap="small")

        with r5c1:
            pred_prior_encounter_count = st.number_input(
                "Số lượt khám trước đó",
                min_value=0,
                value=0,
                step=1
            )

        with r5c2:
            pred_prior_inpatient_count = st.number_input(
                "Số lần nội trú trước đó",
                min_value=0,
                value=0,
                step=1
            )

        with r5c3:
            pred_prior_emergency_count = st.number_input(
                "Số lần cấp cứu trước đó",
                min_value=0,
                value=0,
                step=1
            )


        submitted = st.form_submit_button(
            "Dự đoán chi phí",
            use_container_width=True
        )
payload = {
    "age": int(pred_age),
    "gender": pred_gender,
    "race": pred_race,
    "ethnicity": pred_ethnicity,
    "encounter_class": pred_encounter,
    "payer": pred_payer,
    "condition": pred_condition,

    "condition_count": int(pred_condition_count),

    "procedure_count": int(pred_procedure_count),
    "distinct_procedure_count": int(
        pred_distinct_procedure_count
    ),

    "medication_count": int(pred_medication_count),
    "distinct_medication_count": int(
        pred_distinct_medication_count
    ),

    "observation_count": int(pred_observation_count),

    "encounter_duration_hours": float(
        pred_encounter_duration_hours
    ),

    "prior_encounter_count": int(
        pred_prior_encounter_count
    ),

    "prior_inpatient_count": int(
        pred_prior_inpatient_count
    ),

    "prior_emergency_count": int(
        pred_prior_emergency_count
    ),
}

if "predicted_cost_value" not in st.session_state:
    st.session_state.predicted_cost_value = None
    st.session_state.prediction_mode = ""

if submitted:

    validation_error = None

    if pred_distinct_procedure_count > pred_procedure_count:
        validation_error = (
            "Số loại thủ thuật khác nhau không thể lớn hơn "
            "tổng số thủ thuật."
        )

    elif pred_distinct_medication_count > pred_medication_count:
        validation_error = (
            "Số loại thuốc khác nhau không thể lớn hơn "
            "tổng số thuốc."
        )

    elif pred_prior_inpatient_count > pred_prior_encounter_count:
        validation_error = (
            "Số lần nội trú trước đó không thể lớn hơn "
            "tổng số lượt khám trước đó."
        )

    elif pred_prior_emergency_count > pred_prior_encounter_count:
        validation_error = (
            "Số lần cấp cứu trước đó không thể lớn hơn "
            "tổng số lượt khám trước đó."
        )

    if validation_error:
        st.session_state.predicted_cost_value = None
        st.session_state.prediction_mode = ""
        st.error(validation_error)

    elif api_online:
        result, err = predict_cost(api_base_url, payload)

        if err is None:
            st.session_state.predicted_cost_value = float(
                result["predicted_total_claim_cost"]
            )

            st.session_state.prediction_mode = (
                model_name or "Random Forest (log1p)"
            )

        else:
            st.session_state.predicted_cost_value = None
            st.session_state.prediction_mode = ""
            st.error(f"Không thể dự đoán: {err}")

    else:
        st.session_state.predicted_cost_value = None
        st.session_state.prediction_mode = ""
        st.error(
            "API/model chưa sẵn sàng. Không thể dự đoán."
        )
with result_col:
    value = st.session_state.predicted_cost_value
    if value is None:
        display_value = "—"
        mode = "Chưa dự đoán"
    else:
        display_value = f"${value:,.2f} USD"
        mode = st.session_state.prediction_mode
    st.markdown(
        f"""
        <div class="prediction-result">
          <div class="label">Chi phí điều trị dự kiến</div>
          <div class="value">{display_value}</div>
          <div class="mode">{mode}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption(f"Nguồn dữ liệu: {source_label}")
