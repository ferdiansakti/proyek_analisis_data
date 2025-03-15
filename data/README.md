# Cara menjalankan streamlit di local
## Setup Environment (Shell/Terminal)
### 1. Buat direktori proyek
mkdir proyek_analisis_data
cd proyek_analisis_data

### 2. Inisialisasi lingkungan virtual dengan pipenv
pipenv install
pipenv shell

### 3. Install dependensi dari file requirements.txt
pip install -r requirements.txt

## 4. Run Streamlit App
streamlit run dashboard.py
