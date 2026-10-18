# -*- coding: utf-8 -*-
"""MANAPRINT — OHANA 90 · 4 SÉRIES — nouvelle maquette RETRAVAILLEE par Maeva (16/10).

🌺 La maquette « OHANA 90 · 4 séries » (A4 PAYSAGE, 4 cartes par feuille 2×2 ;
chaque carte : en-tête « OHANA 90 », B·I·N·G·O·90, grille 6 colonnes × 5 rangées
avec un ROND par case) est reprise TELLE QUELLE, posée comme UNE SEULE image de
fond. On n'ajoute QUE les chiffres ; rien n'est redessiné.

REGLE — inchangée (comme OHANA 90 · 2 séries) : 2 numéros par case, les 30 cases
  REMPLIES — le plus petit ENTOURE (dans le rond, Latin Modern) + le second À
  DROITE (DejaVu Condensed Bold). Plages :
  B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75 · 90 76-90.
Chiffres GRIS. Chiffres pleins -> impression Konica rapide.
"""
import io
import math
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

PLAGES = [("B", 1, 15), ("I", 16, 30), ("N", 31, 45),
          ("G", 46, 60), ("O", 61, 75), ("90", 76, 90)]

# ── Géométrie mesurée sur la maquette (image 1684×1191 px, A4 paysage) ──
_IMG_W, _IMG_H = 1684, 1191
# centres de CASE : 2 cartes × 6 colonnes (B I N G O 90)
_COL_PX = [100, 232, 364, 496, 628, 760, 923, 1055, 1187, 1319, 1451, 1583]
# centres de rangées : 2 cartes × 5 rangées
_ROW_PX = [188, 275, 361, 448, 534, 766, 853, 939, 1026, 1113]
_CIRC_DX = -24     # rond : décalage x depuis le centre de case (px)
_RIGHT_DX = 38     # 2e chiffre : décalage x à droite (px)
_RAYON = 34        # rayon du rond (px)
_CELL_W_PX = 132   # largeur de case (px)
_CELL_H_PX = 87    # hauteur de case (px)


def _x(px):
    return px / _IMG_W * PAGE_W


def _y(py):
    return PAGE_H - py / _IMG_H * PAGE_H

COL_X = [_x(p) for p in _COL_PX]
ROW_Y = [_y(p) for p in _ROW_PX]
CIRC_DX = _CIRC_DX / _IMG_W * PAGE_W
RIGHT_DX = _RIGHT_DX / _IMG_W * PAGE_W
CIRCLE_D = 2 * _RAYON / _IMG_W * PAGE_W
_CELL_W_PT = _CELL_W_PX / _IMG_W * PAGE_W
_CELL_H_PT = _CELL_H_PX / _IMG_H * PAGE_H
# N° de série : discret, dans le bandeau du titre (haut-gauche), hors des lettres
_SER_PX = [(46, 88), (869, 88), (46, 666), (869, 666)]


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    p = _os.path.join(d, "ohana90_4series_fond.png")
    if _os.path.exists(p):
        return p
    try:
        for f in _os.listdir(d):
            if "ohana90_4series_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "ohana90_4series_fond.png")
_IMG_FOND = _fond()


def _t_gros():
    t = 34.0
    while t > 8 and (stringWidth("88", POLICE_NUM, t) > CIRCLE_D * 0.74
                     or t * 0.70 > CIRCLE_D * 0.82):
        t -= 0.5
    return t
T_GROS = _t_gros()

# 2e chiffre : poussé en BAS À DROITE de la case. Comme le rond est arrondi,
# plus on descend, plus le bord du rond se dérobe → on peut le grossir.
_R = CIRCLE_D / 2                 # rayon du rond (pt)
_CIRC_CX = CIRC_DX               # centre x du rond (rel. au centre de case)
_CELL_RIGHT = _CELL_W_PT / 2     # bord droit de la case
_CELL_BOTTOM = -_CELL_H_PT / 2   # bord bas de la case (rel. au centre de case)
_VM = 1.5                        # marge intérieure (pt)


_TOL = 2.5    # tolérance de contact avec le trait du rond (pt) : le chiffre peut
              # le frôler légèrement pour pouvoir grossir, sans le chevaucher.


def _fit_petit_bas():
    """Plus gros 2e chiffre calé en BAS À DROITE (aligné coin bas-droit de la case).
    On le grossit tant que son coin haut-gauche ne pénètre pas le rond de plus de
    _TOL. Renvoie (taille, centre_x, centre_y) relatifs au centre de case."""
    right = _CELL_RIGHT - _VM
    for t in [x * 0.5 for x in range(100, 15, -1)]:     # 50 → 8 pt
        h = t * 0.70
        w = stringWidth("88", POLICE_COND, t)
        yc = _CELL_BOTTOM + _VM + h / 2                 # calé en bas
        xc = right - w / 2                              # calé à droite
        left = xc - w / 2
        top = yc + h / 2
        # point du cadre du chiffre le plus proche du centre du rond
        px = min(max(_CIRC_CX, left), right)
        py = min(max(0.0, yc - h / 2), top)
        dmin = math.hypot(px - _CIRC_CX, py)
        if (dmin >= _R - _TOL                            # ne pénètre pas le rond
                and top <= _CELL_H_PT / 2 - _VM):        # ne déborde pas en haut
            return t, xc, yc
    return 8.0, _CELL_RIGHT - 6, _CELL_BOTTOM + 6
T_PETIT = 22.0                                   # taille demandée (coin bas-droit)
_pw = stringWidth("88", POLICE_COND, T_PETIT)
_PETIT_CX = (_CELL_RIGHT - _VM) - _pw / 2         # calé à droite
_PETIT_CY = _CELL_BOTTOM + _VM + (T_PETIT * 0.70) / 2   # calé en bas
_PETIT_DY = _PETIT_CY - T_PETIT * 0.34            # base pour drawCentredString


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
    rng = random.Random(int(serie_start) * 100003 + 607)
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
                k = CR * 2 + CC
                carte = _gen_carte(rng)
                for col_i, (lettre, a, b) in enumerate(PLAGES):
                    cx = COL_X[CC * 6 + col_i]
                    for row in range(5):
                        petit, grand = carte[lettre][row]
                        cy = ROW_Y[CR * 5 + row]
                        c.setFillColor(GRIS)
                        c.setFont(POLICE_NUM, T_GROS)
                        c.drawCentredString(cx + CIRC_DX, cy - T_GROS * 0.34, str(petit))
                        c.setFont(POLICE_COND, T_PETIT)
                        c.drawCentredString(cx + _PETIT_CX, cy + _PETIT_DY, str(grand))
                # N° de série (discret, haut-gauche de la carte)
                sx, sy = _SER_PX[k]
                c.setFillColor(GRIS)
                c.setFont(POLICE_NUM, 8.0)
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
