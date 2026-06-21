import streamlit as st

st.set_page_config(
    page_title="FBBP — Analyse de performance",
    page_icon="⚽",
    layout="wide",
)

pages = [
    st.Page("00_analyse_match.py",  title="Analyse match",   icon="🎯"),
    st.Page("01_analyse_equipe.py", title="Analyse équipe",   icon="📊"),
    st.Page("02_phases_jeu.py",     title="Phases de jeu",    icon="⏱️"),
    st.Page("03_analyse_joueur.py", title="Analyse joueur",   icon="👤"),
    st.Page("04_heatmap.py", title="Heatmap équipe", icon="🔥"),
]

pg = st.navigation(pages)
pg.run()
