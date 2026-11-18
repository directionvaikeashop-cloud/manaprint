# -*- coding: utf-8 -*-
"""MANAPRINT — HIVA OA · 6 numéros (maquette Maeva 17/11/2026).
12 cartons / feuille A4 PORTRAIT (2 colonnes x 6 rangées) — la feuille de
la maquette est reprise TELLE QUELLE comme fond (chiffres d'origine gommés,
traits passés en gris) ; on n'ajoute que les chiffres et le n° de série.
Chaque carton = 1 numéro dans la BULLE + 5 numéros sur l'île (sceau Maeva) :
   la bulle                                   -> 1-15
   colonne 1 (« 22 » en haut, « 18 » en bas)  -> 16-30  (2 numéros)
   colonne 2, en haut (« 45 »)                 -> 31-45
   « 63 » (en bas) et « 75 » (en haut à droite) -> 60-75  (2 numéros)
   -> crieur 1 à 45 et 60 à 75."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PAGE_W, PAGE_H = A4
CARTES_PAGE = 12
GRIS = colors.Color(0.18, 0.18, 0.18)
GRIS_TRAIT = colors.Color(105 / 255.0, 105 / 255.0, 105 / 255.0)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
PLAGES = {"B": (1, 15), "I": (16, 30), "N": (31, 45), "O": (60, 75)}

_ICI = _os.path.dirname(_os.path.abspath(__file__))
# chiffres en LEAGUE GOTHIC (comme FATU HIVA : étroite = chiffres plus hauts)
POLICE, _CAP = "Helvetica-Bold", 0.717
_T_BULLE, _T_NUM = 26.0, 19.0
try:
    pdfmetrics.registerFont(TTFont("LGOTH", _os.path.join(_ICI, "LeagueGothic-Regular.ttf")))
    # ⭐ 17/11 soir (Maeva : « grossir encore ») : les 5 chiffres de l'île sont
    #    REPLACÉS en zigzag (haut/bas/haut/bas/haut, comme la maquette) sur
    #    toute la largeur libre de l'île — positions MESURÉES au pixel, 3 px
    #    de marge au contour, 12 px entre chiffres. « 88 » tient à 28 pt sur
    #    l'île et 35,5 pt dans la bulle. NE PAS MONTER AU-DESSUS.
    POLICE, _CAP = "LGOTH", 0.735
    _T_BULLE, _T_NUM = 35.5, 28.0
except Exception:
    pass

# maquette : 1055 x 1491 px (feuille entière)
_IMG_W, _IMG_H = 1055.0, 1491.0
_IMG_FOND = _os.path.join(_ICI, "hiva_oa_fond.png")

# pour chaque carton (ordre de lecture) : centres (x, y) px de la bulle et
# des emplacements des chiffres d'origine (I = 22 puis 18 ; N = 45 ;
# O = 63 puis 75) ; serie = (x centre, ligne de base) du n° de série.
CARTONS = [
    {'bulle': (116.2, 155.8), 'I': [(240.5, 162.2), (286.5, 190.2)], 'N': [(332.5, 162.2)], 'O': [(378.5, 190.2), (424.5, 162.2)], 'serie': (332, 218)},
    {'bulle': (644.3, 155.8), 'I': [(768.5, 162.2), (814.5, 190.2)], 'N': [(860.5, 162.2)], 'O': [(906.5, 190.2), (952.5, 162.2)], 'serie': (860, 218)},
    {'bulle': (116.2, 406.8), 'I': [(240.5, 413.2), (286.5, 441.2)], 'N': [(332.5, 413.2)], 'O': [(378.5, 441.2), (424.5, 413.2)], 'serie': (332, 469)},
    {'bulle': (644.3, 406.7), 'I': [(768.5, 413.2), (814.5, 441.2)], 'N': [(860.5, 413.2)], 'O': [(906.5, 441.2), (952.5, 413.2)], 'serie': (860, 469)},
    {'bulle': (116.3, 651.5), 'I': [(238.5, 659.2), (284.5, 687.2)], 'N': [(330.5, 659.2)], 'O': [(376.5, 687.2), (422.5, 659.2)], 'serie': (330, 715)},
    {'bulle': (644.2, 651.5), 'I': [(766.5, 659.2), (812.5, 687.2)], 'N': [(858.5, 659.2)], 'O': [(904.5, 687.2), (950.5, 659.2)], 'serie': (858, 715)},
    {'bulle': (116.3, 893.8), 'I': [(239.5, 901.2), (285.5, 929.2)], 'N': [(331.5, 901.2)], 'O': [(377.5, 929.2), (423.5, 901.2)], 'serie': (331, 957)},
    {'bulle': (644.3, 893.8), 'I': [(764.5, 902.2), (810.5, 930.2)], 'N': [(856.5, 902.2)], 'O': [(902.5, 930.2), (948.5, 902.2)], 'serie': (856, 958)},
    {'bulle': (116.4, 1126.0), 'I': [(237.5, 1137.2), (283.5, 1165.2)], 'N': [(329.5, 1137.2)], 'O': [(375.5, 1165.2), (421.5, 1137.2)], 'serie': (329, 1184)},
    {'bulle': (644.4, 1126.0), 'I': [(762.5, 1138.2), (808.5, 1166.2)], 'N': [(854.5, 1138.2)], 'O': [(900.5, 1166.2), (946.5, 1138.2)], 'serie': (854, 1184)},
    {'bulle': (116.4, 1343.3), 'I': [(236.5, 1355.2), (282.5, 1383.2)], 'N': [(328.5, 1355.2)], 'O': [(374.5, 1383.2), (420.5, 1355.2)], 'serie': (328, 1401)},
    {'bulle': (644.4, 1343.3), 'I': [(764.5, 1355.2), (810.5, 1383.2)], 'N': [(856.5, 1355.2)], 'O': [(902.5, 1383.2), (948.5, 1355.2)], 'serie': (856, 1402)},
]


# ⭐ 17/11 (Maeva : « GO ») : chiffres ÉPAISSIS (« League Gothic gras ») —
#    même écriture, même taille, trait de 0,6 pt de la couleur du chiffre
#    autour de chaque lettre (reste dans la marge mesurée de 2 px).
_EPAIS = 0.6


def _chiffre(c, x, y, txt, taille, centre=True):
    txt = str(txt)
    w = c.stringWidth(txt, POLICE, taille)
    x0 = x - w / 2.0 if centre else x
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


def _px(x):
    return x / _IMG_W * PAGE_W


def _py(y):
    return PAGE_H * (1 - y / _IMG_H)


def _numeros(rng):
    b = rng.randint(*PLAGES["B"])
    i = sorted(rng.sample(range(PLAGES["I"][0], PLAGES["I"][1] + 1), 2))
    n = rng.randint(*PLAGES["N"])
    o = sorted(rng.sample(range(PLAGES["O"][0], PLAGES["O"][1] + 1), 2))
    return b, i, n, o


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 7171)
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
            c.setFont("Helvetica-Bold", 7.5)
            c.drawString(_px(40), PAGE_H - 18, entete)
        c.setFillColor(colors.Color(0.6, 0.6, 0.6))
        c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 14, PAGE_H - 18, "%03d" % no_page)

        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ct = CARTONS[idx]
            col = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else GRIS
            b, i, n, o = _numeros(rng)
            c.setFillColor(col)
            # la bulle
            bx, by = ct["bulle"]
            c.setFont(POLICE, _T_BULLE)
            _chiffre(c, _px(bx), _py(by) - _T_BULLE * _CAP / 2.0, b, _T_BULLE)
            # les 5 chiffres sur l'île, aux places des chiffres d'origine
            c.setFont(POLICE, _T_NUM)
            dy = _T_NUM * _CAP / 2.0
            for (x, y), v in list(zip(ct["I"], i)) + list(zip(ct["N"], [n])) + list(zip(ct["O"], o)):
                _chiffre(c, _px(x), _py(y) - dy, v, _T_NUM)
            # n° de série discret, dans un blanc MESURÉ entre « 18 » et « 63 »
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


if __name__ == "__main__":
    open("test_hiva_oa.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("HIVA OA genere")
