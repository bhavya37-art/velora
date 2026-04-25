import math

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Velora",
    page_icon="DS",
    layout="wide",
    initial_sidebar_state="expanded",
)


PRIMARY = "#2563eb"
ACCENT = "#7c3aed"
SUCCESS = "#16a34a"
WARNING = "#d97706"
SURFACE = "#ffffff"
BACKGROUND = "#f5f7fb"
TEXT = "#0f172a"
MUTED = "#64748b"


st.markdown(
    f"""
    <style>
        .stApp {{
            background: {BACKGROUND};
            color: {TEXT};
        }}

        .hero {{
            padding: 2.2rem 2rem 2rem 2rem;
            background: linear-gradient(135deg, rgba(37,99,235,0.08), rgba(124,58,237,0.08));
            border: 1px solid rgba(148,163,184,0.25);
            border-radius: 8px;
        }}

        .hero-title {{
            font-size: 2.3rem;
            font-weight: 700;
            color: {TEXT};
            margin-bottom: 0.5rem;
        }}

        .hero-copy {{
            font-size: 1rem;
            color: {MUTED};
            max-width: 760px;
            margin-bottom: 1rem;
        }}

        .section-card {{
            background: {SURFACE};
            border: 1px solid rgba(148,163,184,0.22);
            border-radius: 8px;
            padding: 1rem 1rem 0.9rem 1rem;
        }}

        .kpi-card {{
            background: {SURFACE};
            border: 1px solid rgba(148,163,184,0.22);
            border-radius: 8px;
            padding: 1rem;
        }}

        .kpi-label {{
            font-size: 0.84rem;
            color: {MUTED};
            margin-bottom: 0.35rem;
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
            background: rgba(37,99,235,0.08);
            border: 1px solid rgba(37,99,235,0.16);
            color: {PRIMARY};
            border-radius: 999px;
            padding: 0.3rem 0.7rem;
            font-size: 0.85rem;
            font-weight: 600;
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
        st.subheader("Data Quality Snapshot")
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
        st.subheader("Column Type Mix")
        type_counts = (
            pd.Series({col: infer_column_role(df[col]) for col in df.columns})
            .value_counts()
            .reset_index()
        )
        type_counts.columns = ["Type", "Count"]
        fig = px.pie(
            type_counts,
            names="Type",
            values="Count",
            hole=0.55,
            color="Type",
            color_discrete_map={
                "numeric": PRIMARY,
                "categorical": ACCENT,
                "text": WARNING,
                "datetime": SUCCESS,
            },
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=10),
            legend_title_text="",
            height=360,
        )
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
        st.subheader(f"Distribution of {selected_numeric}")
        fig = px.histogram(
            df,
            x=selected_numeric,
            nbins=30,
            color_discrete_sequence=[PRIMARY],
        )
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=360)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Summary Statistics")
        stats = df[selected_numeric].describe().to_frame(name="Value").reset_index()
        stats.columns = ["Statistic", "Value"]
        st.dataframe(stats, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if compare_numeric != "None" and compare_numeric != selected_numeric:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader(f"{selected_numeric} vs {compare_numeric}")
        fig = px.scatter(
            df,
            x=selected_numeric,
            y=compare_numeric,
            opacity=0.75,
            color_discrete_sequence=[ACCENT],
        )
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=420)
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

    left, right = st.columns([1.1, 1])
    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader(f"Top Values in {selected_cat}")
        fig = px.bar(
            counts,
            x="Count",
            y=selected_cat,
            orientation="h",
            color="Count",
            color_continuous_scale=["#dbeafe", PRIMARY],
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Quick Summary")
        st.metric("Unique categories", int(df[selected_cat].nunique(dropna=True)))
        st.metric("Missing entries", int(df[selected_cat].isna().sum()))
        st.metric(
            "Most frequent value",
            str(df[selected_cat].mode(dropna=True).iloc[0]) if not df[selected_cat].mode(dropna=True).empty else "-",
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
    st.subheader(f"Rows Over Time by {dt_col}")
    fig = px.line(grouped, x="_date_bucket", y="Rows", markers=True)
    fig.update_traces(line_color=PRIMARY)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=380, xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def build_insights(df: pd.DataFrame) -> None:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = [
        col for col in df.columns if infer_column_role(df[col]) in {"categorical", "text"}
    ]

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Auto Insights")
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
    st.header("Workspace")
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
            <div class="hero-title">Velora</div>
            <div class="hero-copy">
                Upload almost any CSV dataset and get an instant analysis workspace with data quality checks,
                schema detection, summary metrics, charts, distributions, category breakdowns, and quick insights.
            </div>
            <div class="pill-row">
                <div class="pill">Upload-first experience</div>
                <div class="pill">Works with many dataset types</div>
                <div class="pill">Automatic profiling</div>
                <div class="pill">Interactive charts</div>
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
        <div class="hero-title">Dataset Analysis Workspace</div>
        <div class="hero-copy">
            Reviewing <strong>{uploaded_file.name}</strong> with {len(df):,} rows and {len(df.columns):,} columns.
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
    st.subheader("Dataset Preview")
    st.dataframe(df, use_container_width=True)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Current Dataset",
        data=csv_bytes,
        file_name=f"analyzed_{uploaded_file.name}",
        mime="text/csv",
    )
    st.markdown("</div>", unsafe_allow_html=True)
