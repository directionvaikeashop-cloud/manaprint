# -*- coding: utf-8 -*-
"""MANAPRINT — OHANA 75 · 4 SÉRIES — nouvelle maquette RETRAVAILLEE par Maeva (16/10).

🌺 La maquette « OHANA 75 · 4 séries » (A4 PAYSAGE, 4 cartes par feuille 2×2 ;
chaque carte : en-tête « OHANA 75 », B·I·N·G·O, grille 5×5 avec un ROND par case)
est reprise TELLE QUELLE, posée comme UNE SEULE image de fond. On n'ajoute QUE
les chiffres ; rien n'est redessiné.

REGLE — inchangée (comme OHANA 75 · 2 séries) : 2 numéros par case —
  le plus petit ENTOURE (dans le rond, Latin Modern) + le second À DROITE
  (DejaVu Condensed Bold). Plages B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75.
  Case CENTRALE (N du milieu) = FREE : on y imprime le N° de série.
Chiffres GRIS. Chiffres pleins -> impression Konica rapide.
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
CARTES_PAGE = 4

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

PLAGES = [("B", 1, 15), ("I", 16, 30), ("N", 31, 45), ("G", 46, 60), ("O", 61, 75)]

# ── Géométrie mesurée sur la maquette (image 1491×1055 px, A4 paysage) ──
_IMG_W, _IMG_H = 1491, 1055
_COL_PX = [91, 235, 375, 518, 662, 828, 972, 1115, 1258, 1401]   # 2 cartes × 5 colonnes
_ROW_PX = [172, 250, 330, 409, 487, 705, 783, 861, 936, 1009]    # 2 cartes × 5 rangées
_CIRC_DX = -33     # rond : décalage x (px)
_RIGHT_DX = 34     # 2e chiffre : décalage x à droite (px)
_RAYON = 30        # rayon du rond (px)
_FREE_ROW = 2      # rangée centrale (N du milieu) = FREE / série


def _x(px):
    return px / _IMG_W * PAGE_W


def _y(py):
    return PAGE_H - py / _IMG_H * PAGE_H

COL_X = [_x(p) for p in _COL_PX]
ROW_Y = [_y(p) for p in _ROW_PX]
CIRC_DX = _CIRC_DX / _IMG_W * PAGE_W
RIGHT_DX = _RIGHT_DX / _IMG_W * PAGE_W
CIRCLE_D = 2 * _RAYON / _IMG_W * PAGE_W
_CELL_W_PT = 142 / _IMG_W * PAGE_W
_CELL_H_PT = 77 / _IMG_H * PAGE_H


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    p = _os.path.join(d, "ohana75_4series_fond.png")
    if _os.path.exists(p):
        return p
    try:
        for f in _os.listdir(d):
            if "ohana75_4series_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "ohana75_4series_fond.png")
_IMG_FOND = _fond()


def _t_gros():
    t = 34.0
    while t > 8 and (stringWidth("88", POLICE_NUM, t) > CIRCLE_D * 0.74
                     or t * 0.70 > CIRCLE_D * 0.82):
        t -= 0.5
    return t
T_GROS = _t_gros()

# espace à droite du rond
_CIRC_RIGHT = CIRC_DX + CIRCLE_D / 2
_CELL_RIGHT = _CELL_W_PT / 2
_AVAIL_W = (_CELL_RIGHT - 2) - (_CIRC_RIGHT + 2)


def _t_petit():
    t = 40.0
    while t > 8 and (stringWidth("88", POLICE_COND, t) > _AVAIL_W
                     or t * 0.70 > _CELL_H_PT * 0.80):
        t -= 0.5
    return min(t, T_GROS * 1.08)
T_PETIT = _t_petit()


def _gen_carte(rng):
    carte = {}
    for lettre, a, b in PLAGES:
        n_cases = 4 if lettre == "N" else 5
        nums = rng.sample(range(a, b + 1), n_cases * 2)
        carte[lettre] = [sorted(nums[i * 2:i * 2 + 2]) for i in range(n_cases)]
    return carte


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                **_ignore):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 503)
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
        # 4 cartes : 2 rangées (CR) × 2 colonnes (CC)
        for CR in range(2):
            for CC in range(2):
                if faites >= n_:
                    break
                carte = _gen_carte(rng)
                for col_i, (lettre, a, b) in enumerate(PLAGES):
                    cx = COL_X[CC * 5 + col_i]
                    paires = carte[lettre]
                    rows = [0, 1, 3, 4] if lettre == "N" else [0, 1, 2, 3, 4]
                    for pi, row in enumerate(rows):
                        petit, grand = paires[pi]
                        cy = ROW_Y[CR * 5 + row]
                        c.setFillColor(GRIS)
                        c.setFont(POLICE_NUM, T_GROS)
                        c.drawCentredString(cx + CIRC_DX, cy - T_GROS * 0.34, str(petit))
                        c.setFont(POLICE_COND, T_PETIT)
                        c.drawCentredString(cx + RIGHT_DX, cy - T_PETIT * 0.34, str(grand))
                # case centrale (N du milieu) = N° de série
                cxN = COL_X[CC * 5 + 2]
                cyN = ROW_Y[CR * 5 + _FREE_ROW]
                c.setFillColor(GRIS)
                c.setFont(POLICE_NUM, 9.0)
                c.drawCentredString(cxN, cyN - 9.0 * 0.34, "N° %05d" % serie)
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
