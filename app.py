import base64
import math
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


st.set_page_config(
    page_title="Velora",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded",
)


PRIMARY = "#d4a24c"
ACCENT = "#5b8cff"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
ROSE = "#38bdf8"
SURFACE = "#0f172a"
SURFACE_ALT = "#111827"
BACKGROUND = "#020617"
TEXT = "#e2e8f0"
MUTED = "#94a3b8"
BORDER = "rgba(96, 165, 250, 0.16)"
PLOT_BG = "#0b1220"

ASSET_DIR = Path(__file__).resolve().parent / "assets"


def image_data_uri(filename: str) -> str:
    path = ASSET_DIR / filename
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    suffix = path.suffix.lower().replace(".", "") or "png"
    if suffix == "jpg":
        suffix = "jpeg"
    return f"data:image/{suffix};base64,{encoded}"


HERO_BG_URI = image_data_uri("velora-hero-bg.png")


st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600;700&display=swap');

        .stApp {{
            background: {BACKGROUND};
            color: {TEXT};
            background-image:
                radial-gradient(circle at top left, rgba(56,189,248,0.12), transparent 24%),
                radial-gradient(circle at top right, rgba(91,140,255,0.16), transparent 22%),
                radial-gradient(circle at bottom center, rgba(34,197,94,0.06), transparent 30%),
                linear-gradient(180deg, rgba(255,255,255,0.015), transparent 20%);
        }}

        .main .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 1420px;
        }}

        [data-testid="stSidebar"] {{
            background:
                linear-gradient(180deg, rgba(6, 11, 23, 0.98), rgba(2, 6, 23, 0.98));
            background-size: cover;
            background-position: center;
            border-right: 1px solid rgba(96, 165, 250, 0.14);
        }}

        [data-testid="stSidebar"] > div:first-child {{
            backdrop-filter: blur(18px);
        }}

        [data-testid="stSidebar"] * {{
            color: {TEXT};
        }}

        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            font-family: Georgia, "Times New Roman", serif;
        }}

        [data-testid="stSidebar"] .stFileUploader {{
            background: rgba(15, 23, 42, 0.88);
            border: 1px dashed rgba(96, 165, 250, 0.32);
            border-radius: 18px;
            padding: 0.5rem;
        }}

        h1, h2, h3 {{
            letter-spacing: 0;
        }}

        html, body, [class*="css"] {{
            font-family: "Inter", Arial, sans-serif;
        }}

        h1, h2 {{
            font-family: "Space Grotesk", "Inter", Arial, sans-serif;
        }}

        .hero {{
            position: relative;
            overflow: hidden;
            padding: 2.9rem 2.6rem 2.35rem 2.6rem;
            background:
                linear-gradient(135deg, rgba(3,7,18,0.88), rgba(15,23,42,0.82)),
                url("{HERO_BG_URI}");
            background-size: cover;
            background-position: center;
            border: 1px solid {BORDER};
            border-radius: 24px;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.42);
        }}

        .hero::before {{
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 20% 20%, rgba(56,189,248,0.14), transparent 24%),
                linear-gradient(90deg, rgba(2,6,23,0.86), rgba(2,6,23,0.42));
            pointer-events: none;
        }}

        .hero::after {{
            content: "";
            position: absolute;
            inset: auto -8% -42% auto;
            width: 420px;
            height: 420px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(91,140,255,0.18), transparent 66%);
            filter: blur(12px);
            pointer-events: none;
        }}

        .hero-title {{
            position: relative;
            font-size: 3rem;
            font-weight: 700;
            color: {TEXT};
            margin-bottom: 0.6rem;
            text-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
        }}

        .hero-kicker {{
            position: relative;
            display: inline-block;
            margin-bottom: 0.9rem;
            color: {PRIMARY};
            text-transform: uppercase;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.14em;
        }}

        .hero-shell {{
            position: relative;
            display: grid;
            grid-template-columns: minmax(0, 1fr) 160px;
            gap: 1.4rem;
            align-items: start;
        }}

        .hero-mark-wrap {{
            position: relative;
            display: flex;
            justify-content: flex-end;
            align-items: flex-start;
        }}

        .hero-mark {{
            width: 128px;
            height: 128px;
            border-radius: 28px;
            border: 1px solid rgba(96,165,250,0.24);
            background:
                linear-gradient(145deg, rgba(15,23,42,0.92), rgba(30,41,59,0.72));
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.06),
                0 18px 40px rgba(2,6,23,0.45);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }}

        .hero-mark::before {{
            content: "";
            position: absolute;
            inset: 14px;
            border-radius: 22px;
            border: 1px solid rgba(56,189,248,0.16);
            background:
                radial-gradient(circle at top, rgba(56,189,248,0.14), transparent 40%),
                linear-gradient(180deg, rgba(255,255,255,0.02), transparent 80%);
        }}

        .hero-mark-text {{
            position: relative;
            font-family: "Space Grotesk", "Inter", Arial, sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            color: #dbeafe;
            letter-spacing: 0.04em;
            text-shadow: 0 0 30px rgba(91,140,255,0.25);
        }}

        .hero-copy {{
            position: relative;
            font-size: 1rem;
            color: {MUTED};
            max-width: 720px;
            margin-bottom: 1.2rem;
            line-height: 1.7;
        }}

        .hero-metrics {{
            position: relative;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin-top: 1.25rem;
            max-width: 760px;
        }}

        .hero-metric {{
            background: rgba(2, 6, 23, 0.48);
            border: 1px solid rgba(148,163,184,0.12);
            border-radius: 18px;
            padding: 0.85rem 0.95rem;
            backdrop-filter: blur(8px);
        }}

        .hero-metric-label {{
            color: {MUTED};
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.3rem;
        }}

        .hero-metric-value {{
            color: {TEXT};
            font-size: 1.15rem;
            font-weight: 700;
        }}

        .section-card {{
            background:
                linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(2, 6, 23, 0.98));
            border: 1px solid rgba(96, 165, 250, 0.12);
            border-radius: 20px;
            padding: 1.1rem 1.1rem 1rem 1.1rem;
            box-shadow: 0 16px 44px rgba(0, 0, 0, 0.24);
            backdrop-filter: blur(10px);
        }}

        .section-titlebar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.9rem;
        }}

        .section-eyebrow {{
            color: {ACCENT};
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            font-weight: 700;
        }}

        .kpi-card {{
            background:
                linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(3, 7, 18, 0.98));
            border: 1px solid rgba(96, 165, 250, 0.16);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 16px 32px rgba(0, 0, 0, 0.24);
        }}

        .kpi-label {{
            font-size: 0.84rem;
            color: {MUTED};
            margin-bottom: 0.35rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}

        .kpi-value {{
            font-size: 1.7rem;
            font-weight: 700;
            color: {TEXT};
        }}

        .mini-note {{
            color: {MUTED};
            font-size: 0.9rem;
        }}

        .pill-row {{
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
            margin-top: 0.6rem;
        }}

        .pill {{
            position: relative;
            background: rgba(56,189,248,0.08);
            border: 1px solid rgba(56,189,248,0.22);
            color: #bae6fd;
            border-radius: 999px;
            padding: 0.38rem 0.8rem;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin-top: 1.15rem;
        }}

        .feature-tile {{
            background: linear-gradient(180deg, rgba(15,23,42,0.7), rgba(15,23,42,0.38));
            border: 1px solid rgba(148,163,184,0.1);
            border-radius: 18px;
            padding: 1rem;
            backdrop-filter: blur(6px);
        }}

        .feature-title {{
            font-size: 0.9rem;
            font-weight: 600;
            color: {TEXT};
            margin-bottom: 0.25rem;
        }}

        .feature-copy {{
            font-size: 0.84rem;
            color: {MUTED};
            line-height: 1.45;
        }}

        .ornament-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin-top: 1.1rem;
        }}

        .ornament-card {{
            min-height: 130px;
            border-radius: 20px;
            border: 1px solid rgba(96, 165, 250, 0.12);
            background:
                linear-gradient(180deg, rgba(15,23,42,0.95), rgba(2,6,23,0.96));
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 18px 34px rgba(0,0,0,0.2);
            padding: 1rem;
        }}

        .ornament-symbol {{
            font-size: 1.4rem;
            color: {ROSE};
            margin-bottom: 0.55rem;
        }}

        .ornament-title {{
            font-size: 1rem;
            font-weight: 700;
            color: {TEXT};
            margin-bottom: 0.35rem;
        }}

        .ornament-copy {{
            color: {MUTED};
            font-size: 0.88rem;
            line-height: 1.55;
        }}

        .sidebar-brand {{
            padding: 0.95rem 1rem;
            border-radius: 18px;
            border: 1px solid rgba(96, 165, 250, 0.16);
            background: linear-gradient(180deg, rgba(15,23,42,0.72), rgba(15,23,42,0.38));
            margin-bottom: 1rem;
        }}

        .sidebar-brand-head {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }}

        .sidebar-brand-logo {{
            width: 58px;
            height: 58px;
            border-radius: 16px;
            border: 1px solid rgba(96,165,250,0.2);
            background: linear-gradient(145deg, rgba(15,23,42,0.92), rgba(30,41,59,0.76));
            display: flex;
            align-items: center;
            justify-content: center;
            flex: 0 0 auto;
            box-shadow: 0 10px 18px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }}

        .sidebar-brand-logo::before {{
            content: "";
            position: absolute;
            inset: 8px;
            border-radius: 12px;
            border: 1px solid rgba(56,189,248,0.16);
        }}

        .sidebar-brand-logo-text {{
            position: relative;
            font-family: "Space Grotesk", "Inter", Arial, sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: #dbeafe;
            letter-spacing: 0.08em;
        }}

        .sidebar-brand-title {{
            font-family: "Space Grotesk", "Inter", Arial, sans-serif;
            font-size: 1.35rem;
            color: {TEXT};
            margin-bottom: 0.2rem;
        }}

        .sidebar-brand-copy {{
            color: {MUTED};
            font-size: 0.86rem;
            line-height: 1.5;
        }}

        [data-testid="stTabs"] button {{
            background: rgba(255,255,255,0.03);
            border-radius: 999px;
            border: 1px solid rgba(96, 165, 250, 0.12);
            color: {MUTED};
            padding: 0.45rem 0.9rem;
        }}

        [data-testid="stTabs"] button[aria-selected="true"] {{
            background: linear-gradient(90deg, rgba(56,189,248,0.14), rgba(91,140,255,0.18));
            color: {TEXT};
            border-color: rgba(96, 165, 250, 0.28);
        }}

        [data-testid="stMetric"] {{
            background: linear-gradient(180deg, rgba(15,23,42,0.95), rgba(2,6,23,0.98));
            border: 1px solid rgba(96, 165, 250, 0.12);
            padding: 1rem;
            border-radius: 18px;
        }}

        [data-testid="stMetricLabel"] {{
            color: {MUTED};
        }}

        [data-testid="stMetricValue"] {{
            color: {TEXT};
        }}

        [data-testid="stDataFrame"] {{
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(96, 165, 250, 0.12);
        }}

        .stAlert {{
            background: rgba(15, 23, 42, 0.92);
            color: {TEXT};
            border: 1px solid rgba(96, 165, 250, 0.14);
        }}

        .stSelectbox label, .stSlider label {{
            color: {MUTED};
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {{
            background: rgba(15, 23, 42, 0.9);
            border-color: rgba(96, 165, 250, 0.16);
            border-radius: 14px;
        }}

        .stDownloadButton button, .stButton button {{
            background: linear-gradient(90deg, rgba(56,189,248,0.18), rgba(91,140,255,0.2));
            color: {TEXT};
            border: 1px solid rgba(96,165,250,0.22);
            border-radius: 14px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.22);
        }}

        .stDownloadButton button:hover, .stButton button:hover {{
            border-color: rgba(239,231,219,0.28);
            color: white;
        }}

        @media (max-width: 1100px) {{
            .feature-grid,
            .ornament-grid,
            .hero-metrics {{
                grid-template-columns: 1fr;
            }}

            .hero-shell {{
                grid-template-columns: 1fr;
            }}

            .hero-mark-wrap {{
                justify-content: flex-start;
            }}

            .hero-mark {{
                width: 96px;
                height: 96px;
            }}

            .hero-title {{
                font-size: 2.4rem;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


def infer_column_role(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    unique_ratio = series.nunique(dropna=True) / max(len(series), 1)
    if series.nunique(dropna=True) <= 15 or unique_ratio < 0.2:
        return "categorical"

    return "text"


@st.cache_data
def load_csv(uploaded_file) -> pd.DataFrame:
    return pd.read_csv(uploaded_file)


def load_local_csv(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)


def try_parse_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    parsed = df.copy()
    object_columns = parsed.select_dtypes(include=["object"]).columns
    for col in object_columns:
        sample = parsed[col].dropna().astype(str).head(25)
        if sample.empty:
            continue
        success_count = 0
        for value in sample:
            try:
                pd.to_datetime(value)
                success_count += 1
            except Exception:
                pass
        if success_count >= max(5, math.ceil(len(sample) * 0.7)):
            converted = pd.to_datetime(parsed[col], errors="coerce")
            if converted.notna().sum() >= max(5, int(len(parsed) * 0.5)):
                parsed[col] = converted
    return parsed


def apply_cleaning_pipeline(
    df: pd.DataFrame,
    fill_missing: str,
    drop_missing_rows: bool,
    remove_duplicates: bool,
) -> tuple[pd.DataFrame, dict]:
    cleaned = df.copy()
    summary = {
        "rows_before": len(df),
        "rows_after": len(df),
        "missing_before": int(df.isna().sum().sum()),
        "missing_after": int(df.isna().sum().sum()),
        "duplicates_before": int(df.duplicated().sum()),
        "duplicates_after": int(df.duplicated().sum()),
        "actions": [],
    }

    if fill_missing == "Fill numeric with median and categories with mode":
        numeric_cols = cleaned.select_dtypes(include="number").columns.tolist()
        other_cols = [col for col in cleaned.columns if col not in numeric_cols]
        for col in numeric_cols:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
            if cleaned[col].isna().any():
                cleaned[col] = cleaned[col].fillna(cleaned[col].median())
        for col in other_cols:
            if cleaned[col].isna().any():
                mode = cleaned[col].mode(dropna=True)
                fallback = mode.iloc[0] if not mode.empty else "Missing"
                cleaned[col] = cleaned[col].fillna(fallback)
        summary["actions"].append("Filled missing numeric values with median and category values with mode.")
    elif fill_missing == "Fill everything with placeholder":
        for col in cleaned.columns:
            if pd.api.types.is_numeric_dtype(cleaned[col]):
                cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0)
            else:
                cleaned[col] = cleaned[col].fillna("Missing")
        summary["actions"].append("Filled all missing values with placeholders.")

    if drop_missing_rows:
        before = len(cleaned)
        cleaned = cleaned.dropna().copy()
        removed = before - len(cleaned)
        summary["actions"].append(f"Dropped rows with missing values: {removed}.")

    if remove_duplicates:
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates().copy()
        removed = before - len(cleaned)
        summary["actions"].append(f"Removed duplicate rows: {removed}.")

    summary["rows_after"] = len(cleaned)
    summary["missing_after"] = int(cleaned.isna().sum().sum())
    summary["duplicates_after"] = int(cleaned.duplicated().sum())
    return cleaned, summary


def kpi_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, eyebrow: str, note: str | None = None) -> None:
    note_html = f'<div class="mini-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="section-titlebar">
            <div>
                <div class="section-eyebrow">{eyebrow}</div>
                <h3 style="margin: 0.2rem 0 0 0;">{title}</h3>
            </div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def explain_number(value: int | float) -> str:
    if isinstance(value, float):
        return f"{value:,.2f}"
    return f"{value:,}"


def write_plain_summary(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="section-card" style="margin-top: 0.85rem;">
            <div class="section-eyebrow">What This Means</div>
            <div style="font-size: 1.02rem; font-weight: 700; margin: 0.2rem 0 0.45rem 0;">{title}</div>
            <div class="mini-note" style="font-size: 0.95rem; line-height: 1.7; color: {TEXT};">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def describe_overview(df: pd.DataFrame) -> str:
    missing_cells = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = [col for col in df.columns if infer_column_role(df[col]) in {"categorical", "text"}]

    return (
        f"This file has {len(df):,} rows and {len(df.columns):,} columns. "
        f"It includes {len(numeric_cols):,} number-based fields and {len(categorical_cols):,} text or category fields. "
        f"There are {missing_cells:,} missing values and {duplicates:,} duplicate rows, so this section helps you quickly spot whether the dataset looks clean or messy."
    )


def describe_numeric_column(df: pd.DataFrame, column: str) -> str:
    series = df[column].dropna()
    if series.empty:
        return f"There is no usable numeric data in {column} yet."

    avg = series.mean()
    low = series.min()
    high = series.max()

    return (
        f"This chart shows how the values of {column} are spread out. "
        f"Most people can read it like this: taller bars mean more rows fall in that range. "
        f"For {column}, the average is about {avg:,.2f}, with values ranging from {low:,.2f} to {high:,.2f}."
    )


def describe_comparison(df: pd.DataFrame, x_col: str, y_col: str) -> str:
    corr = df[[x_col, y_col]].corr(numeric_only=True).iloc[0, 1]
    if pd.isna(corr):
        relation = "There is not enough clean data here to explain the relationship."
    elif corr > 0.6:
        relation = "These two columns usually rise together pretty strongly."
    elif corr > 0.2:
        relation = "These two columns have a mild positive relationship."
    elif corr < -0.6:
        relation = "When one goes up, the other usually goes down quite strongly."
    elif corr < -0.2:
        relation = "There is a mild opposite relationship between them."
    else:
        relation = "There does not seem to be a strong relationship between them."

    return (
        f"Each dot is one row from your dataset. "
        f"The horizontal position shows {x_col} and the vertical position shows {y_col}. "
        f"{relation}"
    )


def describe_category_counts(counts: pd.DataFrame, column: str) -> str:
    if counts.empty:
        return f"There is no readable category information in {column} yet."

    top_row = counts.iloc[-1]
    return (
        f"This chart shows the most common values in {column}. "
        f"The biggest group here is {top_row[column]}, with {int(top_row['Count']):,} rows, or about {top_row['Share']:.1f}% of the displayed total. "
        f"This helps someone quickly see which group dominates the dataset."
    )


def describe_time_trend(grouped: pd.DataFrame, dt_col: str) -> str:
    if grouped.empty:
        return f"There is no time pattern available for {dt_col}."

    peak = grouped.loc[grouped["Rows"].idxmax()]
    return (
        f"This line shows how many rows appear over time using {dt_col}. "
        f"Higher points mean more records happened in that month. "
        f"The busiest point in this view is {peak['_date_bucket']} with {int(peak['Rows']):,} rows."
    )


def build_analysis_summary_text(df: pd.DataFrame, cleaning_summary: dict | None = None) -> str:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    datetime_cols = [col for col in df.columns if infer_column_role(df[col]) == "datetime"]
    categorical_cols = [col for col in df.columns if infer_column_role(df[col]) in {"categorical", "text"}]

    lines = [
        "Velora Analysis Summary",
        "",
        f"Rows: {len(df):,}",
        f"Columns: {len(df.columns):,}",
        f"Numeric fields: {len(numeric_cols):,}",
        f"Categorical/text fields: {len(categorical_cols):,}",
        f"Datetime fields: {len(datetime_cols):,}",
        f"Missing values: {int(df.isna().sum().sum()):,}",
        f"Duplicate rows: {int(df.duplicated().sum()):,}",
    ]

    if cleaning_summary:
        lines.extend(
            [
                "",
                "Cleaning Summary",
                f"Rows before cleaning: {cleaning_summary['rows_before']:,}",
                f"Rows after cleaning: {cleaning_summary['rows_after']:,}",
                f"Missing values before cleaning: {cleaning_summary['missing_before']:,}",
                f"Missing values after cleaning: {cleaning_summary['missing_after']:,}",
                f"Duplicates before cleaning: {cleaning_summary['duplicates_before']:,}",
                f"Duplicates after cleaning: {cleaning_summary['duplicates_after']:,}",
            ]
        )
        if cleaning_summary["actions"]:
            lines.append("Actions applied:")
            lines.extend([f"- {action}" for action in cleaning_summary["actions"]])

    return "\n".join(lines)


def generate_smart_recommendations(df: pd.DataFrame, model_bundle: dict | None = None) -> list[str]:
    recommendations = []
    missing_total = int(df.isna().sum().sum())
    duplicate_total = int(df.duplicated().sum())

    if missing_total > 0:
        worst_col = df.isna().sum().sort_values(ascending=False).index[0]
        recommendations.append(
            f"Focus on cleaning `{worst_col}` first because the dataset still contains {missing_total:,} missing values."
        )

    if duplicate_total > 0:
        recommendations.append(
            f"Remove or investigate duplicate rows because the file still contains {duplicate_total:,} duplicates that can distort charts and predictions."
        )

    datetime_cols = [col for col in df.columns if infer_column_role(df[col]) == "datetime"]
    if datetime_cols:
        dt_col = datetime_cols[0]
        grouped = (
            df.assign(_date_bucket=df[dt_col].dt.to_period("M").astype(str))
            .groupby("_date_bucket")
            .size()
            .reset_index(name="Rows")
        )
        if len(grouped) >= 2:
            peak = grouped.loc[grouped["Rows"].idxmax()]
            low = grouped.loc[grouped["Rows"].idxmin()]
            if peak["Rows"] > low["Rows"] * 1.5:
                recommendations.append(
                    f"There is a strong time pattern in `{dt_col}`. Compare {peak['_date_bucket']} and {low['_date_bucket']} to investigate spikes or drop-offs."
                )

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        std_series = df[numeric_cols].std(numeric_only=True).sort_values(ascending=False)
        if not std_series.empty:
            top_variable = std_series.index[0]
            recommendations.append(
                f"`{top_variable}` changes the most across the dataset, so it is a strong candidate for deeper analysis or filtering."
            )

    categorical_cols = [col for col in df.columns if infer_column_role(df[col]) in {"categorical", "text"}]
    if categorical_cols:
        cat_col = categorical_cols[0]
        counts = df[cat_col].fillna("Missing").astype(str).value_counts(normalize=True)
        if not counts.empty and counts.iloc[0] > 0.55:
            recommendations.append(
                f"`{cat_col}` is dominated by `{counts.index[0]}` ({counts.iloc[0] * 100:.1f}%), so consider segmenting by other fields for a more balanced view."
            )

    if model_bundle is not None and not model_bundle["feature_importance"].empty:
        top_feature = model_bundle["feature_importance"].iloc[0]
        recommendations.append(
            f"For prediction, prioritize `{top_feature['Feature']}` because it had the strongest influence on the model's output."
        )

        if model_bundle["model_type"] == "regression":
            recommendations.append(
                f"Compare the Random Forest model against the linear baseline to explain why a more flexible model was needed for `{model_bundle['target_col']}`."
            )
        else:
            recommendations.append(
                f"Review the confusion matrix for `{model_bundle['target_col']}` to spot which categories are easiest or hardest for the model to distinguish."
            )

    return recommendations[:6]


def get_prediction_target_options(df: pd.DataFrame) -> list[str]:
    options = []
    for col in df.columns:
        role = infer_column_role(df[col])
        unique_count = df[col].nunique(dropna=True)
        non_null_count = df[col].notna().sum()

        if non_null_count < 12:
            continue

        if role == "numeric" and unique_count >= 8:
            options.append(col)
        elif role == "categorical" and 2 <= unique_count <= 20:
            options.append(col)

    return options


@st.cache_resource(show_spinner=False)
def train_prediction_model(df: pd.DataFrame, target_col: str) -> dict:
    working = df.copy()
    working = working.dropna(subset=[target_col]).copy()

    target_role = infer_column_role(working[target_col])
    feature_cols = [
        col
        for col in working.columns
        if col != target_col and infer_column_role(working[col]) in {"numeric", "categorical"}
    ]

    if not feature_cols:
        raise ValueError("There are no usable feature columns for prediction.")

    model_df = working[feature_cols + [target_col]].copy()

    numeric_features = [col for col in feature_cols if infer_column_role(model_df[col]) == "numeric"]
    categorical_features = [col for col in feature_cols if infer_column_role(model_df[col]) == "categorical"]

    for col in numeric_features:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")
        model_df[col] = model_df[col].fillna(model_df[col].median())

    category_defaults = {}
    for col in categorical_features:
        mode = model_df[col].mode(dropna=True)
        default_value = str(mode.iloc[0]) if not mode.empty else "Missing"
        category_defaults[col] = default_value
        model_df[col] = model_df[col].fillna(default_value).astype(str)

    if target_role == "numeric":
        y = pd.to_numeric(model_df[target_col], errors="coerce")
        usable = y.notna()
        model_df = model_df.loc[usable].copy()
        y = y.loc[usable]
        model_type = "regression"
    else:
        y = model_df[target_col].fillna("Missing").astype(str)
        model_type = "classification"

    X_raw = model_df[feature_cols].copy()
    X_encoded = pd.get_dummies(X_raw, columns=categorical_features, dummy_na=False)

    if len(X_encoded) < 12:
        raise ValueError("This dataset is too small for a meaningful prediction demo.")

    stratify = y if model_type == "classification" and y.nunique() > 1 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded,
        y,
        test_size=0.2,
        random_state=42,
        stratify=stratify,
    )

    if model_type == "regression":
        model = RandomForestRegressor(random_state=42, n_estimators=200)
        baseline_model = LinearRegression()
        model.fit(X_train, y_train)
        baseline_model.fit(X_train, y_train)
        preds = model.predict(X_test)
        baseline_preds = baseline_model.predict(X_test)
        metrics = {
            "primary_label": "Average Error",
            "primary_value": mean_absolute_error(y_test, preds),
            "secondary_label": "R2 Score",
            "secondary_value": r2_score(y_test, preds),
            "baseline_label": "Linear Regression Error",
            "baseline_value": mean_absolute_error(y_test, baseline_preds),
        }
        explanation = (
            f"Velora is predicting a number for `{target_col}`. "
            f"It used 80% of the data for training and 20% for testing. "
            f"On the test data, the random forest model missed by about {metrics['primary_value']:.2f} on average. "
            f"For comparison, the linear baseline missed by about {metrics['baseline_value']:.2f}."
        )
        confusion_df = None
    else:
        model = RandomForestClassifier(random_state=42, n_estimators=200)
        baseline_model = LogisticRegression(max_iter=2000)
        model.fit(X_train, y_train)
        baseline_model.fit(X_train, y_train)
        preds = model.predict(X_test)
        baseline_preds = baseline_model.predict(X_test)
        labels = sorted(pd.Series(y).astype(str).unique().tolist())
        cm = confusion_matrix(y_test, preds, labels=labels)
        confusion_df = pd.DataFrame(cm, index=labels, columns=labels)
        metrics = {
            "primary_label": "Accuracy",
            "primary_value": accuracy_score(y_test, preds),
            "secondary_label": "Classes",
            "secondary_value": y.nunique(),
            "baseline_label": "Logistic Baseline Accuracy",
            "baseline_value": accuracy_score(y_test, baseline_preds),
        }
        explanation = (
            f"Velora is predicting a category for `{target_col}`. "
            f"It used 80% of the data for training and 20% for testing. "
            f"On the test data, the random forest model was correct about {metrics['primary_value'] * 100:.1f}% of the time, "
            f"while the logistic baseline reached about {metrics['baseline_value'] * 100:.1f}%."
        )

    feature_importance = (
        pd.DataFrame(
            {
                "Feature": X_encoded.columns,
                "Importance": model.feature_importances_,
            }
        )
        .sort_values("Importance", ascending=False)
        .head(8)
    )

    defaults = {}
    categorical_choices = {}
    for col in feature_cols:
        if col in numeric_features:
            defaults[col] = float(model_df[col].median())
        else:
            values = sorted(model_df[col].dropna().astype(str).unique().tolist())
            categorical_choices[col] = values
            defaults[col] = category_defaults[col]

    return {
        "target_col": target_col,
        "model_type": model_type,
        "model": model,
        "feature_cols": feature_cols,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "training_columns": X_encoded.columns.tolist(),
        "defaults": defaults,
        "categorical_choices": categorical_choices,
        "metrics": metrics,
        "explanation": explanation,
        "feature_importance": feature_importance,
        "row_count": len(model_df),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "confusion_df": confusion_df,
    }


def build_prediction_lab(df: pd.DataFrame) -> None:
    target_options = get_prediction_target_options(df)
    if not target_options:
        st.info("This dataset does not have a clear prediction target yet. Try a file with a numeric outcome or a low-cardinality category column.")
        return

    selected_target = st.selectbox("Choose the column Velora should predict", target_options, key="prediction_target")

    with st.spinner("Training models and evaluating the prediction setup..."):
        try:
            model_bundle = train_prediction_model(df, selected_target)
        except Exception as exc:
            st.warning(f"Velora could not train a prediction model for this column: {exc}")
            return

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Prediction Readiness", "Machine Learning")
        st.write(f"Target column: `{model_bundle['target_col']}`")
        st.write(f"Model type: `{model_bundle['model_type'].title()}`")
        st.write(f"Training rows used: `{model_bundle['row_count']:,}`")
        st.write(f"Input features used: `{len(model_bundle['feature_cols'])}`")
        st.write(f"Train/Test split: `{model_bundle['train_rows']:,}` for training and `{model_bundle['test_rows']:,}` for testing")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Model Quality", "Score")
        metrics = model_bundle["metrics"]
        if model_bundle["model_type"] == "regression":
            st.metric(metrics["primary_label"], f"{metrics['primary_value']:.2f}")
            st.metric(metrics["secondary_label"], f"{metrics['secondary_value']:.2f}")
            st.metric(metrics["baseline_label"], f"{metrics['baseline_value']:.2f}")
        else:
            st.metric(metrics["primary_label"], f"{metrics['primary_value'] * 100:.1f}%")
            st.metric(metrics["secondary_label"], int(metrics["secondary_value"]))
            st.metric(metrics["baseline_label"], f"{metrics['baseline_value'] * 100:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)

    write_plain_summary("How to read this prediction model", model_bundle["explanation"])

    recommendations = generate_smart_recommendations(df, model_bundle)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Smart Recommendation Engine", "Signature Feature", "Advice generated from the dataset and the trained model")
    for rec in recommendations:
        st.write(f"- {rec}")
    st.markdown("</div>", unsafe_allow_html=True)
    write_plain_summary(
        "Why this matters",
        "Instead of only showing metrics, Velora converts the analysis and model behavior into practical next steps. "
        "This makes the tool easier to present and easier for a non-technical person to act on.",
    )

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Prediction Form", "Try It")
    input_values = {}
    form_cols = st.columns(2)
    for index, col in enumerate(model_bundle["feature_cols"]):
        with form_cols[index % 2]:
            if col in model_bundle["numeric_features"]:
                input_values[col] = st.number_input(
                    col,
                    value=float(model_bundle["defaults"][col]),
                    key=f"pred_input_{col}",
                )
            else:
                choices = model_bundle["categorical_choices"][col]
                default_value = model_bundle["defaults"][col]
                default_index = choices.index(default_value) if default_value in choices else 0
                input_values[col] = st.selectbox(
                    col,
                    choices,
                    index=default_index,
                    key=f"pred_input_{col}",
                )

    if st.button("Generate Prediction"):
        input_df = pd.DataFrame([input_values])
        for col in model_bundle["numeric_features"]:
            input_df[col] = pd.to_numeric(input_df[col], errors="coerce").fillna(model_bundle["defaults"][col])
        for col in model_bundle["categorical_features"]:
            input_df[col] = input_df[col].fillna(model_bundle["defaults"][col]).astype(str)

        input_encoded = pd.get_dummies(input_df, columns=model_bundle["categorical_features"], dummy_na=False)
        input_encoded = input_encoded.reindex(columns=model_bundle["training_columns"], fill_value=0)

        prediction = model_bundle["model"].predict(input_encoded)[0]

        if model_bundle["model_type"] == "regression":
            prediction_text = f"{prediction:,.2f}"
            summary = f"Velora predicts that `{selected_target}` will be about {prediction:,.2f} for the values you entered."
        else:
            prediction_text = str(prediction)
            summary = f"Velora predicts that `{selected_target}` will most likely be `{prediction}` for the values you entered."

        st.success("Prediction ready.")
        st.metric("Predicted Result", prediction_text)
        write_plain_summary("Prediction in plain English", summary)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("What Influences This Prediction Most", "Importance")
    fig = px.bar(
        model_bundle["feature_importance"].sort_values("Importance"),
        x="Importance",
        y="Feature",
        orientation="h",
        text="Importance",
        color_discrete_sequence=[ACCENT],
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    style_figure(fig, height=360)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    write_plain_summary(
        "What this chart means",
        "The features at the top had the biggest impact on the model's decision. "
        "This does not prove cause and effect, but it does show which fields the model relied on most.",
    )

    if model_bundle["model_type"] == "classification" and model_bundle["confusion_df"] is not None:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Confusion Matrix", "Explainability")
        cm_df = model_bundle["confusion_df"]
        fig = px.imshow(
            cm_df,
            text_auto=True,
            color_continuous_scale="Blues",
            aspect="auto",
            labels=dict(x="Predicted", y="Actual", color="Count"),
        )
        style_figure(fig, height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        write_plain_summary(
            "How to read the confusion matrix",
            "The diagonal cells show correct predictions. Off-diagonal cells show where the model confused one category with another. "
            "This helps you explain not just how accurate the model is, but where it makes mistakes.",
        )


def build_data_prep_tab(original_df: pd.DataFrame, cleaned_df: pd.DataFrame, cleaning_summary: dict) -> None:
    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Before vs After", "Data Cleaning")
        comparison_rows = [
            ["Rows", cleaning_summary["rows_before"], cleaning_summary["rows_after"]],
            ["Missing Values", cleaning_summary["missing_before"], cleaning_summary["missing_after"]],
            ["Duplicate Rows", cleaning_summary["duplicates_before"], cleaning_summary["duplicates_after"]],
        ]
        comparison_df = pd.DataFrame(comparison_rows, columns=["Metric", "Before", "After"])
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        if cleaning_summary["actions"]:
            st.write("Applied actions:")
            for action in cleaning_summary["actions"]:
                st.write(f"- {action}")
        else:
            st.write("No cleaning actions applied yet. Use the sidebar controls to modify the dataset.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Export", "Practical Use")
        cleaned_csv = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Cleaned Dataset",
            data=cleaned_csv,
            file_name="velora_cleaned_dataset.csv",
            mime="text/csv",
        )
        summary_text = build_analysis_summary_text(cleaned_df, cleaning_summary)
        st.download_button(
            "Download Analysis Summary",
            data=summary_text.encode("utf-8"),
            file_name="velora_analysis_summary.txt",
            mime="text/plain",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Raw vs Cleaned Preview", "Proof of Impact")
    preview_left, preview_right = st.columns(2)
    with preview_left:
        st.write("Original dataset")
        st.dataframe(original_df.head(8), use_container_width=True)
    with preview_right:
        st.write("Cleaned dataset")
        st.dataframe(cleaned_df.head(8), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    write_plain_summary(
        "Why this tab matters",
        "This section proves that Velora is not only viewing data. It also helps prepare the dataset for better charts and better machine learning results.",
    )


def style_figure(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(l=12, r=12, t=20, b=12),
        height=height,
        font=dict(color=TEXT, family="Inter, Arial"),
        colorway=[PRIMARY, ACCENT, ROSE, SUCCESS, WARNING],
        hoverlabel=dict(bgcolor="#120f1a", font_color=TEXT),
        legend=dict(
            bgcolor="rgba(23, 19, 31, 0.82)",
            bordercolor="rgba(212, 162, 76, 0.14)",
            borderwidth=1,
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(239,231,219,0.08)",
        zeroline=False,
        linecolor="rgba(239,231,219,0.12)",
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(239,231,219,0.08)",
        zeroline=False,
        linecolor="rgba(239,231,219,0.12)",
    )
    return fig


def build_overview(df: pd.DataFrame) -> None:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = [
        col for col in df.columns if infer_column_role(df[col]) in {"categorical", "text"}
    ]
    missing_cells = int(df.isna().sum().sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Rows", f"{len(df):,}")
    with c2:
        kpi_card("Columns", f"{len(df.columns):,}")
    with c3:
        kpi_card("Numeric Fields", f"{len(numeric_cols):,}")
    with c4:
        kpi_card("Missing Values", f"{missing_cells:,}")

    st.markdown("")
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Data Quality Snapshot", "Integrity")
        quality_df = pd.DataFrame(
            {
                "Column": df.columns,
                "Missing Values": [int(df[col].isna().sum()) for col in df.columns],
                "Unique Values": [int(df[col].nunique(dropna=True)) for col in df.columns],
                "Detected Type": [infer_column_role(df[col]) for col in df.columns],
            }
        )
        st.dataframe(quality_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Column Type Mix", "Schema")
        type_counts = (
            pd.Series({col: infer_column_role(df[col]) for col in df.columns})
            .value_counts()
            .reset_index()
        )
        type_counts.columns = ["Type", "Count"]
        fig = px.bar(
            type_counts,
            x="Count",
            y="Type",
            orientation="h",
            color="Type",
            color_discrete_map={
                "numeric": PRIMARY,
                "categorical": ACCENT,
                "text": WARNING,
                "datetime": SUCCESS,
            },
            text="Count",
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        style_figure(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    write_plain_summary("Overview in simple words", describe_overview(df))


def build_numeric_analysis(df: pd.DataFrame) -> None:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        st.info("No numeric columns found in this dataset.")
        return

    selected_numeric = st.selectbox("Primary numeric column", numeric_cols, key="num_primary")
    compare_numeric = st.selectbox(
        "Compare with another numeric column",
        options=["None"] + numeric_cols,
        key="num_secondary",
    )

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header(f"Distribution of {selected_numeric}", "Numeric")
        fig = px.histogram(
            df,
            x=selected_numeric,
            nbins=30,
            color_discrete_sequence=[PRIMARY],
        )
        fig.update_traces(marker_line_color="rgba(255,255,255,0.08)", marker_line_width=1)
        style_figure(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Summary Statistics", "Profile")
        stats = df[selected_numeric].describe().to_frame(name="Value").reset_index()
        stats.columns = ["Statistic", "Value"]
        st.dataframe(stats, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    write_plain_summary(
        f"How to read {selected_numeric}",
        describe_numeric_column(df, selected_numeric),
    )

    if compare_numeric != "None" and compare_numeric != selected_numeric:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header(f"{selected_numeric} vs {compare_numeric}", "Comparison")
        fig = px.scatter(
            df,
            x=selected_numeric,
            y=compare_numeric,
            opacity=0.75,
            color_discrete_sequence=[ACCENT],
        )
        fig.update_traces(marker=dict(size=10, line=dict(width=1, color="rgba(255,255,255,0.08)")))
        style_figure(fig, height=420)
        st.plotly_chart(fig, use_container_width=True)
        corr = df[[selected_numeric, compare_numeric]].corr(numeric_only=True).iloc[0, 1]
        st.caption(f"Correlation: {corr:.3f}")
        st.markdown("</div>", unsafe_allow_html=True)
        write_plain_summary(
            f"Comparing {selected_numeric} and {compare_numeric}",
            describe_comparison(df, selected_numeric, compare_numeric),
        )


def build_categorical_analysis(df: pd.DataFrame) -> None:
    categorical_cols = [
        col for col in df.columns if infer_column_role(df[col]) in {"categorical", "text"}
    ]
    if not categorical_cols:
        st.info("No categorical/text columns found in this dataset.")
        return

    selected_cat = st.selectbox("Categorical column", categorical_cols, key="cat_primary")
    top_n = st.slider("Number of categories to display", 3, 15, 8)

    counts = (
        df[selected_cat]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(top_n)
        .reset_index()
    )
    counts.columns = [selected_cat, "Count"]
    counts["Share"] = (counts["Count"] / counts["Count"].sum() * 100).round(1)
    counts["Label"] = counts["Count"].astype(str) + " (" + counts["Share"].astype(str) + "%)"

    left, right = st.columns([1.1, 1])
    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header(f"Top Values in {selected_cat}", "Categories")
        fig = px.bar(
            counts,
            x="Count",
            y=selected_cat,
            orientation="h",
            text="Label",
            color_discrete_sequence=[PRIMARY],
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        style_figure(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Quick Summary", "Readout")
        st.metric("Unique categories", int(df[selected_cat].nunique(dropna=True)))
        st.metric("Missing entries", int(df[selected_cat].isna().sum()))
        st.metric(
            "Most frequent value",
            str(df[selected_cat].mode(dropna=True).iloc[0]) if not df[selected_cat].mode(dropna=True).empty else "-",
        )
        st.markdown("")
        st.dataframe(
            counts[[selected_cat, "Count", "Share"]],
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    write_plain_summary(
        f"How to read {selected_cat}",
        describe_category_counts(counts, selected_cat),
    )


def build_time_analysis(df: pd.DataFrame) -> None:
    datetime_cols = [col for col in df.columns if infer_column_role(df[col]) == "datetime"]
    if not datetime_cols:
        st.info("No datetime columns were detected automatically.")
        return

    dt_col = st.selectbox("Datetime column", datetime_cols, key="dt_primary")
    grouped = (
        df.assign(_date_bucket=df[dt_col].dt.to_period("M").astype(str))
        .groupby("_date_bucket")
        .size()
        .reset_index(name="Rows")
    )

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header(f"Rows Over Time by {dt_col}", "Timeline")
    fig = px.line(grouped, x="_date_bucket", y="Rows", markers=True)
    fig.update_traces(line_color=PRIMARY)
    fig.update_layout(xaxis_title="")
    style_figure(fig, height=380)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    write_plain_summary(
        f"How to read the timeline for {dt_col}",
        describe_time_trend(grouped, dt_col),
    )


def build_insights(df: pd.DataFrame) -> None:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = [
        col for col in df.columns if infer_column_role(df[col]) in {"categorical", "text"}
    ]

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Auto Insights", "Signals")
    bullets = []

    if numeric_cols:
        missing_by_numeric = df[numeric_cols].isna().sum().sort_values(ascending=False)
        top_missing_num = missing_by_numeric.index[0]
        bullets.append(
            f"Numeric fields detected: {len(numeric_cols)}. The field with the most missing numeric values is `{top_missing_num}`."
        )

        variability = df[numeric_cols].std(numeric_only=True).sort_values(ascending=False)
        most_variable = variability.index[0]
        bullets.append(
            f"`{most_variable}` has the highest spread among numeric columns, which usually makes it a good candidate for closer trend analysis."
        )

    if categorical_cols:
        cardinality = (
            pd.Series({col: df[col].nunique(dropna=True) for col in categorical_cols})
            .sort_values(ascending=False)
        )
        top_category = cardinality.index[0]
        bullets.append(
            f"`{top_category}` has the highest category variety among text-like columns."
        )

    duplicate_rows = int(df.duplicated().sum())
    bullets.append(f"The dataset contains {duplicate_rows} duplicate rows.")

    for bullet in bullets:
        st.write(f"- {bullet}")
    st.markdown("</div>", unsafe_allow_html=True)
    write_plain_summary(
        "Quick takeaway",
        "This section turns the dataset into a few simple observations so someone does not have to inspect every chart manually. "
        "If a field is mentioned here, it usually means it is worth paying attention to first.",
    )

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Smart Recommendations", "Signature Feature", "Action-oriented advice generated from your current dataset")
    for recommendation in generate_smart_recommendations(df):
        st.write(f"- {recommendation}")
    st.markdown("</div>", unsafe_allow_html=True)


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-head">
                <div class="sidebar-brand-logo">
                    <div class="sidebar-brand-logo-text">VL</div>
                </div>
                <div>
                    <div class="sidebar-brand-title">Velora</div>
                    <div class="sidebar-brand-copy">
                        A dark, modern workspace for CSV exploration, fast insights, and lightweight machine learning.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    sample_datasets = {
        "None": None,
        "Sales Demo": "sales_performance_dataset.csv",
        "Student Demo": "student_performance_dataset.csv",
        "Ecommerce Demo": "ecommerce_orders_dataset.csv",
        "HR Demo": "hr_employee_dataset.csv",
    }
    selected_sample = st.selectbox("Try a sample dataset", list(sample_datasets.keys()))
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    st.caption("Upload any structured CSV and the app will profile it automatically.")
    st.markdown("---")
    st.subheader("Cleaning Controls")
    fill_missing = st.selectbox(
        "Missing value handling",
        [
            "Keep as-is",
            "Fill numeric with median and categories with mode",
            "Fill everything with placeholder",
        ],
    )
    drop_missing_rows = st.checkbox("Drop rows with missing values")
    remove_duplicates = st.checkbox("Remove duplicate rows")

    if uploaded_file is not None or sample_datasets[selected_sample] is not None:
        st.success("Dataset loaded")
    else:
        st.info("No file uploaded yet")


active_sample_path = sample_datasets[selected_sample]

if uploaded_file is None and active_sample_path is None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-shell">
                <div>
                    <div class="hero-kicker">Velora / Data Workspace</div>
                    <div class="hero-title">Velora</div>
                    <div class="hero-copy">
                        Upload almost any CSV and turn it into a clean, readable analysis workspace with automatic profiling,
                        plain-English summaries, and built-in prediction tools.
                    </div>
                    <div class="pill-row">
                        <div class="pill">Dark tech interface</div>
                        <div class="pill">Works with many dataset types</div>
                        <div class="pill">Automatic profiling</div>
                        <div class="pill">Built-in ML tab</div>
                    </div>
                    <div class="hero-metrics">
                        <div class="hero-metric">
                            <div class="hero-metric-label">Mode</div>
                            <div class="hero-metric-value">Upload-first workspace</div>
                        </div>
                        <div class="hero-metric">
                            <div class="hero-metric-label">Best for</div>
                            <div class="hero-metric-value">Exploration + prediction</div>
                        </div>
                        <div class="hero-metric">
                            <div class="hero-metric-label">Style</div>
                            <div class="hero-metric-value">Dark glass / electric blue</div>
                        </div>
                    </div>
                </div>
                <div class="hero-mark-wrap">
                    <div class="hero-mark">
                        <div class="hero-mark-text">VL</div>
                    </div>
                </div>
            </div>
            <div class="feature-grid">
                <div class="feature-tile">
                    <div class="feature-title">Quality Review</div>
                    <div class="feature-copy">Missing values, duplicates, type detection, and schema-level checks in one place.</div>
                </div>
                <div class="feature-tile">
                    <div class="feature-title">Visual Exploration</div>
                    <div class="feature-copy">Readable charts with visible labels, better spacing, and cleaner comparisons.</div>
                </div>
                <div class="feature-tile">
                    <div class="feature-title">Flexible Uploads</div>
                    <div class="feature-copy">Use business, survey, operations, finance, or academic CSV datasets.</div>
                </div>
                <div class="feature-tile">
                    <div class="feature-title">Fast Readout</div>
                    <div class="feature-copy">Move from upload to insights without setup screens or manual chart building.</div>
                </div>
            </div>
            <div class="ornament-grid">
                <div class="ornament-card">
                    <div class="ornament-symbol">01</div>
                    <div class="ornament-title">Data Profiling</div>
                    <div class="ornament-copy">Automatic structure checks, missing-value review, and schema detection in a cleaner layout.</div>
                </div>
                <div class="ornament-card">
                    <div class="ornament-symbol">02</div>
                    <div class="ornament-title">Prediction Lab</div>
                    <div class="ornament-copy">Choose a target column, train a model, and test predictions without leaving the app.</div>
                </div>
                <div class="ornament-card">
                    <div class="ornament-symbol">03</div>
                    <div class="ornament-title">Readable by Design</div>
                    <div class="ornament-copy">Charts still look good, but the summaries explain them in plain language for non-technical users.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")
    a, b, c = st.columns(3)
    with a:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("1. Upload")
        st.write("Start with a CSV from finance, sales, students, HR, operations, or survey data.")
        st.markdown("</div>", unsafe_allow_html=True)
    with b:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("2. Analyze")
        st.write("The app detects column types, measures data quality, and builds charts automatically.")
        st.markdown("</div>", unsafe_allow_html=True)
    with c:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("3. Explore")
        st.write("Filter through distributions, top categories, time patterns, and raw records in one place.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    st.info("Use the sidebar on the left to upload a CSV and open the analysis workspace.")
    st.stop()


try:
    with st.spinner("Analyzing data and preparing the workspace..."):
        if uploaded_file is not None:
            source_name = uploaded_file.name
            raw_df = load_csv(uploaded_file)
        else:
            source_name = Path(active_sample_path).name
            raw_df = load_local_csv(active_sample_path)
        raw_df = try_parse_datetimes(raw_df)
        df, cleaning_summary = apply_cleaning_pipeline(
            raw_df,
            fill_missing=fill_missing,
            drop_missing_rows=drop_missing_rows,
            remove_duplicates=remove_duplicates,
        )
except Exception as exc:
    st.error(f"Could not read that CSV file: {exc}")
    st.stop()


st.markdown(
    f"""
    <div class="hero">
        <div class="hero-shell">
            <div>
                <div class="hero-kicker">Analysis Workspace</div>
                <div class="hero-title">Dataset Analysis Workspace</div>
                <div class="hero-copy">
                    Reviewing <strong>{source_name}</strong> with {len(df):,} rows and {len(df.columns):,} columns.
                </div>
                <div class="pill-row">
                    <div class="pill">{len(df):,} rows</div>
                    <div class="pill">{len(df.columns):,} columns</div>
                    <div class="pill">{int(df.isna().sum().sum()):,} missing values</div>
                </div>
                <div class="hero-metrics">
                    <div class="hero-metric">
                        <div class="hero-metric-label">Numeric fields</div>
                        <div class="hero-metric-value">{len(df.select_dtypes(include='number').columns):,}</div>
                    </div>
                    <div class="hero-metric">
                        <div class="hero-metric-label">Categorical fields</div>
                        <div class="hero-metric-value">{len([col for col in df.columns if infer_column_role(df[col]) in {'categorical', 'text'}]):,}</div>
                    </div>
                    <div class="hero-metric">
                        <div class="hero-metric-label">Detected dates</div>
                        <div class="hero-metric-value">{len([col for col in df.columns if infer_column_role(df[col]) == 'datetime']):,}</div>
                    </div>
                </div>
            </div>
            <div class="hero-mark-wrap">
                <div class="hero-mark">
                    <div class="hero-mark-text">VL</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    ["Overview", "Numeric Analysis", "Category Analysis", "Time Analysis", "Prediction Lab", "Data Prep & Export", "Data Table"]
)

with tab1:
    build_overview(df)
    st.markdown("")
    build_insights(df)

with tab2:
    build_numeric_analysis(df)

with tab3:
    build_categorical_analysis(df)

with tab4:
    build_time_analysis(df)

with tab5:
    build_prediction_lab(df)

with tab6:
    build_data_prep_tab(raw_df, df, cleaning_summary)

with tab7:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Dataset Preview", "Table")
    st.dataframe(df, use_container_width=True)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Current Dataset",
        data=csv_bytes,
        file_name=f"analyzed_{source_name}",
        mime="text/csv",
    )
    st.markdown("</div>", unsafe_allow_html=True)
