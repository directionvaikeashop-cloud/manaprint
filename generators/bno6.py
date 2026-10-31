# -*- coding: utf-8 -*-
"""MANAPRINT — BNO 6 BOULES, maquette fournie par Maeva (29/10).
16 cartons / feuille A4 PAYSAGE (grille 4 colonnes x 4 rangées).
Chaque carton : en-tête B · N · O, puis 2 rangées de 3 cases = 6 numéros.
Colonnes (comme le BNO) :  B 1-15  ·  N 31-45  ·  O 61-75
  -> 2 numéros par colonne, tirés d'un coup et triés (le petit en haut).
Maquette reprise telle quelle ; on ajoute seulement les chiffres et la série."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

PAGE_W, PAGE_H = A4[1], A4[0]        # paysage
CARTES_PAGE = 16
POLICE = "Helvetica-Bold"
GRIS = colors.Color(0.38, 0.38, 0.38)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

# La maquette EST déjà une planche de 16 cartons (4 x 4).
_IMG_W, _IMG_H = 1536, 1024

# Centres MESURÉS sur la maquette (pixels).
# 12 colonnes-cases = 4 cartons x 3 cases (B, N, O) de gauche à droite.
_COLX = [94, 208, 322,  468, 582, 696,  836, 950, 1064,  1207, 1321, 1436]
# 8 rangées-cases = 4 cartons x 2 rangées (haut, bas) de haut en bas.
_ROWY = [105, 192,  361, 449,  615, 702,  863, 951]
# série : centre de chaque carton, dans la gouttière basse.
_SERX = [208, 582, 950, 1321]
_SERY = [253, 508, 760, 993]
PLAGES = [(1, 15), (31, 45), (61, 75)]   # B, N, O
_T = 40.0

MARGE = 4.5 * (A4[0] / 297.0)    # 4.5 mm
_AVW = PAGE_W - 2 * MARGE
_AVH = PAGE_H - 2 * MARGE
def _x(px): return MARGE + px / _IMG_W * _AVW
def _y(py): return (PAGE_H - MARGE) - py / _IMG_H * _AVH

def _fond():
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "bno6_fond.png")
_IMG_FOND = _fond()

def _gen_carton(rng):
    """Deux numéros par colonne (B, N, O), distincts et triés (petit en haut)."""
    cols = []
    for a, b in PLAGES:
        cols.append(sorted(rng.sample(range(a, b + 1), 2)))
    return cols

def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 421)
    serie = int(serie_start); faites = 0
    try: page_dep = max(1, int(page_start))
    except Exception: page_dep = 1
    while faites < n_:
        try: c.drawImage(_IMG_FOND, MARGE, MARGE, _AVW, _AVH, preserveAspectRatio=False, mask="auto")
        except Exception: pass
        for cr in range(4):            # carton-rangée
            for cc in range(4):        # carton-colonne
                if faites >= n_: break
                ys = [_ROWY[cr * 2], _ROWY[cr * 2 + 1]]
                xs = [_COLX[cc * 3], _COLX[cc * 3 + 1], _COLX[cc * 3 + 2]]
                col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else GRIS
                c.setFillColor(col); c.setFont(POLICE, _T)
                for ci, deux in enumerate(_gen_carton(rng)):
                    for r in range(2):
                        c.drawCentredString(_x(xs[ci]), _y(ys[r]) - _T * 0.35, str(deux[r]))
                # série discrète, gouttière basse du carton
                c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont("Helvetica", 7)
                c.drawCentredString(_x(_SERX[cc]), _y(_SERY[cr]) - 7 * 0.34, "N° %05d" % serie)
                serie += 1; faites += 1
            if faites >= n_: break
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont("Helvetica", 6)
            nfe = page_dep + (faites - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 6 * (A4[0] / 297.0), PAGE_H - 7 * (A4[0] / 297.0), "%03d" % nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
