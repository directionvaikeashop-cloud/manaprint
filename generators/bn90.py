# -*- coding: utf-8 -*-
"""MANAPRINT — BN 90 — nouvelle maquette RETRAVAILLEE par Maeva (16/10).

🅱️ La maquette « BN 90 » (A4 PAYSAGE, 16 cartons = 4 colonnes × 4 rangées ;
chaque carton : en-tête « B N 90 », grille 3 colonnes × 2 rangées = 6 cases)
est reprise TELLE QUELLE, posée comme UNE SEULE image de fond. On n'ajoute QUE
les chiffres ; rien n'est redessiné.

REGLE — 6 boules, les 6 cases REMPLIES —
  B  : 1-15  (2 numéros, haut et bas)
  N  : 31-45 (2 numéros, haut et bas)
  90 : 76-90 (2 numéros, haut et bas)
Deux sauts dans le tirage : ni 16-30, ni 46-75. Numéros triés vers le bas.
Chiffres pleins (pas de microtexte) → impression Konica rapide. Latin Modern.
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

PLAGE_B = (1, 15)
PLAGE_N = (31, 45)
PLAGE_90 = (76, 90)

# ── Géométrie mesurée sur la maquette (image 1536×1024 px) ──
_IMG_W, _IMG_H = 1536, 1024
_X_PX = [95, 208, 323, 469, 582, 696, 837, 951, 1065, 1208, 1323, 1437]  # 4 cartons × 3 col
_Y_PX = [106, 194, 362, 450, 616, 703, 864, 952]                         # 4 cartons × 2 rang
X_PT = [x / _IMG_W * PAGE_W for x in _X_PX]
Y_PT = [PAGE_H - y / _IMG_H * PAGE_H for y in _Y_PX]
CELL_W = 113 / _IMG_W * PAGE_W         # ≈ 61.9 pt
CELL_H = 87 / _IMG_H * PAGE_H          # ≈ 50.6 pt


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    p = _os.path.join(d, "bn90_fond.png")
    if _os.path.exists(p):
        return p
    try:
        for f in _os.listdir(d):
            if "bn90_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "bn90_fond.png")
_IMG_FOND = _fond()


def _taille_num():
    t = 48.0
    while t > 8 and (stringWidth("88", POLICE_NUM, t) > CELL_W * 0.72
                     or t * 0.70 > CELL_H * 0.80):
        t -= 0.5
    return t
T_NUM = _taille_num()


def _gen_carte(rng):
    """6 boules : B, N et 90 ont chacun 2 numéros (haut et bas)."""
    b = sorted(rng.sample(range(PLAGE_B[0], PLAGE_B[1] + 1), 2))
    n = sorted(rng.sample(range(PLAGE_N[0], PLAGE_N[1] + 1), 2))
    q = sorted(rng.sample(range(PLAGE_90[0], PLAGE_90[1] + 1), 2))
    return b, n, q


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                **_ignore):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 307)
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
                b, n, q = _gen_carte(rng)
                col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else NOIR
                c.setFillColor(col)
                c.setFont(POLICE_NUM, T_NUM)
                xb = X_PT[CC * 3 + 0]      # colonne B
                xn = X_PT[CC * 3 + 1]      # colonne N
                xq = X_PT[CC * 3 + 2]      # colonne 90
                yt = Y_PT[CR * 2 + 0]      # rangée haut
                yb = Y_PT[CR * 2 + 1]      # rangée bas
                dy = T_NUM * 0.34
                # B : 2 numéros (haut, bas)
                c.drawCentredString(xb, yt - dy, str(b[0]))
                c.drawCentredString(xb, yb - dy, str(b[1]))
                # N : 2 numéros (haut, bas)
                c.drawCentredString(xn, yt - dy, str(n[0]))
                c.drawCentredString(xn, yb - dy, str(n[1]))
                # 90 : 2 numéros (haut, bas)
                c.drawCentredString(xq, yt - dy, str(q[0]))
                c.drawCentredString(xq, yb - dy, str(q[1]))
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
