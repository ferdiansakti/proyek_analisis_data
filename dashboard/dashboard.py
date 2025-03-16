# Import library yang diperlukan
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Judul aplikasi
st.title("🚴‍♂️ Analisis Penyewaan Sepeda 🚴‍♀️")
st.markdown("""
Aplikasi ini menganalisis pola penyewaan sepeda berdasarkan pengguna kasual dan terdaftar, waktu, musim, serta kondisi cuaca.
""")

# Memuat dataset langsung dari file CSV
@st.cache_data  # Cache data untuk meningkatkan performa
def load_data():
    data = pd.read_csv('dashboard/hour.csv')
    return data

data_sepeda = load_data()

# Menampilkan data
st.header("📊 Data Awal")
st.write("Berikut adalah 5 baris pertama dari dataset:")
st.write(data_sepeda.head())

# Menampilkan dimensi data
st.write(f"Ukuran dataset: {data_sepeda.shape[0]} baris dan {data_sepeda.shape[1]} kolom.")

# Data Wrangling
st.header("🧹 Data Wrangling")

# Menghapus kolom yang tidak diperlukan
data_sepeda.drop(['instant', 'dteday'], axis=1, inplace=True)

# Mengubah kolom 'season' menjadi kategori
peta_musim = {1: 'Semi', 2: 'Panas', 3: 'Gugur', 4: 'Dingin'}
data_sepeda['season'] = data_sepeda['season'].map(peta_musim)

# Mengubah kolom 'mnth' menjadi kategori
peta_bulan = {1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
              7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'}
data_sepeda['mnth'] = data_sepeda['mnth'].map(peta_bulan)

# Mengubah kolom 'weekday' menjadi kategori
peta_hari = {0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu',
             4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'}
data_sepeda['weekday'] = data_sepeda['weekday'].map(peta_hari)

# Kategorisasi suhu
temp_bins = np.linspace(data_sepeda['temp'].min(), data_sepeda['temp'].max(), 4)
temp_labels = ['Dingin', 'Sedang', 'Panas']
data_sepeda['kategori_suhu'] = pd.cut(data_sepeda['temp'], bins=temp_bins, labels=temp_labels)

# Kategorisasi kelembapan
humidity_bins = np.linspace(data_sepeda['hum'].min(), data_sepeda['hum'].max(), 4)
humidity_labels = ['Rendah', 'Sedang', 'Tinggi']
data_sepeda['kategori_kelembapan'] = pd.cut(data_sepeda['hum'], bins=humidity_bins, labels=humidity_labels)

# Kategorisasi kecepatan angin
wind_bins = np.linspace(data_sepeda['windspeed'].min(), data_sepeda['windspeed'].max(), 4)
wind_labels = ['Tenang', 'Sejuk', 'Berangin']
data_sepeda['kategori_angin'] = pd.cut(data_sepeda['windspeed'], bins=wind_bins, labels=wind_labels)

# Kategorisasi waktu dalam sehari
jam_bins = [0, 6, 12, 18, 24]
jam_labels = ['Dini Hari', 'Pagi', 'Siang', 'Malam']
data_sepeda['waktu_hari'] = pd.cut(data_sepeda['hr'], bins=jam_bins, labels=jam_labels, right=False)

# Kategorisasi jumlah penyewaan sepeda
rental_bins = np.linspace(data_sepeda['cnt'].min(), data_sepeda['cnt'].max(), 4)
rental_labels = ['Rendah', 'Sedang', 'Tinggi']
data_sepeda['kategori_sewa'] = pd.cut(data_sepeda['cnt'], bins=rental_bins, labels=rental_labels)

# Menampilkan data setelah cleaning
st.header("🧼 Data Setelah Cleaning")
st.write("Berikut adalah 5 baris pertama dari dataset setelah pembersihan:")
st.write(data_sepeda.head())

# EDA
st.header("🔍 Exploratory Data Analysis (EDA)")

# Statistik dasar
st.subheader("📈 Statistik Dasar")
st.write("Statistik deskriptif untuk variabel `casual`, `registered`, dan `cnt`:")
st.write(data_sepeda[['casual', 'registered', 'cnt']].describe())

# Jumlah kategori pada variabel kategorikal
st.subheader("📊 Jumlah Kategori pada Variabel Kategorikal")
kolom_kategorikal = ['season', 'yr', 'mnth', 'weekday', 'weathersit', 'kategori_suhu',
                     'kategori_angin', 'kategori_kelembapan', 'waktu_hari', 'kategori_sewa']
for kolom in kolom_kategorikal:
    st.write(f"Jumlah nilai untuk **{kolom}**:")
    st.write(data_sepeda[kolom].value_counts())

# Visualisasi
st.header("📊 Visualisasi Data")

# Pilihan visualisasi
st.sidebar.header("⚙️ Pengaturan Visualisasi")
pilihan_visualisasi = st.sidebar.selectbox(
    "Pilih Visualisasi:",
    ["Tren Penggunaan Sepeda per Jam", "Tren Penggunaan Sepeda per Hari", "Tren Penggunaan Sepeda per Bulan", 
     "Total Penyewaan per Musim", "Pengaruh Suhu", "Pengaruh Kelembapan", "Pengaruh Kecepatan Angin"]
)

# Tren penggunaan sepeda per jam dalam sehari
if pilihan_visualisasi == "Tren Penggunaan Sepeda per Jam":
    st.subheader("🕒 Tren Penggunaan Sepeda per Jam dalam Sehari")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=data_sepeda, x='hr', y='casual', label='Pengguna Kasual', color='blue', ax=ax)
    sns.lineplot(data=data_sepeda, x='hr', y='registered', label='Pengguna Terdaftar', color='red', ax=ax)
    ax.set_title('Tren Penggunaan Sepeda per Jam dalam Sehari')
    ax.set_xlabel('Jam dalam Sehari')
    ax.set_ylabel('Jumlah Pengguna')
    ax.set_xticks(range(0, 25, 1))
    ax.set_xticklabels([f"{i}:00" for i in range(0, 25, 1)], rotation=90)
    ax.legend()
    st.pyplot(fig)

# Tren penggunaan sepeda per hari dalam seminggu
elif pilihan_visualisasi == "Tren Penggunaan Sepeda per Hari":
    st.subheader("📅 Tren Penggunaan Sepeda per Hari dalam Seminggu")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=data_sepeda, x='weekday', y='casual', marker='o', label='Pengguna Kasual', color='blue', ax=ax)
    sns.lineplot(data=data_sepeda, x='weekday', y='registered', marker='o', label='Pengguna Terdaftar', color='red', ax=ax)
    ax.set_title('Tren Penggunaan Sepeda per Hari dalam Seminggu')
    ax.set_xlabel('Hari dalam Seminggu')
    ax.set_ylabel('Jumlah Pengguna')
    ax.legend()
    st.pyplot(fig)

# Tren penggunaan sepeda per bulan dalam setahun
elif pilihan_visualisasi == "Tren Penggunaan Sepeda per Bulan":
    st.subheader("📅 Tren Penggunaan Sepeda per Bulan dalam Setahun")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=data_sepeda, x='mnth', y='casual', marker='o', label='Pengguna Kasual', color='blue', ax=ax)
    sns.lineplot(data=data_sepeda, x='mnth', y='registered', marker='o', label='Pengguna Terdaftar', color='red', ax=ax)
    ax.set_title('Tren Penggunaan Sepeda per Bulan dalam Setahun')
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Jumlah Pengguna')
    ax.legend()
    st.pyplot(fig)

# Visualisasi total penyewaan sepeda per musim
elif pilihan_visualisasi == "Total Penyewaan per Musim":
    st.subheader("🌦️ Total Penyewaan Sepeda per Musim")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=data_sepeda, x='season', y='cnt', ax=ax)
    ax.set_title('Total Penyewaan Sepeda per Musim')
    ax.set_xlabel('Musim')
    ax.set_ylabel('Total Penyewaan')
    st.pyplot(fig)

# Pengaruh suhu terhadap penyewaan sepeda
elif pilihan_visualisasi == "Pengaruh Suhu":
    st.subheader("🌡️ Pengaruh Suhu terhadap Penyewaan Sepeda")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=data_sepeda, x='kategori_suhu', y='cnt', ax=ax)
    ax.set_title('Pengaruh Suhu terhadap Penyewaan Sepeda')
    ax.set_xlabel('Kategori Suhu')
    ax.set_ylabel('Jumlah Penyewaan')
    st.pyplot(fig)

# Pengaruh kelembapan terhadap penyewaan sepeda
elif pilihan_visualisasi == "Pengaruh Kelembapan":
    st.subheader("💧 Pengaruh Kelembapan terhadap Penyewaan Sepeda")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=data_sepeda, x='kategori_kelembapan', y='cnt', ax=ax)
    ax.set_title('Pengaruh Kelembapan terhadap Penyewaan Sepeda')
    ax.set_xlabel('Kategori Kelembapan')
    ax.set_ylabel('Jumlah Penyewaan')
    st.pyplot(fig)

# Pengaruh kecepatan angin terhadap penyewaan sepeda
elif pilihan_visualisasi == "Pengaruh Kecepatan Angin":
    st.subheader("🌬️ Pengaruh Kecepatan Angin terhadap Penyewaan Sepeda")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=data_sepeda, x='kategori_angin', y='cnt', ax=ax)
    ax.set_title('Pengaruh Kecepatan Angin terhadap Penyewaan Sepeda')
    ax.set_xlabel('Kategori Kecepatan Angin')
    ax.set_ylabel('Jumlah Penyewaan')
    st.pyplot(fig)

# Kesimpulan
st.header("📝 Kesimpulan")
st.write("""
1. **Pola Variasi Penyewaan Sepeda antara Pengguna Kasual dan Terdaftar**:
   - Pengguna terdaftar lebih sering menyewa sepeda dibanding pengguna kasual, terutama pada hari kerja dan jam sibuk.
2. **Waktu dan Musim dengan Permintaan Tertinggi/Rendah**:
   - Permintaan tertinggi terjadi di musim gugur, terutama pada siang dan malam hari. Permintaan terendah terjadi di musim semi.
3. **Pengaruh Suhu, Kelembapan, dan Kecepatan Angin**:
   - Penyewaan sepeda meningkat pada suhu sedang, kelembapan rendah hingga sedang, serta kecepatan angin yang tenang dan sejuk.
""")
