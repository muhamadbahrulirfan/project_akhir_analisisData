import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# =========================
# LOAD DATA (HASIL MERGE)
# =========================
df = pd.read_csv("all_data.csv")

# =========================
# PREPROCESSING
# =========================
df['order_date'] = pd.to_datetime(df['order_purchase_timestamp'])
df['delivery_date'] = pd.to_datetime(df['order_delivered_customer_date'])

# delivery time
df['delivery_time'] = (df['delivery_date'] - df['order_date']).dt.days

# total price
df['total_price'] = df['price'] + df['freight_value']

# rename kategori
df['product_name'] = df['product_category_name_english']

# quantity
df['quantity'] = 1


# =========================
# SIDEBAR FILTER
# =========================
min_date = df["order_date"].min()
max_date = df["order_date"].max()

with st.sidebar:
    st.header("Filter Data")
    start_date, end_date = st.date_input(
        "Pilih Rentang Tanggal",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# filter
main_df = df[(df["order_date"] >= pd.to_datetime(start_date)) &
             (df["order_date"] <= pd.to_datetime(end_date))]


# =========================
# DASHBOARD
# =========================
st.title("E-Commerce Dashboard")

# =========================
# DAILY ORDERS
# =========================
st.subheader("Daily Orders & Revenue")

daily_orders = main_df.resample(rule='D', on='order_date').agg({
    "order_id": "nunique",
    "total_price": "sum"
}).reset_index()

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Orders", daily_orders['order_id'].sum())

with col2:
    st.metric("Total Revenue", int(daily_orders['total_price'].sum()))

fig, ax = plt.subplots(figsize=(12,6))
ax.plot(daily_orders['order_date'], daily_orders['order_id'])
ax.set_title("Daily Orders Trend")
st.pyplot(fig)


# =========================
# DELIVERY VS REVIEW
# =========================
st.subheader("Delivery Time vs Review Score")

delivery_review = main_df.groupby('review_score')['delivery_time'].mean()

fig, ax = plt.subplots()
delivery_review.plot(kind='bar', ax=ax)
ax.set_title("Average Delivery Time by Review Score")
st.pyplot(fig)


# =========================
# TOP PRODUCT CATEGORY
# =========================
st.subheader("Top Product Category")

top_category = main_df.groupby('product_name')['total_price'].sum().sort_values(ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10,5))
top_category.plot(kind='bar', ax=ax)
ax.set_title("Top 10 Product Category by Revenue")
st.pyplot(fig)


# =========================
# RFM ANALYSIS
# =========================
st.subheader("RFM Analysis")

rfm = main_df.groupby('order_id').agg({
    'order_date': 'max',
    'total_price': 'sum'
}).reset_index()

recent_date = main_df['order_date'].max()

rfm['recency'] = (recent_date - rfm['order_date']).dt.days
rfm['frequency'] = 1
rfm['monetary'] = rfm['total_price']

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Avg Recency", int(rfm['recency'].mean()))

with col2:
    st.metric("Total Orders", rfm['frequency'].sum())

with col3:
    st.metric("Avg Monetary", int(rfm['monetary'].mean()))

# =========================
# FOOTER
# =========================
st.caption("Dashboard E-Commerce Analysis")