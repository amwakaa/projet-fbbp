import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BLUE   = '#378ADD'
GRAY   = '#B4B2A9'
GREEN  = '#3B6D11'
RED    = '#A32D2D'
ORANGE = '#BA7517'
RES_COLOR = {'W': GREEN, 'D': ORANGE, 'L': RED}

LAYOUT = dict(
    plot_bgcolor='white', paper_bgcolor='white',
    font=dict(color='#333333', family='sans-serif'),
    legend=dict(font=dict(color='#333333')),
    margin=dict(t=30, b=40, l=50, r=20),
)
AXIS = dict(tickfont=dict(color='#333333'), title_font=dict(color='#333333'),
            gridcolor='#eeeeee', linecolor='#dddddd')

MATCHES = {
    'J22 · Orléans — L (0-3)':   'FBBP_ORL_20260220',
    'J23 · QRM — D (2-2)':       'QRM_FBBP_20260228',
    'J24 · Rouen — W (3-1)':     'FBBP_ROU_20260306',
    'J25 · Versailles — L (0-1)':'VER_FBBP_20260313',
    'J26 · Briochin — D (1-1)':  'FBBP_SBR_20260321',
}

MATCH_META = {
    'FBBP_ORL_20260220': {'date':'20/02/2026','adversaire':'Orléans','lieu':'Domicile','resultat':'L','score_fbbp':0,'score_adv':3,'journee':'J22'},
    'QRM_FBBP_20260228': {'date':'28/02/2026','adversaire':'QRM',    'lieu':'Extérieur','resultat':'D','score_fbbp':2,'score_adv':2,'journee':'J23'},
    'FBBP_ROU_20260306': {'date':'06/03/2026','adversaire':'Rouen',  'lieu':'Domicile','resultat':'W','score_fbbp':3,'score_adv':1,'journee':'J24'},
    'VER_FBBP_20260313': {'date':'13/03/2026','adversaire':'Versailles','lieu':'Extérieur','resultat':'L','score_fbbp':0,'score_adv':1,'journee':'J25'},
    'FBBP_SBR_20260321': {'date':'21/03/2026','adversaire':'Briochin','lieu':'Domicile','resultat':'D','score_fbbp':1,'score_adv':1,'journee':'J26'},
}

PERIOD_ORDER = ['1-15', '16-30', '31-45+', '46-60', '61-75', '76-90+']

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

@st.cache_data
def load_data():
    df_matches = pd.read_csv('../data/01_matches_summary.csv')
    df_team    = pd.read_csv('../data/02_teams_stats.csv')
    df_players = pd.read_csv('../data/07_players_stats.csv')
    df_phases  = pd.read_csv('../data/03_matches_phases.csv')
    df_events  = pd.read_csv('../data/04_matches_events.csv')
    df_events['minute'] = df_events['minute'].astype(int)
    df_phases['period'] = pd.Categorical(df_phases['period'], categories=PERIOD_ORDER, ordered=True)
    df_players['poste'] = df_players['player'].map(lambda x: POSTES.get(x, 'Inconnu'))
    df_players['duels_gagnes_pct'] = (df_players['duels_gagnes'] / df_players['duels_total'].replace(0,1) * 100).round(1)
    df_players['rec_p90']          = (df_players['recuperations'] / df_players['minutes'] * 90).round(1)
    df_players['passes_prog_p90']  = (df_players['passes_prog']   / df_players['minutes'] * 90).round(1)
    return df_matches, df_team, df_players, df_phases, df_events

df_matches, df_team, df_players, df_phases, df_events = load_data()

st.title("Analyse match — FBBP")

selected_label = st.selectbox("Sélectionner un match", list(MATCHES.keys()))
match_id = MATCHES[selected_label]
meta     = MATCH_META[match_id]
res      = meta['resultat']
res_label = {'W': 'Victoire', 'D': 'Nul', 'L': 'Défaite'}[res]
res_color = RES_COLOR[res]

# ── HEADER ────────────────────────────────────────────────
st.markdown(f"""
<div style="background:#f4f6fa;border-radius:14px;padding:20px 24px;
            border-left:5px solid {res_color};margin-bottom:1rem;">
    <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
        <div style="font-size:42px;font-weight:700;color:{res_color};line-height:1;">
            {meta['score_fbbp']} – {meta['score_adv']}
        </div>
        <div>
            <div style="font-size:18px;font-weight:500;color:#111;">
                FBBP vs {meta['adversaire']}
            </div>
            <div style="font-size:13px;color:#888;">
                {meta['journee']} · {meta['lieu']} · {meta['date']} · National 1 · {res_label}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── MÉTRIQUES CLÉS ────────────────────────────────────────
row_match  = df_matches[df_matches['match_id'] == match_id].iloc[0]
fbbp_home  = row_match['home_team'] == 'FBBP'
xg_fbbp    = row_match['home_xg']        if fbbp_home else row_match['away_xg']
xg_adv     = row_match['away_xg']        if fbbp_home else row_match['home_xg']
poss_fbbp  = row_match['home_possession'] if fbbp_home else row_match['away_possession']
ppda_fbbp  = row_match['home_ppda']      if fbbp_home else row_match['away_ppda']
ppda_adv   = row_match['away_ppda']      if fbbp_home else row_match['home_ppda']
shots_fbbp = row_match['home_shots']     if fbbp_home else row_match['away_shots']
shots_adv  = row_match['away_shots']     if fbbp_home else row_match['home_shots']

df_team_match = df_team[df_team['match_id'] == match_id]
fbbp_row  = df_team_match[df_team_match['team'] == 'FBBP']
adv_row   = df_team_match[df_team_match['team'] != 'FBBP']
rec_high_fbbp = int(fbbp_row['recoveries_high'].values[0]) if len(fbbp_row) else 0
rec_high_adv  = int(adv_row['recoveries_high'].values[0])  if len(adv_row)  else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("xG FBBP",          f"{xg_fbbp:.2f}", delta=f"{xg_fbbp - xg_adv:+.2f} vs adv.", delta_color="normal")
c2.metric("xG adversaire",    f"{xg_adv:.2f}")
c3.metric("Possession FBBP",  f"{poss_fbbp}%")
c4.metric("PPDA FBBP",        f"{ppda_fbbp:.1f}", delta=f"adv. {ppda_adv:.1f}", delta_color="off")
c5.metric("Récup. hautes",    f"{rec_high_fbbp}", delta=f"adv. {rec_high_adv}", delta_color="off")

st.divider()

col_left, col_right = st.columns([1, 2])

# ── ÉVÉNEMENTS ────────────────────────────────────────────
with col_left:
    st.subheader("Événements clés")

    ev_match = df_events[df_events['match_id'] == match_id].sort_values('minute')
    ev_key   = ev_match[ev_match['event_type'].isin(['goal','red_card','yellow_card'])]

    if ev_key.empty:
        st.markdown("*Aucun événement clé.*")
    else:
        for _, ev in ev_key.iterrows():
            is_fbbp = ev['team'] == 'FBBP'
            if ev['event_type'] == 'goal':
                icon  = '⚽'
                color = GREEN if is_fbbp else RED
            elif ev['event_type'] == 'red_card':
                icon  = '🟥'
                color = RED
            else:
                icon  = '🟨'
                color = ORANGE
            team_label = 'FBBP' if is_fbbp else meta['adversaire']
            player_str = str(ev['player']) if pd.notna(ev['player']) else ''
            st.markdown(
                f"<div style='padding:6px 0;border-bottom:0.5px solid #eee;font-size:13px;'>"
                f"<span style='color:{color};font-weight:500;'>{icon} {int(ev['minute'])}'</span>"
                f" &nbsp; {player_str} <span style='color:#aaa;'>({team_label})</span>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("")
    st.subheader("Remplacements FBBP")
    subs = ev_match[(ev_match['event_type'] == 'substitution') & (ev_match['team'] == 'FBBP')]
    if subs.empty:
        st.markdown("*Aucun remplacement.*")
    else:
        for _, s in subs.iterrows():
            entrant  = str(s['player'])         if pd.notna(s['player'])          else '?'
            sortant  = str(s['player_replaced']) if pd.notna(s['player_replaced']) else '?'
            st.markdown(
                f"<div style='padding:5px 0;border-bottom:0.5px solid #eee;font-size:13px;'>"
                f"<span style='color:#888;'>{int(s['minute'])}'</span>"
                f" &nbsp; ↑ {entrant} &nbsp; ↓ {sortant}"
                f"</div>",
                unsafe_allow_html=True
            )

# ── STATS ÉQUIPE ──────────────────────────────────────────
with col_right:
    st.subheader("Stats équipe — FBBP vs adversaire")

    stats_labels = ['Tirs', 'xG', 'Possession %', 'PPDA', 'Récup. hautes', 'Passes %']

    if len(fbbp_row) and len(adv_row):
        fbbp_vals = [
            shots_fbbp, xg_fbbp, poss_fbbp, ppda_fbbp,
            rec_high_fbbp,
            round(float(fbbp_row['passes_completed'].values[0]) / float(fbbp_row['passes_total'].values[0]) * 100, 1)
            if float(fbbp_row['passes_total'].values[0]) > 0 else 0,
        ]
        adv_vals = [
            shots_adv, xg_adv, 100 - poss_fbbp, ppda_adv,
            rec_high_adv,
            round(float(adv_row['passes_completed'].values[0]) / float(adv_row['passes_total'].values[0]) * 100, 1)
            if float(adv_row['passes_total'].values[0]) > 0 else 0,
        ]

        fig_stats = go.Figure()
        fig_stats.add_trace(go.Bar(
            name='FBBP', y=stats_labels, x=[-v for v in fbbp_vals],
            orientation='h', marker_color=BLUE, opacity=0.85,
            text=[str(v) for v in fbbp_vals],
            textposition='inside', textfont=dict(color='white', size=11),
        ))
        fig_stats.add_trace(go.Bar(
            name=meta['adversaire'], y=stats_labels, x=adv_vals,
            orientation='h', marker_color=GRAY, opacity=0.85,
            text=[str(v) for v in adv_vals],
            textposition='inside', textfont=dict(color='white', size=11),
        ))
        fig_stats.add_vline(x=0, line_color='#333', line_width=1)
        fig_stats.update_layout(
            **LAYOUT, barmode='relative', height=320,
            bargap=0.25,
            xaxis=dict(showticklabels=False, gridcolor='#eeeeee', zeroline=False),
            yaxis=dict(tickfont=dict(color='#333333', size=12), gridcolor='white'),
        )
        st.plotly_chart(fig_stats, use_container_width=True)

st.divider()

# ── TOP PERFORMERS ────────────────────────────────────────
st.subheader("Top performers FBBP")
st.caption("Joueurs ayant joué au moins 45 minutes — classés par indicateur.")

df_match_players = df_players[
    (df_players['match_id'] == match_id) &
    (df_players['team'] == 'FBBP') &
    (df_players['minutes'] >= 45)
].copy() if 'team' in df_players.columns else df_players[
    (df_players['match_id'] == match_id) &
    (df_players['minutes'] >= 45)
].copy()

if not df_match_players.empty:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**Passes progressives / 90**")
        top_prog = df_match_players.nlargest(3, 'passes_prog_p90')[['player','passes_prog_p90','poste']]
        for i, (_, r) in enumerate(top_prog.iterrows()):
            medal = ['🥇','🥈','🥉'][i]
            st.markdown(f"{medal} **{r['player']}** — {r['passes_prog_p90']:.1f} <span style='color:#aaa;font-size:12px;'>({r['poste']})</span>", unsafe_allow_html=True)

    with col_b:
        st.markdown("**Duels gagnés %**")
        top_duels = df_match_players.nlargest(3, 'duels_gagnes_pct')[['player','duels_gagnes_pct','poste']]
        for i, (_, r) in enumerate(top_duels.iterrows()):
            medal = ['🥇','🥈','🥉'][i]
            st.markdown(f"{medal} **{r['player']}** — {r['duels_gagnes_pct']:.0f}% <span style='color:#aaa;font-size:12px;'>({r['poste']})</span>", unsafe_allow_html=True)

    with col_c:
        st.markdown("**Récupérations / 90**")
        top_rec = df_match_players.nlargest(3, 'rec_p90')[['player','rec_p90','poste']]
        for i, (_, r) in enumerate(top_rec.iterrows()):
            medal = ['🥇','🥈','🥉'][i]
            st.markdown(f"{medal} **{r['player']}** — {r['rec_p90']:.1f} <span style='color:#aaa;font-size:12px;'>({r['poste']})</span>", unsafe_allow_html=True)

st.divider()

# ── DYNAMIQUE PAR PÉRIODE ─────────────────────────────────
st.subheader("Dynamique par période")

df_ph_match = df_phases[df_phases['match_id'] == match_id]
df_ph_fbbp  = df_ph_match[df_ph_match['team'] == 'FBBP'].sort_values('period')
df_ph_adv   = df_ph_match[df_ph_match['team'] != 'FBBP'].sort_values('period')

ev_goals = df_events[
    (df_events['match_id'] == match_id) &
    (df_events['event_type'] == 'goal')
]
ev_reds = df_events[
    (df_events['match_id'] == match_id) &
    (df_events['event_type'] == 'red_card')
]

def minute_to_period_idx(minute):
    if minute <= 15:   return 0
    elif minute <= 30: return 1
    elif minute <= 45: return 2
    elif minute <= 60: return 3
    elif minute <= 75: return 4
    else:              return 5

x_idx = list(range(len(PERIOD_ORDER)))

# Regroupe les événements par période pour éviter les chevauchements
def build_period_events(ev_goals, ev_reds):
    period_events = {i: [] for i in range(6)}
    for _, g in ev_goals.iterrows():
        idx = minute_to_period_idx(int(g['minute']))
        symbol = 'But FBBP' if g['team'] == 'FBBP' else 'But adv.'
        color  = GREEN if g['team'] == 'FBBP' else RED
        period_events[idx].append((int(g['minute']), symbol, color))
    for _, r in ev_reds.iterrows():
        idx = minute_to_period_idx(int(r['minute']))
        symbol = 'Rouge FBBP' if r['team'] == 'FBBP' else 'Rouge adv.'
        color  = RED if r['team'] == 'FBBP' else ORANGE
        period_events[idx].append((int(r['minute']), symbol, color))
    return period_events

period_events = build_period_events(ev_goals, ev_reds)

col_dyn1, col_dyn2 = st.columns(2)

with col_dyn1:
    st.markdown("**PPDA par période**")
    fig_ppda = go.Figure()

    fig_ppda.add_trace(go.Scatter(
        x=x_idx, y=df_ph_fbbp['ppda'].values,
        mode='lines+markers+text', name='PPDA FBBP',
        line=dict(color=BLUE, width=2.5), marker=dict(size=8),
        text=[f"{v:.1f}" for v in df_ph_fbbp['ppda'].values],
        textposition='top center', textfont=dict(color=BLUE, size=10),
    ))
    fig_ppda.add_trace(go.Scatter(
        x=x_idx, y=df_ph_adv['ppda'].values,
        mode='lines+markers+text', name=f"PPDA {meta['adversaire']}",
        line=dict(color=GRAY, width=2.5, dash='dash'), marker=dict(size=8),
        text=[f"{v:.1f}" for v in df_ph_adv['ppda'].values],
        textposition='bottom center', textfont=dict(color='#666', size=10),
    ))

    for idx, evs in period_events.items():
        if not evs:
            continue
        evs_sorted = sorted(evs, key=lambda x: x[0])
        label = ' | '.join([f"{e[1]} {e[0]}'" for e in evs_sorted])
        color = RED if any(e[2] == RED for e in evs_sorted) else evs_sorted[0][2]
        fig_ppda.add_vline(
            x=idx, line_dash='dash', line_color=color, line_width=1.5,
            annotation_text=label,
            annotation_font_color=color,
            annotation_font_size=9,
            annotation_position='top left',
        )

    fig_ppda.update_layout(**LAYOUT, height=340, title='')
    fig_ppda.update_xaxes(tickvals=x_idx, ticktext=PERIOD_ORDER,
                          tickfont=dict(color='#333'), gridcolor='#eeeeee')
    fig_ppda.update_yaxes(tickfont=dict(color='#333'), gridcolor='#eeeeee',
                          title_text='PPDA', title_font=dict(color='#333'))
    st.plotly_chart(fig_ppda, use_container_width=True)

with col_dyn2:
    st.markdown("**Attaques / min**")
    fig_atk = go.Figure()

    fig_atk.add_trace(go.Bar(
        name='FBBP', x=x_idx, y=df_ph_fbbp['attacks_per_min'].values,
        marker_color=BLUE, opacity=0.85,
        text=[f"{v:.2f}" for v in df_ph_fbbp['attacks_per_min'].values],
        textposition='outside', textfont=dict(color=BLUE, size=10),
    ))
    fig_atk.add_trace(go.Bar(
        name=meta['adversaire'], x=x_idx, y=df_ph_adv['attacks_per_min'].values,
        marker_color=GRAY, opacity=0.85,
        text=[f"{v:.2f}" for v in df_ph_adv['attacks_per_min'].values],
        textposition='outside', textfont=dict(color='#666', size=10),
    ))

    fig_atk.update_layout(**LAYOUT, height=340, title='', barmode='group')
    fig_atk.update_xaxes(tickvals=x_idx, ticktext=PERIOD_ORDER,
                         tickfont=dict(color='#333'), gridcolor='#eeeeee')
    fig_atk.update_yaxes(tickfont=dict(color='#333'), gridcolor='#eeeeee',
                         title_text='Attaques / min', title_font=dict(color='#333'))
    st.plotly_chart(fig_atk, use_container_width=True)