import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Velora",
    page_icon="DS",
    layout="wide",
    initial_sidebar_state="expanded",
)


PRIMARY = "#d4a24c"
ACCENT = "#8f5cf6"
SUCCESS = "#4fbf8f"
WARNING = "#d1703c"
ROSE = "#e879c6"
SURFACE = "#17131f"
SURFACE_ALT = "#221a2c"
BACKGROUND = "#0d0a13"
TEXT = "#efe7db"
MUTED = "#b2a6c2"
BORDER = "rgba(212, 162, 76, 0.18)"
PLOT_BG = "#17131f"


st.markdown(
    f"""
    <style>
        .stApp {{
            background: {BACKGROUND};
            color: {TEXT};
            background-image:
                radial-gradient(circle at top left, rgba(143,92,246,0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(209,112,60,0.15), transparent 24%),
                radial-gradient(circle at bottom center, rgba(232,121,198,0.08), transparent 30%),
                linear-gradient(180deg, rgba(255,255,255,0.02), transparent 20%);
        }}

        .main .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 1420px;
        }}

        [data-testid="stSidebar"] {{
            background:
                linear-gradient(180deg, rgba(18, 13, 27, 0.98), rgba(11, 9, 17, 0.98)),
                url("https://images.unsplash.com/photo-1518709268805-4e9042af2176?auto=format&fit=crop&w=900&q=80");
            background-size: cover;
            background-position: center;
            border-right: 1px solid rgba(212, 162, 76, 0.14);
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
            background: rgba(23, 19, 31, 0.75);
            border: 1px dashed rgba(212, 162, 76, 0.34);
            border-radius: 18px;
            padding: 0.5rem;
        }}

        h1, h2, h3 {{
            letter-spacing: 0;
        }}

        h1, h2 {{
            font-family: Georgia, "Times New Roman", serif;
        }}

        .hero {{
            position: relative;
            overflow: hidden;
            padding: 2.9rem 2.6rem 2.35rem 2.6rem;
            background:
                linear-gradient(135deg, rgba(13,10,19,0.82), rgba(30,19,40,0.88)),
                url("https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=1600&q=80");
            background-size: cover;
            background-position: center;
            border: 1px solid {BORDER};
            border-radius: 24px;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.35);
        }}

        .hero::before {{
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 20% 20%, rgba(212,162,76,0.18), transparent 25%),
                linear-gradient(90deg, rgba(13,10,19,0.84), rgba(13,10,19,0.35));
            pointer-events: none;
        }}

        .hero::after {{
            content: "";
            position: absolute;
            inset: auto -8% -42% auto;
            width: 420px;
            height: 420px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(212,162,76,0.16), transparent 66%);
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
            background: rgba(10, 8, 15, 0.46);
            border: 1px solid rgba(239,231,219,0.1);
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
                linear-gradient(180deg, rgba(34, 26, 44, 0.95), rgba(23, 19, 31, 0.98));
            border: 1px solid rgba(212, 162, 76, 0.14);
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
            color: {PRIMARY};
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            font-weight: 700;
        }}

        .kpi-card {{
            background:
                linear-gradient(180deg, rgba(34, 26, 44, 0.96), rgba(20, 16, 28, 0.96));
            border: 1px solid rgba(212, 162, 76, 0.18);
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
            background: rgba(212,162,76,0.12);
            border: 1px solid rgba(212,162,76,0.26);
            color: #f8d998;
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
            background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
            border: 1px solid rgba(239,231,219,0.08);
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
            border: 1px solid rgba(212, 162, 76, 0.16);
            background:
                linear-gradient(180deg, rgba(31, 23, 42, 0.95), rgba(17, 13, 24, 0.96));
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 18px 34px rgba(0,0,0,0.2);
            padding: 1rem;
        }}

        .ornament-symbol {{
            font-size: 1.4rem;
            color: {PRIMARY};
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
            border: 1px solid rgba(212, 162, 76, 0.18);
            background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
            margin-bottom: 1rem;
        }}

        .sidebar-brand-title {{
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.55rem;
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
            border: 1px solid rgba(212, 162, 76, 0.14);
            color: {MUTED};
            padding: 0.45rem 0.9rem;
        }}

        [data-testid="stTabs"] button[aria-selected="true"] {{
            background: linear-gradient(90deg, rgba(212,162,76,0.18), rgba(143,92,246,0.18));
            color: {TEXT};
            border-color: rgba(212, 162, 76, 0.3);
        }}

        [data-testid="stMetric"] {{
            background: linear-gradient(180deg, rgba(34, 26, 44, 0.95), rgba(23, 19, 31, 0.98));
            border: 1px solid rgba(212, 162, 76, 0.14);
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
            border: 1px solid rgba(212, 162, 76, 0.12);
        }}

        .stAlert {{
            background: rgba(34, 26, 44, 0.92);
            color: {TEXT};
            border: 1px solid rgba(212, 162, 76, 0.16);
        }}

        .stSelectbox label, .stSlider label {{
            color: {MUTED};
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {{
            background: rgba(18, 14, 24, 0.9);
            border-color: rgba(212, 162, 76, 0.18);
            border-radius: 14px;
        }}

        .stDownloadButton button, .stButton button {{
            background: linear-gradient(90deg, rgba(212,162,76,0.22), rgba(143,92,246,0.18));
            color: {TEXT};
            border: 1px solid rgba(212,162,76,0.25);
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


def style_figure(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(l=12, r=12, t=20, b=12),
        height=height,
        font=dict(color=TEXT, family="Inter, Arial"),
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


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">Velora</div>
            <div class="sidebar-brand-copy">
                A dramatic little observatory for CSVs, strange patterns, and unexpectedly pretty evidence.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    st.caption("Upload any structured CSV and the app will profile it automatically.")

    if uploaded_file is not None:
        st.success("Dataset loaded")
    else:
        st.info("No file uploaded yet")


if uploaded_file is None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Velora / Archive Session</div>
            <div class="hero-title">Velora</div>
            <div class="hero-copy">
                A moody little analysis studio for chaotic CSVs. Upload almost any dataset and Velora turns it into
                a readable artifact with structure detection, data-quality checks, visible category summaries,
                distributions, and fast exploratory visuals.
            </div>
            <div class="pill-row">
                <div class="pill">Dark archive aesthetic</div>
                <div class="pill">Works with many dataset types</div>
                <div class="pill">Automatic profiling</div>
                <div class="pill">Visible labels, not hover traps</div>
            </div>
            <div class="hero-metrics">
                <div class="hero-metric">
                    <div class="hero-metric-label">Mode</div>
                    <div class="hero-metric-value">Upload-first studio</div>
                </div>
                <div class="hero-metric">
                    <div class="hero-metric-label">Best for</div>
                    <div class="hero-metric-value">Exploration + storyfinding</div>
                </div>
                <div class="hero-metric">
                    <div class="hero-metric-label">Visual language</div>
                    <div class="hero-metric-value">Dark archive / ember violet</div>
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
                    <div class="ornament-title">Dark Academia Spine</div>
                    <div class="ornament-copy">Ink-dark surfaces, brass highlights, serif display type, and a little old-library drama.</div>
                </div>
                <div class="ornament-card">
                    <div class="ornament-symbol">02</div>
                    <div class="ornament-title">Dragon Core Edge</div>
                    <div class="ornament-copy">Smoky violet, ember copper, and jewel-tone accents that make charts feel less corporate and more collectible.</div>
                </div>
                <div class="ornament-card">
                    <div class="ornament-symbol">03</div>
                    <div class="ornament-title">Readable by Design</div>
                    <div class="ornament-copy">Counts, shares, and type mix are shown directly so you do not have to hunt for the meaning with a cursor.</div>
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
    df = load_csv(uploaded_file)
    df = try_parse_datetimes(df)
except Exception as exc:
    st.error(f"Could not read that CSV file: {exc}")
    st.stop()


st.markdown(
    f"""
    <div class="hero">
        <div class="hero-kicker">Analysis Workspace</div>
        <div class="hero-title">Dataset Analysis Workspace</div>
        <div class="hero-copy">
            Reviewing <strong>{uploaded_file.name}</strong> with {len(df):,} rows and {len(df.columns):,} columns.
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
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Numeric Analysis", "Category Analysis", "Time Analysis", "Data Table"]
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
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Dataset Preview", "Table")
    st.dataframe(df, use_container_width=True)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Current Dataset",
        data=csv_bytes,
        file_name=f"analyzed_{uploaded_file.name}",
        mime="text/csv",
    )
    st.markdown("</div>", unsafe_allow_html=True)
