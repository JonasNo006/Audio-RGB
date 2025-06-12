import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import ImageColor
import gspread
from google.oauth2.service_account import Credentials



import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Setup ---
SHEET_NAME = "FarbWahrnehmung"  # kein .xlsx!
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# --- Erwartete Spalten ---
SPALTEN = [
    "Zeitstempel", "Song", "Farbe 1", "Farbe 2", "Farbe 3",
    "Kalt-Warm", "Grell-Pastell", "Form (rund-spitz)", "Formdynamik",
    "Farbübergänge", "Visuelle Dichte", "Emotion"
]

# --- Bestehende Daten laden ---
records = sheet.get_all_records()
df = pd.DataFrame(records)

# 🛠 Fallback: Wenn das Sheet leer ist, erstelle Header-Zeile
if df.empty or df.columns[0] == "":
    sheet.clear()
    sheet.append_row(SPALTEN)
    df = pd.DataFrame(columns=SPALTEN)

# 🧠 Ergebnis aus Streamlit-Eingaben speichern
neuer_eintrag = {
    "Zeitstempel": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "Song": song.strip(),
    "Farbe 1": farbe1,
    "Farbe 2": farbe2,
    "Farbe 3": farbe3,
    "Kalt-Warm": kalt_warm,
    "Grell-Pastell": grell_pastell,
    "Form (rund-spitz)": form_slider,
    "Formdynamik": dynamik_slider,
    "Farbübergänge": farbverlauf,
    "Visuelle Dichte": dichte,
    "Emotion": ", ".join(emotion),  # als String speichern
}

st.set_page_config(page_title="🎶 Farb-Musik-Wahrnehmung", layout="centered")
st.title("🎨 Visuelle Wahrnehmung & Songanalyse")

# --- SONGTITEL ---
song = st.text_input("🎵 Aktueller Songtitel oder Spotify-Link:")

# --- FARBAUSWAHL ---
st.subheader("🎨 Hauptfarben (bis zu 3)")
farbe1 = st.color_picker("Farbe 1", "#FF0000")
farbe2 = st.color_picker("Farbe 2", "#00FF00")
farbe3 = st.color_picker("Farbe 3", "#0000FF")

# --- FARBSTIMMUNG ---
st.subheader("🌡️ Farbstimmung")
kalt_warm = st.slider("Kalt ←→ Warm", 0.0, 1.0, 0.5)
grell_pastell = st.slider("Grell ←→ Pastell", 0.0, 1.0, 0.5)

# --- FORMWAHRNEHMUNG ---
st.subheader("🔺 Formwahrnehmung")
form_slider = st.slider("Rund ←→ Spitz", 0.0, 1.0, 0.5)

# --- FORM-DYNAMIK ---
st.subheader("💫 Dynamik der Formen")
dynamik_slider = st.slider("Wabernd/Fließend ←→ Ruckartig", 0.0, 1.0, 0.5)

# --- FARBÜBERGÄNGE ---
st.subheader("🎨 Farbverläufe")
farbverlauf = st.slider("Sanft ←→ Abrupt", 0.0, 1.0, 0.5)

# --- VISUELLE DICHTE ---
st.subheader("🔳 Visuelle Dichte")
dichte = st.slider("Leer ←→ Überladen", 0.0, 1.0, 0.5)

# --- EMOTIONALE WIRKUNG ---
st.subheader("❤️ Emotionale Wirkung")
emotion = st.multiselect(
    "Wähle bis zu zwei Emotionen:",
    ["Fröhlich", "Traurig", "Party", "Luxuriös", "Melancholisch",
     "Entspannt", "Energetisch", "Rhythmisch", "Bedrohlich", "Verträumt", "Düster",
     "Aetherisch", ],
    max_selections=2
)

# --- ÄHNLICHE SONGS BASIEREND AUF FARBE 1 ---
def hex_to_rgb(hex_code):
    return ImageColor.getcolor(hex_code, "RGB")

def farbdistanz(rgb1, rgb2):
    return sum((a - b)**2 for a, b in zip(rgb1, rgb2))**0.5

st.sidebar.title("🔍 Ähnliche Songs nach Farbe 1")

try:
    df = pd.DataFrame(sheet.get_all_records())

    if not df.empty:
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
except:
    st.sidebar.info("Noch keine gespeicherten Songs vorhanden.")

# --- SPEICHERN ---
if st.button("💾 Ergebnisse speichern"):
    if song.strip() == "":
        st.warning("Bitte gib einen Songtitel oder Link ein.")
    else:
        df = pd.DataFrame(sheet.get_all_records())
        if song.strip() in df["Song"].values:
            idx = df[df["Song"] == song.strip()].index[0]
            sheet.delete_rows(idx + 2)  # Header + 0-indexiert

        neue_zeile = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            song.strip(),
            farbe1,
            farbe2,
            farbe3,
            kalt_warm,
            grell_pastell,
            form_slider,
            dynamik_slider,
            farbverlauf,
            dichte,
            ", ".join(emotion),
        ]

        sheet.append_row(neue_zeile)
        st.success(f"✅ Gespeichert in Google Sheet: {SHEET_NAME}")

# ✅ Duplikatprüfung
    if song.strip() in df["Song"].values:
        st.warning("Dieser Song wurde bereits gespeichert.")
    else:
        sheet.append_row(list(neuer_eintrag.values()))
        st.success("✅ Song erfolgreich gespeichert!")

# --- ANZEIGE ALLER EINTRÄGE ---
if st.button("📋 Alle gespeicherten Songs anzeigen"):
    df = pd.DataFrame(sheet.get_all_records())
    if not df.empty:
        st.subheader("🎶 Alle gespeicherten Songs")
        for _, row in df.iterrows():
            cols = st.columns([7, 1, 1, 1])
            cols[0].markdown(
                f"**🎵 {row['Song']}**  \n<small><i>{row['Emotion']}</i></small>",
                unsafe_allow_html=True
            )
            farben = [row["Farbe 1"], row["Farbe 2"], row["Farbe 3"]]
            for i in range(3):
                cols[i+1].markdown(
                    f'<div style="width:20px; height:20px; background-color:{farben[i]}; border-radius:4px;"></div>',
                    unsafe_allow_html=True
                )
    else:
        st.info("Keine gespeicherten Songs gefunden.")
