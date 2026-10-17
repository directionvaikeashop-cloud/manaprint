# -*- coding: utf-8 -*-
"""MANAPRINT — LOVER — maquette créée par Maeva (16/10).

❤️ La maquette « LOVER » (A4 portrait, 12 cartons = 2 colonnes × 6 rangées ;
chaque carton : en-tête « L O V E R », grille 5 colonnes × 2 rangées avec des
cases en QUINCONCE) est reprise TELLE QUELLE, posée comme UNE SEULE image de
fond. On n'ajoute QUE les chiffres ; rien n'est redessiné.

RÈGLE — plages du B·I·N·G·O, un numéro par colonne, posé dans la case
« pleine » (quinconce) : L en HAUT, O en BAS, V en HAUT, E en BAS, R en HAUT.
  L : 1-15 · O : 16-30 · V : 31-45 · E : 46-60 · R : 61-75.
Cinq numéros par carton. Chiffres pleins (pas de microtexte) → impression rapide.
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

# L · O · V · E · R  (plages BINGO)
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
# Case pleine de chaque colonne (quinconce) : 0 = HAUT, 1 = BAS
ZIGZAG = [0, 1, 0, 1, 0]              # L haut, O bas, V haut, E bas, R haut

# ── Géométrie mesurée sur la maquette (image 1489×2105 px, A4 portrait) ──
_IMG_W, _IMG_H = 1489, 2105
_FRAME_X = [64, 767]                                  # 2 colonnes de cartons
_FRAME_Y = [81, 410, 740, 1069, 1399, 1729]          # 6 rangées de cartons
_COL_REL = [77, 202, 329, 456, 588]                  # centres colonnes (px, dans le carton)
_ROW_REL = [102, 220]                                # centres rangées haut / bas (px)


def _px2pt_x(x):
    return x / _IMG_W * PAGE_W


def _px2pt_y(y):
    return PAGE_H - y / _IMG_H * PAGE_H


# centres de cases en points, par carton (cc, cr) puis colonne (0..4) et rangée (0/1)
CELL_X = [[_px2pt_x(fx + cr_) for cr_ in _COL_REL] for fx in _FRAME_X]   # [cc][col]
CELL_Y = [[_px2pt_y(fy + rr) for rr in _ROW_REL] for fy in _FRAME_Y]     # [cr][0/1]

_COL_SP = _px2pt_x(_COL_REL[1]) - _px2pt_x(_COL_REL[0])    # ≈ 50 pt
_ROW_SP = _px2pt_y(_ROW_REL[0]) - _px2pt_y(_ROW_REL[1])    # ≈ 47 pt


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    for nom in ("lover_fond.png",):
        p = _os.path.join(d, nom)
        if _os.path.exists(p):
            return p
    try:
        for f in _os.listdir(d):
            if "lover_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "lover_fond.png")
_IMG_FOND = _fond()


def _taille_num():
    t = 46.0
    while t > 8 and (stringWidth("88", POLICE_NUM, t) > _COL_SP * 0.78
                     or t * 0.70 > _ROW_SP * 0.80):
        t -= 0.5
    return t
T_NUM = _taille_num()


def _gen_carte(rng):
    """Un numéro distinct par colonne, dans sa plage BINGO."""
    return [rng.randint(lo, hi) for (lo, hi) in RANGES]


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                **_ignore):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 131)
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
        # 12 cartons : 6 rangées (CR) × 2 colonnes (CC)
        for CR in range(6):
            for CC in range(2):
                if faites >= n_:
                    break
                nums = _gen_carte(rng)
                col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else NOIR
                c.setFillColor(col)
                c.setFont(POLICE_NUM, T_NUM)
                for k in range(5):                          # L O V E R
                    cx = CELL_X[CC][k]
                    cy = CELL_Y[CR][ZIGZAG[k]]
                    c.drawCentredString(cx, cy - T_NUM * 0.34, str(nums[k]))
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
