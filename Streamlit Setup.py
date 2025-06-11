import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import ImageColor

DATEIPFAD = r"C:\Users\jonas\Jonas\Skills\Projekte\Musik-Farb-Theorie\Website\Farb Wahrnehmung.xlsx"

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
     "Aetherisch"],
    max_selections=2
)


# --- ÄHNLICHE SONGS BASIEREND AUF FARBE 1 ---
def hex_to_rgb(hex_code):
    return ImageColor.getcolor(hex_code, "RGB")

def farbdistanz(rgb1, rgb2):
    return sum((a - b)**2 for a, b in zip(rgb1, rgb2))**0.5

st.sidebar.title("🔍 Ähnliche Songs nach Farbe 1")

if os.path.exists(DATEIPFAD):
    df = pd.read_excel(DATEIPFAD)

    try:
        aktuelle_rgb = hex_to_rgb(farbe1)
        df["Farbe 1 RGB"] = df["Farbe 1"].apply(hex_to_rgb)
        df["Farbdistanz"] = df["Farbe 1 RGB"].apply(lambda rgb: farbdistanz(rgb, aktuelle_rgb))
        ähnliche = df.sort_values("Farbdistanz").head(5)

        for _, row in ähnliche.iterrows():
            st.sidebar.markdown(f"**🎵 {row['Song']}**  \n💡 Emotion: *{row['Emotion']}*")
            # Farben als farbige Kästchen anzeigen
            farben = [row["Farbe 1"], row["Farbe 2"], row["Farbe 3"]]
            cols = st.sidebar.columns(3)
            for i, col in enumerate(cols):
                col.markdown(
                    f'<div style="width:30px; height:30px; background-color:{farben[i]}; border-radius:5px; margin-bottom:5px;"></div>',
                    unsafe_allow_html=True
                )
    except Exception as e:
        st.sidebar.error("Fehler beim Vergleichen der Farben.")


else:
    st.sidebar.info("Noch keine gespeicherten Songs vorhanden.")

# --- SPEICHERN ---
if st.button("💾 Ergebnisse speichern"):
    if song.strip() == "":
        st.warning("Bitte gib einen Songtitel oder Link ein.")
    else:
        neuer_eintrag = {
            "Zeitstempel": datetime.now(),
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
            "Emotion": emotion,
        }

        if os.path.exists(DATEIPFAD):
            df = pd.read_excel(DATEIPFAD)
            df = df[df["Song"] != song.strip()]  # Duplikate vermeiden
            df = pd.concat([df, pd.DataFrame([neuer_eintrag])], ignore_index=True)
        else:
            df = pd.DataFrame([neuer_eintrag])

        df.to_excel(DATEIPFAD, index=False)
        st.success(f"✅ Gespeichert: {DATEIPFAD}")

if st.button("📋 Alle gespeicherten Songs anzeigen"):
    if os.path.exists(DATEIPFAD):
        df = pd.read_excel(DATEIPFAD)
        if not df.empty:
            st.subheader("🎶 Alle gespeicherten Songs")
            for _, row in df.iterrows():
                cols = st.columns([7, 1, 1, 1])
                # Songtitel + Emotion (als kleiner Text darunter)
                cols[0].markdown(
                    f"**🎵 {row['Song']}**  \n<small><i>{row['Emotion']}</i></small>",
                    unsafe_allow_html=True
                )
                # Farbkästchen nebeneinander
                farben = [row["Farbe 1"], row["Farbe 2"], row["Farbe 3"]]
                for i in range(3):
                    cols[i+1].markdown(
                        f'<div style="width:20px; height:20px; background-color:{farben[i]}; border-radius:4px;"></div>',
                        unsafe_allow_html=True
                    )
        else:
            st.info("Keine gespeicherten Songs gefunden.")
    else:
        st.info("Noch keine gespeicherte Datei vorhanden.")

