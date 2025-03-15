import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Judul aplikasi
st.title('Analisis Penyewaan Sepeda')

# Menambahkan sidebar untuk navigasi
st.sidebar.title('Navigasi')
options = st.sidebar.radio('Pilih bagian:', 
                           ['Pertanyaan Bisnis', 'Data Wrangling', 'Exploratory Data Analysis', 'Visualization & Explanatory Analysis', 'Conclusion'])

# Load dataset dengan caching
@st.cache_data
def load_data():
    return pd.read_csv('dashboard/hour.csv')

df_hour = load_data()

# Data Cleaning (sesuai dengan kode sebelumnya)
df_hour.drop(['instant', 'dteday'], axis=1, inplace=True)
season_string = {1: 'winter', 2: 'spring', 3: 'summer', 4: 'fall'}
df_hour['season'] = df_hour['season'].map(season_string)
mnth_string = {1: 'january', 2: 'february', 3: 'march', 4: 'april', 5: 'may', 6: 'june', 
               7: 'july', 8: 'august', 9: 'september', 10: 'october', 11: 'november', 12: 'december'}
df_hour['mnth'] = df_hour['mnth'].map(mnth_string)
weekday_string = {0: 'sunday', 1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday', 5: 'friday', 6: 'saturday'}
df_hour['weekday'] = df_hour['weekday'].map(weekday_string)
df_hour['temp'] = df_hour['temp'] / 41
df_hour['atemp'] = df_hour['atemp'] / 50
df_hour['hum'] = df_hour['hum'] / 100
df_hour['windspeed'] = df_hour['windspeed'] / 67

# Binning data
temp_bins = np.linspace(df_hour['temp'].min(), df_hour['temp'].max(), 4)
temp_labels = ['cold', 'mild', 'hot']
df_hour['temp_binned'] = pd.cut(df_hour['temp'], bins=temp_bins, labels=temp_labels)
hum_bins = np.linspace(df_hour['hum'].min(), df_hour['hum'].max(), 4)
hum_labels = ['low', 'medium', 'high']
df_hour['hum_binned'] = pd.cut(df_hour['hum'], bins=hum_bins, labels=hum_labels)
wind_bins = np.linspace(df_hour['windspeed'].min(), df_hour['windspeed'].max(), 4)
wind_labels = ['Calm', 'Breezy', 'Windy']
df_hour['wind_binned'] = pd.cut(df_hour['windspeed'], bins=wind_bins, labels=wind_labels)
hour_bins = [0, 6, 12, 18, 24]
hour_labels = ['Early Morning', 'Morning', 'Afternoon', 'Evening']
df_hour['hour_binned'] = pd.cut(df_hour['hr'], bins=hour_bins, labels=hour_labels, right=False)
cnt_bins = np.linspace(df_hour['cnt'].min(), df_hour['cnt'].max(), 4)
cnt_labels = ['Low', 'Medium', 'High']
df_hour['cnt_binned'] = pd.cut(df_hour['cnt'], bins=cnt_bins, labels=cnt_labels)

if options == 'Pertanyaan Bisnis':
    st.header('Menentukan Pertanyaan Bisnis')
    st.write("""
    - Bagaimana pengaruh suhu, kelembapan, dan kecepatan angin terhadap jumlah penyewaan sepeda?
    - Apakah ada musim tertentu di mana permintaan sepeda lebih tinggi atau lebih rendah?
    - Bagaimana pola penyewaan sepeda bervariasi antara pengguna casual dan registered?
    - Apakah ada perbedaan pola penyewaan sepeda antara hari kerja dan akhir pekan?
    """)

elif options == 'Data Wrangling':
    st.header('Data Wrangling')
    if st.checkbox('Tampilkan 5 baris teratas dataset'):
        st.dataframe(df_hour.head())
    
    if st.checkbox('Tampilkan informasi dataset'):
        st.write("Informasi Dataset:")
        buffer = st.write(df_hour.info())
    
    if st.checkbox('Tampilkan jumlah missing values'):
        st.write("Jumlah Missing Values:")
        st.write(df_hour.isna().sum())

elif options == 'Exploratory Data Analysis':
    st.header('Exploratory Data Analysis')
    if st.checkbox('Tampilkan statistik dasar'):
        st.write(df_hour[['casual', 'registered', 'cnt']].describe())
    
    if st.checkbox('Tampilkan value counts untuk kolom kategorikal'):
        categorical_columns = ['season', 'yr', 'mnth', 'weekday', 'weathersit']
        for column in categorical_columns:
            st.write(f"Value counts for {column}:")
            st.write(df_hour[column].value_counts())

elif options == 'Visualization & Explanatory Analysis':
    st.header('Visualization & Explanatory Analysis')
    
    st.subheader('Pola Penggunaan Sepeda per Bulan')
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df_hour, x='mnth', y='casual', marker='o', label='Casual Users', color='blue', ax=ax1)
    sns.lineplot(data=df_hour, x='mnth', y='registered', marker='o', label='Registered Users', color='red', ax=ax1)
    ax1.set_title('Monthly Casual and Registered Riders')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Number of Riders')
    ax1.legend()
    st.pyplot(fig1)

    st.subheader('Pola Penggunaan Sepeda per Hari')
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df_hour, x='weekday', y='casual', marker='o', label='Casual Users', color='blue', ax=ax2)
    sns.lineplot(data=df_hour, x='weekday', y='registered', marker='o', label='Registered Users', color='red', ax=ax2)
    ax2.set_title('Daily Casual and Registered Riders')
    ax2.set_xlabel('Day')
    ax2.set_ylabel('Number of Riders')
    ax2.legend()
    st.pyplot(fig2)

    st.subheader('Pola Penggunaan Sepeda per Jam')
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df_hour, x='hr', y='casual', marker='o', label='Casual Users', color='blue', ax=ax3)
    sns.lineplot(data=df_hour, x='hr', y='registered', marker='o', label='Registered Users', color='red', ax=ax3)
    ax3.set_title('Hourly Casual and Registered Riders')
    ax3.set_xlabel('Hour')
    ax3.set_ylabel('Number of Riders')
    ax3.legend()
    st.pyplot(fig3)

    st.subheader('Total Pengguna Sepeda per Musim')
    fig4, ax4 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_hour, x='season', y='cnt', ax=ax4)
    ax4.set_title('Total Users by Season')
    ax4.set_xlabel('Season')
    ax4.set_ylabel('Total Users')
    st.pyplot(fig4)

    st.subheader('Total Pengguna Sepeda pada Hari Libur vs Hari Biasa')
    fig5, ax5 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_hour, x='holiday', y='cnt', ax=ax5)
    ax5.set_title('Total Users by Holiday')
    ax5.set_xlabel('Holiday')
    ax5.set_ylabel('Total Users')
    ax5.set_xticks([0, 1])
    ax5.set_xticklabels(['Non-Holiday', 'Holiday'])
    st.pyplot(fig5)

    st.subheader('Total Pengguna Sepeda berdasarkan Suhu')
    fig6, ax6 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_hour, x='temp_binned', y='cnt', ax=ax6)
    ax6.set_title('Total Users by Temperature Situation')
    ax6.set_xlabel('Temperature Situation')
    ax6.set_ylabel('Total Users')
    st.pyplot(fig6)

    st.subheader('Total Pengguna Sepeda berdasarkan Kelembapan')
    fig7, ax7 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_hour, x='hum_binned', y='cnt', ax=ax7)
    ax7.set_title('Total Users by Humidity Situation')
    ax7.set_xlabel('Humidity Situation')
    ax7.set_ylabel('Total Users')
    st.pyplot(fig7)

    st.subheader('Total Pengguna Sepeda berdasarkan Kecepatan Angin')
    fig8, ax8 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_hour, x='wind_binned', y='cnt', ax=ax8)
    ax8.set_title('Total Users by Wind Speed Situation')
    ax8.set_xlabel('Wind Speed Situation')
    ax8.set_ylabel('Total Users')
    st.pyplot(fig8)

    st.subheader('Heatmap Korelasi')
    numeric_columns = ['temp', 'atemp', 'hum', 'windspeed', 'casual', 'registered', 'cnt']
    correlation_matrix = df_hour[numeric_columns].corr()
    fig9, ax9 = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax9)
    ax9.set_title('Correlation Matrix')
    st.pyplot(fig9)

elif options == 'Conclusion':
    st.header('Conclusion')
    st.write("""
    1. Pengaruh Faktor Cuaca terhadap Penyewaan Sepeda
    - Terdapat korelasi positif antara suhu dan jumlah penyewaan sepeda, di mana penyewaan meningkat saat suhu lebih tinggi.
    - Kelembapan tinggi cenderung mengurangi jumlah penyewaan sepeda.
    2. Pengaruh Musim terhadap Permintaan Sepeda
    - Penyewaan sepeda tertinggi terjadi pada musim panas dan musim gugur, sementara musim dingin memiliki jumlah penyewaan yang paling rendah.
    - Pengguna terdaftar (registered) mendominasi penyewaan sepeda di semua musim dibandingkan pengguna kasual.
    3. Perbedaan Pola Penyewaan antara Pengguna Casual dan Registered
    - Pengguna terdaftar (registered) memiliki jumlah penyewaan yang lebih tinggi dibandingkan pengguna kasual.
    - Pengguna kasual cenderung lebih banyak menyewa pada akhir pekan, sedangkan pengguna terdaftar lebih stabil dalam penyewaan sepanjang minggu.
    4. Perbedaan Pola Penyewaan antara Hari Kerja dan Akhir Pekan
    - Penyewaan pada hari kerja lebih banyak dilakukan oleh pengguna terdaftar, terutama pada jam sibuk (pagi dan sore).
    - Pada akhir pekan, jumlah penyewaan oleh pengguna kasual meningkat secara signifikan dibanding dengan hari biasa.
    """)
