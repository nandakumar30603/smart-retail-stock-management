import streamlit as st
import pandas as pd
import numpy as np

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Retail Stock Management",
    page_icon="🛒",
    layout="wide"
)

# --------------------------------------------------
# Sample Inventory Data
# --------------------------------------------------

# --------------------------------------------------
# Load Inventory Data
# --------------------------------------------------

@st.cache_data
def load_inventory():
    return pd.read_csv("data/inventory.csv")


inventory = load_inventory()
# --------------------------------------------------
# Calculate Stock Status
# --------------------------------------------------

def get_status(row):
    if row["Stock"] <= row["Reorder_Level"]:
        return "🔴 Low Stock"
    elif row["Stock"] <= row["Reorder_Level"] * 1.5:
        return "🟡 Medium"
    else:
        return "🟢 Healthy"


inventory["Status"] = inventory.apply(get_status, axis=1)

inventory["Inventory Value"] = (
    inventory["Stock"] * inventory["Price"]
)

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🛒 Smart Retail Stock Management System")

st.markdown(
    """
    Monitor inventory levels, identify low-stock products,
    and analyze retail stock performance using a simple
    data-driven dashboard.
    """
)

st.divider()

# --------------------------------------------------
# Dashboard Metrics
# --------------------------------------------------

total_products = len(inventory)
total_units = int(inventory["Stock"].sum())
low_stock = int(
    (inventory["Stock"] <= inventory["Reorder_Level"]).sum()
)
inventory_value = inventory["Inventory Value"].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📦 Total Products",
        total_products
    )

with col2:
    st.metric(
        "🔢 Total Stock Units",
        total_units
    )

with col3:
    st.metric(
        "⚠️ Low Stock Items",
        low_stock
    )

with col4:
    st.metric(
        "💰 Inventory Value",
        f"₹{inventory_value:,.0f}"
    )

st.divider()

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------

st.sidebar.header("🔎 Inventory Filters")

categories = ["All"] + sorted(
    inventory["Category"].unique().tolist()
)

selected_category = st.sidebar.selectbox(
    "Select Category",
    categories
)

status_options = [
    "All",
    "🔴 Low Stock",
    "🟡 Medium",
    "🟢 Healthy"
]

selected_status = st.sidebar.selectbox(
    "Select Stock Status",
    status_options
)

# --------------------------------------------------
# Apply Filters
# --------------------------------------------------

filtered_data = inventory.copy()

if selected_category != "All":
    filtered_data = filtered_data[
        filtered_data["Category"] == selected_category
    ]

if selected_status != "All":
    filtered_data = filtered_data[
        filtered_data["Status"] == selected_status
    ]

# --------------------------------------------------
# Inventory Table
# --------------------------------------------------

st.subheader("📋 Inventory Overview")

display_data = filtered_data[
    [
        "Product",
        "Category",
        "Stock",
        "Reorder_Level",
        "Price",
        "Inventory Value",
        "Status"
    ]
].copy()

display_data["Price"] = display_data["Price"].apply(
    lambda x: f"₹{x:,.0f}"
)

display_data["Inventory Value"] = display_data[
    "Inventory Value"
].apply(lambda x: f"₹{x:,.0f}")

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# Low Stock Alerts
# --------------------------------------------------

st.subheader("⚠️ Stock Alerts")

low_stock_data = filtered_data[
    filtered_data["Stock"] <= filtered_data["Reorder_Level"]
]

if low_stock_data.empty:
    st.success("All selected products have sufficient stock.")
else:
    for _, row in low_stock_data.iterrows():
        st.warning(
            f"**{row['Product']}** — "
            f"Current stock: {row['Stock']} units | "
            f"Reorder level: {row['Reorder_Level']} units"
        )

# --------------------------------------------------
# Analytics
# --------------------------------------------------

st.subheader("📊 Inventory Analytics")

col1, col2 = st.columns(2)

with col1:
    st.write("### Stock by Product")

    chart_data = filtered_data.set_index("Product")[
        "Stock"
    ]

    st.bar_chart(chart_data)

with col2:
    st.write("### Inventory Value by Category")

    category_value = (
        filtered_data
        .groupby("Category")["Inventory Value"]
        .sum()
    )

    st.bar_chart(category_value)

# --------------------------------------------------
# Reorder Recommendations
# --------------------------------------------------

st.subheader("🔄 Reorder Recommendations")

if low_stock_data.empty:
    st.info("No products currently require replenishment.")
else:
    reorder_data = low_stock_data[
        ["Product", "Stock", "Reorder_Level"]
    ].copy()

    reorder_data["Recommended Order"] = (
        reorder_data["Reorder_Level"]
        - reorder_data["Stock"]
        + reorder_data["Reorder_Level"]
    )

    st.dataframe(
        reorder_data,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Smart Retail Stock Management | "
    "Python • Streamlit • Pandas • NumPy"
)
