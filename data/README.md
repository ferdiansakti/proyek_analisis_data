# Setup Environment (Shell/Terminal)
## Buat direktori proyek
mkdir proyek_analisis_data
cd proyek_analisis_data

## Inisialisasi lingkungan virtual dengan pipenv
pipenv install
pipenv shell

## Install dependensi dari file requirements.txt
pip install -r requirements.txt

# Run Streamlit App
streamlit run dashboard.py
