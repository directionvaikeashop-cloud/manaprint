# -*- coding: utf-8 -*-
"""MANAPRINT — LETTRE U — nouvelle maquette RETRAVAILLEE par Maeva (16/10).

🔡 La maquette « LETTRE U » (A4 portrait, 12 cartons = 3 colonnes x 4 rangees ;
chaque carton : un GRAND U de 13 cases + le petit personnage U aux yeux) est
reprise TELLE QUELLE, posee comme UNE SEULE image de fond. On n'ajoute QUE les
chiffres ; rien n'est redessine.

REGLE — inchangee : 13 numeros en U —
  bras GAUCHE : 5 numeros 1-15 (tries, haut -> bas, dernier = coin bas-gauche)
  PLANCHER (3 cases du milieu) : un 16-30, un 31-45, un 46-60 (gauche -> droite)
  bras DROIT : 5 numeros 61-75 (tries, haut -> bas, dernier = coin bas-droit)
Chiffres pleins (pas de microtexte) -> impression Konica rapide. Latin Modern.
"""
import io
import os as _os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4
CARTES_PAGE = 12

try:
    pdfmetrics.registerFont(TTFont("LMROMAN", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    POLICE_NUM = "LMROMAN"
except Exception:
    POLICE_NUM = "Times-Bold"
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
NOIR = colors.Color(0, 0, 0)

PLAGE_GAUCHE = (1, 15)
PLANCHER = [(16, 30), (31, 45), (46, 60)]
PLAGE_DROITE = (61, 75)

# Positions (points PDF) des 13 cases de chaque carton, mesurees sur la maquette.
# LEFT/RIGHT : 5 cases du haut vers le bas. FLOOR : 3 cases du milieu (g -> d).
LEFT = [
    [(37.0, 804.6), (37.0, 766.2), (37.0, 728.1), (37.0, 692.0), (37.0, 655.8)],
    [(228.5, 804.6), (228.5, 766.2), (228.5, 728.1), (228.5, 692.0), (228.5, 655.8)],
    [(420.4, 804.6), (420.1, 766.2), (420.1, 728.1), (420.1, 692.0), (420.4, 655.8)],
    [(37.0, 600.2), (37.0, 562.4), (37.0, 524.3), (37.0, 487.0), (37.0, 450.6)],
    [(228.5, 600.2), (228.5, 562.4), (228.5, 524.3), (228.5, 487.0), (228.5, 450.6)],
    [(420.1, 600.2), (420.1, 562.4), (420.1, 524.3), (420.1, 487.0), (420.1, 450.6)],
    [(37.0, 394.4), (37.0, 356.6), (37.0, 318.5), (37.0, 282.6), (37.0, 247.0)],
    [(228.5, 394.4), (228.5, 356.6), (228.5, 318.5), (228.5, 282.6), (228.5, 247.3)],
    [(420.1, 394.1), (420.1, 356.6), (420.1, 318.5), (420.1, 282.6), (420.1, 247.3)],
    [(37.0, 190.9), (37.0, 152.2), (37.0, 114.9), (37.0, 79.6), (37.0, 44.0)],
    [(228.5, 190.9), (228.5, 152.5), (228.5, 114.9), (228.5, 79.9), (228.5, 44.0)],
    [(420.1, 190.9), (420.1, 152.5), (420.1, 114.9), (420.1, 79.9), (420.1, 44.0)],
]
FLOOR = [
    [(72.5, 655.8), (106.1, 655.8), (139.9, 655.8)],
    [(264.4, 655.8), (297.9, 655.8), (331.8, 655.8)],
    [(456.2, 655.8), (489.5, 655.8), (523.6, 655.8)],
    [(72.5, 450.6), (106.1, 450.6), (139.9, 450.6)],
    [(264.4, 450.6), (297.9, 450.6), (331.8, 450.6)],
    [(456.2, 450.6), (489.5, 450.6), (523.4, 450.6)],
    [(72.5, 247.0), (106.1, 247.0), (139.7, 247.0)],
    [(264.4, 247.3), (297.9, 247.0), (331.8, 247.3)],
    [(456.2, 247.3), (489.5, 247.3), (523.4, 247.3)],
    [(72.5, 44.0), (106.1, 44.0), (139.9, 44.0)],
    [(264.4, 44.0), (297.9, 44.0), (331.8, 44.0)],
    [(456.2, 44.0), (489.5, 44.0), (523.4, 44.0)],
]
RIGHT = [
    [(175.8, 804.6), (175.8, 766.2), (175.8, 728.1), (175.8, 692.0), (175.8, 655.8)],
    [(367.3, 804.6), (367.3, 766.2), (367.3, 728.1), (367.3, 692.0), (367.3, 655.8)],
    [(559.2, 804.6), (559.2, 766.2), (559.2, 728.1), (559.2, 692.0), (559.2, 655.8)],
    [(175.8, 600.2), (175.8, 562.7), (175.8, 524.3), (175.8, 486.7), (175.8, 450.6)],
    [(367.3, 600.2), (367.3, 562.7), (367.3, 524.3), (367.3, 487.0), (367.3, 450.6)],
    [(559.2, 600.2), (559.2, 562.7), (559.2, 524.3), (559.2, 487.0), (559.2, 450.6)],
    [(175.8, 394.7), (175.8, 356.6), (175.8, 318.5), (175.8, 282.9), (175.8, 247.3)],
    [(367.3, 394.7), (367.3, 356.6), (367.3, 318.5), (367.3, 282.9), (367.3, 247.3)],
    [(559.2, 394.4), (559.2, 356.6), (559.2, 318.5), (559.2, 282.9), (559.2, 247.3)],
    [(175.8, 190.9), (175.8, 152.7), (175.8, 114.9), (175.8, 79.9), (175.8, 44.3)],
    [(367.3, 190.9), (367.3, 152.7), (367.3, 114.9), (367.3, 79.9), (367.3, 44.3)],
    [(559.2, 190.9), (559.2, 152.7), (559.2, 114.9), (558.9, 79.9), (559.2, 44.3)],
]
CELL = 37.8   # cote d'une case (pt)


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    p = _os.path.join(d, "lettre_u_fond.png")
    if _os.path.exists(p):
        return p
    try:
        for f in _os.listdir(d):
            if "lettre_u_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "lettre_u_fond.png")
_IMG_FOND = _fond()


def _taille_num():
    t = 34.0
    while t > 8 and (stringWidth("88", POLICE_NUM, t) > CELL * 0.72
                     or t * 0.70 > CELL * 0.78):
        t -= 0.5
    return t
T_NUM = _taille_num()


def _gen_carte(rng):
    gauche = sorted(rng.sample(range(PLAGE_GAUCHE[0], PLAGE_GAUCHE[1] + 1), 5))
    plancher = [rng.randint(lo, hi) for (lo, hi) in PLANCHER]
    droite = sorted(rng.sample(range(PLAGE_DROITE[0], PLAGE_DROITE[1] + 1), 5))
    return gauche, plancher, droite


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                **_ignore):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 211)
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
        for idx in range(CARTES_PAGE):
            if faites >= n_:
                break
            gauche, plancher, droite = _gen_carte(rng)
            col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col)
            c.setFont(POLICE_NUM, T_NUM)
            dy = T_NUM * 0.34
            for i in range(5):                         # bras gauche
                x, y = LEFT[idx][i]
                c.drawCentredString(x, y - dy, str(gauche[i]))
            for i in range(3):                         # plancher milieu
                x, y = FLOOR[idx][i]
                c.drawCentredString(x, y - dy, str(plancher[i]))
            for i in range(5):                         # bras droit
                x, y = RIGHT[idx][i]
                c.drawCentredString(x, y - dy, str(droite[i]))
            serie += 1
            faites += 1
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(colors.Color(0.45, 0.45, 0.45))
            c.setFont("Helvetica", 6.0)
            nfe = page_dep + (faites - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 9 * mm, "%03d" % nfe)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf
