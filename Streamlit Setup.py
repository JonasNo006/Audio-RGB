import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import ImageColor
import gspread
from google.oauth2.service_account import Credentials

# === CONFIG ===
SHEET_NAME = "FarbMusik"
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPALTEN = [
    "Zeitstempel","Song","Farbe 1","Farbe 2","Farbe 3",
    "Kalt-Warm","Grell-Pastell","Form (rund-spitz)","Formdynamik",
    "Farbübergänge","Visuelle Dichte","Emotion"
]

# === GOOGLE SHEETS SETUP ===
creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Daten laden
records = sheet.get_all_records()
df = pd.DataFrame(records)

# Header prüfen
header_row = sheet.row_values(1)
if header_row != SPALTEN:
    sheet.clear()
    sheet.append_row(SPALTEN)
    df = pd.DataFrame(columns=SPALTEN)

# === STREAMLIT UI ===
st.set_page_config(page_title="🎶 Farb-Musik-Wahrnehmung")
st.title("🎨 Visuelle Wahrnehmung & Songanalyse")

song = st.text_input("🎵 Songtitel oder Spotify-Link:")
farbe1 = st.color_picker("Farbe 1", "#FF0000")
farbe2 = st.color_picker("Farbe 2", "#00FF00")
farbe3 = st.color_picker("Farbe 3", "#0000FF")
kalt_warm = st.slider("Kalt ←→ Warm", 0.0, 1.0, 0.5)
grell_pastell = st.slider("Grell ←→ Pastell", 0.0, 1.0, 0.5)
form_slider = st.slider("Rund ←→ Spitz", 0.0, 1.0, 0.5)
dynamik_slider = st.slider("Wabernd/Fließend ←→ Ruckartig", 0.0, 1.0, 0.5)
farbverlauf = st.slider("Sanft ←→ Abrupt", 0.0, 1.0, 0.5)
dichte = st.slider("Leer ←→ Überladen", 0.0, 1.0, 0.5)
emotion = st.multiselect(
    "Wähle bis zu zwei Emotionen:",
    ["Fröhlich","Traurig","Party","Luxuriös","Melancholisch",
     "Entspannt","Energetisch","Rhythmisch","Bedrohlich","Verträumt","Düster","Aetherisch"],
    max_selections=2
)

# === ÄHNLICHE SONGS ===
st.sidebar.title("🔍 Ähnliche Songs nach Farbe 1")

def hex_to_rgb(h): return ImageColor.getcolor(h, "RGB")
def farbdistanz(a, b): return sum((x-y)**2 for x,y in zip(a,b))**0.5

if not df.empty:
    aktuelle = hex_to_rgb(farbe1)
    df["F1RGB"] = df["Farbe 1"].apply(hex_to_rgb)
    df["Distanz"] = df["F1RGB"].apply(lambda x: farbdistanz(x, aktuelle))
    top5 = df.sort_values("Distanz").head(5)
    cols = st.sidebar.columns(3)
    for i, (_, row) in enumerate(top5.iterrows()):
        st.sidebar.markdown(f"**🎵 {row['Song']}**  \n*{row['Emotion']}*")
        for j in range(3):
            cols[j].markdown(
                f"<div style='width:30px;height:30px;background:{row.get(f'Farbe {j+1}', '#FFFFFF')};'></div>",
                unsafe_allow_html=True
            )

# === SPEICHERN BUTTON ===
if st.button("💾 Ergebnisse speichern"):
    if not song.strip():
        st.warning("❗ Bitte Songtitel eingeben.")
    elif song.strip() in df["Song"].astype(str).tolist():
        st.warning("⚠️ Dieser Song wurde bereits gespeichert.")
    else:
        eintrag = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            song.strip(), farbe1, farbe2, farbe3,
            float(kalt_warm), float(grell_pastell),
            float(form_slider), float(dynamik_slider),
            float(farbverlauf), float(dichte),
            ", ".join(emotion)
        ]
        sheet.append_row(eintrag)
        st.success("✅ Gespeichert!")
        st.experimental_rerun()

# === ALLE ANZEIGEN ===
if st.button("📋 Alle gespeicherten Songs anzeigen"):
    recs = sheet.get_all_records()
    df_all = pd.DataFrame(recs)
    if df_all.empty:
        st.info("Keine Einträge gefunden.")
    else:
        st.subheader("🎶 Alle Songs")
        for _, row in df_all.iterrows():
            c0, c1, c2, c3 = st.columns([7,1,1,1])
            c0.markdown(f"**🎵 {row['Song']}**<br><i>{row['Emotion']}</i>", unsafe_allow_html=True)
            for i in range(3):
                c = [c1, c2, c3][i]
                c.markdown(f"<div style='width:20px;height:20px;background:{row.get(f'Farbe {i+1}', '#FFFFFF')};'></div>", unsafe_allow_html=True)
