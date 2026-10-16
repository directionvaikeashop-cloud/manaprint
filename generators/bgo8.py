# -*- coding: utf-8 -*-
"""MANAPRINT — BGO 8 boules — nouvelle maquette RETRAVAILLÉE par Maeva (15/10).

🔠 La maquette « BGO 8 boules » (A4 PAYSAGE, 16 cartons = 4 colonnes × 4 rangées ;
chaque carton : en-tête « B G O », grille 3 colonnes × 3 rangées = 9 cases) est
reprise TELLE QUELLE, posée comme UNE SEULE image de fond. On n'ajoute QUE les
chiffres ; rien n'est redessiné.

RÈGLE — HUIT numéros par carton, la case du CENTRE reste LIBRE (vide) :
  colonne B : 1-15 (3 numéros, haut/milieu/bas)
  colonne G : 46-60 (2 numéros, haut et bas — le milieu est libre)
  colonne O : 61-75 (3 numéros, haut/milieu/bas)
Numéros distincts et triés (croissants du haut vers le bas) dans chaque colonne.
Chiffres pleins (pas de microtexte) → impression Konica rapide.
"""
import io
import os as _os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = landscape(A4)        # 841.9 × 595.3
CARTES_PAGE = 16

try:
    pdfmetrics.registerFont(TTFont("LMROMAN", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    POLICE_NUM = "LMROMAN"
except Exception:
    POLICE_NUM = "Times-Bold"
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
NOIR = colors.Color(0, 0, 0)

# B · G · O
PLAGES = [(1, 15), (46, 60), (61, 75)]

# ── Géométrie mesurée sur la maquette (image 1536×1024 px) ──
_IMG_W, _IMG_H = 1536, 1024
# 12 colonnes de cases (4 cartons × 3 colonnes B/G/O), en px
_X_PX = [100, 212, 324, 472, 584, 695, 840, 951, 1062, 1212, 1324, 1435]
# 12 rangées de cases (4 cartons × 3 rangées haut/milieu/bas), en px
_Y_PX = [86, 148, 210, 338, 400, 462, 590, 652, 714, 842, 904, 966]
# conversion px -> points PDF (paysage)
X_PT = [x / _IMG_W * PAGE_W for x in _X_PX]
Y_PT = [PAGE_H - y / _IMG_H * PAGE_H for y in _Y_PX]
CELL_W = 109 / _IMG_W * PAGE_W         # ≈ 59.7 pt
CELL_H = 63 / _IMG_H * PAGE_H          # ≈ 36.6 pt


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    for nom in ("bgo8_fond.png", "bgo_8_fond.png"):
        p = _os.path.join(d, nom)
        if _os.path.exists(p):
            return p
    try:
        for f in _os.listdir(d):
            if "bgo8_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "bgo8_fond.png")
_IMG_FOND = _fond()


def _taille_num():
    t = 44.0
    while t > 8 and (stringWidth("88", POLICE_NUM, t) > CELL_W * 0.72
                     or t * 0.70 > CELL_H * 0.82):
        t -= 0.5
    return t
T_NUM = _taille_num()


def _gen_carte(rng):
    """B : 3 numéros (1-15) ; G : 2 numéros (46-60) ; O : 3 numéros (61-75)."""
    b = sorted(rng.sample(range(1, 16), 3))
    g = sorted(rng.sample(range(46, 61), 2))
    o = sorted(rng.sample(range(61, 76), 3))
    return b, g, o


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                **_ignore):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 83)
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
        # 16 cartons : 4 colonnes (CC) × 4 rangées (CR)
        for CR in range(4):
            for CC in range(4):
                if faites >= n_:
                    break
                b, g, o = _gen_carte(rng)
                col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else NOIR
                c.setFillColor(col)
                c.setFont(POLICE_NUM, T_NUM)
                xb = X_PT[CC * 3 + 0]      # colonne B
                xg = X_PT[CC * 3 + 1]      # colonne G
                xo = X_PT[CC * 3 + 2]      # colonne O
                yt = Y_PT[CR * 3 + 0]      # rangée haut
                ym = Y_PT[CR * 3 + 1]      # rangée milieu (centre = G = LIBRE)
                yb = Y_PT[CR * 3 + 2]      # rangée bas
                dy = T_NUM * 0.34
                # B : 3 numéros
                c.drawCentredString(xb, yt - dy, str(b[0]))
                c.drawCentredString(xb, ym - dy, str(b[1]))
                c.drawCentredString(xb, yb - dy, str(b[2]))
                # G : 2 numéros (milieu LIBRE)
                c.drawCentredString(xg, yt - dy, str(g[0]))
                c.drawCentredString(xg, yb - dy, str(g[1]))
                # O : 3 numéros
                c.drawCentredString(xo, yt - dy, str(o[0]))
                c.drawCentredString(xo, ym - dy, str(o[1]))
                c.drawCentredString(xo, yb - dy, str(o[2]))
                serie += 1
                faites += 1
        # numéro de feuille (marge sûre, jamais rogné)
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(colors.Color(0.45, 0.45, 0.45))
            c.setFont("Helvetica", 6.0)
            nfe = page_dep + (faites - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 9 * mm, "%03d" % nfe)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf
