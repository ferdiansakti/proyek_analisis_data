import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="Analisis Penyewaan Sepeda",
    page_icon="🚴",
    layout="wide"
)

# Load data
data_sepeda = pd.read_csv('data_sepeda_cleaned.csv')
data_sepeda['dteday'] = pd.to_datetime(data_sepeda['dteday'])

# ======================
# SIDEBAR FILTER
# ======================
with st.sidebar:
    st.title("🔍 Filter Data")
    
    # Filter tanggal
    min_date = data_sepeda['dteday'].min().date()
    max_date = data_sepeda['dteday'].max().date()
    date_range = st.date_input(
        "Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter musim
    selected_seasons = st.multiselect(
        "Pilih Musim",
        options=data_sepeda['season'].unique(),
        default=data_sepeda['season'].unique()
    )
    
    # Filter tipe hari
    day_type = st.multiselect(
        "Tipe Hari",
        options=['Hari Kerja', 'Hari Libur'],
        default=['Hari Kerja', 'Hari Libur']
    )

# Proses Filter Data
def apply_filters(data):
    # Filter tanggal
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        data = data[(data['dteday'] >= start_date) & (data['dteday'] <= end_date)]
    
    # Filter musim
    data = data[data['season'].isin(selected_seasons)]
    
    # Filter tipe hari
    day_map = {'Hari Kerja': 1, 'Hari Libur': 0}
    workingday_values = [day_map[day] for day in day_type]
    data = data[data['workingday'].isin(workingday_values)]
    
    return data

filtered_data = apply_filters(data_sepeda)

# ======================
# BAGIAN UTAMA DASHBOARD
# ======================
st.title("📊 Dashboard Analisis Penyewaan Sepeda")

# ===========================================
# VISUALISASI 1: POLA PENGGUNA KASUAL vs TERDAFTAR
# ===========================================
st.header("1. Pola Penyewaan Sepeda: Pengguna Kasual vs Terdaftar")

# Agregasi data per bulan
filtered_data['bulan'] = filtered_data['dteday'].dt.month
penyewaan_per_bulan = filtered_data.groupby('bulan')[['casual', 'registered', 'cnt']].sum().reset_index()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Per Bulan")
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.plot(penyewaan_per_bulan['bulan'], penyewaan_per_bulan['casual'], label='Pengguna Kasual', marker='o')
    plt.plot(penyewaan_per_bulan['bulan'], penyewaan_per_bulan['registered'], label='Pengguna Terdaftar', marker='o')
    plt.title('Pola Penyewaan Sepeda: Pengguna Kasual vs Terdaftar (Per Bulan)')
    plt.xlabel('Bulan')
    plt.ylabel('Jumlah Penyewaan')
    plt.legend()
    plt.grid()
    st.pyplot(fig)

with col2:
    st.subheader("Statistik Pengguna")
    st.metric("Rata-rata Pengguna Kasual", f"{filtered_data['casual'].mean():.1f}")
    st.metric("Rata-rata Pengguna Terdaftar", f"{filtered_data['registered'].mean():.1f}")
    st.metric("Persentase Pengguna Terdaftar", 
              f"{(filtered_data['registered'].sum()/filtered_data['cnt'].sum())*100:.1f}%")

# Visualisasi tambahan
tab1, tab2, tab3, tab4 = st.tabs(["Per Jam", "Per Hari", "Per Bulan", "Per Musim"])

with tab1:
    st.subheader("Tren per Jam")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=filtered_data, x='hr', y='casual', label='Pengguna Kasual', color='blue')
    sns.lineplot(data=filtered_data, x='hr', y='registered', label='Pengguna Terdaftar', color='red')
    plt.title('Tren Penggunaan Sepeda per Jam dalam Sehari')
    plt.xlabel('Jam dalam Sehari')
    plt.ylabel('Jumlah Pengguna')
    plt.xticks(ticks=range(0, 25, 1), labels=[f"{i}:00" for i in range(0, 25, 1)], rotation=90)
    plt.legend()
    st.pyplot(fig)

with tab2:
    st.subheader("Tren per Hari")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=filtered_data, x='weekday', y='casual', marker='o', label='Pengguna Kasual', color='blue')
    sns.lineplot(data=filtered_data, x='weekday', y='registered', marker='o', label='Pengguna Terdaftar', color='red')
    plt.title('Tren Penggunaan Sepeda per Hari dalam Seminggu')
    plt.xlabel('Hari dalam Seminggu')
    plt.ylabel('Jumlah Pengguna')
    plt.legend()
    st.pyplot(fig)

with tab3:
    st.subheader("Tren per Bulan")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=data_sepeda, x='mnth', y='casual', marker='o', label='Pengguna Kasual', color='blue', ax=ax)
    sns.lineplot(data=data_sepeda, x='mnth', y='registered', marker='o', label='Pengguna Terdaftar', color='red', ax=ax)
    plt.title('Tren Penggunaan Sepeda per Bulan dalam Setahun')
    plt.xlabel('Bulan')
    plt.ylabel('Jumlah Pengguna')
    ax.legend()
    st.pyplot(fig)

with tab4:
    st.subheader("Per Musim")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=filtered_data, x='season', y='cnt')
    plt.title('Total Penyewaan Sepeda per Musim')
    plt.xlabel('Musim')
    plt.ylabel('Total Penyewaan')
    st.pyplot(fig)

# ===========================================
# VISUALISASI 2: HARI KERJA vs HARI LIBUR
# ===========================================
st.header("2. Distribusi dan Perbedaan Penyewaan: Hari Kerja vs Hari Libur")

# Agregasi data
penyewaan_harian = filtered_data.groupby(['dteday', 'workingday'])['cnt'].sum().reset_index()

# 2 kolom baris pertama
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    # Boxplot Distribusi
    st.subheader("Distribusi Penyewaan")
    fig, ax = plt.subplots(figsize=(10, 5))
    if 'Hari Kerja' in day_type and 'Hari Libur' not in day_type:
        plot_data = penyewaan_harian[penyewaan_harian['workingday'] == 1]
        x_order = [1]
        labels = ["Hari Kerja"]
    elif 'Hari Libur' in day_type and 'Hari Kerja' not in day_type:
        plot_data = penyewaan_harian[penyewaan_harian['workingday'] == 0]
        x_order = [0]
        labels = ["Hari Libur"]
    else:
        plot_data = penyewaan_harian
        x_order = [0, 1]
        labels = ["Hari Libur", "Hari Kerja"]
    sns.boxplot(x='workingday', y='cnt', data=plot_data, order=x_order, ax=ax)
    ax.set_xticks(range(len(x_order)))
    ax.set_xticklabels(labels)
    ax.set_title("Distribusi Penyewaan")
    st.pyplot(fig)

with row1_col2:
    # Barplot Rata-rata
    st.subheader("Rata-Rata Penyewaan")
    ratarata_sewa = penyewaan_harian.groupby('workingday')['cnt'].mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    if 'Hari Kerja' in day_type and 'Hari Libur' not in day_type:
        colors = {'1': "blue"}
        order = ['1']
        labels = ["Hari Kerja"]
    elif 'Hari Libur' in day_type and 'Hari Kerja' not in day_type:
        colors = {'0': "red"}
        order = ['0']
        labels = ["Hari Libur"]
    else:
        colors = {'0': "red", '1': "blue"}
        order = ['0', '1']
        labels = ["Hari Libur", "Hari Kerja"]
    sns.barplot(x=ratarata_sewa.index.astype(str), y=ratarata_sewa.values,
               palette=colors, order=order, ax=ax)
    for i, val in enumerate(ratarata_sewa[ratarata_sewa.index.isin([int(x) for x in order])].values):
        ax.text(i, val + 20, f"{val:.0f}", ha='center', fontweight='bold')
    ax.set_title("Rata-Rata Harian")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(labels)
    st.pyplot(fig)

# 2 kolom baris kedua
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    # Tren per Jam
    st.subheader("Tren per Jam")
    fig, ax = plt.subplots(figsize=(10, 5))
    if 'Hari Kerja' in day_type:
        hari_kerja = filtered_data[filtered_data['workingday'] == 1].groupby('hr')['cnt'].mean()
        sns.lineplot(x=hari_kerja.index, y=hari_kerja, label='Hari Kerja', color='blue')
    if 'Hari Libur' in day_type:
        hari_libur = filtered_data[filtered_data['workingday'] == 0].groupby('hr')['cnt'].mean()
        sns.lineplot(x=hari_libur.index, y=hari_libur, label='Hari Libur', color='red')
    ax.set_title("Pola Penyewaan per Jam")
    ax.set_xlabel("Jam dalam Sehari")
    ax.set_ylabel("Rata-Rata Penyewaan")
    ax.set_xticks(range(0, 24, 2))
    ax.legend(title="Kategori Hari")
    ax.grid(True)
    st.pyplot(fig)

with row2_col2:
    # Timeline Harian
    st.subheader("Tren Harian")
    fig, ax = plt.subplots(figsize=(10, 5))
    palette = {0: "red", 1: "blue"}
    sns.lineplot(x='dteday', y='cnt', hue='workingday', data=penyewaan_harian,
                palette=palette, style='workingday', markers=True, dashes=False)
    ax.set_title("Perkembangan Harian")
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Total Penyewaan")
    plt.xticks(rotation=45)
    handles, labels = ax.get_legend_handles_labels()
    custom_labels = ["Hari Libur", "Hari Kerja"]
    ax.legend(handles, custom_labels, title="Hari")
    st.pyplot(fig)

# ===========================================
# VISUALISASI 3: PENGARUH CUACA
# ===========================================
st.header("3. Pengaruh Kondisi Cuaca terhadap Penyewaan")

# Scatter plot
st.subheader("Hubungan Variabel Cuaca dengan Penyewaan")
col1, col2, col3 = st.columns(3)

with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=filtered_data, x='temp', y='cnt', alpha=0.5)
    plt.title('Hubungan Suhu vs Penyewaan')
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=filtered_data, x='hum', y='cnt', alpha=0.5)
    plt.title('Hubungan Kelembapan vs Penyewaan')
    st.pyplot(fig)

with col3:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=filtered_data, x='windspeed', y='cnt', alpha=0.5)
    plt.title('Hubungan Kecepatan Angin vs Penyewaan')
    st.pyplot(fig)

# Heatmap korelasi
st.subheader("Korelasi Variabel Cuaca")
korelasi = filtered_data[['temp','hum','windspeed','cnt']].corr()
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(korelasi, annot=True, cmap='coolwarm', fmt='.2f')
plt.title("Korelasi antara Kondisi Cuaca dan Penyewaan")
st.pyplot(fig)

# Boxplot kategori cuaca
st.subheader("Pengaruh Kategori Cuaca")
col1, col2, col3 = st.columns(3)

with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=filtered_data, x='kategori_suhu', y='cnt')
    plt.title('Pengaruh Suhu terhadap Penyewaan')
    plt.xlabel('Kategori Suhu')
    plt.ylabel('Jumlah Penyewaan')
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8, 6))
    filtered_data['kategori_kelembapan'] = filtered_data['kategori_kelembapan'].str.strip().str.lower()
    existing_cats = filtered_data['kategori_kelembapan'].dropna().unique()
    desired_order = ['rendah', 'sedang', 'tinggi']
    valid_order = [cat for cat in desired_order if cat in existing_cats]
    if len(valid_order) > 0:
        sns.boxplot(
            data=filtered_data,
            x='kategori_kelembapan',
            y='cnt',
            order=valid_order,
            ax=ax
        )
        ax.set_title('Pengaruh Kelembapan terhadap Penyewaan')
        ax.set_xlabel('Kategori Kelembapan')
        ax.set_ylabel('Jumlah Penyewaan')
    st.pyplot(fig)

with col3:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=filtered_data, x='kategori_angin', y='cnt')
    plt.title('Pengaruh Kecepatan Angin terhadap Penyewaan')
    plt.xlabel('Kategori Kecepatan Angin')
    plt.ylabel('Jumlah Penyewaan')
    st.pyplot(fig)

# Analisis lanjutan
st.subheader("Analisis Lanjutan")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_table = filtered_data.pivot_table(values='cnt', index='kategori_suhu', 
                                          columns='waktu_hari', aggfunc='mean', observed=False)
    sns.heatmap(pivot_table, annot=True, cmap='coolwarm', fmt='.1f')
    plt.title('Rata-Rata Penyewaan: Suhu vs Waktu Hari')
    plt.xlabel('Waktu Hari')
    plt.ylabel('Kategori Suhu')
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=filtered_data, x='waktu_hari', y='cnt', hue='season', 
               palette='coolwarm', order=['Dini Hari', 'Pagi', 'Siang', 'Malam'])
    plt.title('Penyewaan: Waktu Hari vs Musim')
    plt.xlabel('Waktu Hari')
    plt.ylabel('Rata-Rata Penyewaan')
    plt.legend(title='Musim')
    st.pyplot(fig)

# ===========================================
# KESIMPULAN DAN REKOMENDASI
# ===========================================
st.header("🎯 Kesimpulan dan Rekomendasi")

with st.expander("Lihat Detail Lengkap", expanded=True):
    st.markdown("""
    ### 1. Pengguna Terdaftar sebagai Segmen Dominan
    - Pengguna terdaftar mendominasi penyewaan sepeda, dengan rata-rata {:.1f}% dari total penyewaan.
    - Mereka lebih sering menggunakan sepeda untuk keperluan transportasi harian, terutama selama jam sibuk pagi (07:00-09:00) dan sore (16:00-18:00).
    - Pola penyewaan mereka lebih stabil dibandingkan pengguna kasual, menandakan kebiasaan rutin dalam penggunaan sepeda.

    ### 2. Pola Penyewaan pada Hari Kerja vs Hari Libur
    **Hari Kerja:**  
    - Penyewaan meningkat signifikan pada pagi dan sore hari, sesuai dengan jam berangkat dan pulang kerja/sekolah.  
    - Pola penyewaan lebih stabil dibandingkan dengan hari libur.  

    **Hari Libur:**  
    - Penyewaan lebih tinggi secara keseluruhan, tetapi pola lebih fluktuatif dengan puncak di siang hari.  
    - Menunjukkan dominasi penggunaan untuk rekreasi dan aktivitas santai.  

    ### 3. Faktor Cuaca yang Mempengaruhi Penyewaan
    **Kondisi Optimal:**  
    - Suhu 20-25°C (korelasi: {:.2f})  
    - Kelembapan sedang (40-70%) (korelasi: {:.2f})  
    - Kecepatan angin rendah (<20 km/jam)  

    **Faktor Penghambat:**  
    - Kelembapan tinggi (>80%)  
    - Angin kencang (>20 km/jam)  
    - Cuaca ekstrem (suhu terlalu panas/dingin)  

    ### 4. Strategi Segmentasi Pelanggan
    **🚴‍♂️ Pengguna Terdaftar (Commuter)**  
    **Karakteristik:**  
    - Rutin menyewa saat jam sibuk pagi & sore  

    **Strategi:**  
    - **Program Loyalitas & Langganan:** Diskon mingguan/bulanan bagi pengguna rutin  
    - **Optimalisasi Aplikasi & Reservasi:** Tambahkan fitur pemesanan cepat untuk jam sibuk  

    **🌳 Pengguna Kasual (Recreational)**  
    **Karakteristik:**  
    - Aktif saat akhir pekan, dominan di siang hari  

    **Strategi:**  
    - **Paket Promosi Akhir Pekan:** Diskon atau paket spesial untuk penyewaan lebih lama  
    - **Kolaborasi dengan Tempat Wisata:** Titik penyewaan di taman, museum, atau area wisata  

    **🌦 Pengguna Sensitif terhadap Cuaca**  
    **Karakteristik:**  
    - Penyewaan meningkat saat suhu **20-25°C** dengan kelembapan **40-70%**  
    - Penyewaan menurun saat kelembapan tinggi **(>80%)** atau kecepatan angin **(>20 km/jam)**  
    - Cuaca ekstrem menjadi faktor utama dalam penurunan penyewaan  

    **Strategi:**  
    - **Tambahkan aksesori:** Jas hujan ringan atau pelindung angin di titik penyewaan  
    - **Penyesuaian stok:** Sesuaikan jumlah sepeda berdasarkan prediksi cuaca  

    **Kesimpulan Umum:**  
    Penyewaan sepeda memiliki tren yang jelas berdasarkan tipe pengguna, hari, dan faktor cuaca. Untuk meningkatkan jumlah penyewaan, strategi optimasi harga, promosi berbasis cuaca, dan insentif loyalitas sangat penting. Selain itu, pemanfaatan teknologi seperti notifikasi cuaca dan rekomendasi waktu penyewaan dapat meningkatkan kenyamanan dan pengalaman pengguna secara keseluruhan.
    """.format(
        (filtered_data['registered'].sum()/filtered_data['cnt'].sum())*100,
        filtered_data[['temp','hum','windspeed','cnt']].corr().loc['temp', 'cnt'],
        filtered_data[['temp','hum','windspeed','cnt']].corr().loc['hum', 'cnt']
    ))