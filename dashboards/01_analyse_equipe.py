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
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='#333333', family='sans-serif'),
    title_font=dict(size=14, color='#111111'),
    legend=dict(font=dict(color='#333333')),
    margin=dict(t=50, b=40, l=50, r=20),
)

AXIS = dict(tickfont=dict(color='#333333'), title_font=dict(color='#333333'), gridcolor='#eeeeee', linecolor='#dddddd')

@st.cache_data
def load_data():
    df_raw = pd.read_csv('../data/01_matches_summary.csv').sort_values('round').reset_index(drop=True)

    def get_fbbp_stats(row):
        if row['home_team'] == 'FBBP':
            return pd.Series({
                'xg_fbbp':      row['home_xg'],
                'xg_adv':       row['away_xg'],
                'tirs_fbbp':    row['home_shots'],
                'tirs_adv':     row['away_shots'],
                'dist_tir':     row['home_avg_shot_distance'],
                'dist_tir_adv': row['away_avg_shot_distance'],
                'ppda_fbbp':    row['home_ppda'],
                'ppda_adv':     row['away_ppda'],
                'lieu':         'Dom',
                'adversaire':   row['away_team'],
                'resultat':     'W' if row['home_goals'] > row['away_goals'] else ('D' if row['home_goals'] == row['away_goals'] else 'L'),
                'score':        f"{row['home_goals']}-{row['away_goals']}",
            })
        else:
            return pd.Series({
                'xg_fbbp':      row['away_xg'],
                'xg_adv':       row['home_xg'],
                'tirs_fbbp':    row['away_shots'],
                'tirs_adv':     row['home_shots'],
                'dist_tir':     row['away_avg_shot_distance'],
                'dist_tir_adv': row['home_avg_shot_distance'],
                'ppda_fbbp':    row['away_ppda'],
                'ppda_adv':     row['home_ppda'],
                'lieu':         'Ext',
                'adversaire':   row['home_team'],
                'resultat':     'W' if row['away_goals'] > row['home_goals'] else ('D' if row['away_goals'] == row['home_goals'] else 'L'),
                'score':        f"{row['away_goals']}-{row['home_goals']}",
            })

    df = df_raw.apply(get_fbbp_stats, axis=1)
    df['journee']     = 'J' + df_raw['round'].astype(str).values
    df = df.sort_values('journee').reset_index(drop=True)
    df['xg_diff']     = df['xg_fbbp'] - df['xg_adv']
    df['xg_per_shot'] = (df['xg_fbbp'] / df['tirs_fbbp']).round(3)
    df['label']       = df['journee'] + ' · ' + df['adversaire'] + ' · ' + df['lieu'] + ' · ' + df['score']

    df_raw_team  = pd.read_csv('../data/02_teams_stats.csv')
    df_team_fbbp = df_raw_team[df_raw_team['team'] == 'FBBP'].copy().reset_index(drop=True)
    df_team_adv  = df_raw_team[df_raw_team['team'] != 'FBBP'].copy().reset_index(drop=True)

    df['poss_surf_pct']        = (df_team_fbbp['possessions_to_box'] / df_team_fbbp['possessions'] * 100).round(1).values
    df['poss_surf_pct_adv']    = (df_team_adv['possessions_to_box']  / df_team_adv['possessions']  * 100).round(1).values
    df['rec_high']             = df_team_fbbp['recoveries_high'].values
    df['rec_high_adv']         = df_team_adv['recoveries_high'].values
    df['prog_passes']          = df_team_fbbp['passes_progressive'].values
    df['poss_to_box']          = df_team_fbbp['possessions_to_box'].values
    df['ratio_rec_to_box']     = (df['poss_to_box'] / df['rec_high']).round(2)
    df['prog_passes_per_poss'] = (df['prog_passes'] / df_team_fbbp['possessions'].values).round(3)

    return df

df = load_data()

st.title("Analyse équipe — FBBP")
st.caption("J22 → J26 · National 1 · 5 matchs analysés")

tab1, tab2, tab3 = st.tabs(["Chapitre 1 — Offensif", "Chapitre 1 — Défensif", "Chapitre 2 — Transitions"])

# ─────────────────────────────────────────────────────────
# TAB 1 — OFFENSIF
# ─────────────────────────────────────────────────────────
with tab1:
    st.subheader("Manques offensifs globaux")
    st.markdown("Sur 5 matchs, FBBP produit du jeu mais rarement des occasions franches. Les indicateurs sont dans les moyennes du National 1, mais l'accumulation de ces petits écarts se traduit par un bilan de 1V 2N 2D.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("xG produit / match", f"{df['xg_fbbp'].mean():.2f}",
              delta=f"{df['xg_fbbp'].mean() - df['xg_adv'].mean():.2f} vs adversaires",
              delta_color="inverse")
    c2.metric("xG / tir", f"{df['xg_per_shot'].mean():.3f}",
              delta=f"{df['xg_per_shot'].mean() - 0.13:.3f} vs adversaires",
              delta_color="inverse")
    c3.metric("Distance moy. tir", f"{df['dist_tir'].mean():.1f} m",
              delta=f"+{df['dist_tir'].mean() - df['dist_tir_adv'].mean():.1f} m vs adversaires",
              delta_color="inverse")
    c4.metric("% poss → surface", f"{df['poss_surf_pct'].mean():.1f}%",
              delta=f"{df['poss_surf_pct'].mean() - df['poss_surf_pct_adv'].mean():.1f}% vs adversaires",
              delta_color="inverse")

    st.divider()

    st.markdown("**Domination xG par match** — Le différentiel xG mesure qui a créé les meilleures occasions. FBBP ne domine que 2 matchs sur 5.")
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=df['label'], y=df['xg_diff'],
        marker_color=[GREEN if v >= 0 else RED for v in df['xg_diff']],
        text=[f"{v:+.2f}" for v in df['xg_diff']],
        textposition='outside',
        textfont=dict(color='#333333', size=12),
    ))
    fig1.add_hline(y=0, line_dash='dash', line_color='#aaaaaa',
                   annotation_text='équilibre', annotation_font_color='#666666')
    fig1.update_layout(**LAYOUT, title='xG différentiel par match',
                       showlegend=False, height=350)
    fig1.update_xaxes(**AXIS)
    fig1.update_yaxes(**AXIS, title_text='xG diff (FBBP − Adversaire)',
                      range=[df['xg_diff'].min() * 1.3, df['xg_diff'].max() * 1.3])
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("**Volume de tirs vs qualité par tir** — FBBP tire autant que ses adversaires mais son xG/tir reste structurellement bas (0.08 vs 0.13).")
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.add_trace(go.Bar(name='Tirs FBBP', x=df['label'], y=df['tirs_fbbp'],
                          marker_color=BLUE, opacity=0.85), secondary_y=False)
    fig2.add_trace(go.Bar(name='Tirs adversaire', x=df['label'], y=df['tirs_adv'],
                          marker_color=GRAY, opacity=0.85), secondary_y=False)
    fig2.add_trace(go.Scatter(name='xG/tir FBBP', x=df['label'], y=df['xg_per_shot'],
                              mode='lines+markers+text',
                              line=dict(color=ORANGE, width=2.5, dash='dash'),
                              marker=dict(size=8),
                              text=[f"{v:.3f}" for v in df['xg_per_shot']],
                              textposition='top center',
                              textfont=dict(color=ORANGE, size=11)), secondary_y=True)
    fig2.update_layout(**LAYOUT, title='Volume de tirs vs qualité par tir',
                       barmode='group', height=370)
    fig2.update_xaxes(**AXIS)
    fig2.update_yaxes(title_text='Nombre de tirs', **AXIS, secondary_y=False)
    fig2.update_yaxes(title_text='xG / tir', tickfont=dict(color=ORANGE),
                      title_font=dict(color=ORANGE), secondary_y=True)
    st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Distance moyenne de tir** — FBBP tire 2.5m plus loin que ses adversaires en moyenne.")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            y=df['label'], x=df['dist_tir'],
            orientation='h',
            marker_color=[RES_COLOR[r] for r in df['resultat']],
            text=[f"{v:.1f} m" for v in df['dist_tir']],
            textposition='outside',
            textfont=dict(color='#333333', size=11),
        ))
        fig3.add_vline(x=df['dist_tir_adv'].mean(), line_dash='dash', line_color='#888888',
                       annotation_text=f"moy. adv. {df['dist_tir_adv'].mean():.1f}m",
                       annotation_font_color='#555555',
                       annotation_position='top right')
        fig3.update_layout(**LAYOUT, title='Distance moyenne de tir — FBBP',
                           height=370, showlegend=False)
        fig3.update_xaxes(**AXIS, title_text='Distance (m)')
        fig3.update_yaxes(**AXIS)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown("**Pénétration surface** — FBBP et ses adversaires atteignent la surface à un taux quasi identique (~9%). La pénétration n'est pas le problème.")
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(name='FBBP', x=df['label'], y=df['poss_surf_pct'],
                              marker_color=BLUE,
                              text=[f"{v:.0f}%" for v in df['poss_surf_pct']],
                              textposition='outside',
                              textfont=dict(color=BLUE, size=11)))
        fig4.add_trace(go.Bar(name='Adversaire', x=df['label'], y=df['poss_surf_pct_adv'],
                              marker_color=GRAY,
                              text=[f"{v:.0f}%" for v in df['poss_surf_pct_adv']],
                              textposition='outside',
                              textfont=dict(color='#666666', size=11)))
        fig4.add_hline(y=df['poss_surf_pct'].mean(), line_dash='dot', line_color=BLUE,
                       annotation_text=f"moy. FBBP {df['poss_surf_pct'].mean():.1f}%",
                       annotation_font_color=BLUE)
        fig4.update_layout(**LAYOUT, title='Pénétration offensive — accès à la surface',
                           barmode='group', height=370)
        fig4.update_xaxes(**AXIS)
        fig4.update_yaxes(**AXIS, title_text='% possessions → surface')
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    st.markdown("""
    #### Synthèse offensive

    | Indicateur | FBBP (moy.) | Moy. adversaires | Lecture |
    |---|---|---|---|
    | xG produit / match | 0.88 | 1.13 | FBBP crée moins et moins bien |
    | xG / tir | 0.08 | 0.13 | Les adversaires créent des occasions 60% plus dangereuses |
    | Distance moy. tir | 21.9 m | 19.4 m | FBBP tire 2.5m plus loin en moyenne |
    | % possessions → surface | ~9% | ~9.2% | Taux similaire — le problème est dans la surface, pas avant |

    FBBP atteint la surface aussi souvent que ses adversaires mais génère deux fois moins de danger une fois à l'intérieur.

    **Comment créer des situations de but plus dangereuses ?**
    """)

# ─────────────────────────────────────────────────────────
# TAB 2 — DÉFENSIF
# ─────────────────────────────────────────────────────────
with tab2:
    st.subheader("Analyse défensive")
    st.markdown("FBBP présente un xG concédé moyen de 1.13 sur 5 matchs. Le pressing existe mais ne protège pas suffisamment dans les matchs difficiles.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**xG concédé par match** — 3 matchs sur 5 au-dessus de 1.0 xG concédé. L'exposition défensive est structurelle.")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['label'], y=df['xg_adv'],
            marker_color=[GREEN if v <= df['xg_adv'].mean() else RED for v in df['xg_adv']],
            text=[f"{v:.2f}" for v in df['xg_adv']],
            textposition='outside',
            textfont=dict(color='#333333', size=12),
        ))
        fig.add_hline(y=df['xg_adv'].mean(), line_dash='dash', line_color='#888888',
                      annotation_text=f"moy. {df['xg_adv'].mean():.2f}",
                      annotation_font_color='#555555')
        fig.update_layout(**LAYOUT, title='xG concédé par match', height=370, showlegend=False)
        fig.update_xaxes(**AXIS)
        fig.update_yaxes(**AXIS, title_text='xG concédé', range=[0, df['xg_adv'].max() * 1.25])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Pressing vs xG concédé** — Quand FBBP presse fort (PPDA bas) il concède peu. Versailles reste l'anomalie.")
        fig2 = go.Figure()
        for _, row in df.iterrows():
            fig2.add_trace(go.Scatter(
                x=[row['ppda_fbbp']], y=[row['xg_adv']],
                mode='markers+text',
                marker=dict(color=RES_COLOR[row['resultat']], size=16,
                            line=dict(color='white', width=1.5)),
                text=[row['adversaire']],
                textposition='top right',
                textfont=dict(color='#333333', size=11),
                name=f"{row['adversaire']} ({row['resultat']})",
            ))
        fig2.add_vline(x=df['ppda_fbbp'].mean(), line_dash='dash', line_color='#cccccc',
                       annotation_text='moy. PPDA', annotation_font_color='#888888')
        fig2.add_hline(y=df['xg_adv'].mean(), line_dash='dash', line_color='#cccccc',
                       annotation_text='moy. xG conc.', annotation_font_color='#888888')
        fig2.update_layout(**LAYOUT, title='Pressing FBBP vs xG concédé', height=370)
        fig2.update_xaxes(**AXIS, title_text='PPDA FBBP  ←  bas = pressing fort', autorange='reversed')
        fig2.update_yaxes(**AXIS, title_text='xG concédé')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Récupérations hautes** — FBBP récupère haut plus souvent que ses adversaires sur 4 matchs sur 5.")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name='FBBP', x=df['label'], y=df['rec_high'],
                          marker_color=BLUE,
                          text=df['rec_high'].astype(int),
                          textposition='outside',
                          textfont=dict(color=BLUE, size=11)))
    fig3.add_trace(go.Bar(name='Adversaire', x=df['label'], y=df['rec_high_adv'],
                          marker_color=GRAY,
                          text=df['rec_high_adv'].astype(int),
                          textposition='outside',
                          textfont=dict(color='#666666', size=11)))
    fig3.update_layout(**LAYOUT, title='Récupérations hautes — FBBP vs adversaires',
                       barmode='group', height=370)
    fig3.update_xaxes(**AXIS)
    fig3.update_yaxes(**AXIS, title_text='Récupérations hautes')
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.markdown("""
    #### Synthèse défensive

    FBBP presse et récupère haut de façon consistante, mais ça ne suffit pas à protéger le but.
    Les adversaires créent du danger malgré un pressing correct — notamment Versailles et Orléans
    qui génèrent respectivement 1.90 et 1.44 xG.

    **Le pressing existe. La protection du but ne suit pas.**
    """)

# ─────────────────────────────────────────────────────────
# TAB 3 — TRANSITIONS
# ─────────────────────────────────────────────────────────
with tab3:
    st.subheader("Exploitation des transitions")
    st.markdown("FBBP récupère haut de manière consistante. La question est : que se passe-t-il après ? Dans les défaites, ces récupérations se transforment rarement en danger réel.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Ratio récupérations hautes → surface** — Dans les deux défaites, moins d'une récupération haute sur trois débouche sur une possession atteignant la surface.")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['label'], y=df['ratio_rec_to_box'],
            marker_color=[RES_COLOR[r] for r in df['resultat']],
            text=[f"{v:.2f}" for v in df['ratio_rec_to_box']],
            textposition='outside',
            textfont=dict(color='#333333', size=12),
        ))
        fig.add_hline(y=df['ratio_rec_to_box'].mean(), line_dash='dash', line_color='#888888',
                      annotation_text=f"moy. {df['ratio_rec_to_box'].mean():.2f}",
                      annotation_font_color='#555555')
        fig.update_layout(**LAYOUT, title='Exploitation des récupérations hautes',
                          height=390, showlegend=False)
        fig.update_xaxes(**AXIS)
        fig.update_yaxes(**AXIS, title_text='Possessions → surface / récup. hautes',
                         range=[0, df['ratio_rec_to_box'].max() * 1.25])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Progression du jeu vs transitions** — Plus FBBP progresse avec le ballon, mieux il exploite ses transitions. Briochin est l'anomalie (adversaire trop faible, PPDA 21.8).")
        fig2 = go.Figure()
        for _, row in df.iterrows():
            fig2.add_trace(go.Scatter(
                x=[row['prog_passes_per_poss']], y=[row['ratio_rec_to_box']],
                mode='markers+text',
                marker=dict(color=RES_COLOR[row['resultat']], size=16,
                            line=dict(color='white', width=1.5)),
                text=[row['adversaire']],
                textposition='top right',
                textfont=dict(color='#333333', size=11),
                name=f"{row['adversaire']} ({row['resultat']})",
            ))
        fig2.update_layout(**LAYOUT, title='Progression du jeu vs exploitation des transitions',
                           height=390)
        fig2.update_xaxes(**AXIS, title_text='Passes progressives / possession')
        fig2.update_yaxes(**AXIS, title_text='Ratio récup. hautes → surface')
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.markdown("""
    #### Synthèse transitions

    FBBP atteint la surface adverse aussi souvent que ses adversaires (~9% des possessions),
    mais génère un xG/tir de 0.08 contre 0.13 pour ses adversaires. Dans les défaites,
    moins d'une récupération haute sur trois débouche sur une possession atteignant la surface.

    La variable la plus corrélée au résultat est la capacité à progresser avec le ballon.
    FBBP dépasse 1.0 passes progressives par possession uniquement contre Rouen (victoire).

    **Le pressing existe. L'exploitation ne suit pas.**
    """)