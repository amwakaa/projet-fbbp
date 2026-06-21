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

PERIOD_ORDER = ['1-15', '16-30', '31-45+', '46-60', '61-75', '76-90+']
PERIOD_IDX   = list(range(len(PERIOD_ORDER)))

MATCH_INFO = {
    'FBBP_ORL_20260220': ('L', 'Orléans'),
    'FBBP_ROU_20260306': ('W', 'Rouen'),
    'FBBP_SBR_20260321': ('D', 'Briochin'),
    'QRM_FBBP_20260228': ('D', 'QRM'),
    'VER_FBBP_20260313': ('L', 'Versailles'),
}

LAYOUT = dict(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='#333333', family='sans-serif'),
    title_font=dict(size=14, color='#111111'),
    legend=dict(font=dict(color='#333333')),
    margin=dict(t=50, b=40, l=50, r=20),
)
AXIS = dict(
    tickfont=dict(color='#333333'),
    title_font=dict(color='#333333'),
    gridcolor='#eeeeee',
    linecolor='#dddddd',
    tickvals=PERIOD_IDX,
    ticktext=PERIOD_ORDER,
)

def minute_to_period(minute):
    if minute <= 15:   return '1-15'
    elif minute <= 30: return '16-30'
    elif minute <= 45: return '31-45+'
    elif minute <= 60: return '46-60'
    elif minute <= 75: return '61-75'
    else:              return '76-90+'

@st.cache_data
def load_data():
    df = pd.read_csv((_DATA / "03_matches_phases.csv"))
    df['period'] = pd.Categorical(df['period'], categories=PERIOD_ORDER, ordered=True)
    df['period_idx'] = df['period'].map({p: i for i, p in enumerate(PERIOD_ORDER)})
    df_fbbp = df[df['team'] == 'FBBP'].copy().reset_index(drop=True)
    df_adv  = df[df['team'] != 'FBBP'].copy().reset_index(drop=True)
    df_fbbp['resultat']   = df_fbbp['match_id'].map(lambda x: MATCH_INFO[x][0])
    df_fbbp['adversaire'] = df_fbbp['match_id'].map(lambda x: MATCH_INFO[x][1])

    ev = pd.read_csv((_DATA / "04_matches_events.csv"))
    ev['minute']     = ev['minute'].astype(int)
    ev['period']     = ev['minute'].apply(minute_to_period)
    ev['period_idx'] = ev['period'].map({p: i for i, p in enumerate(PERIOD_ORDER)})
    return df_fbbp, df_adv, ev

df_fbbp, df_adv, events = load_data()

st.title("Phases de jeu — FBBP")
st.caption("Analyse par tranche de 15 minutes · J22 → J26")

match_options = {f"{v[1]} ({v[0]})": k for k, v in MATCH_INFO.items()}
selected  = st.selectbox("Sélectionner un match", list(match_options.keys()))
match_id  = match_options[selected]
res       = MATCH_INFO[match_id][0]
res_label = {'W': 'Victoire', 'D': 'Nul', 'L': 'Défaite'}[res]

st.markdown(f"Résultat : **{res_label}**")
st.markdown("Évolution du pressing (PPDA) et de l'intensité offensive par tranche de 15 minutes. Les buts et cartons rouges sont annotés sur le graphique PPDA.")

ev_match = events[
    (events['match_id'] == match_id) &
    (events['event_type'].isin(['goal', 'red_card']))
].copy()

col1, col2 = st.columns(2)

with col1:
    data     = df_fbbp[df_fbbp['match_id'] == match_id].sort_values('period_idx')
    data_adv = df_adv[df_adv['match_id']   == match_id].sort_values('period_idx')

    st.markdown("**PPDA par période** — Un PPDA bas indique un pressing intense. Les événements clés (buts, cartons rouges) sont annotés en ligne verticale.")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=PERIOD_IDX, y=data['ppda'].values,
        mode='lines+markers+text', name='PPDA FBBP',
        line=dict(color=BLUE, width=2.5), marker=dict(size=8),
        text=[f'{v:.1f}' for v in data['ppda'].values],
        textposition='top center',
        textfont=dict(color=BLUE, size=10),
    ))
    fig.add_trace(go.Scatter(
        x=PERIOD_IDX, y=data_adv['ppda'].values,
        mode='lines+markers+text', name='PPDA adversaire',
        line=dict(color=GRAY, width=2.5, dash='dash'), marker=dict(size=8),
        text=[f'{v:.1f}' for v in data_adv['ppda'].values],
        textposition='bottom center',
        textfont=dict(color='#666666', size=10),
    ))
    fig.add_hline(y=10, line_dash='dot', line_color='#aaaaaa',
                  annotation_text='seuil ~10', annotation_font_color='#888888')

    for _, row_ev in ev_match.sort_values('minute').iterrows():
        is_fbbp_goal = row_ev['event_type'] == 'goal'    and row_ev['team'] == 'FBBP'
        is_adv_goal  = row_ev['event_type'] == 'goal'    and row_ev['team'] != 'FBBP'
        is_fbbp_red  = row_ev['event_type'] == 'red_card' and row_ev['team'] == 'FBBP'

        if is_fbbp_goal:
            color, symbol = GREEN, f"But FBBP {int(row_ev['minute'])}'"
        elif is_adv_goal:
            color, symbol = RED,   f"But {int(row_ev['minute'])}'"
        elif is_fbbp_red:
            color, symbol = RED,   f"Rouge FBBP {int(row_ev['minute'])}'"
        else:
            color, symbol = ORANGE, f"Rouge adv. {int(row_ev['minute'])}'"

        fig.add_vline(
            x=int(row_ev['period_idx']),
            line_dash='dash', line_color=color, line_width=1.5,
            annotation_text=symbol,
            annotation_font_color=color,
            annotation_font_size=10,
            annotation_position='top left',
        )

    fig.update_layout(**LAYOUT, title=f'PPDA par période — {selected}', height=420)
    fig.update_xaxes(**AXIS, title_text='Période')
    fig.update_yaxes(tickfont=dict(color='#333333'), title_font=dict(color='#333333'),
                     gridcolor='#eeeeee', title_text='PPDA (bas = pressing fort)')
    st.plotly_chart(fig, use_container_width=True)

    if not ev_match.empty:
        st.markdown("**Événements clés :**")
        for _, row_ev in ev_match.sort_values('minute').iterrows():
            is_fbbp = row_ev['team'] == 'FBBP'
            if row_ev['event_type'] == 'goal':
                icon = '⚽'
                team = 'FBBP' if is_fbbp else MATCH_INFO[match_id][1]
            else:
                icon = '🟥'
                team = 'FBBP' if is_fbbp else MATCH_INFO[match_id][1]
            st.markdown(f"- {icon} **{int(row_ev['minute'])}'** — {row_ev['player']} ({team})")

with col2:
    st.markdown("**Attaques par minute** — Volume offensif de chaque équipe par tranche. Montre qui prend le dessus dans chaque période.")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name='Attaques FBBP', x=PERIOD_IDX,
        y=data['attacks_per_min'].values,
        marker_color=BLUE, opacity=0.85,
        text=[f'{v:.2f}' for v in data['attacks_per_min'].values],
        textposition='outside',
        textfont=dict(color=BLUE, size=10),
    ))
    fig2.add_trace(go.Bar(
        name='Attaques adversaire', x=PERIOD_IDX,
        y=data_adv['attacks_per_min'].values,
        marker_color=GRAY, opacity=0.85,
        text=[f'{v:.2f}' for v in data_adv['attacks_per_min'].values],
        textposition='outside',
        textfont=dict(color='#666666', size=10),
    ))
    fig2.update_layout(**LAYOUT, title=f'Attaques / minute — {selected}',
                       barmode='group', height=420)
    fig2.update_xaxes(**AXIS, title_text='Période')
    fig2.update_yaxes(tickfont=dict(color='#333333'), title_font=dict(color='#333333'),
                      gridcolor='#eeeeee', title_text='Attaques / min')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Vue globale — tous matchs")
st.markdown("Moyennes sur les 5 matchs pour identifier des patterns récurrents indépendamment des adversaires.")

col3, col4 = st.columns(2)

with col3:
    avg_ppda_fbbp = df_fbbp.groupby('period_idx')['ppda'].mean().reindex(PERIOD_IDX)
    avg_ppda_adv  = df_adv.groupby('period_idx')['ppda'].mean().reindex(PERIOD_IDX)

    st.markdown("**PPDA moyen par période** — Pattern clair : FBBP presse mieux en seconde mi-temps. Les 30 premières minutes sont la zone de vulnérabilité défensive.")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=PERIOD_IDX, y=avg_ppda_fbbp.values,
        mode='lines+markers+text', name='PPDA FBBP (moy.)',
        line=dict(color=BLUE, width=2.5), marker=dict(size=8),
        text=[f'{v:.1f}' for v in avg_ppda_fbbp.values],
        textposition='top center',
        textfont=dict(color=BLUE, size=11),
    ))
    fig3.add_trace(go.Scatter(
        x=PERIOD_IDX, y=avg_ppda_adv.values,
        mode='lines+markers+text', name='PPDA adversaires (moy.)',
        line=dict(color=GRAY, width=2.5, dash='dash'), marker=dict(size=8),
        text=[f'{v:.1f}' for v in avg_ppda_adv.values],
        textposition='bottom center',
        textfont=dict(color='#666666', size=11),
    ))
    fig3.add_hline(y=10, line_dash='dot', line_color='#aaaaaa',
                   annotation_text='seuil ~10', annotation_font_color='#888888')
    fig3.update_layout(**LAYOUT, title='PPDA moyen — tous matchs', height=380)
    fig3.update_xaxes(**AXIS, title_text='Période')
    fig3.update_yaxes(tickfont=dict(color='#333333'), title_font=dict(color='#333333'),
                      gridcolor='#eeeeee', title_text='PPDA moyen')
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    avg_poss = df_fbbp.groupby('period_idx')['possession_pct'].mean().reindex(PERIOD_IDX)

    st.markdown("**Possession moyenne par période** — FBBP monte en possession au fil du match, ce qui confirme une montée en puissance progressive.")
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=PERIOD_IDX, y=avg_poss.values,
        marker_color=BLUE, opacity=0.85,
        text=[f'{v:.0f}%' for v in avg_poss.values],
        textposition='outside',
        textfont=dict(color=BLUE, size=11),
    ))
    fig4.add_hline(y=50, line_dash='dash', line_color='#aaaaaa',
                   annotation_text='50%', annotation_font_color='#888888')
    fig4.update_layout(**LAYOUT, title='Possession moyenne FBBP par période',
                       height=380, showlegend=False)
    fig4.update_xaxes(**AXIS, title_text='Période')
    fig4.update_yaxes(tickfont=dict(color='#333333'), title_font=dict(color='#333333'),
                      gridcolor='#eeeeee', title_text='Possession (%)', range=[0, 90])
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.markdown("""
#### Synthèse phases de jeu

FBBP présente un pattern clair sur l'ensemble des matchs : les 30 premières minutes
sont la zone de vulnérabilité défensive, avec un PPDA moyen de 16.6 en 1-15 et 18.0
en 16-30. L'équipe monte en puissance en seconde mi-temps — PPDA chute à 7.5 en 46-60
— mais les dégâts sont souvent déjà faits.

En parallèle, la possession progresse au fil du match. Ce ciseau entre pressing qui
s'améliore et possession qui monte suggère que FBBP a besoin de temps pour s'installer
dans les matchs.

**Piste pour l'analyse vidéo** : observer les séquences des 30 premières minutes,
notamment les situations défensives à haute pression où l'équipe concède des espaces.
""")