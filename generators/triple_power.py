# -*- coding: utf-8 -*-
"""MANAPRINT — TRIPLE POWER (maquette de Maeva du 22/11/2026).

10 tickets par feuille A4 PORTRAIT (5 x 2). La maquette (N° ____, fleur et logo
TRIPLE POWER, 4 bulles ON / OFF / ON / OFF) est reprise TELLE QUELLE comme fond,
en gris uni.
RÈGLE = celle de TRIPLE ACTION 75 (Maeva) — 4 lignes, de haut en bas :
   B 1-15 · I 16-30 · G 46-60 · O 61-75  (pas de N)
Une ligne = 3 numéros de sa plage, triés : le plus petit DANS la bulle, le moyen
à droite en haut, le plus grand en petit dessous (comme sa feuille remplie).
Sur une rangée de 5 tickets, chaque numéro d'une plage ne sort qu'une fois.
Crieur : 1-30 et 46-75. Chiffres NOIRS gras, grossis au maximum.
"""
import io, os as _os, random, json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PAGE_W, PAGE_H = A4
CARTES_PAGE = 10
LIGNES = "BIGO"
PLAGES = {"B": (1, 15), "I": (16, 30), "G": (46, 60), "O": (61, 75)}

_ICI = _os.path.dirname(_os.path.abspath(__file__))
POLICE, CAP = "Times-Bold", 0.66
try:
    pdfmetrics.registerFont(TTFont("TPOWB", _os.path.join(_ICI, "LiberationSerif-Bold.ttf")))
    POLICE, CAP = "TPOWB", 0.66
except Exception:
    pass
NOIR = colors.Color(0.05, 0.05, 0.05)
GRIS = colors.Color(0.30, 0.30, 0.30)
RAINBOW = ["#E53935", "#FB8C00", "#43A047", "#00ACC1", "#1E88E5", "#8E24AA", "#D81B60", "#6D4C41"]

_FOND = _os.path.join(_ICI, "triple_power_fond.png")
_IMG_W, _IMG_H = 1058.0, 1486.0
MARGE = 6 * 72 / 25.4
ECH = min((PAGE_W - 2 * MARGE) / _IMG_W, (PAGE_H - 2 * MARGE - 12) / _IMG_H)
OX = (PAGE_W - _IMG_W * ECH) / 2.0
OY = MARGE

# les 40 bulles relevées sur la maquette (cx, cy, rayon) — ordre : rangée, colonne, ligne B I G O
BULLES = [(71.5, 280.5, 50.5), (71.0, 402.5, 53.0), (72.0, 531.0, 52.0), (72.5, 655.5, 54.5), (287.5, 282.5, 49.5), (287.5, 402.5, 52.5), (289.5, 532.5, 51.5), (289.5, 656.0, 54.5), (496.5, 281.5, 50.5), (497.0, 402.5, 53.0), (498.0, 531.0, 52.0), (499.0, 655.5, 55.0), (702.0, 282.0, 50.0), (702.0, 403.0, 53.0), (702.0, 532.0, 51.0), (704.0, 656.5, 55.0), (911.0, 282.0, 50.0), (911.5, 403.0, 52.5), (912.5, 532.5, 51.5), (913.5, 656.5, 54.5), (72.0, 1000.0, 51.0), (71.5, 1117.5, 53.5), (71.5, 1239.5, 51.5), (72.5, 1362.5, 55.5), (288.0, 1001.0, 50.0), (288.0, 1117.5, 53.0), (289.5, 1239.5, 51.5), (290.5, 1362.5, 55.5), (496.5, 1000.5, 50.5), (497.0, 1117.5, 53.0), (497.5, 1239.5, 51.5), (499.0, 1361.5, 55.0), (702.5, 1001.5, 50.5), (703.0, 1118.0, 54.0), (702.5, 1239.5, 51.5), (705.5, 1362.0, 55.5), (912.5, 1000.5, 50.5), (912.5, 1117.5, 53.5), (913.0, 1239.0, 52.0), (914.5, 1362.5, 55.5)]
SERIE_Y = [72.0, 800.0]          # sur le trait « N° ____ »
SERIE_DX = 138.0                 # px depuis le bord gauche de la colonne (x 0, 220, 428, 634, 842)
COL_X0 = [8.0, 225.0, 433.0, 639.0, 847.0]


def _px(x):
    return OX + x * ECH


def _py(y):
    return OY + (_IMG_H - y) * ECH


def _ajuste(txt, larg_px, haut_px):
    t = 60.0
    while t > 6 and (pdfmetrics.stringWidth(txt, POLICE, t) > larg_px * ECH or t * CAP > haut_px * ECH):
        t -= 0.25
    return t


T_BULLE = _ajuste("88", 62.0, 40.0)     # dans la bulle, sous ON / OFF
T_DROITE = _ajuste("88", 58.0, 40.0)    # à droite, en haut
T_DESSOUS = _ajuste("88", 46.0, 26.0)   # en petit, dessous


def _rangee(rng, deja):
    r = None
    for _ in range(200):
        r = [{} for _ in range(5)]
        for k in LIGNES:
            a, b = PLAGES[k]
            t = list(range(a, b + 1))
            rng.shuffle(t)
            for i in range(5):
                r[i][k] = sorted(t[3 * i:3 * i + 3])
        cles = [tuple(tuple(r[i][k]) for k in LIGNES) for i in range(5)]
        if not any(cl in deja for cl in cles):
            deja.update(cles)
            return r
    return r


def _num(c, s, xc, yc, t):
    o = c.beginText()
    o.setTextRenderMode(2)
    c.setLineWidth(0.02 * t)
    o.setFont(POLICE, t)
    o.setTextOrigin(xc - c.stringWidth(s, POLICE, t) / 2.0, yc - t * CAP / 2.0)
    o.textOut(s)
    c.drawText(o)


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                _deja=None, **_ig):
    n_ = nb_tickets if nb_tickets is not None else nb_cartes
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("TRIPLE POWER")
    rng = random.Random(int(serie_start) * 100003 + 7577)
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
        for rg in range(2):
            rangee = _rangee(rng, deja)
            for col in range(5):
                if faits >= n_:
                    break
                nums = rangee[col]
                coul = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else NOIR
                c.saveState()
                c.setFillColor(coul)
                c.setStrokeColor(coul)
                c.setLineJoin(1)
                for li, k in enumerate(LIGNES):
                    cx, cy, r = BULLES[rg * 20 + col * 4 + li]
                    v1, v2, v3 = nums[k]
                    _num(c, str(v1), _px(cx), _py(cy + 0.22 * r), T_BULLE)
                    _num(c, str(v2), _px(cx + r + 44), _py(cy - 0.30 * r), T_DROITE)
                    _num(c, str(v3), _px(cx + r + 26), _py(cy + 0.66 * r), T_DESSOUS)
                c.restoreState()
                c.setFillColor(GRIS)
                c.setFont("Helvetica-Bold", 9)
                c.drawCentredString(_px(COL_X0[col] + SERIE_DX), _py(SERIE_Y[rg]), "%06d" % serie)
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
    open("test_triple_power.pdf", "wb").write(generer_pdf(nb_tickets=10, couleur=False).read())
    print("TRIPLE POWER genere")
