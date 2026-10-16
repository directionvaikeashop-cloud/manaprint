# -*- coding: utf-8 -*-
"""MANAPRINT — ALOHA 75 — nouvelle maquette RETRAVAILLÉE par Maeva (15/10).

🌺 La maquette « ALOHA 75 » (12 cartons par feuille A4 portrait, 2 colonnes ×
6 rangées ; chaque carton : en-tête « N° ___ · ALOHA 75 · fleur », lettres
A·L·O·H·A, grille 5 colonnes × 2 rangées = 10 cases) est reprise TELLE QUELLE,
posée comme UNE SEULE image de fond. On n'ajoute QUE les chiffres et le numéro
de série ; rien n'est redessiné.

RÈGLE — inchangée : 5 colonnes A·L·O·H·A, plages
  A : 1-15 · L : 16-30 · O : 31-45 · H : 46-60 · A : 61-75.
Deux numéros distincts par colonne (un en haut, un en bas), triés.
Chiffres pleins (pas de microtexte) → impression Konica rapide.
"""
import io
import os as _os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4
CARTES_PAGE = 12

POLICE_NUM = "Helvetica-Bold"
POLICE_SER = "Helvetica"
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
NOIR = colors.Color(0, 0, 0)
GRIS = colors.Color(0.45, 0.45, 0.45)

LETTERS = ["A", "L", "O", "H", "A"]
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

# ── Géométrie mesurée sur la maquette (plein cadre A4, points PDF) ──
# 10 colonnes de cases (5 pour le carton de gauche, 5 pour celui de droite)
X_PT = [48.6, 100.7, 152.9, 205.3, 257.5, 337.4, 389.6, 442.0, 494.2, 546.3]
# 12 rangées de cases (6 cartons × 2 rangées : haut / bas)
Y_PT = [766.5, 722.5, 630.7, 586.7, 494.9, 450.9,
        359.0, 315.1, 223.4, 179.4, 87.4, 43.4]
# Début du blanc « N° ___ » de chaque carton (2 colonnes × 6 rangées), points PDF
SER_X = [35.2, 323.8]                 # gauche / droite
SER_Y = [813.6, 677.6, 541.7, 405.7, 269.8, 133.8]

# Taille de case ≈ 50.8 × 39.6 pt ; espacement colonnes ≈ 52.2 pt
_COL_SP = 52.2
_ROW_SP = 44.0
CELL_W = 50.8          # largeur d'une case (pt)
CELL_H = 39.6          # hauteur d'une case (pt)
CELL_R = 6.0           # rayon des coins arrondis (pt)
BLANC = colors.Color(1, 1, 1)


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    for nom in ("aloha75_fond.png", "aloha_75_fond.png"):
        p = _os.path.join(d, nom)
        if _os.path.exists(p):
            return p
    try:
        for f in _os.listdir(d):
            if "aloha75_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "aloha75_fond.png")
_IMG_FOND = _fond()


# Taille des chiffres : le plus gros « 88 » qui tient dans une case, centré.
def _taille_num():
    t = 44.0
    while t > 8 and (stringWidth("88", POLICE_NUM, t) > CELL_W * 0.80
                     or t * 0.70 > CELL_H * 0.82):
        t -= 0.5
    return t
T_NUM = _taille_num()


def _gen_carte(rng):
    """5 colonnes, 2 numéros distincts triés par colonne."""
    return [sorted(rng.sample(range(lo, hi + 1), 2)) for (lo, hi) in RANGES]


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                **_ignore):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 29)
    serie = int(serie_start)
    faites = 0
    try:
        page_dep = max(1, int(page_start))
    except Exception:
        page_dep = 1

    while faites < n_:
        try:
            c.drawImage(_IMG_FOND, 0, 0, PAGE_W, PAGE_H,
                        preserveAspectRatio=False, mask="auto")
        except Exception:
            pass
        # 12 cartons : 2 colonnes (C) × 6 rangées (R)
        for R in range(6):
            for C in range(2):
                if faites >= n_:
                    break
                carte = _gen_carte(rng)
                col = colors.HexColor(RAINBOW[serie % len(RAINBOW)])
                y_haut = Y_PT[R * 2]
                y_bas = Y_PT[R * 2 + 1]
                # ── LA GRILLE EN COULEUR (si couleur) : on recouvre la case
                #    grise de la maquette par une case blanche bordée couleur.
                if couleur:
                    for k in range(5):
                        cx = X_PT[C * 5 + k]
                        for cyc in (y_haut, y_bas):
                            x0 = cx - CELL_W / 2
                            c.setFillColor(BLANC)
                            c.setLineWidth(0)
                            c.roundRect(x0 - 1, cyc - CELL_H / 2 - 1, CELL_W + 2,
                                        CELL_H + 2, CELL_R + 1, stroke=0, fill=1)
                            c.setStrokeColor(col)
                            c.setLineWidth(1.4)
                            c.roundRect(x0, cyc - CELL_H / 2, CELL_W, CELL_H,
                                        CELL_R, stroke=1, fill=0)
                # ── LES CHIFFRES EN NOIR, au centre de chaque case ──
                c.setFillColor(NOIR)
                c.setFont(POLICE_NUM, T_NUM)
                for k in range(5):                       # colonnes A·L·O·H·A
                    cx = X_PT[C * 5 + k]
                    haut, bas = carte[k][0], carte[k][1]
                    c.drawCentredString(cx, y_haut - T_NUM * 0.34, str(haut))
                    c.drawCentredString(cx, y_bas - T_NUM * 0.34, str(bas))
                # numéro de série sur le « N° ___ »
                c.setFillColor(GRIS)
                c.setFont(POLICE_SER, 8.0)
                c.drawString(SER_X[C], SER_Y[R], "%05d" % serie)
                serie += 1
                faites += 1
        # numéro de feuille (marge sûre, jamais rogné)
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(GRIS)
            c.setFont(POLICE_SER, 6.0)
            nfe = page_dep + (faites - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 9 * mm, "%03d" % nfe)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf
