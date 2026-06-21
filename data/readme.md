# Structure des fichiers CSV - Analyse matchs football (National 1)
# Format Wyscout - 5 matchs

## Clé de jointure commune : `match_id`
Format recommandé : {EQUIPE_DOM}_{EQUIPE_EXT}_{DATE}
Exemple : FBBP_ORL_20260220

---

## 01_match_general.csv
**1 ligne par match**
Informations globales : score, xG, possession, tirs, cartons, formations, entraîneurs, PPDA global.
→ Utilisé pour : vue d'ensemble, comparaison inter-matchs, tendances globales

## 02_equipes_stats.csv
**3 lignes par match par équipe (total / 1ère MT / 2ème MT) = 6 lignes/match**
Statistiques collectives détaillées : passes, attaques, défense, duels, récupérations, pressing (PPDA), formation ligne.
→ Utilisé pour : analyse tactique, impact des mi-temps, intensité du pressing

## 03_joueurs_stats.csv
**1 ligne par joueur par match**
Stats individuelles complètes : passes (toutes catégories), dribbles, duels, tirs, centres, fautes, récupérations, pertes, xG, xA.
→ Utilisé pour : profilage joueurs, détection de patterns individuels, comparaisons

## 04_tirs_xg.csv
**1 ligne par tir**
Détail de chaque tir : minute, joueur, type, résultat (but/cadré/raté/contré), xG, PsxG, zone.
→ Utilisé pour : analyse danger offensif, qualité des occasions, timing des tirs

## 05_evenements.csv
**1 ligne par événement clé**
Buts, cartons (jaune/rouge), remplacements avec minute précise.
→ Utilisé pour : analyse momentum, impact des événements sur le match

## 06_dynamique_match.csv
**6 lignes par équipe par match (tranches 1-15, 16-30, 31-45+, 46-60, 61-75, 76-90+)**
Évolution temporelle : possession, précision passes, duels, attaques/min, récup/min, PPDA, formation ligne.
→ Utilisé pour : identifier les périodes de domination, les ruptures tactiques, la gestion de match

## 07_gardiens.csv
**1 ligne par gardien par match**
Statistiques spécifiques : arrêts, buts concédés, passes, sorties, tirs contre.
→ Utilisé pour : évaluation des gardiens, analyse du jeu au pied

---

## Insights prioritaires à analyser sur 5 matchs

### Offensif
- xG créé vs buts marqués (efficacité)
- Distance moyenne des tirs (profil de jeu)
- Part des attaques aboutissant en zone de réparation
- Répartition flanc gauche / centre / flanc droit (attaques de flanc)
- Précision des centres et résultats

### Défensif
- PPDA par période (intensité du pressing)
- Récupérations hautes vs basses (bloc défensif haut ou bas)
- Duels aériens gagnés (solidité défensive)
- Pertes dans propre terrain → tirs adverses

### Tactique / Dynamique
- Évolution possession par tranche 15 min
- Formation ligne moyenne (compact vs haut)
- Impact des remplacements (avant/après)
- Patterns de passes (courtes/longues, progression)

### Joueurs clés
- Top contributeurs xG + xA
- Joueurs avec le plus de récupérations en terrain adverse
- Ratios duels gagnés par poste
- Pertes de balle critiques (zone + timing)