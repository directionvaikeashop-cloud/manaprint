# -*- coding: utf-8 -*-
"""MANAPRINT — OHANA 75 · 2 SÉRIES — nouvelle maquette RETRAVAILLEE par Maeva (16/10).

🌺 La maquette « OHANA 75 · 2 séries » (A4 portrait, 2 cartes par feuille séparées
par un trait de découpe ; chaque carte : en-tête « OHANA 75 », B·I·N·G·O, grille
5×5 avec un ROND par case) est reprise TELLE QUELLE, posée comme UNE SEULE image
de fond. On n'ajoute QUE les chiffres ; rien n'est redessiné.

REGLE — inchangée : 2 numéros par case (règle MARATHON, 2 séries) —
  le plus petit ENTOURE (dans le rond, gros), le second À DROITE (plus petit).
  Plages B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75.
  Case CENTRALE (N du milieu) = FREE : on y imprime le N° de série.
Chiffres GRIS (comme l'actuel), Latin Modern. Chiffres pleins -> impression rapide.
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
# 2e chiffre (à droite) : police DIFFÉRENTE — DejaVu Condensed Bold (comme TRIPLE ACTION 75)
try:
    pdfmetrics.registerFont(TTFont("DJCONDB", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "DejaVuSansCondensed-Bold.ttf")))
    POLICE_COND = "DJCONDB"
except Exception:
    POLICE_COND = "Helvetica-Bold"
GRIS = colors.Color(0.42, 0.42, 0.42)

PLAGES = [("B", 1, 15), ("I", 16, 30), ("N", 31, 45), ("G", 46, 60), ("O", 61, 75)]

# ── Géométrie mesurée sur la maquette (image 1122×1402 px, A4 portrait) ──
_IMG_W, _IMG_H = 1122, 1402
_COL_PX = [140, 351, 562, 773, 983]                     # centres des 5 colonnes (B I N G O)
_ROW_PX = [[204, 306, 408, 510, 613],                   # carte 1 : 5 rangées
           [915, 1017, 1120, 1222, 1325]]               # carte 2 : 5 rangées
_CIRC_DX = -53     # rond : décalage x depuis le centre de case (px)
_RIGHT_DX = 52     # 2e chiffre : décalage x à droite (px)
_FREE_ROW = 2      # rangée centrale (N du milieu) = FREE / série


def _x(px):
    return px / _IMG_W * PAGE_W


def _y(py):
    return PAGE_H - py / _IMG_H * PAGE_H

# positions en points
COL_X = [_x(p) for p in _COL_PX]
ROW_Y = [[_y(p) for p in carte] for carte in _ROW_PX]
CIRC_DX = _CIRC_DX / _IMG_W * PAGE_W
RIGHT_DX = _RIGHT_DX / _IMG_W * PAGE_W

# Diamètre du rond (pt) mesuré sur la maquette (rayon ≈ 42 px)
CIRCLE_D = 2 * 42 / _IMG_W * PAGE_W


def _t_gros():
    """Chiffre entouré AU PLUS GROS qui tient dans la bulle (pire cas « 88 »)."""
    t = 44.0
    while t > 8 and (stringWidth("88", POLICE_NUM, t) > CIRCLE_D * 0.74
                     or t * 0.70 > CIRCLE_D * 0.82):
        t -= 0.5
    return t
T_GROS = _t_gros()     # chiffre entouré (dans le rond) — au max

# Espace disponible pour le 2e chiffre : à DROITE du rond, dans la case.
_CELL_W_PT = 210 / _IMG_W * PAGE_W
_CELL_H_PT = 102 / _IMG_H * PAGE_H
_CIRC_RIGHT = CIRC_DX + CIRCLE_D / 2          # bord droit du rond (rel. au centre de case)
_CELL_RIGHT = _CELL_W_PT / 2                  # bord droit de la case
RIGHT_DX = (_CIRC_RIGHT + _CELL_RIGHT) / 2    # on centre le chiffre dans l'espace restant
_AVAIL_W = (_CELL_RIGHT - 3) - (_CIRC_RIGHT + 3)   # largeur dispo (marges)


def _t_petit():
    """2e chiffre au plus gros DANS L'ESPACE À DROITE, mais équilibré :
    on le plafonne juste au-dessus du chiffre entouré (style TRIPLE ACTION 75),
    pour qu'il ne domine pas la bulle."""
    t = 46.0
    while t > 8 and (stringWidth("88", POLICE_COND, t) > _AVAIL_W
                     or t * 0.70 > _CELL_H_PT * 0.80):
        t -= 0.5
    return min(t, T_GROS * 1.08)
T_PETIT = _t_petit()   # 2e chiffre (à droite), DejaVu Condensed Bold


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    p = _os.path.join(d, "ohana75_2series_fond.png")
    if _os.path.exists(p):
        return p
    try:
        for f in _os.listdir(d):
            if "ohana75_2series_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "ohana75_2series_fond.png")
_IMG_FOND = _fond()


def _gen_carte(rng):
    """Pour chaque colonne : 5 cases (4 pour N), 2 numéros distincts triés par case."""
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
    rng = random.Random(int(serie_start) * 100003 + 401)
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
        for k in range(CARTES_PAGE):          # 2 cartes par feuille
            if faites >= n_:
                break
            carte = _gen_carte(rng)
            rows_y = ROW_Y[k]
            for col_i, (lettre, a, b) in enumerate(PLAGES):
                cx = COL_X[col_i]
                paires = carte[lettre]
                # rangées à remplir : toutes sauf la centrale pour N
                if lettre == "N":
                    rows = [0, 1, 3, 4]
                else:
                    rows = [0, 1, 2, 3, 4]
                for pi, row in enumerate(rows):
                    petit, grand = paires[pi]      # trié : petit = entouré, grand = à droite
                    cy = rows_y[row]
                    c.setFillColor(GRIS)
                    # chiffre ENTOURE (dans le rond, à gauche) — plus gros
                    c.setFont(POLICE_NUM, T_GROS)
                    c.drawCentredString(cx + CIRC_DX, cy - T_GROS * 0.34, str(petit))
                    # 2e chiffre (à droite) — autre police (DejaVu Condensed Bold)
                    c.setFont(POLICE_COND, T_PETIT)
                    c.drawCentredString(cx + RIGHT_DX, cy - T_PETIT * 0.34, str(grand))
            # case centrale (N du milieu) = N° de série
            cxN = COL_X[2]
            cyN = rows_y[_FREE_ROW]
            c.setFillColor(GRIS)
            c.setFont(POLICE_NUM, 11.0)
            c.drawCentredString(cxN, cyN - 11.0 * 0.34, "N° %05d" % serie)
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
