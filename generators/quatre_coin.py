# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur 4 COINS (jeu des 4 coins, format A4 portrait)

🖨️ REFAIT LE 10/10 (sceau Maeva) : maquette « 4 COINS » officielle, et on
GARDE L'IDÉE ORIGINALE du 4 COIN — 16 numéros par carton, QUATRE par coin.
Chaque coin est un bloc de 2×2 cases, rempli de 4 numéros DIFFÉRENTS tirés
dans sa plage :
    Coin HAUT-GAUCHE  : 4 numéros de 1-15
    Coin HAUT-DROITE  : 4 numéros de 61-75
    Coin BAS-GAUCHE   : 4 numéros de 16-30
    Coin BAS-DROITE   : 4 numéros de 46-60
(la colonne centrale 31-45 reste vide : le sac du crieur saute 31-45.)

La maquette est reprise TELLE QUELLE, posée comme UNE SEULE image de fond
pleine page — impression rapide sur la bizhub (le RIP pose une image au
lieu de recalculer des milliers de tracés). 12 cartons par feuille A4.
Sous les cases : N° de série à gauche, téléphone à droite (89 52 98 83).
Chiffres NOIRS en N&B, écriture Latin Modern.
"""
import io
import os as _os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg4

PAGE_W, PAGE_H = A4            # 595.2755 x 841.8897 (portrait)
CARTES_PAGE = 12

# Écriture des chiffres : Latin Modern (choix Maeva 10/10)
try:
    pdfmetrics.registerFont(TTFont("LMROMAN", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    POLICE_NUM = "LMROMAN"
except Exception:
    POLICE_NUM = "Times-Bold"
POLICE_PETIT = "Helvetica"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
NOIR = colors.Color(0, 0, 0)
GRIS = colors.Color(0.45, 0.45, 0.45)
TEL_DEFAUT = "89 52 98 83"

# ── Géométrie relevée sur la maquette (en points PDF) ────────────────
# 6 colonnes de blocs (centre x) × 8 lignes de blocs (centre y),
# chaque bloc = 2×2 cases ; une case fait CELL_W × CELL_H.
BX = [70.16, 157.05, 256.89, 339.46, 439.31, 525.66]
BY = [764.55, 685.44, 560.87, 481.16, 354.23, 275.12, 149.96, 69.67]
QX, QY = 20.51, 18.60          # décalage case ↔ centre du bloc
CELL_W, CELL_H = 41.02, 37.19
BLK_HW, BLK_HH = 41.02, 37.19  # demi-dimensions d'un bloc

# ── Plages des 4 coins (bingo 75, le 31-45 est sauté) ────────────────
PLAGES = {"HG": (1, 15), "HD": (61, 75), "BG": (16, 30), "BD": (46, 60)}

# Taille des chiffres : AU MAX — le plus grand « 88 » qui tient dans la case
_T_NUM = min(CELL_W * 0.90 / max(_lg4("88", POLICE_NUM, 1.0), 0.01),
             CELL_H * 0.94)


def _cells(col, row):
    """Les 4 centres de cases d'un bloc (col, row)."""
    bx, by = BX[col], BY[row]
    return [(bx - QX, by + QY), (bx + QX, by + QY),
            (bx - QX, by - QY), (bx + QX, by - QY)]


# Les 12 cartons : pour chacun, les 4 coins (chaque coin = 4 cases) + pied
CARTONS = []
for cr in range(4):
    for cc in range(3):
        d = {
            "HG": _cells(cc * 2, cr * 2),
            "HD": _cells(cc * 2 + 1, cr * 2),
            "BG": _cells(cc * 2, cr * 2 + 1),
            "BD": _cells(cc * 2 + 1, cr * 2 + 1),
        }
        d["foot"] = BY[cr * 2 + 1] - BLK_HH - 6.5
        d["L"] = BX[cc * 2] - BLK_HW
        d["R"] = BX[cc * 2 + 1] + BLK_HW
        CARTONS.append(d)


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    for nom in ("quatre_coins_fond.png", "4coins_fond.png", "quatre_coin_fond.png"):
        p = _os.path.join(d, nom)
        if _os.path.exists(p):
            return p
    try:
        for f in _os.listdir(d):
            if "coin" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "quatre_coins_fond.png")


_IMG_FOND = _fond()


def _gen_carte(rng):
    """16 numéros : 4 DIFFÉRENTS par coin, dans la plage du coin."""
    return {k: rng.sample(range(a, b + 1), 4) for k, (a, b) in PLAGES.items()}


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                motif="", **_ignore):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    rng = random.Random(int(serie_start) * 100003 + 4)
    tel = (telephone or "").strip() or TEL_DEFAUT

    n = max(1, int(nb_cartes))
    serie = int(serie_start)
    faites = 0
    try:
        page_dep = max(1, int(page_start))
    except Exception:
        page_dep = 1

    while faites < n:
        try:
            c.drawImage(_IMG_FOND, 0, 0, PAGE_W, PAGE_H,
                        preserveAspectRatio=False, mask="auto")
        except Exception:
            pass

        for pos in CARTONS:
            if faites >= n:
                break
            carte = _gen_carte(rng)
            col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM, _T_NUM)
            for coin in ("HG", "HD", "BG", "BD"):
                for (cx, cy), val in zip(pos[coin], carte[coin]):
                    c.drawCentredString(cx, cy - _T_NUM * 0.35, str(val))
            # pied : N° de série à gauche, téléphone à droite
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT, 5.8)
            yb = pos["foot"]
            c.drawString(pos["L"] + 1.0, yb, "N° %06d" % serie)
            c.drawRightString(pos["R"] - 1.0, yb, tel)
            serie += 1
            faites += 1

        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT, 6.0)
            nfe = page_dep + (faites - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 6, PAGE_H - 10, "%03d" % nfe)
        c.showPage()

    c.save()
    buf.seek(0)
    return buf
