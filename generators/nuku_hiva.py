# -*- coding: utf-8 -*-
"""MANAPRINT — NUKU HIVA · 6 numéros (maquette MARIO, Maeva 17/11/2026).
8 cartons / feuille A4 PORTRAIT (2 colonnes x 4 rangées) — la feuille de la
maquette est reprise TELLE QUELLE comme fond (chiffres d'origine gommés,
traits passés en gris) ; on n'ajoute que les chiffres et le n° de série.
Chaque carton = 6 BULLES (sceau Maeva : plages 1 à 75 par 15) :
   gauche haut  -> B  1-15      droite haut   -> G 46-60
   gauche milieu-> I 16-30      droite milieu -> O 61-75 (le plus petit)
   gauche bas   -> N 31-45      droite bas    -> O 61-75 (le plus grand)
   -> 6 numéros différents, crieur 1 à 75."""
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
# chiffres en LEAGUE GOTHIC épaissi (comme FATU HIVA / HIVA OA)
POLICE, _CAP, _T_NUM = "Helvetica-Bold", 0.717, 30.0
try:
    pdfmetrics.registerFont(TTFont("LGOTH", _os.path.join(_ICI, "LeagueGothic-Regular.ttf")))
    # ⭐ MESURÉ (17/11) : « 88 » tient entier jusqu'à 36,7 pt dans la plus
    #    petite bulle (rangée du bas), 5 px de marge au trait. NE PAS MONTER.
    POLICE, _CAP, _T_NUM = "LGOTH", 0.75, 36.0
except Exception:
    pass
_EPAIS = 0.6

# maquette : 1055 x 1491 px (feuille entière)
_IMG_W, _IMG_H = 1055.0, 1491.0
_IMG_FOND = _os.path.join(_ICI, "nuku_hiva_fond.png")

# centres (x, y) px des 6 bulles de chaque carton (ordre de lecture) et
# (x centre, ligne de base) du n° de série
CARTONS = [
    {'B': (93.7, 101.4), 'I': (91.7, 191.7), 'N': (91.2, 283.6), 'G': (448.1, 101.6), 'O': [(450.6, 192.6), (451.3, 283.9)], 'serie': (375, 180)},
    {'B': (606.5, 101.0), 'I': (604.5, 191.8), 'N': (603.7, 283.6), 'G': (961.4, 101.4), 'O': [(963.7, 192.5), (963.9, 284.0)], 'serie': (887, 180)},
    {'B': (93.6, 473.9), 'I': (91.7, 564.1), 'N': (91.2, 656.3), 'G': (448.2, 474.3), 'O': [(450.6, 565.1), (451.2, 656.6)], 'serie': (376, 552)},
    {'B': (606.7, 473.5), 'I': (604.6, 564.3), 'N': (603.8, 656.3), 'G': (961.4, 474.2), 'O': [(963.6, 565.1), (963.9, 656.7)], 'serie': (888, 552)},
    {'B': (93.6, 845.5), 'I': (91.7, 935.7), 'N': (91.3, 1027.1), 'G': (448.2, 846.1), 'O': [(450.7, 936.8), (451.2, 1027.5)], 'serie': (376, 923)},
    {'B': (606.7, 845.3), 'I': (604.7, 935.8), 'N': (604.2, 1027.0), 'G': (961.4, 846.0), 'O': [(963.8, 936.8), (963.9, 1027.6)], 'serie': (887, 924)},
    {'B': (93.7, 1206.5), 'I': (92.0, 1289.8), 'N': (91.9, 1376.3), 'G': (448.5, 1206.9), 'O': [(450.7, 1290.7), (451.4, 1376.7)], 'serie': (376, 1280)},
    {'B': (607.0, 1206.0), 'I': (604.8, 1289.7), 'N': (603.9, 1376.3), 'G': (961.9, 1206.8), 'O': [(963.8, 1290.7), (964.2, 1376.9)], 'serie': (886, 1280)},
]


def _px(x):
    return x / _IMG_W * PAGE_W


def _py(y):
    return PAGE_H * (1 - y / _IMG_H)


def _chiffre(c, x, y, txt, taille):
    txt = str(txt)
    x0 = x - c.stringWidth(txt, POLICE, taille) / 2.0
    c.saveState()
    try:
        c.setStrokeColor(c._fillColorObj)
        c.setLineWidth(_EPAIS)
        c.setLineJoin(1)
        t = c.beginText()
        t.setTextRenderMode(2)
        t.setFont(POLICE, taille)
        t.setTextOrigin(x0, y)
        t.textOut(txt)
        c.drawText(t)
    finally:
        c.restoreState()


def _numeros(rng):
    b = rng.randint(1, 15)
    i = rng.randint(16, 30)
    n = rng.randint(31, 45)
    g = rng.randint(46, 60)
    o = sorted(rng.sample(range(61, 76), 2))
    return b, i, n, g, o


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 8181)
    serie = int(serie_start)
    faits = 0
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
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - 4.5, entete)
        c.setFillColor(colors.Color(0.6, 0.6, 0.6))
        c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 10, PAGE_H - 4.5, "%03d" % no_page)

        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ct = CARTONS[idx]
            col = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else GRIS
            b, i, n, g, o = _numeros(rng)
            c.setFillColor(col)
            dy = _T_NUM * _CAP / 2.0
            for (x, y), v in ((ct["B"], b), (ct["I"], i), (ct["N"], n), (ct["G"], g),
                              (ct["O"][0], o[0]), (ct["O"][1], o[1])):
                _chiffre(c, _px(x), _py(y) - dy, v, _T_NUM)
            sx, sy = ct["serie"]
            c.setFillColor(GRIS_TRAIT)
            c.setFont("Helvetica-Bold", 5)
            c.drawCentredString(_px(sx), _py(sy), "N° %06d" % serie)
            serie += 1
            faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf
