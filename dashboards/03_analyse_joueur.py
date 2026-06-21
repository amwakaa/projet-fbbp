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

LAYOUT = dict(
    plot_bgcolor='white', paper_bgcolor='white',
    font=dict(color='#333333', family='sans-serif'),
    title_font=dict(size=14, color='#111111'),
    legend=dict(font=dict(color='#333333')),
    margin=dict(t=30, b=40, l=50, r=20),
)
AXIS = dict(tickfont=dict(color='#333333'), title_font=dict(color='#333333'),
            gridcolor="#eeeeee", linecolor='#dddddd')

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

MIN_COMPARISON = 180

@st.cache_data
def load_data():
    df = pd.read_csv('../data/07_players_stats.csv')
    df['resultat']   = df['match_id'].map(lambda x: MATCH_INFO[x][0])
    df['adversaire'] = df['match_id'].map(lambda x: MATCH_INFO[x][1])
    df['journee']    = df['match_id'].map(lambda x: MATCH_INFO[x][2])
    df = df.sort_values(['player', 'journee']).reset_index(drop=True)
    df['label'] = df['journee'] + ' · ' + df['adversaire']
    df['poste'] = df['player'].map(lambda x: POSTES.get(x, 'Inconnu'))

    df['passes_prog_p90']  = (df['passes_prog']      / df['minutes'] * 90).round(1)
    df['passes_tiers_p90'] = (df['passes_tiers']     / df['minutes'] * 90).round(1)
    df['duels_gagnes_pct'] = (df['duels_gagnes']     / df['duels_total'].replace(0, 1) * 100).round(1)
    df['duels_def_pct']    = (df['duels_def_gagnes'] / df['duels_def'].replace(0, 1) * 100).round(1)
    df['duels_air_pct']    = (df['duels_air_gagnes'] / df['duels_air'].replace(0, 1) * 100).round(1)
    df['rec_p90']          = (df['recuperations']    / df['minutes'] * 90).round(1)
    df['rec_adv_p90']      = (df['recuperations_adv']/ df['minutes'] * 90).round(1)
    df['pertes_p90']       = (df['pertes']           / df['minutes'] * 90).round(1)
    df['xg_p90']           = (df['xg']               / df['minutes'] * 90).round(3)
    df['xa_p90']           = (df['xa']               / df['minutes'] * 90).round(3)

    ev = pd.read_csv('../data/04_matches_events.csv')
    ev['minute'] = ev['minute'].astype(int)
    return df, ev

df_all, events = load_data()

st.sidebar.title("Sélection joueur")
selected_player = st.sidebar.selectbox("Joueur", sorted(df_all['player'].unique()))

df           = df_all[df_all['player'] == selected_player].sort_values('journee').reset_index(drop=True)
df_played    = df[df['minutes'] >= 20]
poste        = POSTES.get(selected_player, 'Inconnu')
total_min    = df['minutes'].sum()
nb_matchs    = len(df_played)
total_buts   = df['goals'].sum()
total_xa     = df['xa'].sum()
total_cj     = df['cartons_jaunes'].sum()
total_cr     = df['cartons_rouges'].sum()
moy_passes   = df_played['passes_pct'].mean()
moy_duels    = df_played['duels_gagnes_pct'].mean()
player_goals = events[(events['player'] == selected_player) & (events['event_type'] == 'goal')]

st.title("Analyse joueur — FBBP")

col_card, col_main = st.columns([1, 3])

with col_card:
    st.markdown(f"# {selected_player}")
    st.markdown(f"*{poste} · FBBP · National 1*")
    st.divider()
    st.markdown(f"⏱ **{total_min}'** jouées ({nb_matchs} matchs)")
    st.markdown(f"⚽ **{int(total_buts)}** but{'s' if total_buts > 1 else ''}")
    st.markdown(f"🎯 **{total_xa:.2f}** xA total")
    st.markdown(f"✅ **{moy_passes:.0f}%** passes réussies")
    st.markdown(f"⚔️ **{moy_duels:.0f}%** duels gagnés")
    if total_cj > 0:
        s = 's' if total_cj > 1 else ''
        st.markdown(f"🟨 **{int(total_cj)}** carton{s} jaune{s}")
    if total_cr > 0:
        st.markdown(f"🟥 **{int(total_cr)}** carton rouge")
    if not player_goals.empty:
        st.divider()
        st.markdown("**Buts**")
        for _, g in player_goals.iterrows():
            adv = MATCH_INFO[g['match_id']][1]
            det = str(g['detail']).split(' - ')[0]\
                .replace('right_foot', 'pied droit')\
                .replace('left_foot', 'pied gauche')\
                .replace('header', 'tête')\
                .replace('penalty', 'penalty')
            st.markdown(f"- {int(g['minute'])}' vs {adv} — {det}")

with col_main:
    tab1, tab2, tab3 = st.tabs(["Création", "Défense & Duels", "Match par match"])

    with tab1:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Passes % moy.",     f"{df_played['passes_pct'].mean():.0f}%")
        m2.metric("Passes prog. / 90", f"{df_played['passes_prog_p90'].mean():.1f}")
        m3.metric("Passes tiers / 90", f"{df_played['passes_tiers_p90'].mean():.1f}")
        m4.metric("xG + xA / 90",      f"{(df_played['xg_p90'] + df_played['xa_p90']).mean():.3f}")

        st.markdown("**Volume de création par match** — Passes progressives et dernier tiers ramenées à 90 minutes.")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df_played['label'], y=df_played['passes_prog_p90'],
            mode='lines+markers+text', name='Passes prog. / 90',
            line=dict(color=ORANGE, width=2.5), marker=dict(size=8),
            text=[f"{v:.1f}" for v in df_played['passes_prog_p90']],
            textposition='top center', textfont=dict(color=ORANGE, size=11),
        ))
        fig1.add_trace(go.Scatter(
            x=df_played['label'], y=df_played['passes_tiers_p90'],
            mode='lines+markers+text', name='Passes tiers / 90',
            line=dict(color=BLUE, width=2.5), marker=dict(size=8),
            text=[f"{v:.1f}" for v in df_played['passes_tiers_p90']],
            textposition='bottom center', textfont=dict(color=BLUE, size=11),
        ))
        for i, res in enumerate(df_played['resultat']):
            fig1.add_vrect(x0=i-0.5, x1=i+0.5, fillcolor=RES_COLOR[res], opacity=0.35, line_width=0)
        fig1.update_layout(**LAYOUT, height=300, title='')
        fig1.update_xaxes(**AXIS)
        fig1.update_yaxes(**AXIS, title_text='Actions / 90 min')
        st.plotly_chart(fig1, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Précision des passes** — Globale vs passes progressives.")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name='Passes %', x=df_played['label'], y=df_played['passes_pct'],
                                  marker_color=BLUE, opacity=0.85,
                                  text=[f"{v:.0f}%" for v in df_played['passes_pct']],
                                  textposition='outside', textfont=dict(color=BLUE, size=11)))
            fig2.add_trace(go.Bar(name='Passes prog. %', x=df_played['label'], y=df_played['passes_prog_pct'],
                                  marker_color=ORANGE, opacity=0.85,
                                  text=[f"{v:.0f}%" for v in df_played['passes_prog_pct']],
                                  textposition='outside', textfont=dict(color=ORANGE, size=11)))
            for i, res in enumerate(df_played['resultat']):
                fig2.add_vrect(x0=i-0.5, x1=i+0.5, fillcolor=RES_COLOR[res], opacity=0.05, line_width=0)
            fig2.update_layout(**LAYOUT, barmode='group', height=300, title='')
            fig2.update_xaxes(**AXIS)
            fig2.update_yaxes(**AXIS, title_text='%', range=[0, 120])
            st.plotly_chart(fig2, use_container_width=True)

        with col_b:
            st.markdown("**xG + xA par match** — Contribution directe au danger offensif.")
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(name='xG', x=df_played['label'], y=df_played['xg'],
                                  marker_color=GREEN, opacity=0.85,
                                  text=[f"{v:.2f}" for v in df_played['xg']],
                                  textposition='outside', textfont=dict(color=GREEN, size=11)))
            fig3.add_trace(go.Bar(name='xA', x=df_played['label'], y=df_played['xa'],
                                  marker_color=ORANGE, opacity=0.85,
                                  text=[f"{v:.2f}" for v in df_played['xa']],
                                  textposition='outside', textfont=dict(color=ORANGE, size=11)))
            for i, res in enumerate(df_played['resultat']):
                fig3.add_vrect(x0=i-0.5, x1=i+0.5, fillcolor=RES_COLOR[res], opacity=0.05, line_width=0)
            fig3.update_layout(**LAYOUT, barmode='stack', height=300, title='')
            fig3.update_xaxes(**AXIS)
            fig3.update_yaxes(**AXIS, title_text='xG + xA')
            st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Duels gagnés %",   f"{df_played['duels_gagnes_pct'].mean():.0f}%")
        m2.metric("Duels déf. %",     f"{df_played['duels_def_pct'].mean():.0f}%")
        m3.metric("Duels aériens %",  f"{df_played['duels_air_pct'].mean():.0f}%")
        m4.metric("Récup. adv. / 90", f"{df_played['rec_adv_p90'].mean():.1f}")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Duels gagnés % par match** — Global, défensif et aérien.")
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=df_played['label'], y=df_played['duels_gagnes_pct'],
                                      mode='lines+markers+text', name='Duels total %',
                                      line=dict(color=BLUE, width=2.5), marker=dict(size=8),
                                      text=[f"{v:.0f}%" for v in df_played['duels_gagnes_pct']],
                                      textposition='top center', textfont=dict(color=BLUE, size=10)))
            fig4.add_trace(go.Scatter(x=df_played['label'], y=df_played['duels_def_pct'],
                                      mode='lines+markers+text', name='Duels déf. %',
                                      line=dict(color=GREEN, width=2, dash='dash'), marker=dict(size=7),
                                      text=[f"{v:.0f}%" for v in df_played['duels_def_pct']],
                                      textposition='bottom center', textfont=dict(color=GREEN, size=10)))
            fig4.add_trace(go.Scatter(x=df_played['label'], y=df_played['duels_air_pct'],
                                      mode='lines+markers+text', name='Duels aér. %',
                                      line=dict(color=ORANGE, width=2, dash='dot'), marker=dict(size=7),
                                      text=[f"{v:.0f}%" for v in df_played['duels_air_pct']],
                                      textposition='top center', textfont=dict(color=ORANGE, size=10)))
            for i, res in enumerate(df_played['resultat']):
                fig4.add_vrect(x0=i-0.5, x1=i+0.5, fillcolor=RES_COLOR[res], opacity=0.05, line_width=0)
            fig4.add_hline(y=50, line_dash='dot', line_color='#cccccc',
                           annotation_text='50%', annotation_font_color='#aaaaaa')
            fig4.update_layout(**LAYOUT, height=320, title='')
            fig4.update_xaxes(**AXIS)
            fig4.update_yaxes(**AXIS, title_text='%', range=[0, 120])
            st.plotly_chart(fig4, use_container_width=True)

        with col_b:
            st.markdown("**Récupérations vs pertes / 90** — Contribution défensive vs prise de risque.")
            fig5 = go.Figure()
            fig5.add_trace(go.Bar(name='Récup. / 90', x=df_played['label'], y=df_played['rec_p90'],
                                  marker_color=GREEN, opacity=0.85,
                                  text=[f"{v:.1f}" for v in df_played['rec_p90']],
                                  textposition='outside', textfont=dict(color=GREEN, size=11)))
            fig5.add_trace(go.Bar(name='Pertes / 90', x=df_played['label'], y=df_played['pertes_p90'],
                                  marker_color=RED, opacity=0.7,
                                  text=[f"{v:.1f}" for v in df_played['pertes_p90']],
                                  textposition='outside', textfont=dict(color=RED, size=11)))
            for i, res in enumerate(df_played['resultat']):
                fig5.add_vrect(x0=i-0.5, x1=i+0.5, fillcolor=RES_COLOR[res], opacity=0.05, line_width=0)
            fig5.update_layout(**LAYOUT, barmode='group', height=320, title='')
            fig5.update_xaxes(**AXIS)
            fig5.update_yaxes(**AXIS, title_text='Actions / 90 min')
            st.plotly_chart(fig5, use_container_width=True)

    with tab3:
        st.markdown("Matchs avec au moins 20 minutes jouées. La couleur de fond indique le résultat.")
        rows = []
        for _, row in df_played.iterrows():
            rows.append({
                'Match':        row['label'],
                'Résultat':     row['resultat'],
                "Min.'":        int(row['minutes']),
                'Buts':         int(row['goals']),
                'xG':           round(row['xg'], 2),
                'xA':           round(row['xa'], 2),
                'Passes %':     f"{row['passes_pct']:.0f}%",
                'Passes prog.': int(row['passes_prog']),
                'Passes tiers': int(row['passes_tiers']),
                'Duels %':      f"{row['duels_gagnes_pct']:.0f}%",
                'Duels déf. %': f"{row['duels_def_pct']:.0f}%",
                'Récup.':       int(row['recuperations']),
                'Récup. adv.':  int(row['recuperations_adv']),
                'Pertes':       int(row['pertes']),
                'Inter.':       int(row['interceptions']),
            })
        df_display = pd.DataFrame(rows)
        df_table   = df_display.drop(columns=['Résultat']).reset_index(drop=True)
        df_res     = df_display['Résultat'].reset_index(drop=True)

        def color_row(row):
            res   = df_res.iloc[row.name]
            color = {'W': '#c8e6c0', 'D': '#fff3cd', 'L': '#f5c6cb'}.get(res, 'white')
            return [f'background-color: {color}; color: #111111'] * len(row)

        styled = df_table.style.apply(color_row, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Position dans l'équipe")
st.caption(f"Joueurs avec au moins {MIN_COMPARISON} minutes jouées sur la période — stats moyennes / 90 min.")

df_team = df_all.groupby('player').agg(
    total_min=('minutes', 'sum'),
    passes_pct=('passes_pct', 'mean'),
    passes_prog_p90=('passes_prog_p90', 'mean'),
    duels_gagnes_pct=('duels_gagnes_pct', 'mean'),
    rec_p90=('rec_p90', 'mean'),
    xg_p90=('xg_p90', 'mean'),
).reset_index()
df_team = df_team[df_team['total_min'] >= MIN_COMPARISON].copy()
df_team['label_comp'] = df_team['player'] + ' (' + df_team['total_min'].astype(str) + "')"

metric_comp = st.selectbox("Indicateur", [
    'passes_prog_p90', 'passes_pct', 'duels_gagnes_pct', 'rec_p90', 'xg_p90'
], format_func=lambda x: {
    'passes_prog_p90':  'Passes progressives / 90',
    'passes_pct':       'Passes % moyen',
    'duels_gagnes_pct': 'Duels gagnés %',
    'rec_p90':          'Récupérations / 90',
    'xg_p90':           'xG / 90',
}[x])

df_sorted   = df_team.sort_values(metric_comp, ascending=True)
colors_comp = [BLUE if p == selected_player else GRAY for p in df_sorted['player']]

fig_comp = go.Figure()
fig_comp.add_trace(go.Bar(
    y=df_sorted['label_comp'],
    x=df_sorted[metric_comp],
    orientation='h',
    marker_color=colors_comp,
    text=[f"{v:.1f}" for v in df_sorted[metric_comp]],
    textposition='outside',
    textfont=dict(color='#333333', size=11),
))
fig_comp.update_layout(**LAYOUT, height=max(350, len(df_sorted) * 38),
                        title='', showlegend=False)
fig_comp.update_xaxes(**AXIS)
fig_comp.update_yaxes(**AXIS)
st.plotly_chart(fig_comp, use_container_width=True)

st.divider()
st.markdown(f"#### Synthèse — {selected_player}")
st.markdown(f"**Poste** : {poste} · **Minutes jouées** : {total_min}' ({nb_matchs} matchs) · **Buts** : {int(total_buts)} · **xA total** : {total_xa:.2f}")