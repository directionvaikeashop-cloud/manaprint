# -*- coding: utf-8 -*-
"""MANAPRINT — OHANA 90 · 2 SÉRIES — nouvelle maquette RETRAVAILLEE par Maeva (16/10).

🌺 La maquette « OHANA 90 · 2 séries » (A4 portrait, 2 cartes empilées ; chaque carte :
en-tête « OHANA 90 », B·I·N·G·O·90, grille 6 colonnes × 5 rangées avec un ROND par
case) est reprise TELLE QUELLE, posée comme UNE SEULE image de fond. On n'ajoute QUE
les chiffres ; rien n'est redessiné.

REGLE — 2 numéros par case (comme OHANA 75 · 2 séries), les 30 cases REMPLIES —
  le plus petit ENTOURE (dans le rond, Latin Modern) + le second À DROITE
  (DejaVu Condensed Bold). Plages :
  B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75 · 90 76-90.
Chiffres GRIS. Chiffres pleins -> impression Konica rapide.
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
CARTES_PAGE = 2

try:
    pdfmetrics.registerFont(TTFont("LMROMAN", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    POLICE_NUM = "LMROMAN"
except Exception:
    POLICE_NUM = "Times-Bold"
try:
    pdfmetrics.registerFont(TTFont("DJCONDB", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "DejaVuSansCondensed-Bold.ttf")))
    POLICE_COND = "DJCONDB"
except Exception:
    POLICE_COND = "Helvetica-Bold"
GRIS = colors.Color(0.42, 0.42, 0.42)

PLAGES = [("B", 1, 15), ("I", 16, 30), ("N", 31, 45),
          ("G", 46, 60), ("O", 61, 75), ("90", 76, 90)]

# ── Géométrie mesurée sur la maquette (image 1103×1426 px, A4 portrait) ──
_IMG_W, _IMG_H = 1103, 1426
_COL_PX = [120, 293, 467, 638, 812, 984]                 # 6 colonnes (B I N G O 90)
_ROW_PX = [[219, 322, 425, 529, 633],                    # carte 1 : 5 rangées
           [927, 1032, 1136, 1239, 1344]]                # carte 2 : 5 rangées
_CIRC_DX = -34     # rond : décalage x (px)
_RIGHT_DX = 46     # 2e chiffre : décalage x à droite (px)
_RAYON = 41        # rayon du rond (px)


def _x(px):
    return px / _IMG_W * PAGE_W


def _y(py):
    return PAGE_H - py / _IMG_H * PAGE_H

COL_X = [_x(p) for p in _COL_PX]
ROW_Y = [[_y(p) for p in carte] for carte in _ROW_PX]
CIRC_DX = _CIRC_DX / _IMG_W * PAGE_W
RIGHT_DX = _RIGHT_DX / _IMG_W * PAGE_W
CIRCLE_D = 2 * _RAYON / _IMG_W * PAGE_W
_CELL_W_PT = 171 / _IMG_W * PAGE_W
_CELL_H_PT = 104 / _IMG_H * PAGE_H
# N° de série : discret, en haut à gauche de chaque carte
_SER_PX = [(60, 95), (60, 803)]


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    p = _os.path.join(d, "ohana90_2series_fond.png")
    if _os.path.exists(p):
        return p
    try:
        for f in _os.listdir(d):
            if "ohana90_2series_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "ohana90_2series_fond.png")
_IMG_FOND = _fond()


def _t_gros():
    t = 34.0
    while t > 8 and (stringWidth("88", POLICE_NUM, t) > CIRCLE_D * 0.74
                     or t * 0.70 > CIRCLE_D * 0.82):
        t -= 0.5
    return t
T_GROS = _t_gros()

_CIRC_RIGHT = CIRC_DX + CIRCLE_D / 2
_CELL_RIGHT = _CELL_W_PT / 2
_AVAIL_W = (_CELL_RIGHT - 2) - (_CIRC_RIGHT + 2)


def _t_petit():
    t = 42.0
    while t > 8 and (stringWidth("88", POLICE_COND, t) > _AVAIL_W
                     or t * 0.70 > _CELL_H_PT * 0.80):
        t -= 0.5
    return min(t, T_GROS * 1.08)
T_PETIT = _t_petit()


def _gen_carte(rng):
    """Par colonne : 5 cases de 2 numéros distincts triés (toutes les cases)."""
    carte = {}
    for lettre, a, b in PLAGES:
        nums = rng.sample(range(a, b + 1), 5 * 2)
        carte[lettre] = [sorted(nums[i * 2:i * 2 + 2]) for i in range(5)]
    return carte


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                **_ignore):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 601)
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
        for k in range(CARTES_PAGE):
            if faites >= n_:
                break
            carte = _gen_carte(rng)
            rows_y = ROW_Y[k]
            for col_i, (lettre, a, b) in enumerate(PLAGES):
                cx = COL_X[col_i]
                for row in range(5):
                    petit, grand = carte[lettre][row]
                    cy = rows_y[row]
                    c.setFillColor(GRIS)
                    c.setFont(POLICE_NUM, T_GROS)
                    c.drawCentredString(cx + CIRC_DX, cy - T_GROS * 0.34, str(petit))
                    c.setFont(POLICE_COND, T_PETIT)
                    c.drawCentredString(cx + RIGHT_DX, cy - T_PETIT * 0.34, str(grand))
            # N° de série (discret, haut-gauche)
            sx, sy = _SER_PX[k]
            c.setFillColor(GRIS)
            c.setFont(POLICE_NUM, 9.0)
            c.drawString(_x(sx), _y(sy), "N° %05d" % serie)
            serie += 1
            faites += 1
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(GRIS)
            c.setFont("Helvetica", 6.0)
            nfe = page_dep + (faites - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 9 * mm, "%03d" % nfe)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf
