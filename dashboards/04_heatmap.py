from pathlib import Path as _Path
_DATA = _Path(__file__).resolve().parent.parent / "data"
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

BLUE   = '#378ADD'
GRAY   = '#B4B2A9'
GREEN  = '#3B6D11'
RED    = '#A32D2D'
ORANGE = '#BA7517'
RES_COLOR = {'W': GREEN, 'D': ORANGE, 'L': RED}

MATCH_INFO = {
    'FBBP_ORL_20260220': ('L', 'Orléans',   'J22'),
    'FBBP_ROU_20260306': ('W', 'Rouen',     'J24'),
    'FBBP_SBR_20260321': ('D', 'Briochin',  'J26'),
    'QRM_FBBP_20260228': ('D', 'QRM',       'J23'),
    'VER_FBBP_20260313': ('L', 'Versailles','J25'),
}

POSTES = {
    'Player_52':         'DCentral',
    'Player_59':        'DCentral',
    'Player_55':         'DCentral',
    'Player_61':     'Piston D/G',
    'Player_15': 'Piston D/G',
    'Player_65':       'Milieu déf.',
    'Player_72':        'Milieu déf.',
    'Player_43':        'Milieu déf.',
    'Player_33':         'Milieu créa.',
    'Player_11':         'Attaquant',
    'Player_05':         'Attaquant',
    'Player_68':         'Attaquant',
    'Player_44':     'Attaquant',
    'Player_16':      'Attaquant',
    'Player_21':       'Attaquant',
    'Player_12':       'Piston D/G',
    'Player_64':          'DCentral',
    'Player_50':    'DCentral',
    'Player_45':         'Milieu déf.',
}

POSTE_ORDER = ['DCentral', 'Piston D/G', 'Milieu déf.', 'Milieu créa.', 'Attaquant']

MIN_HEATMAP = 180

@st.cache_data
def load_data():
    df = pd.read_csv((_DATA / "07_players_stats.csv"))
    df['resultat']   = df['match_id'].map(lambda x: MATCH_INFO[x][0])
    df['adversaire'] = df['match_id'].map(lambda x: MATCH_INFO[x][1])
    df['journee']    = df['match_id'].map(lambda x: MATCH_INFO[x][2])
    df['label']      = df['journee'] + ' · ' + df['adversaire']
    df['poste']      = df['player'].map(lambda x: POSTES.get(x, 'Inconnu'))
    df['poste_order']= df['poste'].map(lambda x: POSTE_ORDER.index(x) if x in POSTE_ORDER else 99)

    df['passes_prog_p90']  = (df['passes_prog']      / df['minutes'] * 90).round(1)
    df['passes_tiers_p90'] = (df['passes_tiers']     / df['minutes'] * 90).round(1)
    df['duels_gagnes_pct'] = (df['duels_gagnes']     / df['duels_total'].replace(0,1) * 100).round(1)
    df['duels_def_pct']    = (df['duels_def_gagnes'] / df['duels_def'].replace(0,1) * 100).round(1)
    df['duels_air_pct']    = (df['duels_air_gagnes'] / df['duels_air'].replace(0,1) * 100).round(1)
    df['rec_p90']          = (df['recuperations']    / df['minutes'] * 90).round(1)
    df['rec_adv_p90']      = (df['recuperations_adv']/ df['minutes'] * 90).round(1)
    df['pertes_p90']       = (df['pertes']           / df['minutes'] * 90).round(1)
    df['xg_p90']           = (df['xg']               / df['minutes'] * 90).round(3)
    df['xa_p90']           = (df['xa']               / df['minutes'] * 90).round(3)
    return df

df_all = load_data()

df_team = df_all.groupby(['player','poste','poste_order']).agg(
    total_min        = ('minutes',          'sum'),
    passes_pct       = ('passes_pct',       'mean'),
    passes_prog_p90  = ('passes_prog_p90',  'mean'),
    passes_tiers_p90 = ('passes_tiers_p90', 'mean'),
    duels_gagnes_pct = ('duels_gagnes_pct', 'mean'),
    duels_def_pct    = ('duels_def_pct',    'mean'),
    duels_air_pct    = ('duels_air_pct',    'mean'),
    rec_p90          = ('rec_p90',          'mean'),
    rec_adv_p90      = ('rec_adv_p90',      'mean'),
    pertes_p90       = ('pertes_p90',       'mean'),
    xg_p90           = ('xg_p90',           'mean'),
    xa_p90           = ('xa_p90',           'mean'),
).reset_index()

df_team = df_team[df_team['total_min'] >= MIN_HEATMAP]\
    .sort_values(['poste_order','player']).reset_index(drop=True)

st.title("Heatmap équipe — FBBP")
st.caption(f"Joueurs avec au moins {MIN_HEATMAP} minutes jouées · moyennes sur 5 matchs · J22 → J26")

st.markdown("")
with st.expander("Définitions des indicateurs"):
    st.markdown("""
    - **Passes %** — part des passes qui atteignent un coéquipier
    - **Passes prog. / 90** — passes qui font avancer le ballon significativement vers le but adverse, ramenées à 90 min
    - **Passes tiers / 90** — passes atteignant le dernier tiers du terrain (35m du but adverse), ramenées à 90 min
    - **Duels gagnés %** — part des duels remportés (tous types confondus)
    - **Duels déf. %** — part des duels défensifs remportés (quand l'adversaire a le ballon)
    - **Duels aériens %** — part des duels aériens remportés
    - **Récup. / 90** — récupérations de balle toutes zones confondues, ramenées à 90 min
    - **Récup. adv. / 90** — récupérations effectuées dans le camp adverse, ramenées à 90 min
    - **Pertes / 90** — pertes de balle ramenées à 90 min *(échelle inversée — moins = meilleur)*
    - **xG / 90** — expected goals ramenés à 90 min — probabilité de marquer sur les tirs tentés
    - **xA / 90** — expected assists ramenés à 90 min — probabilité que la passe décisive mène à un but
    """)

tab1, tab2, tab3 = st.tabs([
    "Vue globale — joueurs × indicateurs",
    "Consistance — joueurs × matchs",
    "Phases de jeu — périodes × indicateurs",
])

# ── TAB 1 : JOUEURS × INDICATEURS ────────────────────────
with tab1:
    st.markdown("Chaque cellule montre la valeur brute. La couleur indique la position relative dans l'effectif — **vert = meilleur, rouge = plus faible**.")

    INDICATORS = {
        'Passes %':          'passes_pct',
        'Passes prog. / 90': 'passes_prog_p90',
        'Passes tiers / 90': 'passes_tiers_p90',
        'Duels gagnés %':    'duels_gagnes_pct',
        'Duels déf. %':      'duels_def_pct',
        'Duels aériens %':   'duels_air_pct',
        'Récup. / 90':       'rec_p90',
        'Récup. adv. / 90':  'rec_adv_p90',
        'Pertes / 90':       'pertes_p90',
        'xG / 90':           'xg_p90',
        'xA / 90':           'xa_p90',
    }

    INVERT = {'pertes_p90'}

    players  = df_team['player'].tolist()
    postes   = df_team['poste'].tolist()
    ind_keys = list(INDICATORS.keys())
    ind_cols = list(INDICATORS.values())

    z_matrix   = []
    text_matrix = []
    for col in ind_cols:
        vals  = df_team[col].values.astype(float)
        mn, mx = vals.min(), vals.max()
        if mx == mn:
            normed = [0.5] * len(vals)
        else:
            normed = [(v - mn) / (mx - mn) for v in vals]
            if col in INVERT:
                normed = [1 - n for n in normed]
        z_matrix.append(normed)
        fmt = '.0f' if 'pct' in col or col == 'passes_pct' else '.2f' if 'xg' in col or 'xa' in col else '.1f'
        text_matrix.append([f"{v:{fmt}}" for v in vals])

    z_matrix    = np.array(z_matrix)
    text_matrix = np.array(text_matrix)

    y_labels = [f"{p}<br><span style='font-size:10px;color:#888'>{post}</span>"
                for p, post in zip(players, postes)]

    fig1 = go.Figure(go.Heatmap(
        z=z_matrix,
        x=players,
        y=ind_keys,
        text=text_matrix,
        texttemplate='%{text}',
        textfont=dict(size=11, color='#111111'),
        colorscale=[
            [0.0,  '#A32D2D'],
            [0.5,  '#f8f8f6'],
            [1.0,  '#3B6D11'],
        ],
        showscale=False,
        xgap=2,
        ygap=2,
    ))

    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#333333', family='sans-serif'),
        height=480,
        margin=dict(t=20, b=80, l=140, r=20),
        xaxis=dict(tickfont=dict(size=11, color='#333333'), tickangle=30,
                   side='bottom', gridcolor='white'),
        yaxis=dict(tickfont=dict(size=11, color='#333333'), autorange='reversed',
                   gridcolor='white'),
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    <hr style="border:none;border-top:0.5px solid #ddd;margin:8px 0;">
    La normalisation est faite par indicateur — le vert le plus foncé = meilleur de l'effectif sur cet indicateur.
    Pour les pertes / 90, l'échelle est inversée (moins de pertes = meilleur).
    """, unsafe_allow_html=True)

# ── TAB 2 : JOUEURS × MATCHS ─────────────────────────────
with tab2:
    st.markdown("Choisissez un indicateur pour voir comment chaque joueur a performé match par match.")

    IND_MATCH = {
        'Passes %':          'passes_pct',
        'Passes prog. / 90': 'passes_prog_p90',
        'Duels gagnés %':    'duels_gagnes_pct',
        'Duels déf. %':      'duels_def_pct',
        'Récup. / 90':       'rec_p90',
        'Pertes / 90':       'pertes_p90',
        'xG':                'xg',
        'xA':                'xa',
    }

    selected_ind = st.selectbox("Indicateur", list(IND_MATCH.keys()), key='ind_match')
    col_match    = IND_MATCH[selected_ind]
    invert_match = col_match in INVERT

    match_order  = ['J22', 'J23', 'J24', 'J25', 'J26']
    match_labels = ['J22 · Orléans (L)', 'J23 · QRM (D)', 'J24 · Rouen (W)', 'J25 · Versailles (L)', 'J26 · Briochin (D)']

    eligible = df_team['player'].tolist()
    df_match = df_all[df_all['player'].isin(eligible)].copy()
    df_match = df_match[df_match['minutes'] >= 20]

    pivot = df_match.pivot_table(index='player', columns='journee', values=col_match, aggfunc='mean')
    pivot = pivot.reindex(columns=match_order)
    pivot = pivot.reindex(eligible)

    z2    = pivot.values.astype(float)
    mn2, mx2 = np.nanmin(z2), np.nanmax(z2)
    if mx2 == mn2:
        z_norm2 = np.full_like(z2, 0.5)
    else:
        z_norm2 = (z2 - mn2) / (mx2 - mn2)
        if invert_match:
            z_norm2 = 1 - z_norm2

    fmt2 = '.0f' if 'pct' in col_match or col_match == 'passes_pct' else '.2f' if col_match in ['xg','xa'] else '.1f'
    text2 = np.where(np.isnan(z2), '—', [[f"{v:{fmt2}}" if not np.isnan(v) else '—' for v in row] for row in z2])

    fig2 = go.Figure(go.Heatmap(
        z=z_norm2,
        x=match_labels,
        y=eligible,
        text=text2,
        texttemplate='%{text}',
        textfont=dict(size=11, color='#111111'),
        colorscale=[
            [0.0, '#A32D2D'],
            [0.5, '#f8f8f6'],
            [1.0, '#3B6D11'],
        ],
        showscale=False,
        xgap=2, ygap=2,
    ))
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#333333', family='sans-serif'),
        height=max(400, len(eligible) * 32),
        margin=dict(t=20, b=60, l=140, r=20),
        xaxis=dict(tickfont=dict(size=11, color='#333333'), tickangle=20, gridcolor='white'),
        yaxis=dict(tickfont=dict(size=11, color='#333333'), autorange='reversed', gridcolor='white'),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("**—** indique que le joueur n'a pas joué ou a joué moins de 20 minutes sur ce match.")

# ── TAB 3 : PHASES DE JEU ────────────────────────────────
with tab3:
    st.markdown("Moyennes sur les 5 matchs par tranche de 15 minutes — FBBP vs adversaires.")

    @st.cache_data
    def load_phases():
        df_p = pd.read_csv((_DATA / "03_matches_phases.csv"))
        PERIOD_ORDER = ['1-15', '16-30', '31-45+', '46-60', '61-75', '76-90+']
        df_p['period'] = pd.Categorical(df_p['period'], categories=PERIOD_ORDER, ordered=True)
        return df_p, PERIOD_ORDER

    df_phases, PERIOD_ORDER = load_phases()
    df_fbbp = df_phases[df_phases['team'] == 'FBBP']
    df_adv  = df_phases[df_phases['team'] != 'FBBP']

    PHASE_IND = {
        'PPDA':               'ppda',
        'Possession %':       'possession_pct',
        'Attaques / min':     'attacks_per_min',
        'Récup. / min':       'recoveries_per_min',
        'Précision passes %': 'pass_accuracy_pct',
    }

    selected_phase = st.selectbox("Indicateur", list(PHASE_IND.keys()), key='ind_phase')
    col_phase = PHASE_IND[selected_phase]
    invert_phase = col_phase == 'ppda'

    avg_fbbp = df_fbbp.groupby('period')[col_phase].mean().reindex(PERIOD_ORDER).values
    avg_adv  = df_adv.groupby('period')[col_phase].mean().reindex(PERIOD_ORDER).values

    z3    = np.array([avg_fbbp, avg_adv])
    mn3, mx3 = np.nanmin(z3), np.nanmax(z3)
    z_norm3 = (z3 - mn3) / (mx3 - mn3) if mx3 != mn3 else np.full_like(z3, 0.5)
    if invert_phase:
        z_norm3 = 1 - z_norm3

    text3 = [[f"{v:.1f}" for v in row] for row in z3]

    fig3 = go.Figure(go.Heatmap(
        z=z_norm3,
        x=PERIOD_ORDER,
        y=['FBBP', 'Adversaires (moy.)'],
        text=text3,
        texttemplate='%{text}',
        textfont=dict(size=13, color='#111111'),
        colorscale=[
            [0.0, '#A32D2D'],
            [0.5, '#f8f8f6'],
            [1.0, '#3B6D11'],
        ],
        showscale=False,
        xgap=3, ygap=3,
    ))
    fig3.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#333333', family='sans-serif'),
        height=220,
        margin=dict(t=20, b=40, l=160, r=20),
        xaxis=dict(tickfont=dict(size=12, color='#333333'), gridcolor='white'),
        yaxis=dict(tickfont=dict(size=12, color='#333333'), gridcolor='white'),
    )
    st.plotly_chart(fig3, use_container_width=True)

    if invert_phase:
        st.markdown("Pour le PPDA, **vert = pressing fort** (valeur basse), **rouge = pressing relâché**.")
    else:
        st.markdown(f"**Vert = valeur élevée**, **rouge = valeur faible** pour {selected_phase}.")

    st.divider()
    st.markdown("""
    #### Synthèse heatmap phases de jeu

    Ce graphique permet de lire d'un coup d'œil les périodes de force et de faiblesse
    de FBBP par rapport à ses adversaires. Combinez avec la page Phases de jeu pour
    voir les détails match par match.
    """)

