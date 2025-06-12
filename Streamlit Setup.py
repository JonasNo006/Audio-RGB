import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import ImageColor
import gspread
from google.oauth2.service_account import Credentials

# === CONFIG ===
SHEET_NAME = "FarbWahrnehmung"  # Name deines Google Sheets
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SPALTEN = [
    "Zeitstempel", "Song", "Farbe 1", "Farbe 2", "Farbe 3",
    "Kalt-Warm", "Grell-Pastell", "Form (rund-spitz)", "Formdynamik",
    "Farbübergänge", "Visuelle Dichte", "Emotion"
]

# === GOOGLE SHEETS SETUP ===
creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Bestehende Daten laden (oder Spalten erstellen)
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty or df.columns[0] == "":
    sheet.clear()
    sheet.append_row(SPALTEN)
    df = pd.DataFrame(columns=SPALTEN)

# === STREAMLIT UI ===
st.set_page_config(page_title="🎶 Farb-Musik-Wahrnehmung", layout="centered")
st.title("🎨 Visuelle Wahrnehmung & Songanalyse")

song = st.text_input("🎵 Aktueller Songtitel oder Spotify-Link:")
st.subheader("🎨 Hauptfarben (bis zu 3)")
farbe1 = st.color_picker("Farbe 1", "#FF0000")
farbe2 = st.color_picker("Farbe 2", "#00FF00")
farbe3 = st.color_picker("Farbe 3", "#0000FF")

st.subheader("🌡️ Farbstimmung")
kalt_warm = st.slider("Kalt ←→ Warm", 0.0, 1.0, 0.5)
grell_pastell = st.slider("Grell ←→ Pastell", 0.0, 1.0, 0.5)

st.subheader("🔺 Formwahrnehmung")
form_slider = st.slider("Rund ←→ Spitz", 0.0, 1.0, 0.5)

st.subheader("💫 Dynamik der Formen")
dynamik_slider = st.slider("Wabernd/Fließend ←→ Ruckartig", 0.0, 1.0, 0.5)

st.subheader("🎨 Farbverläufe")
farbverlauf = st.slider("Sanft ←→ Abrupt", 0.0, 1.0, 0.5)

st.subheader("🔳 Visuelle Dichte")
dichte = st.slider("Leer ←→ Überladen", 0.0, 1.0, 0.5)

st.subheader("❤️ Emotionale Wirkung")
emotion = st.multiselect(
    "Wähle bis zu zwei Emotionen:",
    ["Fröhlich", "Traurig", "Party", "Luxuriös", "Melancholisch",
     "Entspannt", "Energetisch", "Rhythmisch", "Bedrohlich", "Verträumt", "Düster",
     "Aetherisch"],
    max_selections=2
)

# === ÄHNLICHE SONGS ===
def hex_to_rgb(hex_code):
    return ImageColor.getcolor(hex_code, "RGB")

def farbdistanz(rgb1, rgb2):
    return sum((a - b)**2 for a, b in zip(rgb1, rgb2))**0.5

st.sidebar.title("🔍 Ähnliche Songs nach Farbe 1")

try:
    aktuelle_rgb = hex_to_rgb(farbe1)
    df["Farbe 1 RGB"] = df["Farbe 1"].apply(hex_to_rgb)
    df["Farbdistanz"] = df["Farbe 1 RGB"].apply(lambda rgb: farbdistanz(rgb, aktuelle_rgb))
    ähnliche = df.sort_values("Farbdistanz").head(5)

for _, row in ähnliche.iterrows():
    st.sidebar.markdown(f"**🎵 {row['Song']}**  \n💡 Emotion: *{row['Emotion']}*")
    farben = [row["Farbe 1"], row["Farbe 2"], row["Farbe 3"]]
    cols = st.sidebar.columns(3)
    for i, col in enumerate(cols):
        col.markdown(
            f'<div style="width:30px; height:30px; background-color:{farben[i]}; border-radius:5px; margin-bottom:5px;"></div>',
            unsafe_allow_html=True
        )

