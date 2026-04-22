import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Southwind Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS styling
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('UTS Yudistian Dzaky Yassar 09010624019-59FYGPnfrOEgTv5ZOfBRzqFENdKObv.csv', sep=';')
    # Convert date columns
    df['tanggal_pemesanan'] = pd.to_datetime(df['tanggal_pemesanan'], format='%d/%m/%Y')
    df['tanggal_pengiriman'] = pd.to_datetime(df['tanggal_pengiriman'], format='%d/%m/%Y')
    
    # Convert numeric columns - replace comma with dot for decimal separator
    numeric_cols = ['Penjualan', 'keuntungan', 'diskon', 'jumlah']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
    
    return df

df = load_data()

# Dashboard title
st.markdown("<h1 class='dashboard-title'>📊 Southwind Sales Analytics Dashboard</h1>", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.markdown("<h2 class='sidebar-header'>🔍 Filter Data</h2>", unsafe_allow_html=True)

# Date range filter
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Dari Tanggal", value=df['tanggal_pemesanan'].min())
with col2:
    end_date = st.date_input("Sampai Tanggal", value=df['tanggal_pemesanan'].max())

# Category filter
categories = st.sidebar.multiselect(
    "Pilih Kategori Produk",
    options=df["Kategori_produk"].unique(),
    default=df["Kategori_produk"].unique()
)

# Region filter
regions = st.sidebar.multiselect(
    "Pilih Wilayah",
    options=df["wilayah"].unique(),
    default=df["wilayah"].unique()
)

# Segment filter
segments = st.sidebar.multiselect(
    "Pilih Segmen",
    options=df["segmen"].unique(),
    default=df["segmen"].unique()
)

# Filter data based on selections
df_filtered = df[
    (df['tanggal_pemesanan'] >= pd.Timestamp(start_date)) &
    (df['tanggal_pemesanan'] <= pd.Timestamp(end_date)) &
    (df['Kategori_produk'].isin(categories)) &
    (df['wilayah'].isin(regions)) &
    (df['segmen'].isin(segments))
]

# Key metrics section
st.markdown("<h2 class='section-title'>📈 Ringkasan Kinerja</h2>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = df_filtered['Penjualan'].sum()
    st.metric(
        label="Total Penjualan",
        value=f"${total_sales:,.0f}",
        delta=f"${total_sales - df['Penjualan'].sum():,.0f}" if total_sales != df['Penjualan'].sum() else None
    )

with col2:
    total_profit = df_filtered['keuntungan'].sum()
    st.metric(
        label="Total Keuntungan",
        value=f"${total_profit:,.0f}",
        delta=f"{(total_profit/total_sales)*100:.1f}%" if total_sales > 0 else "0%"
    )

with col3:
    avg_discount = df_filtered['diskon'].mean()
    st.metric(
        label="Rata-rata Diskon",
        value=f"{avg_discount*100:.1f}%"
    )

with col4:
    total_orders = df_filtered['id_pemesanan'].nunique()
    st.metric(
        label="Total Pesanan",
        value=f"{total_orders:,.0f}"
    )

st.markdown("<hr class='divider'/>", unsafe_allow_html=True)

# Charts row 1
st.markdown("<h2 class='section-title'>💼 Analisis Penjualan</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Sales by Category
with col1:
    sales_category = df_filtered.groupby('Kategori_produk')['Penjualan'].sum().sort_values(ascending=False)
    fig_category = px.bar(
        x=sales_category.values,
        y=sales_category.index,
        orientation='h',
        title="Penjualan berdasarkan Kategori Produk",
        labels={'x': 'Penjualan ($)', 'y': 'Kategori'},
        color=sales_category.values,
        color_continuous_scale='Viridis'
    )
    fig_category.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_category, use_container_width=True)

# Profit by Region
with col2:
    profit_region = df_filtered.groupby('wilayah')['keuntungan'].sum().sort_values(ascending=False)
    fig_region = px.pie(
        values=profit_region.values,
        names=profit_region.index,
        title="Keuntungan berdasarkan Wilayah",
        hole=0.3
    )
    fig_region.update_layout(height=400)
    st.plotly_chart(fig_region, use_container_width=True)

st.markdown("<hr class='divider'/>", unsafe_allow_html=True)

# Charts row 2
col1, col2 = st.columns(2)

# Sales trend over time
with col1:
    sales_trend = df_filtered.groupby(df_filtered['tanggal_pemesanan'].dt.to_period('W'))['Penjualan'].sum()
    sales_trend.index = sales_trend.index.to_timestamp()
    
    fig_trend = px.line(
        x=sales_trend.index,
        y=sales_trend.values,
        title="Tren Penjualan Mingguan",
        labels={'x': 'Tanggal', 'y': 'Penjualan ($)'},
        markers=True
    )
    fig_trend.update_layout(height=400)
    st.plotly_chart(fig_trend, use_container_width=True)

# Sales by Segment
with col2:
    segment_data = df_filtered.groupby('segmen').agg({
        'Penjualan': 'sum',
        'keuntungan': 'sum',
        'id_pemesanan': 'count'
    }).reset_index()
    
    fig_segment = px.bar(
        segment_data,
        x='segmen',
        y=['Penjualan', 'keuntungan'],
        barmode='group',
        title="Penjualan vs Keuntungan per Segmen",
        labels={'value': 'Jumlah ($)', 'segmen': 'Segmen'}
    )
    fig_segment.update_layout(height=400)
    st.plotly_chart(fig_segment, use_container_width=True)

st.markdown("<hr class='divider'/>", unsafe_allow_html=True)

# Charts row 3
col1, col2 = st.columns(2)

# Top 10 Products
with col1:
    top_products = df_filtered.groupby('nama_produk')['Penjualan'].sum().nlargest(10).sort_values()
    fig_products = px.barh(
        x=top_products.values,
        y=top_products.index,
        title="Top 10 Produk Terbaik",
        labels={'x': 'Penjualan ($)', 'y': 'Produk'},
        color=top_products.values,
        color_continuous_scale='Blues'
    )
    fig_products.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_products, use_container_width=True)

# Shipping Method Analysis
with col2:
    shipping_data = df_filtered.groupby('jenis_pengiriman').agg({
        'Penjualan': 'sum',
        'id_pemesanan': 'count'
    }).reset_index()
    shipping_data.columns = ['Jenis Pengiriman', 'Total Penjualan', 'Jumlah Pesanan']
    
    fig_shipping = px.bar(
        shipping_data,
        x='Jenis Pengiriman',
        y=['Total Penjualan', 'Jumlah Pesanan'],
        barmode='group',
        title="Analisis Metode Pengiriman",
        labels={'value': 'Nilai', 'variable': 'Tipe'}
    )
    fig_shipping.update_layout(height=400)
    st.plotly_chart(fig_shipping, use_container_width=True)

st.markdown("<hr class='divider'/>", unsafe_allow_html=True)

# Data table section
st.markdown("<h2 class='section-title'>📋 Detail Data</h2>", unsafe_allow_html=True)

with st.expander("Tampilkan Tabel Data Detail", expanded=False):
    # Column selection
    columns_to_show = st.multiselect(
        'Pilih kolom yang ingin ditampilkan:',
        options=df_filtered.columns.tolist(),
        default=['tanggal_pemesanan', 'nama_pelanggan', 'Kategori_produk', 'nama_produk', 'Penjualan', 'keuntungan', 'segmen', 'wilayah']
    )
    
    # Display table
    st.dataframe(
        df_filtered[columns_to_show].sort_values('tanggal_pemesanan', ascending=False),
        use_container_width=True,
        height=400
    )
    
    # Download CSV
    csv = df_filtered[columns_to_show].to_csv(index=False)
    st.download_button(
        label="📥 Download Data sebagai CSV",
        data=csv,
        file_name="southwind_sales_data.csv",
        mime="text/csv"
    )

# Statistics summary
with st.expander("📊 Statistik Ringkas", expanded=False):
    st.dataframe(
        df_filtered[['Penjualan', 'keuntungan', 'jumlah', 'diskon']].describe().T,
        use_container_width=True
    )

st.markdown("<hr class='divider'/>", unsafe_allow_html=True)
st.markdown("<p class='footer'>Southwind Sales Analytics Dashboard © 2024</p>", unsafe_allow_html=True)
