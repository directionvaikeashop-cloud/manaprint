# -*- coding: utf-8 -*-
"""MANAPRINT — L'AS DES AS (maquette de Maeva du 22/11/2026).

10 tickets par feuille A4 PORTRAIT (2 x 5). La maquette (fleur de lys, bandeau
« L'AS DES AS », le grand As, les 4 cartes, couronne, jetons, lauriers,
bandeau TUKEA 89 22 23 05) est reprise TELLE QUELLE comme fond, en gris uni.
RÈGLE (Maeva, 22/11) — 4 numéros, un par carte, de gauche à droite :
   1re carte : 1-15 · 2e : 16-30 · 3e : 31-45 · 4e : 46-75
Crieur : 1 à 75. Chiffres NOIRS, gras, serrés comme sur sa feuille, au maximum.
"""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PAGE_W, PAGE_H = A4
CARTES_PAGE = 10
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 75)]

_ICI = _os.path.dirname(_os.path.abspath(__file__))
POLICE, CAP = "Times-Bold", 0.66
try:
    pdfmetrics.registerFont(TTFont("ASDESASB", _os.path.join(_ICI, "LiberationSerif-Bold.ttf")))
    POLICE, CAP = "ASDESASB", 0.66
except Exception:
    pass
NOIR = colors.Color(0.05, 0.05, 0.05)
GRIS = colors.Color(0.40, 0.40, 0.40)
RAINBOW = ["#E53935", "#FB8C00", "#43A047", "#00ACC1", "#1E88E5", "#8E24AA", "#D81B60", "#6D4C41"]

_FOND = _os.path.join(_ICI, "as_des_as_fond.png")
_IMG_W, _IMG_H = 1070.0, 1470.0
MARGE = 6 * 72 / 25.4
ECH = min((PAGE_W - 2 * MARGE) / _IMG_W, (PAGE_H - 2 * MARGE - 12) / _IMG_H)
OX = (PAGE_W - _IMG_W * ECH) / 2.0
OY = MARGE

# géométrie relevée sur sa feuille (px) — ticket en haut à gauche
COL_DX = 520.0
ROW_DY = [0.0, 295.0, 584.0, 860.0, 1137.5]      # ⚠️ les rangées ne sont pas régulières
CENTRES = [(202.0, 186.0), (279.0, 178.0), (361.0, 184.0), (444.0, 196.0)]   # milieu du chiffre, SOUS le petit As
HAUT_PX = 40.0      # hauteur des chiffres : tout le blanc entre le petit As et le bas de la carte
LARGE_PX = 54.0     # largeur maximale de « 88 » dans la carte la plus étroite
SERIE_XY = (84.0, 42.0)


def _px(x):
    return OX + x * ECH


def _py(y):
    return OY + (_IMG_H - y) * ECH


TAILLE = HAUT_PX * ECH / CAP
_L88 = pdfmetrics.stringWidth("88", POLICE, TAILLE)
SERRE = min(100.0, 100.0 * LARGE_PX * ECH / _L88)   # écriture serrée (% de largeur)


def _tirage(rng):
    return [rng.randint(a, b) for a, b in PLAGES]


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                _deja=None, **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("L'AS DES AS")
    rng = random.Random(int(serie_start) * 100003 + 1144)
    deja = _deja if _deja is not None else set()
    col_imposee = None
    if couleur and couleur_perso:
        try:
            col_imposee = colors.HexColor(couleur_perso)
        except Exception:
            col_imposee = None
    try:
        no_page = max(1, int(page_start))
    except Exception:
        no_page = 1
    serie = int(serie_start)
    faits = 0
    while faits < n_:
        c.drawImage(_FOND, OX, OY, _IMG_W * ECH, _IMG_H * ECH, preserveAspectRatio=False, mask="auto")
        for k in range(CARTES_PAGE):
            if faits >= n_:
                break
            ligne, col_ = divmod(k, 2)
            dx, dy = col_ * COL_DX, ROW_DY[ligne]
            while True:
                nums = _tirage(rng)
                if tuple(nums) not in deja:
                    deja.add(tuple(nums))
                    break
            coul = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else NOIR
            c.saveState()
            c.setFillColor(coul)
            c.setStrokeColor(coul)
            c.setLineJoin(1)
            c.setLineWidth(0.02 * TAILLE)
            for (x, y), v in zip(CENTRES, nums):
                s = str(v)
                w = c.stringWidth(s, POLICE, TAILLE) * SERRE / 100.0
                o = c.beginText()
                o.setTextRenderMode(2)
                o.setFont(POLICE, TAILLE)
                o.setHorizScale(SERRE)
                o.setTextOrigin(_px(x + dx) - w / 2.0, _py(y + dy) - TAILLE * CAP / 2.0)
                o.textOut(s)
                c.drawText(o)
            c.restoreState()
            c.setFillColor(GRIS)
            c.setFont("Helvetica", 5.0)
            c.drawCentredString(_px(SERIE_XY[0] + dx), _py(SERIE_XY[1] + dy), "N° %06d" % serie)
            serie += 1
            faits += 1
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 7)
        c.drawRightString(PAGE_W - MARGE - 4, PAGE_H - MARGE - 7, "%d" % no_page)
        if (nom_evenement or "").strip():
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - MARGE - 7, nom_evenement.strip()[:90])
        no_page += 1
        c.showPage()
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_as_des_as.pdf", "wb").write(generer_pdf(nb_cartes=10, couleur=False).read())
    print("L'AS DES AS genere")
