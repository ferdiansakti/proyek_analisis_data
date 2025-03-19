import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
data_sepeda = pd.read_csv('data_sepeda_cleaned.csv')
data_sepeda['dteday'] = pd.to_datetime(data_sepeda['dteday'])

# Menambahkan kolom numerik untuk urutan bulan
bulan_ke_angka = {
    'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4, 
    'Mei': 5, 'Juni': 6, 'Juli': 7, 'Agustus': 8, 
    'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
}
data_sepeda['mnth_num'] = data_sepeda['mnth'].map(bulan_ke_angka)

# Sidebar untuk filter interaktif
st.sidebar.header("Filter Data")

# Filter berdasarkan periode waktu tertentu
min_date = data_sepeda['dteday'].min()
max_date = data_sepeda['dteday'].max()
start_date = st.sidebar.date_input("Tanggal Mulai", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.sidebar.date_input("Tanggal Akhir", min_value=min_date, max_value=max_date, value=max_date)

# Filter berdasarkan musim
selected_season = st.sidebar.multiselect(
    "Pilih Musim", 
    options=data_sepeda['season'].unique(), 
    default=data_sepeda['season'].unique()
)

# Filter data berdasarkan pilihan pengguna
filtered_data = data_sepeda[
    (data_sepeda['dteday'] >= pd.Timestamp(start_date)) & 
    (data_sepeda['dteday'] <= pd.Timestamp(end_date)) & 
    (data_sepeda['season'].isin(selected_season))
]

# Judul Dashboard
st.title("🚴‍♂️ Dashboard Analisis Penyewaan Sepeda 🚴‍♀️")

# Tampilkan rentang tanggal dan musim yang dipilih
st.write(f"📅 **Rentang Tanggal:** {start_date} sampai {end_date}")
st.write(f"🌤️ **Musim yang Dipilih:** {', '.join(selected_season)}")

# Menampilkan metrik dalam bentuk tabel
st.subheader("📊 Ringkasan Penyewaan Sepeda")

# Buat DataFrame untuk tabel metrik
metrik_data = {
    "Metrik": ["Total Penyewaan", "Rata-Rata Penyewaan per Hari", "Pengguna Kasual", "Pengguna Terdaftar"],
    "Nilai": [
        f"{filtered_data['cnt'].sum():,} sepeda",  # Total Penyewaan
        f"{filtered_data['cnt'].mean():,.2f} sepeda/hari",  # Rata-Rata Penyewaan per Hari
        f"{filtered_data['casual'].sum():,} sepeda",  # Pengguna Kasual
        f"{filtered_data['registered'].sum():,} sepeda"  # Pengguna Terdaftar
    ]
}
metrik_df = pd.DataFrame(metrik_data)

# Tampilkan tabel
st.table(metrik_df)

# Visualisasi pola penggunaan sepeda dalam sehari
st.subheader("📊 Tren Penggunaan Sepeda per Jam dalam Sehari")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=filtered_data, x='hr', y='casual', label='Pengguna Kasual', color='blue', ax=ax)
sns.lineplot(data=filtered_data, x='hr', y='registered', label='Pengguna Terdaftar', color='red', ax=ax)
ax.set_title('Tren Penggunaan Sepeda per Jam')
ax.set_xlabel('Jam')
ax.set_ylabel('Jumlah Pengguna')
st.pyplot(fig)

# Visualisasi pola penggunaan sepeda dalam seminggu
st.subheader("📊 Tren Penggunaan Sepeda per Hari dalam Seminggu")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=filtered_data, x='weekday', y='cnt', ax=ax)
ax.set_title('Total Penyewaan Sepeda per Hari')
ax.set_xlabel('Hari')
ax.set_ylabel('Jumlah Penyewaan')
st.pyplot(fig)

# Visualisasi pola penggunaan sepeda dalam setahun
st.subheader("📊 Tren Penggunaan Sepeda per Bulan")
fig, ax = plt.subplots(figsize=(12, 6))

# Ambil daftar bulan yang tersedia dalam data yang difilter
bulan_tersedia = filtered_data['mnth'].unique()
bulan_tersedia_urut = sorted(bulan_tersedia, key=lambda x: bulan_ke_angka[x])  # Urutkan berdasarkan numerik

# Buat barplot dengan urutan bulan yang benar
sns.barplot(
    data=filtered_data, 
    x='mnth',  # Gunakan kolom bulan sebagai string
    y='cnt', 
    ax=ax,
    order=bulan_tersedia_urut  # Urutkan berdasarkan bulan yang tersedia
)

# Atur label sumbu x sebagai nama bulan yang tersedia
ax.set_xticks(range(len(bulan_tersedia_urut)))
ax.set_xticklabels(bulan_tersedia_urut, rotation=45)

ax.set_title('Total Penyewaan Sepeda per Bulan')
ax.set_xlabel('Bulan')
ax.set_ylabel('Jumlah Penyewaan')
st.pyplot(fig)

# Tampilkan data yang difilter
st.write("ℹ️ **Catatan:** Data yang ditampilkan adalah hasil filter berdasarkan tanggal dan musim yang dipilih.")