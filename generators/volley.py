# -*- coding: utf-8 -*-
"""MANAPRINT — VOLLEY-BALL (Ranihei, maquette Maeva 17/11/2026).
8 cartons / feuille A4 PORTRAIT (2 colonnes x 4 rangées) — la feuille de la
maquette est reprise TELLE QUELLE comme fond (chiffres d'origine gommés,
traits passés en gris) ; on n'ajoute que les chiffres et le n° de série.
5 numéros par carton, sur les maillots, de gauche à droite :
   joueur accroupi à gauche      -> B 1-15
   petit joueur accroupi         -> I 16-30
   attaquant qui saute           -> N 31-45
   contreur de gauche            -> G 46-60
   contreur de droite            -> O 61-75
   -> crieur 1 à 75. Chiffres sur 2 caractères (« 05 ») comme la maquette."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PAGE_W, PAGE_H = A4
CARTES_PAGE = 8
GRIS = colors.Color(0.18, 0.18, 0.18)
GRIS_TRAIT = colors.Color(105 / 255.0, 105 / 255.0, 105 / 255.0)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
PLAGES = {"B": (1, 15), "I": (16, 30), "N": (31, 45), "G": (46, 60), "O": (61, 75)}

_ICI = _os.path.dirname(_os.path.abspath(__file__))
# chiffres en LEAGUE GOTHIC épaissi ; tailles = le plus gros « 88 » qui tient
# dans le blanc de CHAQUE maillot (mesuré au pixel, 3 px de marge). NE PAS MONTER.
POLICE, _CAP = "Helvetica-Bold", 0.717
TAILLES = {"B": 17.0, "I": 16.0, "N": 24.0, "G": 27.0, "O": 27.0}
try:
    pdfmetrics.registerFont(TTFont("LGOTH", _os.path.join(_ICI, "LeagueGothic-Regular.ttf")))
    POLICE, _CAP = "LGOTH", 0.735
    TAILLES = {"B": 23.5, "I": 22.0, "N": 33.5, "G": 38.0, "O": 38.0}
except Exception:
    pass

_IMG_W, _IMG_H = 1054.0, 1492.0
_IMG_FOND = _os.path.join(_ICI, "volley_fond.png")

# centres (x, y) px des chiffres sur chaque carton (ordre de lecture) ;
# serie = (x centre, ligne de base) du n° de série, dans le blanc à gauche du titre.
CARTONS = [
    {'B': (82.0, 290.5), 'I': (184.5, 306.5), 'N': (242.5, 148.5), 'G': (349.5, 260.0), 'O': (439.0, 263.0), 'serie': (53, 30)},
    {'B': (597.5, 290.5), 'I': (700.0, 308.0), 'N': (752.5, 147.0), 'G': (868.0, 266.0), 'O': (957.0, 261.0), 'serie': (569, 30)},
    {'B': (78.5, 662.0), 'I': (183.5, 678.5), 'N': (240.5, 521.0), 'G': (350.0, 632.0), 'O': (441.0, 635.0), 'serie': (53, 404)},
    {'B': (598.5, 662.0), 'I': (700.5, 680.0), 'N': (752.5, 520.0), 'G': (864.0, 637.0), 'O': (957.0, 635.5), 'serie': (571, 404)},
    {'B': (81.0, 1033.0), 'I': (181.5, 1050.5), 'N': (240.0, 893.0), 'G': (351.0, 1004.0), 'O': (441.0, 1005.5), 'serie': (53, 777)},
    {'B': (597.5, 1029.5), 'I': (699.5, 1050.5), 'N': (752.5, 893.0), 'G': (863.0, 1008.0), 'O': (957.0, 1003.0), 'serie': (569, 777)},
    {'B': (82.5, 1378.0), 'I': (186.0, 1394.5), 'N': (242.5, 1253.0), 'G': (350.0, 1353.5), 'O': (440.0, 1352.0), 'serie': (53, 1147)},
    {'B': (599.5, 1377.5), 'I': (699.5, 1395.0), 'N': (757.5, 1253.0), 'G': (864.0, 1353.0), 'O': (958.0, 1352.0), 'serie': (571, 1147)},
]

_EPAIS = 0.6


def _chiffre(c, x, y, txt, taille):
    txt = str(txt)
    w = c.stringWidth(txt, POLICE, taille)
    c.saveState()
    try:
        c.setStrokeColor(c._fillColorObj)
        c.setLineWidth(_EPAIS)
        c.setLineJoin(1)
        t = c.beginText()
        t.setTextRenderMode(2)
        t.setFont(POLICE, taille)
        t.setTextOrigin(x - w / 2.0, y)
        t.textOut(txt)
        c.drawText(t)
    finally:
        c.restoreState()


def _px(x):
    return x / _IMG_W * PAGE_W


def _py(y):
    return PAGE_H * (1 - y / _IMG_H)


def _numeros(rng, deja=None):
    # jamais deux cartons identiques dans un même tirage
    while True:
        d = {k: rng.randint(a, b) for k, (a, b) in PLAGES.items()}
        cle = tuple(d[k] for k in "BINGO")
        if deja is None or cle not in deja:
            if deja is not None:
                deja.add(cle)
            return d


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("VOLLEY-BALL")
    rng = random.Random(int(serie_start) * 100003 + 8686)
    serie = int(serie_start)
    faits = 0
    deja = set()
    try:
        no_page = max(1, int(page_start))
    except Exception:
        no_page = 1
    col_imposee = None
    if couleur and couleur_perso:
        try:
            col_imposee = colors.HexColor(couleur_perso)
        except Exception:
            col_imposee = None

    while faits < n_:
        try:
            c.drawImage(_IMG_FOND, 0, 0, PAGE_W, PAGE_H, preserveAspectRatio=False, mask="auto")
        except Exception:
            pass
        entete = "  ·  ".join(t for t in ((nom_evenement or "").strip(),
                                          (date_lieu or "").strip(),
                                          (telephone or "").strip()) if t)
        if entete:
            c.setFillColor(GRIS)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawString(_px(20), PAGE_H - 6.5, entete)
        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ct = CARTONS[idx]
            col = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else GRIS
            nums = _numeros(rng, deja)
            c.setFillColor(col)
            for k in "BINGO":
                x, y = ct[k]
                t = TAILLES[k]
                _chiffre(c, _px(x), _py(y) - t * _CAP / 2.0, "%02d" % nums[k], t)
            sx, sy = ct["serie"]
            c.setFillColor(GRIS_TRAIT)
            c.setFont("Helvetica-Bold", 5.5)
            c.drawCentredString(_px(sx), _py(sy), "N° %06d" % serie)
            serie += 1
            faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_volley.pdf", "wb").write(generer_pdf(nb_cartes=8, couleur=False).read())
    print("VOLLEY genere")
