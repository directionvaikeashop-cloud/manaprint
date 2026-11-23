# -*- coding: utf-8 -*-
"""MANAPRINT — CASINO (maquette de Maeva du 22/11/2026).

8 cartes par feuille A4 PAYSAGE (4 x 2). La maquette (couleurs des cartes,
fleur de lys, bandeau CASINO, 5 jetons B N O / I G, as, dés, roulette, piles
de jetons) est reprise TELLE QUELLE comme fond, en gris uni (propre sur la Konica).
RÈGLE (déduite de sa feuille remplie) — 5 numéros, un par jeton :
   B : 1-15 · I : 16-30 · N : 31-45 · G : 46-60 · O : 61-75
Crieur : 1 à 75. Chiffres NOIRS, gras, grossis au maximum dans chaque jeton.
"""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PAGE_W, PAGE_H = landscape(A4)
CARTES_PAGE = 8
PLAGES = {"B": (1, 15), "I": (16, 30), "N": (31, 45), "G": (46, 60), "O": (61, 75)}

_ICI = _os.path.dirname(_os.path.abspath(__file__))
POLICE, CAP = "Times-Bold", 0.66
try:
    pdfmetrics.registerFont(TTFont("CASINOB", _os.path.join(_ICI, "LiberationSerif-Bold.ttf")))
    POLICE, CAP = "CASINOB", 0.66
except Exception:
    pass
NOIR = colors.Color(0.05, 0.05, 0.05)
GRIS = colors.Color(0.40, 0.40, 0.40)
RAINBOW = ["#E53935", "#FB8C00", "#43A047", "#00ACC1", "#1E88E5", "#8E24AA", "#D81B60", "#6D4C41"]

_FOND = _os.path.join(_ICI, "casino_fond.png")
_IMG_W, _IMG_H = 1536.0, 1024.0
MARGE = 6 * 72 / 25.4
ECH = min((PAGE_W - 2 * MARGE) / _IMG_W, (PAGE_H - 2 * MARGE - 14) / _IMG_H)
OX = (PAGE_W - _IMG_W * ECH) / 2.0
OY = MARGE + 2

# géométrie relevée sur la carte en haut à gauche (px) : (centre x, centre y, largeur utile)
CARTE_DX, CARTE_DY = 384.0, 500.0
POSTES = {
    "B": (76.0, 211.0, 84.0),
    "N": (195.5, 211.0, 83.0),
    "O": (314.0, 211.0, 84.0),
    "I": (131.5, 319.0, 90.0),
    "G": (260.5, 319.5, 89.0),
}
DY_CHIFFRE = 6.0      # px : le chiffre descend un peu sous la lettre du jeton
SERIE_XY = (350.0, 368.0)


def _px(x):
    return OX + x * ECH


def _py(y):
    return OY + (_IMG_H - y) * ECH


def _taille(txt_max, largeur_px, hauteur_px):
    t = 60.0
    while t > 6 and (pdfmetrics.stringWidth(txt_max, POLICE, t) > largeur_px * ECH * 0.74
                     or t * CAP > hauteur_px * ECH * 0.56):
        t -= 0.25
    return t


T_BULLE = _taille("88", 76.0, 86.0)   # ⚠️ le blanc du jeton est rond : « 88 » ne doit pas mordre les rayures
T_LOSANGE = T_BULLE


def _tirage(rng):
    return {k: rng.randint(a, b) for k, (a, b) in PLAGES.items()}


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                _deja=None, **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("CASINO")
    rng = random.Random(int(serie_start) * 100003 + 7716)
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
            ligne, col_ = divmod(k, 4)
            dx, dy = col_ * CARTE_DX, ligne * CARTE_DY
            while True:
                nums = _tirage(rng)
                cle = tuple(nums[p] for p in "BINGO")
                if cle not in deja:
                    deja.add(cle)
                    break
            coul = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else NOIR
            c.saveState()
            c.setFillColor(coul)
            c.setStrokeColor(coul)
            c.setLineJoin(1)
            for p, (x, y, _l) in POSTES.items():
                t = T_LOSANGE if p == "L" else T_BULLE
                s = str(nums[p])
                yc = y + (0 if p == "L" else DY_CHIFFRE)
                o = c.beginText()
                o.setTextRenderMode(2)
                c.setLineWidth(0.02 * t)
                o.setFont(POLICE, t)
                o.setTextOrigin(_px(x + dx) - c.stringWidth(s, POLICE, t) / 2.0, _py(yc + dy) - t * CAP / 2.0)
                o.textOut(s)
                c.drawText(o)
            c.restoreState()
            c.setFillColor(GRIS)
            c.setFont("Helvetica", 5.5)
            c.drawCentredString(_px(SERIE_XY[0] + dx), _py(SERIE_XY[1] + dy), "N° %06d" % serie)
            serie += 1
            faits += 1
        # n° de page + personnalisation, dans la bande du haut (> 6 mm du bord)
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
    open("test_casino.pdf", "wb").write(generer_pdf(nb_cartes=8, couleur=False).read())
    print("CASINO genere")
