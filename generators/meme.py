# -*- coding: utf-8 -*-
"""MANAPRINT — MÉMÉ (RANIHEI SISTERS & SHOP), maquette mémé qui tresse un collier.
8 cartons/feuille (grille 4 colonnes x 2 lignes). 5 bulles-fleurs en bas de
chaque carton, en RANGÉE (gauche -> droite).
Règle (sceau Maeva 26/10) : mêmes plages que BATEAU PIRATE, de gauche à droite :
  1-15, 16-30, 31-45, 46-60, 61-75.
Maquette reprise telle quelle ; on ajoute seulement les chiffres et la série."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4[1], A4[0]        # paysage
CARTES_PAGE = 8
POLICE = "Helvetica-Bold"
GRIS = colors.Color(0.38, 0.38, 0.38)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

# La maquette EST déjà une planche de 8 cartons (4 x 2).
_IMG_W, _IMG_H = 1491, 1055
_COLS, _ROWS = 4, 2
_CW, _CH = _IMG_W / _COLS, _IMG_H / _ROWS

# Centres MESURÉS des 5 bulles-fleurs (rangée du bas), par carton, en pixels.
# Ordre gauche -> droite = plages 1-15, 16-30, 31-45, 46-60, 61-75.
_BULLES = [
    [(44, 471), (116, 471), (186, 471), (257, 471), (328, 471)],
    [(417, 471), (488, 471), (559, 471), (629, 471), (700, 471)],
    [(789, 471), (861, 471), (931, 471), (1002, 471), (1073, 471)],
    [(1162, 471), (1233, 471), (1303, 471), (1373, 471), (1444, 471)],
    [(44, 997), (115, 997), (186, 997), (257, 997), (328, 997)],
    [(417, 997), (488, 997), (559, 998), (629, 997), (700, 998)],
    [(789, 998), (860, 998), (931, 998), (1001, 998), (1073, 998)],
    [(1161, 998), (1232, 998), (1303, 998), (1373, 998), (1444, 998)],
]
_RB_PX = 30.0   # rayon utile (cercle inscrit) d'une bulle-fleur -> taille chiffre
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]   # gauche -> droite

MARGE = 4.5 * mm
_AVW = PAGE_W - 2 * MARGE
_AVH = PAGE_H - 2 * MARGE
def _x(px): return MARGE + px / _IMG_W * _AVW
def _y(py): return (PAGE_H - MARGE) - py / _IMG_H * _AVH

# série : coin bas-gauche du carton (sous la rangée de bulles), calé sur la grille
_POS_SER = (0.06, 0.985)
_SER = []
for _r in range(_ROWS):
    for _c in range(_COLS):
        _SER.append((_c * _CW + _POS_SER[0] * _CW, _r * _CH + _POS_SER[1] * _CH))

def _fond():
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "meme_fond.png")
_IMG_FOND = _fond()

# taille chiffre UNIFORME, au MAXIMUM qui tient dans la bulle-fleur (sceau
# Maeva 26/10 « grossis »). La fleur offre un peu de marge aux pétales -> on
# tolère un chouïa au-delà du cercle inscrit (facteur 1.07).
def _taille(rb_px):
    rb_pt = rb_px / _IMG_W * _AVW
    t = 40.0
    while t > 8:
        w = stringWidth("88", POLICE, t); h = t * 0.70
        if ((w / 2) ** 2 + (h / 2) ** 2) ** 0.5 <= rb_pt * 1.07:
            break
        t -= 0.5
    return t
_T = _taille(_RB_PX)

def _gen_carton(rng):
    return [rng.randint(a, b) for (a, b) in PLAGES]

def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 811)
    serie = int(serie_start); faites = 0
    try: page_dep = max(1, int(page_start))
    except Exception: page_dep = 1
    while faites < n_:
        try: c.drawImage(_IMG_FOND, MARGE, MARGE, _AVW, _AVH, preserveAspectRatio=False, mask="auto")
        except Exception: pass
        for k in range(CARTES_PAGE):
            if faites >= n_: break
            vals = _gen_carton(rng)
            col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else GRIS
            c.setFillColor(col); c.setFont(POLICE, _T)
            for (px, py), v in zip(_BULLES[k], vals):
                c.drawCentredString(_x(px), _y(py) - _T * 0.36, str(v))
            # série discrète, coin bas-gauche
            sx, sy = _SER[k]
            c.setFillColor(colors.white)
            c.rect(_x(sx) - 15, _y(sy) - 6, 30, 13, fill=1, stroke=0)
            c.setFillColor(colors.Color(0.30, 0.30, 0.30)); c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(_x(sx), _y(sy) - 9 * 0.34, "%03d" % serie)
            serie += 1; faites += 1
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont("Helvetica", 6)
            nfe = page_dep + (faites - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 7 * mm, "%03d" % nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
