# -*- coding: utf-8 -*-
"""MANAPRINT — CIBLE · 8 numéros (création RANIHEI Sisters & Shop),
maquette Maeva 15/11/2026.
6 cartons / feuille A4 PORTRAIT (3 colonnes x 2 rangées) — la feuille de la
maquette est reprise TELLE QUELLE comme fond (traits passés en gris) ; on
n'ajoute que les chiffres et le n° de série.
Chaque carton = 8 CIBLES, 1 numéro au centre de chacune (sceau Maeva 15/11) :
   2 cibles du haut      -> B  1-15
   2 cibles du milieu    -> I 16-30
   2 cibles du bas       -> N 31-45
   petite cible centre haut -> G 46-60
   petite cible centre bas  -> O 61-75
   Dans une rangée de 2, le plus petit à gauche. Crieur 1 à 75.
Chiffres en BEBAS NEUE (comme PING-PONG GO : écriture étroite = chiffres
plus hauts, traits fins = économie de toner)."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4
CARTES_PAGE = 6
GRIS = colors.Color(0.18, 0.18, 0.18)
GRIS_TRAIT = colors.Color(105 / 255.0, 105 / 255.0, 105 / 255.0)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
PLAGES = {"B": (1, 15), "I": (16, 30), "N": (31, 45), "G": (46, 60), "O": (61, 75)}

_ICI = _os.path.dirname(_os.path.abspath(__file__))
POLICE, _CAP = "Helvetica-Bold", 0.717
try:
    pdfmetrics.registerFont(TTFont("BEBAS", _os.path.join(_ICI, "BebasNeue-Regular.ttf")))
    POLICE, _CAP = "BEBAS", 0.70
except Exception:
    pass
try:
    pdfmetrics.registerFont(TTFont("CIBSERIE", _os.path.join(_ICI, "DejaVuSansCondensed-Bold.ttf")))
    _POLICE_SERIE = "CIBSERIE"
except Exception:
    _POLICE_SERIE = "Helvetica-Bold"

# maquette : 1054 x 1492 px (feuille entière)
_IMG_W, _IMG_H = 1054.0, 1492.0
_IMG_FOND = _os.path.join(_ICI, "cible_fond.png")

# pour chaque carton (ordre de lecture) :
#   serie : rectangle des chiffres du n° dans le cartouche (x0, y0, x1, y1) px
#   pots  : par plage, les cibles (cx, cy, r) = centre et rayon du rond blanc
CARTONS = [
    {'serie': (149, 19, 242, 41),
     'pots': {'B': [(97.5, 248.3, 39.6), (264.0, 248.6, 39.4)], 'I': [(88.8, 415.1, 38.5), (271.3, 415.9, 36.7)], 'N': [(89.6, 582.1, 37.3), (269.7, 582.4, 37.0)], 'G': [(179.3, 340.6, 31.0)], 'O': [(179.4, 496.3, 30.8)]}},
    {'serie': (498, 19, 596, 41),
     'pots': {'B': [(445.0, 248.8, 39.9), (611.9, 248.7, 39.2)], 'I': [(436.2, 415.3, 38.5), (619.6, 415.9, 36.4)], 'N': [(438.5, 582.3, 37.1), (617.5, 582.9, 37.7)], 'G': [(527.4, 340.6, 31.8)], 'O': [(528.0, 496.3, 31.2)]}},
    {'serie': (844, 19, 942, 41),
     'pots': {'B': [(794.1, 248.3, 39.8), (960.8, 248.9, 39.4)], 'I': [(783.8, 415.2, 38.4), (968.5, 415.9, 36.9)], 'N': [(786.8, 582.0, 37.5), (967.0, 582.9, 37.6)], 'G': [(875.8, 340.6, 31.1)], 'O': [(875.6, 496.4, 31.1)]}},
    {'serie': (148, 761, 248, 784),
     'pots': {'B': [(97.4, 992.9, 39.2), (264.3, 993.1, 38.9)], 'I': [(88.9, 1159.7, 38.2), (271.4, 1160.1, 37.0)], 'N': [(89.6, 1325.6, 37.5), (269.6, 1325.8, 37.6)], 'G': [(179.5, 1084.4, 30.8)], 'O': [(179.5, 1240.2, 30.4)]}},
    {'serie': (498, 761, 596, 784),
     'pots': {'B': [(445.1, 993.1, 39.4), (611.8, 993.0, 38.6)], 'I': [(436.5, 1159.6, 38.2), (619.5, 1160.2, 36.7)], 'N': [(438.4, 1325.7, 37.5), (617.4, 1326.2, 37.5)], 'G': [(527.3, 1084.4, 31.8)], 'O': [(527.9, 1240.0, 31.1)]}},
    {'serie': (844, 761, 944, 784),
     'pots': {'B': [(793.7, 992.5, 39.8), (961.0, 993.2, 39.1)], 'I': [(783.9, 1159.7, 38.3), (968.5, 1160.1, 37.0)], 'N': [(786.8, 1325.6, 37.5), (967.0, 1326.2, 37.5)], 'G': [(875.6, 1084.4, 31.8)], 'O': [(875.7, 1240.1, 31.1)]}},
]


def _px(x):
    return x / _IMG_W * PAGE_W


def _py(y):
    return PAGE_H * (1 - y / _IMG_H)


def _taille_pour(r):
    """La plus grande taille où « 88 » (pire cas) tient ENTIER dans un rond
    blanc de rayon r px (coins du texte dans le cercle, marge 8 %)."""
    r_pt = r / _IMG_W * PAGE_W * 0.92
    t = 2 * r_pt / _CAP
    while t > 6:
        w = stringWidth("88", POLICE, t) / 2.0
        h = t * _CAP / 2.0
        if w * w + h * h <= r_pt * r_pt:
            break
        t -= 0.25
    return t


# ⭐ 15/11 (Maeva : « le pt de chiffre ») : DEUX tailles — les 6 grandes
#    cibles (B, I, N) ne sont plus bridées par les 2 petites du centre (G, O).
#    Chaque taille = le maximum où « 88 » tient dans la plus petite cible de
#    son groupe.
_R_GRANDES = min(c[2] for ct in CARTONS for k in ("B", "I", "N") for c in ct["pots"][k])
_R_PETITES = min(c[2] for ct in CARTONS for k in ("G", "O") for c in ct["pots"][k])
_T_GRANDES = _taille_pour(_R_GRANDES)
_T_PETITES = _taille_pour(_R_PETITES)
_T_NUM = _T_PETITES


def _taille_serie():
    x0, y0, x1, y1 = CARTONS[0]["serie"]
    t = (y1 - y0) / _IMG_H * PAGE_H / 0.729
    while t > 4 and stringWidth("000000", _POLICE_SERIE, t) > (x1 - x0 + 4) / _IMG_W * PAGE_W:
        t -= 0.25
    return t
_T_SERIE = _taille_serie()


def _numeros(rng):
    """{plage: [numéros]} — tous différents, le plus petit à gauche."""
    return {k: sorted(rng.sample(range(lo, hi + 1), len(CARTONS[0]["pots"][k])))
            for k, (lo, hi) in PLAGES.items()}


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 1717)
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
            c.setFillColor(GRIS_TRAIT)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - 4.0, entete)
        c.setFillColor(colors.Color(0.6, 0.6, 0.6))
        c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 10, PAGE_H - 4.0, "%03d" % no_page)

        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ct = CARTONS[idx]
            col = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else GRIS
            # n° de série à la place de « 000001 » dans le cartouche
            x0, y0, x1, y1 = ct["serie"]
            c.setFillColor(GRIS_TRAIT)
            c.setFont(_POLICE_SERIE, _T_SERIE)
            c.drawString(_px(x0), _py(y1), "%06d" % serie)
            # les 8 chiffres, au centre des cibles
            c.setFillColor(col)
            nums = _numeros(rng)
            for k, cibles in ct["pots"].items():
                t = _T_PETITES if k in ("G", "O") else _T_GRANDES
                c.setFont(POLICE, t)
                for (cx, cy, _r), v in zip(cibles, nums[k]):
                    c.drawCentredString(_px(cx), _py(cy) - t * _CAP / 2.0, str(v))
            serie += 1
            faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_cible.pdf", "wb").write(generer_pdf(nb_cartes=6, couleur=False).read())
    print("CIBLE genere")
