# -*- coding: utf-8 -*-
"""MANAPRINT — FATU HIVA · 16 numéros (maquette Maeva 17/11/2026).
8 cartons / feuille A4 PORTRAIT (2 colonnes x 4 rangées) — la feuille de la
maquette est reprise TELLE QUELLE comme fond (chiffres d'origine gommés,
traits passés en gris) ; on n'ajoute que les chiffres et le n° de série.
Chaque carton = 8 cases rondes + 8 cases simples : sur chaque ligne, un
numéro dans le ROND et un numéro JUSTE À SA DROITE.
Plages = OHANA 75 · 2 séries, B I G O (sceau Maeva 17/11) :
   gauche, lignes 1 et 4  -> B  1-15   (4 numéros)
   gauche, lignes 2 et 3  -> I 16-30   (4 numéros)
   droite, lignes 2 et 3  -> G 46-60   (4 numéros)
   droite, lignes 1 et 4  -> O 61-75   (4 numéros)
   -> 16 numéros différents par carton, crieur 1 à 75 SANS le N (31-45)."""
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
PLAGES = {"B": (1, 15), "I": (16, 30), "G": (46, 60), "O": (61, 75)}

_ICI = _os.path.dirname(_os.path.abspath(__file__))
# chiffres gras à empattements, comme la maquette (Liberation Serif = Times)
POLICE = "Times-Bold"
for _f in (_os.path.join(_ICI, "LiberationSerif-Bold.ttf"),
           "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"):
    try:
        pdfmetrics.registerFont(TTFont("FATUSERIF", _f))
        POLICE = "FATUSERIF"
        break
    except Exception:
        pass
_CAP = 0.66
# ⭐ 17/11 (Maeva : « GO pour le B ») : chiffres en LEAGUE GOTHIC, écriture
#    très étroite -> chiffres 10 % plus hauts qu'en Bebas Neue.
#    (Bebas Neue gardée en secours si League Gothic manque.)
try:
    pdfmetrics.registerFont(TTFont("LGOTH", _os.path.join(_ICI, "LeagueGothic-Regular.ttf")))
    POLICE, _CAP = "LGOTH", 0.735
except Exception:
    try:
        pdfmetrics.registerFont(TTFont("BEBAS", _os.path.join(_ICI, "BebasNeue-Regular.ttf")))
        POLICE, _CAP = "BEBAS", 0.71
    except Exception:
        pass

# maquette v2 (17/11, ronds agrandis) : 1058 x 1486 px (feuille entière)
_IMG_W, _IMG_H = 1058.0, 1486.0
_IMG_FOND = _os.path.join(_ICI, "fatu_hiva_fond.png")

# pour chaque carton (ordre de lecture) :
#   serie : (x, ligne de base) px du n° de série, sous le cadre du carton
#   ronds : par plage, (cx, cy, rayon blanc intérieur, x du 2e numéro) en px ;
#           le 2e numéro est centré dans le blanc MESURÉ à droite du rond.
CARTONS = [
    {'serie': (70, 409),
     'ronds': {'B': [(59.5, 122.5, 25.0, 119.5), (59.1, 343.4, 24.5, 117.0)], 'I': [(102.6, 196.0, 23.0, 156.5), (104.6, 269.5, 23.5, 162.0)], 'O': [(414.8, 122.3, 23.5, 475.0), (416.3, 343.4, 24.5, 477.0)], 'G': [(385.2, 196.1, 23.5, 442.0), (374.3, 269.8, 23.5, 432.5)]}},
    {'serie': (598, 409),
     'ronds': {'B': [(588.4, 122.5, 25.0, 648.5), (588.1, 343.5, 24.5, 646.0)], 'I': [(631.1, 196.0, 22.5, 685.0), (633.3, 269.7, 23.5, 691.0)], 'O': [(943.4, 122.2, 23.0, 1004.0), (945.0, 343.4, 24.5, 1005.5)], 'G': [(913.9, 196.2, 23.5, 971.0), (903.3, 269.8, 23.5, 961.5)]}},
    {'serie': (70, 770),
     'ronds': {'B': [(59.5, 484.2, 25.0, 119.5), (59.1, 705.6, 24.0, 117.0)], 'I': [(102.8, 558.3, 22.5, 156.5), (104.6, 631.3, 24.0, 162.0)], 'O': [(414.8, 484.1, 23.5, 475.0), (416.4, 705.3, 24.0, 477.0)], 'G': [(385.2, 558.7, 23.5, 442.0), (374.3, 631.6, 23.5, 432.5)]}},
    {'serie': (598, 770),
     'ronds': {'B': [(588.5, 484.2, 25.0, 648.0), (588.2, 705.6, 24.0, 646.0)], 'I': [(631.4, 558.4, 22.5, 685.0), (633.4, 631.4, 23.5, 691.0)], 'O': [(943.4, 484.2, 23.0, 1004.0), (945.3, 705.4, 24.5, 1005.5)], 'G': [(913.9, 558.7, 23.5, 971.0), (903.2, 631.6, 23.5, 961.5)]}},
    {'serie': (70, 1113),
     'ronds': {'B': [(59.5, 842.1, 24.5, 119.5), (59.2, 1052.8, 22.0, 117.0)], 'I': [(102.6, 915.1, 22.5, 156.5), (104.4, 984.6, 22.0, 162.0)], 'O': [(414.8, 842.1, 23.5, 475.0), (416.4, 1052.8, 22.0, 477.0)], 'G': [(385.3, 915.5, 23.0, 442.0), (374.4, 984.8, 22.0, 432.5)]}},
    {'serie': (599, 1113),
     'ronds': {'B': [(588.5, 842.1, 24.5, 648.0), (588.1, 1052.7, 22.0, 646.0)], 'I': [(631.2, 915.1, 22.5, 685.0), (633.3, 984.5, 22.0, 691.0)], 'O': [(943.7, 842.0, 23.5, 1004.0), (945.4, 1052.8, 22.0, 1006.0)], 'G': [(914.0, 915.6, 23.0, 971.0), (903.3, 984.8, 22.0, 961.5)]}},
    {'serie': (71, 1449),
     'ronds': {'B': [(59.5, 1177.9, 23.5, 119.5), (59.1, 1385.4, 23.5, 117.0)], 'I': [(102.6, 1247.6, 22.0, 156.5), (104.5, 1315.2, 22.0, 162.0)], 'O': [(414.8, 1177.8, 22.5, 475.0), (416.3, 1385.1, 23.5, 477.0)], 'G': [(385.3, 1248.1, 22.5, 442.0), (374.4, 1315.3, 21.5, 432.5)]}},
    {'serie': (600, 1449),
     'ronds': {'B': [(588.5, 1177.9, 23.5, 648.0), (588.1, 1385.4, 23.0, 646.0)], 'I': [(631.3, 1247.5, 22.0, 685.5), (633.5, 1315.2, 22.0, 691.0)], 'O': [(943.6, 1177.8, 22.5, 1004.0), (945.3, 1385.0, 23.5, 1005.5)], 'G': [(913.9, 1248.2, 22.5, 970.5), (903.3, 1315.3, 22.0, 961.5)]}},
]

# ⭐ taille MESURÉE (17/11, maquette v2 aux ronds agrandis), 2 px de marge :
#    « 88 » tient jusqu'à 27,3 pt en League Gothic, 25,8 pt en Bebas Neue,
#    22,5 pt en Times gras, dans le plus petit rond. NE PAS MONTER AU-DESSUS.
_T_NUM = {"LGOTH": 27.0, "BEBAS": 25.5}.get(POLICE, 22.0)


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
    """{plage: [8 numéros... ]} : 4 par plage, tous différents."""
    return {k: rng.sample(range(lo, hi + 1), 4) for k, (lo, hi) in PLAGES.items()}


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 1717 + 17)
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
            c.drawString(_px(20), PAGE_H - 22, entete)
        c.setFillColor(colors.Color(0.6, 0.6, 0.6))
        c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 14, PAGE_H - 22, "%03d" % no_page)

        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ct = CARTONS[idx]
            col = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else GRIS
            # n° de série, discret, sous le cadre du carton
            sx, sy = ct["serie"]
            c.setFillColor(GRIS_TRAIT)
            c.setFont("Helvetica-Bold", 5.5)
            c.drawString(_px(sx), _py(sy), "N° %06d" % serie)
            # les 16 chiffres : un dans le rond, un juste à droite
            c.setFillColor(col)
            c.setFont(POLICE, _T_NUM)
            nums = _numeros(rng)
            dy = _T_NUM * _CAP / 2.0
            for k, ronds in ct["ronds"].items():
                vals = nums[k]
                for i, (cx, cy, ri, x2) in enumerate(ronds):
                    a, b = vals[2 * i], vals[2 * i + 1]
                    _chiffre(c, _px(cx), _py(cy) - dy, a, _T_NUM)
                    _chiffre(c, _px(x2), _py(cy) - dy, b, _T_NUM)
            serie += 1
            faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_fatu_hiva.pdf", "wb").write(generer_pdf(nb_cartes=8, couleur=False).read())
    print("FATU HIVA genere")
