import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Product Profitability Dashboard",
    layout="wide"
)

st.title("📊 Product Profitability Dashboard")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("cleaned_sales_data2.csv")

# Convert date column
df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    format="%d-%m-%Y"
)

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

start_date, end_date = st.sidebar.date_input(
    "Date Range",
    value=(
        df["Order Date"].min(),
        df["Order Date"].max()
    )
)

division_filter = st.sidebar.multiselect(
    "Division",
    options=sorted(df["Division"].dropna().unique()),
    default=sorted(df["Division"].dropna().unique())
)

margin_threshold = st.sidebar.slider(
    "Minimum Margin %",
    min_value=0.0,
    max_value=float(df["Gross_Margin_%"].max()),
    value=0.0
)

product_search = st.sidebar.text_input(
    "Search Product"
)

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df[
    (df["Order Date"] >= pd.to_datetime(start_date)) &
    (df["Order Date"] <= pd.to_datetime(end_date)) &
    (df["Division"].isin(division_filter)) &
    (df["Gross_Margin_%"] >= margin_threshold)
]

if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(
            product_search,
            case=False,
            na=False
        )
    ]

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

total_revenue = filtered_df["Sales"].sum()

total_profit = filtered_df["Total_Profit"].sum()

avg_margin = filtered_df["Gross_Margin_%"].mean()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Revenue",
    f"${total_revenue:,.0f}"
)

col2.metric(
    "Profit",
    f"${total_profit:,.0f}"
)

col3.metric(
    "Avg Margin %",
    f"{avg_margin:.2f}%"
)

st.divider()

# --------------------------------------------------
# PRODUCT PROFITABILITY OVERVIEW
# --------------------------------------------------

st.header("Product Profitability Overview")

product_summary = filtered_df.groupby("Product Name").agg(
    Revenue=("Sales", "sum"),
    Profit=("Total_Profit", "sum"),
    Margin=("Gross_Margin_%", "mean")
).reset_index()

top_margin = product_summary.sort_values(
    "Margin",
    ascending=False
).head(10)

st.subheader("Top Margin Products")

st.dataframe(top_margin)

profit_chart = product_summary.sort_values(
    "Profit",
    ascending=False
).head(10)

fig_profit = px.bar(
    profit_chart,
    x="Product Name",
    y="Profit",
    title="Top Profit Contributing Products"
)

st.plotly_chart(
    fig_profit,
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# DIVISION PERFORMANCE DASHBOARD
# --------------------------------------------------

st.header("Division Performance Dashboard")

division_summary = filtered_df.groupby("Division").agg(
    Revenue=("Sales", "sum"),
    Profit=("Total_Profit", "sum"),
    Margin=("Gross_Margin_%", "mean")
).reset_index()

st.dataframe(division_summary)

fig_division = px.bar(
    division_summary,
    x="Division",
    y=["Revenue", "Profit"],
    barmode="group",
    title="Revenue vs Profit by Division"
)

st.plotly_chart(
    fig_division,
    use_container_width=True
)

fig_margin = px.box(
    filtered_df,
    x="Division",
    y="Gross_Margin_%",
    title="Margin Distribution by Division"
)

st.plotly_chart(
    fig_margin,
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# COST VS SALES DIAGNOSTICS
# --------------------------------------------------

st.header("Cost vs Sales Diagnostics")

correlation = filtered_df["Cost"].corr(
    filtered_df["Sales"]
)

st.metric(
    "Cost-Sales Correlation",
    f"{correlation:.2f}"
)

fig_scatter = px.scatter(
    filtered_df,
    x="Cost",
    y="Sales",
    color="Gross_Margin_%",
    title="Cost vs Sales Scatter Analysis"
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)

margin_risk = filtered_df[
    filtered_df["Gross_Margin_%"]
    < filtered_df["Gross_Margin_%"].mean()
]

st.subheader("Margin Risk Products")

st.dataframe(
    margin_risk[
        [
            "Product Name",
            "Gross_Margin_%",
            "Total_Profit"
        ]
    ].head(100)
)

st.divider()

# --------------------------------------------------
# PARETO ANALYSIS
# --------------------------------------------------

st.header("Profit Concentration Analysis")

revenue_pareto = filtered_df.groupby(
    "Product Name"
)["Sales"].sum().reset_index()

revenue_pareto = revenue_pareto.sort_values(
    "Sales",
    ascending=False
)

revenue_pareto["Cum_Revenue_%"] = (
    revenue_pareto["Sales"].cumsum()
    /
    revenue_pareto["Sales"].sum()
) * 100

fig_pareto = px.line(
    revenue_pareto,
    x=revenue_pareto.index,
    y="Cum_Revenue_%",
    title="Revenue Pareto Analysis"
)

st.plotly_chart(
    fig_pareto,
    use_container_width=True
)

profit_pareto = filtered_df.groupby(
    "Product Name"
)["Total_Profit"].sum().reset_index()

profit_pareto = profit_pareto.sort_values(
    "Total_Profit",
    ascending=False
)

profit_pareto["Cum_Profit_%"] = (
    profit_pareto["Total_Profit"].cumsum()
    /
    profit_pareto["Total_Profit"].sum()
) * 100

fig_profit_pareto = px.line(
    profit_pareto,
    x=profit_pareto.index,
    y="Cum_Profit_%",
    title="Profit Pareto Analysis"
)

st.plotly_chart(
    fig_profit_pareto,
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# RECOMMENDATION SUMMARY
# --------------------------------------------------

if "Recommendation" in filtered_df.columns:

    st.header("Product Recommendations")

    recommendation_summary = (
        filtered_df["Recommendation"]
        .value_counts()
        .reset_index()
    )

    recommendation_summary.columns = [
        "Recommendation",
        "Count"
    ]

    fig_recommendation = px.pie(
        recommendation_summary,
        names="Recommendation",
        values="Count",
        title="Recommendation Distribution"
    )

    st.plotly_chart(
        fig_recommendation,
        use_container_width=True
    )

    st.dataframe(recommendation_summary)

# --------------------------------------------------
# RAW DATA
# --------------------------------------------------

with st.expander("View Filtered Dataset"):
    st.dataframe(filtered_df)