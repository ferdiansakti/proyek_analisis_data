import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Konfigurasi halaman
st.set_page_config(page_title="Analisis Penyewaan Sepeda", page_icon="🚴", layout="wide")

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    data = pd.read_csv('dashboard/data_sepeda_cleaned.csv')
    data['dteday'] = pd.to_datetime(data['dteday'])
    return data

data = load_data()

# Sidebar untuk filter
with st.sidebar:
    st.title("🚴 Filter Data")
    st.subheader("Filter Waktu")
    tahun = st.multiselect(
        "Tahun",
        options=data['yr'].unique(),
        default=data['yr'].unique(),
        format_func=lambda x: "Tahun 2011" if x == 0 else "Tahun 2012"
    )
    
    musim = st.multiselect(
        "Musim",
        options=data['season'].unique(),
        default=data['season'].unique()
    )
    
    bulan = st.multiselect(
        "Bulan",
        options=data['mnth'].unique(),
        default=data['mnth'].unique()
    )
    
 # Filter Cuaca berdasarkan weathersit
    st.subheader("Filter Kondisi Cuaca")
    cuaca_options = {
        1: "Cerah",
        2: "Berawan",
        3: "Hujan Ringan",
        4: "Hujan Lebat"
    }
    cuaca = st.multiselect(
        "Kondisi Cuaca",
        options=sorted(data['weathersit'].unique()),
        default=sorted(data['weathersit'].unique()),
        format_func=lambda x: cuaca_options[x]
    )

# Filter data
filtered_data = data[
    (data['yr'].isin(tahun)) &
    (data['season'].isin(musim)) &
    (data['mnth'].isin(bulan)) &
    (data['weathersit'].isin(cuaca))
]

# Header dashboard
st.title("📊 Dashboard Analisis Penyewaan Sepeda")
st.markdown("""
Analisis pola penyewaan sepeda berdasarkan:
- Perbedaan pengguna kasual vs terdaftar
- Perbandingan hari kerja vs hari libur
- Pengaruh kondisi cuaca
""")

# ======================
# BAGIAN 1: OVERVIEW
# ======================
st.header("📈 Overview Penyewaan")

col1, col2, col3 = st.columns(3)
with col1:
    total_penyewaan = filtered_data['cnt'].sum()
    st.metric("Total Penyewaan", f"{total_penyewaan:,}")

with col2:
    avg_daily = filtered_data.groupby('dteday')['cnt'].sum().mean()
    st.metric("Rata-rata Harian", f"{avg_daily:,.1f}")

with col3:
    pct_registered = (filtered_data['registered'].sum() / total_penyewaan) * 100
    st.metric("Persentase Pengguna Terdaftar", f"{pct_registered:.1f}%")

# Trend waktu
st.subheader("Trend Penyewaan Harian")
fig, ax = plt.subplots(figsize=(12, 4))
sns.lineplot(
    data=filtered_data.groupby('dteday')['cnt'].sum().reset_index(),
    x='dteday',
    y='cnt',
    ax=ax
)
ax.set_title("Trend Penyewaan Harian")
ax.set_xlabel("Tanggal")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig)

# Visualisasi total penyewaan sepeda per musim
st.write("### Total Penyewaan Sepeda per Musim")

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=filtered_data, x="season", y="cnt", ax=ax)
ax.set_title("Total Penyewaan Sepeda per Musim")
ax.set_xlabel("Musim")
ax.set_ylabel("Total Penyewaan")

st.pyplot(fig)

# ======================
# BAGIAN 2: PERBANDINGAN PENGGUNA
# ======================
st.header("👥 Perbandingan Pengguna Kasual vs Terdaftar")

tab1, tab2, tab3 = st.tabs(["Per Jam", "Per Hari", "Per Bulan"])

with tab1:
    st.subheader("Pola Penyewaan per Jam")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=filtered_data.groupby('hr')[['casual','registered']].mean().reset_index(),
        x='hr',
        y='casual',
        label='Kasual',
        ax=ax
    )
    sns.lineplot(
        data=filtered_data.groupby('hr')[['casual','registered']].mean().reset_index(),
        x='hr',
        y='registered',
        label='Terdaftar',
        ax=ax
    )
    ax.set_xticks(range(0, 24))
    ax.set_title("Rata-rata Penyewaan per Jam")
    ax.set_xlabel("Jam dalam Sehari")
    ax.set_ylabel("Jumlah Penyewaan")
    st.pyplot(fig)

with tab2:
    st.subheader("Pola Penyewaan per Hari")
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Prepare data dengan melt
    weekday_data = filtered_data.groupby('weekday')[['casual','registered']].mean().reset_index()
    melted_data = weekday_data.melt(id_vars='weekday', var_name='tipe', value_name='jumlah')
    
    # Plot dengan hue
    sns.barplot(
        data=melted_data,
        x='weekday',
        y='jumlah',
        hue='tipe',
        palette={'casual': 'blue', 'registered': 'orange'},
        ax=ax
    )
    
    ax.set_title("Rata-rata Penyewaan per Hari")
    ax.set_xlabel("Hari dalam Minggu")
    ax.set_ylabel("Jumlah Penyewaan")
    ax.legend(title='Tipe Pengguna')
    st.pyplot(fig)

with tab3:
    st.subheader("Pola Penyewaan per Bulan")
    fig, ax = plt.subplots(figsize=(10, 5))
    monthly_data = filtered_data.groupby('mnth')[['casual','registered']].sum().reset_index()
    monthly_data_melt = monthly_data.melt(id_vars='mnth', var_name='type', value_name='count')
    
    sns.barplot(
        data=monthly_data_melt,
        x='mnth',
        y='count',
        hue='type',
        ax=ax
    )
    ax.set_title("Total Penyewaan per Bulan")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Jumlah Penyewaan")
    st.pyplot(fig)

# ======================
# BAGIAN 3: HARI KERJA vs HARI LIBUR - PERBAIKAN
# ======================
st.header("🏢 vs 🏖️ Hari Kerja vs Hari Libur")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Penyewaan")
    fig, ax = plt.subplots(figsize=(8, 5))
    palette = {'0': 'lightblue', '1': 'lightgreen'}
    
    sns.boxplot(
        data=filtered_data,
        x='workingday',
        y='cnt',
        ax=ax,
        palette=palette,
        order=['0', '1']
    )
    ax.set_xticks([0, 1], ['Hari Libur', 'Hari Kerja'])
    ax.set_title("Distribusi Jumlah Penyewaan")
    st.pyplot(fig)

with col2:
    st.subheader("Rata-rata per Jam")
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_data = filtered_data.copy()
    plot_data['workingday'] = plot_data['workingday'].map({0: 'Libur', 1: 'Kerja'})
    
    sns.lineplot(
        data=plot_data.groupby(['hr','workingday'])['cnt'].mean().reset_index(),
        x='hr',
        y='cnt',
        hue='workingday',
        palette={'Libur': 'blue', 'Kerja': 'orange'},
        linewidth=2,
        ax=ax
    )
    
    ax.set_xticks(range(0, 24, 2))
    ax.set_title("Rata-rata Penyewaan per Jam")
    ax.set_xlabel("Jam dalam Sehari")
    ax.set_ylabel("Jumlah Penyewaan")

    from matplotlib.lines import Line2D
    custom_lines = [
        Line2D([0], [0], color='blue', lw=2),
        Line2D([0], [0], color='orange', lw=2)
    ]
    ax.legend(
        custom_lines,
        ['Libur', 'Kerja'],
        title='Tipe Hari',
        frameon=True
    )
    
    st.pyplot(fig)

# ======================
# BAGIAN 4: PENGARUH CUACA
# ======================
st.header("☀️ Pengaruh Kondisi Cuaca")

# Heatmap korelasi
st.subheader("Korelasi Variabel Cuaca")
fig, ax = plt.subplots(figsize=(8, 6))
corr = filtered_data[['temp','hum','windspeed','cnt']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
ax.set_title("Korelasi antara Kondisi Cuaca dan Penyewaan")
st.pyplot(fig)

# Pengaruh masing-masing faktor cuaca
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Pengaruh Suhu")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(
        data=filtered_data,
        x='temp',
        y='cnt',
        alpha=0.5,
        ax=ax
    )
    ax.set_title("Suhu vs Penyewaan")
    st.pyplot(fig)

with col2:
    st.subheader("Pengaruh Kelembapan")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(
        data=filtered_data,
        x='hum',
        y='cnt',
        alpha=0.5,
        ax=ax
    )
    ax.set_title("Kelembapan vs Penyewaan")
    st.pyplot(fig)

with col3:
    st.subheader("Pengaruh Kecepatan Angin")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(
        data=filtered_data,
        x='windspeed',
        y='cnt',
        alpha=0.5,
        ax=ax
    )
    ax.set_title("Kecepatan Angin vs Penyewaan")
    st.pyplot(fig)

# ======================
# BAGIAN 5: ANALISIS RFM
# ======================
st.header("🏆 Analisis RFM Pelanggan")

if st.checkbox("Tampilkan Analisis RFM"):
    # Hitung RFM
    snapshot_date = filtered_data['dteday'].max() + pd.Timedelta(days=1)
    rfm = filtered_data.groupby('registered').agg({
        'dteday': lambda x: (snapshot_date - x.max()).days,
        'instant': 'count',
        'cnt': 'sum'
    }).rename(columns={
        'dteday': 'recency',
        'instant': 'frequency',
        'cnt': 'monetary'
    })
    
    # Beri skor
    rfm['R'] = pd.qcut(rfm['recency'], q=4, labels=[4,3,2,1])
    rfm['F'] = pd.qcut(rfm['frequency'], q=4, labels=[1,2,3,4])
    rfm['M'] = pd.qcut(rfm['monetary'], q=4, labels=[1,2,3,4])
    
    # Segmentasi
    rfm['segment'] = np.where(
        (rfm['R']>=3) & (rfm['F']>=3) & (rfm['M']>=3),
        'Pelanggan Setia',
        np.where(
            (rfm['R']>=2) & (rfm['F']>=2),
            'Pelanggan Potensial',
            'Pelanggan Biasa'
        )
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Segmentasi Pelanggan")
        fig, ax = plt.subplots(figsize=(8, 6))
        rfm['segment'].value_counts().plot.pie(
            autopct='%1.1f%%',
            colors=['#66b3ff','#99ff99','#ff9999'],
            explode=(0.1, 0, 0),
            ax=ax
        )
        ax.set_ylabel('')
        st.pyplot(fig)
    
    with col2:
        st.subheader("Karakteristik Segment")
        
        st.markdown("""
        **Pelanggan Setia**  
        - Frekuensi tinggi & transaksi terbaru  
        - Kontribusi pendapatan utama  
        """)
        
        st.markdown("""
        **Pelanggan Potensial**  
        - Aktif tetapi frekuensi sedang  
        - Butuh insentif untuk meningkatkan loyalitas  
        """)
        
        st.markdown("""
        **Pelanggan Biasa**  
        - Jarang melakukan penyewaan  
        - Perlu program reaktivasi  
        """)

# ======================
# BAGIAN 6: KESIMPULAN
# ======================
st.header("🎯 Kesimpulan dan Rekomendasi")
st.markdown("""
1. **Pengguna Terdaftar sebagai Segmen Dominan**  
   - Pengguna terdaftar mendominasi penyewaan sepeda, dengan rata-rata dari total penyewaan.  
   - Mereka lebih sering menggunakan sepeda untuk keperluan transportasi harian, terutama selama jam sibuk pagi (07:00-09:00) dan sore (16:00-18:00).  
   - Pola penyewaan mereka lebih stabil dibandingkan pengguna kasual, menandakan kebiasaan rutin dalam penggunaan sepeda.

2. **Pola Penyewaan pada Hari Kerja vs Hari Libur**  
   - **Hari Kerja:** Penyewaan meningkat signifikan pada pagi dan sore hari, sesuai dengan jam berangkat dan pulang kerja/sekolah.  
   - **Hari Libur:** Penyewaan lebih tinggi secara keseluruhan, tetapi pola lebih fluktuatif dengan puncak di siang hari, menunjukkan dominasi penggunaan untuk rekreasi dan aktivitas santai.  
   - Data juga menunjukkan bahwa pada hari kerja, pola penyewaan lebih stabil dibandingkan dengan hari libur.

3. **Faktor Cuaca yang Mempengaruhi Penyewaan**  
   - **Suhu Optimal:** Penyewaan meningkat pada suhu 20-25°C, menunjukkan preferensi pengguna terhadap kondisi cuaca yang nyaman.  
   - **Kelembapan:** Kelembapan sedang (40-70%) mendorong lebih banyak penyewaan, sementara kelembapan tinggi (>80%) menyebabkan penurunan signifikan.  
   - **Kecepatan Angin:** Penyewaan lebih tinggi ketika kecepatan angin rendah (<20 km/jam), tetapi berkurang drastis saat angin kencang yang dapat mengganggu kenyamanan bersepeda.  
   - Cuaca ekstrem (suhu terlalu panas/dingin, kelembapan tinggi, dan angin kencang) menjadi faktor penghambat utama dalam penyewaan sepeda.

4. **Strategi Segmentasi Pelanggan dan Rekomendasi**  
   - **Pelanggan Setia (Terdaftar Aktif):** Fokus pada program loyalitas, seperti diskon berlangganan atau fasilitas tambahan.  
   - **Pelanggan Potensial (Pengguna Kasual):** Menawarkan insentif seperti tarif promosi di hari libur atau referral program agar lebih sering menggunakan layanan.  
   - **Pelanggan Biasa (Tidak Konsisten):** Reaktivasi dengan promo khusus di cuaca optimal atau kerja sama dengan acara komunitas untuk meningkatkan keterlibatan.  
   - **Adaptasi terhadap Cuaca:** Menyediakan informasi real-time mengenai kondisi cuaca dan menawarkan insentif untuk mendorong penyewaan saat cuaca mendukung.

**Kesimpulan Umum:**  
Penyewaan sepeda memiliki tren yang jelas berdasarkan tipe pengguna, hari, dan faktor cuaca. Untuk meningkatkan jumlah penyewaan, strategi optimasi harga, promosi berbasis cuaca, dan insentif loyalitas sangat penting. Selain itu, pemanfaatan teknologi seperti notifikasi cuaca dan rekomendasi waktu penyewaan dapat meningkatkan kenyamanan dan pengalaman pengguna secara keseluruhan.
""")
