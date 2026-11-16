# -*- coding: utf-8 -*-
"""MANAPRINT — PING-PONG GO · 16 numéros (création RANIHEI Sisters & Shop),
maquette Maeva 15/11/2026.
6 cartons / feuille A4 PORTRAIT (2 colonnes x 3 rangées) — la feuille de la
maquette est reprise TELLE QUELLE comme fond (traits passés en gris, comme
CARBASS / MONTRE) ; on n'ajoute que les chiffres et le n° de série.
Chaque carton = 8 PAIRES DE RAQUETTES, 2 numéros par paire (le plus petit sur
la raquette de gauche, le plus grand sur celle de droite).
Plages = celles de l'OHANA 75 · 2 séries (sceau Maeva 15/11) :
   rangée du haut   (2 paires)        -> B  1-15
   rangée du milieu (2 paires)        -> I 16-30
   rangée du bas    (2 paires)        -> N 31-45
   paire du centre, en haut           -> G 46-60
   paire du centre, en bas            -> O 61-75
   -> 16 numéros différents par carton, crieur 1 à 75."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4
CARTES_PAGE = 6
POLICE = "Helvetica-Bold"
_CAP = 0.717          # hauteur des chiffres / taille de police
GRIS = colors.Color(0.18, 0.18, 0.18)
GRIS_TRAIT = colors.Color(105 / 255.0, 105 / 255.0, 105 / 255.0)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
PLAGES = {"B": (1, 15), "I": (16, 30), "N": (31, 45), "G": (46, 60), "O": (61, 75)}

_ICI = _os.path.dirname(_os.path.abspath(__file__))
try:
    pdfmetrics.registerFont(TTFont("PPGSERIE", _os.path.join(_ICI, "DejaVuSansCondensed-Bold.ttf")))
    _POLICE_SERIE = "PPGSERIE"
except Exception:
    try:
        pdfmetrics.registerFont(TTFont("PPGSERIE", "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"))
        _POLICE_SERIE = "PPGSERIE"
    except Exception:
        _POLICE_SERIE = "Helvetica-Bold"
# ⭐ 15/11 (choix Maeva « D ») : chiffres en BEBAS NEUE, écriture étroite ->
#    chiffres 20 % plus hauts qu'en Helvetica, traits fins (économie de toner).
try:
    pdfmetrics.registerFont(TTFont("BEBAS", _os.path.join(_ICI, "BebasNeue-Regular.ttf")))
    POLICE, _CAP = "BEBAS", 0.70
except Exception:
    pass

# maquette : 1058 x 1486 px (feuille entière)
_IMG_W, _IMG_H = 1058.0, 1486.0
_IMG_FOND = _os.path.join(_ICI, "pingpong_go_fond.png")

# pour chaque carton (dans l'ordre de lecture) :
#   serie : rectangle des chiffres du n° (x0, y0, x1, y1) en px
#   pots  : par plage, les paires [(cx, cy, r) gauche, (cx, cy, r) droite] —
#           centre et rayon du plus grand rond blanc libre de chaque raquette
CARTONS = [
    {'serie': (68, 26, 153, 47),
     'pots': {'B': [[(126.0, 96.0, 36.4), (222.0, 96.0, 34.7)], [(367.0, 96.0, 37.5), (456.0, 96.0, 36.9)]], 'I': [[(63.0, 211.0, 33.6), (144.0, 211.0, 34.8)], [(392.0, 216.0, 32.6), (472.0, 216.0, 32.8)]], 'N': [[(67.0, 354.0, 33.4), (146.0, 354.0, 33.5)], [(383.0, 354.0, 33.5), (465.0, 355.0, 33.9)]], 'G': [[(237.0, 181.0, 31.9), (318.0, 179.0, 33.0)]], 'O': [[(226.0, 298.0, 35.4), (315.0, 298.0, 34.9)]]}},
    {'serie': (593, 26, 679, 47),
     'pots': {'B': [[(651.0, 96.0, 36.4), (749.0, 94.0, 35.2)], [(892.0, 95.0, 37.3), (981.0, 96.0, 37.2)]], 'I': [[(588.0, 211.0, 33.5), (669.0, 211.0, 35.1)], [(918.0, 216.0, 33.1), (997.0, 217.0, 33.1)]], 'N': [[(593.0, 354.0, 33.2), (673.0, 353.0, 33.2)], [(909.0, 354.0, 33.7), (991.0, 355.0, 33.9)]], 'G': [[(762.0, 181.0, 32.6), (842.0, 179.0, 33.0)]], 'O': [[(752.0, 298.0, 35.4), (840.0, 298.0, 35.1)]]}},
    {'serie': (68, 520, 153, 541),
     'pots': {'B': [[(126.0, 590.0, 37.0), (221.0, 590.0, 35.0)], [(367.0, 589.0, 37.2), (456.0, 589.0, 36.7)]], 'I': [[(63.0, 702.0, 34.0), (145.0, 703.0, 34.0)], [(393.0, 708.0, 32.8), (472.0, 709.0, 33.0)]], 'N': [[(66.0, 846.0, 32.5), (145.0, 845.0, 32.0)], [(385.0, 845.0, 31.8), (465.0, 846.0, 32.6)]], 'G': [[(237.0, 674.0, 32.4), (318.0, 672.0, 32.6)]], 'O': [[(226.0, 791.0, 34.5), (313.0, 791.0, 34.5)]]}},
    {'serie': (595, 520, 681, 541),
     'pots': {'B': [[(653.0, 590.0, 36.8), (750.0, 588.0, 34.8)], [(894.0, 588.0, 37.0), (981.0, 590.0, 36.8)]], 'I': [[(590.0, 702.0, 34.5), (671.0, 703.0, 34.5)], [(919.0, 709.0, 32.8), (1000.0, 709.0, 32.6)]], 'N': [[(593.0, 844.0, 32.6), (672.0, 845.0, 32.0)], [(912.0, 844.0, 32.0), (991.0, 846.0, 32.8)]], 'G': [[(765.0, 673.0, 32.2), (845.0, 671.0, 32.3)]], 'O': [[(753.0, 790.0, 34.5), (840.0, 790.0, 34.8)]]}},
    {'serie': (69, 1011, 154, 1033),
     'pots': {'B': [[(128.0, 1077.0, 35.0), (222.0, 1078.0, 33.6)], [(368.0, 1076.0, 35.6), (456.0, 1077.0, 35.4)]], 'I': [[(63.0, 1186.0, 33.3), (143.0, 1187.0, 33.6)], [(394.0, 1194.0, 32.8), (473.0, 1195.0, 32.2)]], 'N': [[(65.0, 1331.0, 32.4), (147.0, 1330.0, 32.7)], [(385.0, 1331.0, 33.2), (466.0, 1331.0, 32.6)]], 'G': [[(239.0, 1159.0, 30.5), (318.0, 1158.0, 31.9)]], 'O': [[(227.0, 1275.0, 35.3), (315.0, 1275.0, 34.8)]]}},
    {'serie': (595, 1011, 681, 1033),
     'pots': {'B': [[(654.0, 1077.0, 34.8), (751.0, 1076.0, 33.8)], [(892.0, 1076.0, 36.4), (981.0, 1077.0, 35.7)]], 'I': [[(592.0, 1186.0, 33.0), (671.0, 1187.0, 33.8)], [(920.0, 1194.0, 33.2), (999.0, 1195.0, 32.4)]], 'N': [[(593.0, 1331.0, 32.4), (673.0, 1330.0, 32.6)], [(911.0, 1330.0, 32.8), (992.0, 1331.0, 32.7)]], 'G': [[(765.0, 1159.0, 31.0), (843.0, 1158.0, 32.2)]], 'O': [[(754.0, 1275.0, 35.1), (841.0, 1274.0, 34.7)]]}},
]


def _px(x):
    return x / _IMG_W * PAGE_W


def _py(y):
    return PAGE_H * (1 - y / _IMG_H)


def _taille_num():
    """La plus grande taille où « 88 » (pire cas) tient ENTIER dans le rond
    blanc de la plus petite raquette (coins du texte dans le cercle, marge 6 %)."""
    r = min(p[2] for ct in CARTONS for prs in ct["pots"].values() for pr in prs for p in pr)
    r_pt = r / _IMG_W * PAGE_W * 0.94
    t = 2 * r_pt / 0.717
    while t > 6:
        w = stringWidth("88", POLICE, t) / 2.0
        h = t * 0.717 / 2.0
        if w * w + h * h <= r_pt * r_pt:
            break
        t -= 0.25
    return t
# ⭐ 15/11 (Maeva : « le pt de chiffre ») : MESURÉ sur la vraie forme ovale
#    de chacune des 96 raquettes de la maquette (et non plus le cercle
#    inscrit), 2 px de marge : « 88 » tient jusqu'à 31,1 pt en Bebas Neue
#    (26,4 pt en Helvetica-Bold). NE PAS MONTER AU-DESSUS.
_T_NUM = 30.5 if POLICE == "BEBAS" else 26.0


def _taille_serie():
    x0, y0, x1, y1 = CARTONS[0]["serie"]
    t = (y1 - y0) / _IMG_H * PAGE_H / 0.729
    while t > 4 and stringWidth("000000", _POLICE_SERIE, t) > (x1 - x0 + 4) / _IMG_W * PAGE_W:
        t -= 0.25
    return t
_T_SERIE = _taille_serie()


def _numeros(rng):
    """{plage: [(petit, grand), ...]} — numéros tous différents dans le carton."""
    sortie = {}
    for k, (lo, hi) in PLAGES.items():
        n_paires = len(CARTONS[0]["pots"][k])
        tires = rng.sample(range(lo, hi + 1), 2 * n_paires)
        sortie[k] = [tuple(sorted(tires[2 * i:2 * i + 2])) for i in range(n_paires)]
    return sortie


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 1515)
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
        # en-tête (rame personnalisée) + n° de feuille, dans la marge du haut
        entete = "  ·  ".join(t for t in ((nom_evenement or "").strip(),
                                          (date_lieu or "").strip(),
                                          (telephone or "").strip()) if t)
        if entete:
            c.setFillColor(GRIS_TRAIT)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - 4.2, entete)
        c.setFillColor(colors.Color(0.6, 0.6, 0.6))
        c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 10, PAGE_H - 4.2, "%03d" % no_page)

        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ct = CARTONS[idx]
            if couleur:
                col = col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])
            else:
                col = GRIS
            # n° de série à la place de « 000001 »
            x0, y0, x1, y1 = ct["serie"]
            c.setFillColor(GRIS_TRAIT)
            c.setFont(_POLICE_SERIE, _T_SERIE)
            c.drawString(_px(x0), _py(y1), "%06d" % serie)
            # les 16 chiffres
            c.setFillColor(col)
            c.setFont(POLICE, _T_NUM)
            nums = _numeros(rng)
            for k, paires in ct["pots"].items():
                for (g, d), (a, b) in zip(paires, nums[k]):
                    for (cx, cy, _r), v in ((g, a), (d, b)):
                        c.drawCentredString(_px(cx), _py(cy) - _T_NUM * _CAP / 2.0, str(v))
            serie += 1
            faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_pingpong_go.pdf", "wb").write(generer_pdf(nb_cartes=6, couleur=False).read())
    print("PING-PONG GO genere")
