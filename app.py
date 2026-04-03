import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Overview Dashboard", layout="wide")

REQUIRED_COLUMNS = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Dispatch Date",
    "Delivery Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "City",
    "State/Province",
    "Country/Region",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
]


def missing_required_columns(df: pd.DataFrame) -> list[str]:
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


# -----------------------------
# Helpers
# -----------------------------
@st.cache_data
def load_data(file_obj) -> pd.DataFrame:
    if file_obj is None:
        raise ValueError("No CSV file provided.")

    # Streamlit uploaded files are BytesIO-like; rewinding avoids partial reads
    # on reruns after previous reads.
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)

    df = pd.read_csv(file_obj)

    # Clean column names
    df.columns = [c.strip() for c in df.columns]

    missing_cols = missing_required_columns(df)
    if missing_cols:
        raise ValueError(
            "Dataset schema mismatch. Missing required columns: "
            + ", ".join(missing_cols)
        )

    # Parse dates
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    if "Dispatch Date" in df.columns:
        df["Dispatch Date"] = pd.to_datetime(df["Dispatch Date"], errors="coerce")

    # Numeric conversions
    numeric_cols = ["Sales", "Quantity", "Discount", "Profit"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Extra fields
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)

    return df


def pct_change(curr: float, prev: float):
    if prev is None or prev == 0 or pd.isna(prev):
        return None
    return (curr - prev) / prev


def format_delta(delta):
    if delta is None:
        return "N/A"
    arrow = "▲" if delta >= 0 else "▼"
    return f"{arrow} {abs(delta)*100:.1f}% vs. PY"


def metric_value(df: pd.DataFrame, metric: str) -> float:
    if metric == "Sales":
        return df["Sales"].sum()
    elif metric == "Profit":
        return df["Profit"].sum()
    elif metric == "Orders":
        return df["Order ID"].nunique()
    else:
        raise ValueError("Unsupported metric")


def currency_or_number(value, metric):
    if metric in ["Sales", "Profit"]:
        return f"${value:,.1f}"
    return f"{int(value):,}"


def simple_kpi_card(title, value, delta_text):
    st.markdown(
        f"""
        <div style="
            background-color:white;
            padding:18px 20px;
            border:1px solid #E6EAF2;
            border-radius:10px;
            height:120px;
            box-shadow:0 0 0 rgba(0,0,0,0);">
            <div style="font-size:12px; letter-spacing:2px; color:#6B7280; font-weight:600;">{title.upper()}</div>
            <div style="font-size:20px; font-weight:700; margin-top:12px; color:#3A3A3A;">{value}</div>
            <div style="font-size:13px; color:#16A34A; margin-top:10px;">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def chart_container(fig, title):
    st.markdown(
        f"""
        <div style="font-size:16px; font-weight:600; margin-bottom:8px; color:#3A3A3A;">
            {title}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Load data
# -----------------------------
st.sidebar.header("Data")
base_dir = Path(__file__).resolve().parent
default_candidates = [
    base_dir / "data" / "demo" / "Orders.csv",
    base_dir / "Orders.csv",
    base_dir / "orders.csv",
]
default_file = next((p for p in default_candidates if p.exists()), None)
template_csv_path = base_dir / "data" / "template" / "orders_template.csv"
data_source_option = st.sidebar.radio(
    "Data source",
    ["Use bundled demo (Orders.csv)", "Upload your own CSV"],
)
uploaded_file = None
if data_source_option == "Upload your own CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

with st.sidebar.expander("Required CSV columns", expanded=False):
    st.code(", ".join(REQUIRED_COLUMNS))
template_csv_content = ",".join(REQUIRED_COLUMNS) + "\n"
if template_csv_path.exists():
    template_csv_content = template_csv_path.read_text(encoding="utf-8")
st.sidebar.download_button(
    label="Download template CSV",
    data=template_csv_content,
    file_name="orders_template.csv",
    mime="text/csv",
)

if data_source_option == "Use bundled demo (Orders.csv)":
    source = default_file
    if source is None:
        st.error("Bundled demo not found. Add `data/demo/Orders.csv` or choose 'Upload your own CSV'.")
        st.stop()
else:
    source = uploaded_file
    if source is None:
        st.info("Upload a CSV file to continue.")
        st.stop()

df = None
try:
    df = load_data(source)
except Exception as exc:
    st.error(f"Could not load CSV: {exc}")
    st.stop()

if df is None:
    st.stop()

if df["Order Date"].isna().all():
    st.error("Could not parse 'Order Date'. Check date format in your CSV.")
    st.stop()

# -----------------------------
# Filters
# -----------------------------
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 1rem;}
    </style>
    """,
    unsafe_allow_html=True
)

header_left, header_mid, header_right = st.columns([3, 2, 2])

with header_left:
    st.markdown(
        "<h1 style='margin-bottom:0; color:#4B5563; font-weight:500;'>Overview Dashboard</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='color:#6B7280; margin-bottom:8px;'>Commercial performance view based on your order dataset</div>",
        unsafe_allow_html=True
    )

with header_mid:
    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

with header_right:
    metric_choice = st.radio(
        "Metric",
        ["Sales", "Profit", "Orders"],
        horizontal=True
    )

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    (df["Order Date"].dt.date >= start_date) &
    (df["Order Date"].dt.date <= end_date)
].copy()

# Optional side filters
with st.sidebar:
    st.header("Filters")

    regions = st.multiselect(
        "Region",
        options=sorted(filtered["Region"].dropna().unique()),
        default=sorted(filtered["Region"].dropna().unique())
    )

    segments = st.multiselect(
        "Segment",
        options=sorted(filtered["Segment"].dropna().unique()),
        default=sorted(filtered["Segment"].dropna().unique())
    )

    categories = st.multiselect(
        "Category",
        options=sorted(filtered["Category"].dropna().unique()),
        default=sorted(filtered["Category"].dropna().unique())
    )

filtered = filtered[
    filtered["Region"].isin(regions) &
    filtered["Segment"].isin(segments) &
    filtered["Category"].isin(categories)
].copy()

# -----------------------------
# Previous year comparison
# -----------------------------
days_selected = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days
prev_start = pd.Timestamp(start_date) - pd.DateOffset(years=1)
prev_end = pd.Timestamp(end_date) - pd.DateOffset(years=1)

prev_df = df[
    (df["Order Date"] >= prev_start) &
    (df["Order Date"] <= prev_end) &
    (df["Region"].isin(regions)) &
    (df["Segment"].isin(segments)) &
    (df["Category"].isin(categories))
].copy()

# KPI values
curr_sales = filtered["Sales"].sum()
prev_sales = prev_df["Sales"].sum()

curr_profit = filtered["Profit"].sum()
prev_profit = prev_df["Profit"].sum()

curr_orders = filtered["Order ID"].nunique()
prev_orders = prev_df["Order ID"].nunique()

curr_customers = filtered["Customer ID"].nunique() if "Customer ID" in filtered.columns else filtered["Customer Name"].nunique()
prev_customers = prev_df["Customer ID"].nunique() if "Customer ID" in prev_df.columns else prev_df["Customer Name"].nunique()

sales_delta = pct_change(curr_sales, prev_sales)
profit_delta = pct_change(curr_profit, prev_profit)
orders_delta = pct_change(curr_orders, prev_orders)
customers_delta = pct_change(curr_customers, prev_customers)

# -----------------------------
# KPI cards
# -----------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    simple_kpi_card("Sales", f"${curr_sales:,.1f}", format_delta(sales_delta))
with c2:
    simple_kpi_card("Profit", f"${curr_profit:,.1f}", format_delta(profit_delta))
with c3:
    simple_kpi_card("Orders", f"{curr_orders:,}", format_delta(orders_delta))
with c4:
    simple_kpi_card("Customers", f"{curr_customers:,}", format_delta(customers_delta))

st.write("")

# -----------------------------
# Chart 1: Metric by Region
# -----------------------------
row1_col1, row1_col2, row1_col3 = st.columns(3)

metric_col = metric_choice if metric_choice != "Orders" else "Order ID"

with row1_col1:
    if metric_choice == "Orders":
        region_df = (
            filtered.groupby("Region")["Order ID"]
            .nunique()
            .reset_index(name="Value")
            .sort_values("Value", ascending=False)
        )
    else:
        region_df = (
            filtered.groupby("Region")[metric_choice]
            .sum()
            .reset_index(name="Value")
            .sort_values("Value", ascending=False)
        )

    fig_region = px.bar(
        region_df,
        x="Region",
        y="Value",
        text="Value"
    )
    fig_region.update_traces(marker_color="#7AA6FF")
    fig_region.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    chart_container(fig_region, f"{metric_choice} | By Region")

# -----------------------------
# Chart 2: Metric by Segment
# -----------------------------
with row1_col2:
    if metric_choice == "Orders":
        segment_df = (
            filtered.groupby("Segment")["Order ID"]
            .nunique()
            .reset_index(name="Value")
            .sort_values("Value", ascending=False)
        )
    else:
        segment_df = (
            filtered.groupby("Segment")[metric_choice]
            .sum()
            .reset_index(name="Value")
            .sort_values("Value", ascending=False)
        )

    fig_segment = px.bar(
        segment_df,
        x="Segment",
        y="Value",
        text="Value"
    )
    fig_segment.update_traces(marker_color=["#7AA6FF", "#D8DEE9", "#D8DEE9"])
    fig_segment.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    chart_container(fig_segment, f"{metric_choice} | By Segment")

# -----------------------------
# Chart 3: Top 10 Products
# -----------------------------
with row1_col3:
    if metric_choice == "Orders":
        product_df = (
            filtered.groupby("Product Name")["Order ID"]
            .nunique()
            .reset_index(name="Value")
            .sort_values("Value", ascending=False)
            .head(10)
        )
    else:
        product_df = (
            filtered.groupby("Product Name")[metric_choice]
            .sum()
            .reset_index(name="Value")
            .sort_values("Value", ascending=False)
            .head(10)
        )

    fig_products = px.bar(
        product_df.sort_values("Value", ascending=True),
        x="Value",
        y="Product Name",
        orientation="h",
        text="Value"
    )
    fig_products.update_traces(marker_color="#7AA6FF")
    fig_products.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    chart_container(fig_products, f"{metric_choice} | By Top 10 Products")

# -----------------------------
# Row 2
# -----------------------------
row2_col1, row2_col2, row2_col3 = st.columns(3)

# Sales by Category
with row2_col1:
    cat_df = (
        filtered.groupby("Category")[metric_choice].sum().reset_index(name="Value")
        if metric_choice != "Orders"
        else filtered.groupby("Category")["Order ID"].nunique().reset_index(name="Value")
    )
    cat_df = cat_df.sort_values("Value", ascending=False)

    fig_cat = px.bar(
        cat_df,
        x="Category",
        y="Value",
        text="Value"
    )
    fig_cat.update_traces(marker_color=["#7AA6FF", "#D8DEE9", "#D8DEE9"])
    fig_cat.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    chart_container(fig_cat, f"{metric_choice} | By Category")

# Sales by Sub-Category
with row2_col2:
    if metric_choice == "Orders":
        sub_df = (
            filtered.groupby("Sub-Category")["Order ID"]
            .nunique()
            .reset_index(name="Value")
            .sort_values("Value", ascending=False)
            .head(10)
        )
    else:
        sub_df = (
            filtered.groupby("Sub-Category")[metric_choice]
            .sum()
            .reset_index(name="Value")
            .sort_values("Value", ascending=False)
            .head(10)
        )

    fig_sub = px.bar(
        sub_df.sort_values("Value", ascending=True),
        x="Value",
        y="Sub-Category",
        orientation="h",
        text="Value"
    )
    fig_sub.update_traces(marker_color="#7AA6FF")
    fig_sub.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    chart_container(fig_sub, f"{metric_choice} | By Sub-Category")

# Top 10 Customers
with row2_col3:
    if metric_choice == "Orders":
        cust_df = (
            filtered.groupby("Customer Name")["Order ID"]
            .nunique()
            .reset_index(name="Value")
            .sort_values("Value", ascending=False)
            .head(10)
        )
    else:
        cust_df = (
            filtered.groupby("Customer Name")[metric_choice]
            .sum()
            .reset_index(name="Value")
            .sort_values("Value", ascending=False)
            .head(10)
        )

    fig_cust = px.bar(
        cust_df.sort_values("Value", ascending=True),
        x="Value",
        y="Customer Name",
        orientation="h",
        text="Value"
    )
    fig_cust.update_traces(marker_color="#7AA6FF")
    fig_cust.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    chart_container(fig_cust, f"{metric_choice} | By Top 10 Customers")

# -----------------------------
# Sales trend
# -----------------------------
st.write("")
trend_df = (
    filtered.groupby(pd.Grouper(key="Order Date", freq="ME"))[metric_choice].sum().reset_index(name="Value")
    if metric_choice != "Orders"
    else filtered.groupby(pd.Grouper(key="Order Date", freq="ME"))["Order ID"].nunique().reset_index(name="Value")
)

fig_trend = px.line(
    trend_df,
    x="Order Date",
    y="Value",
    markers=True
)
fig_trend.update_traces(line_color="#7AA6FF")
fig_trend.update_layout(
    height=350,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="",
    yaxis_title="",
    plot_bgcolor="white",
    paper_bgcolor="white"
)
chart_container(fig_trend, f"Monthly {metric_choice} Trend")
