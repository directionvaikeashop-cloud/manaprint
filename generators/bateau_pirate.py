# -*- coding: utf-8 -*-
"""MANAPRINT — BATEAU PIRATE (RANIHEI SISTERS & SHOP), maquette bateau pirate.
8 cartons/feuille (grille 4 colonnes x 2 lignes). 5 bulles par bateau.
Règle (sceau Maeva 26/10) : 5 plages de 15, posées dans le SENS HORAIRE
  en partant de la bulle HAUT-GAUCHE :
    haut-gauche  1-15
    haut-droite  16-30
    milieu-droite 31-45
    bas-centre   46-60
    milieu-gauche 61-75
Maquette reprise telle quelle ; on ajoute seulement les chiffres et la série."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4[1], A4[0]        # paysage
CARTES_PAGE = 8
POLICE = "Helvetica-Bold"
GRIS = colors.Color(0.38, 0.38, 0.38)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

# La maquette EST déjà une planche de 8 cartons (4 x 2).
_IMG_W, _IMG_H = 1491, 1055
_COLS, _ROWS = 4, 2
_CW, _CH = _IMG_W / _COLS, _IMG_H / _ROWS

# ⚠️ 26/10 : les 8 bateaux de la maquette ne sont PAS parfaitement identiques
#    (dessin AI). On utilise donc le centre MESURÉ de CHAQUE bulle sur CHAQUE
#    carton (centroïde du disque blanc) -> les chiffres tombent pile au centre.
# Ordre horaire des 5 bulles : haut-gauche, haut-droite, milieu-droite,
#    bas-centre, milieu-gauche. Coordonnées en pixels de la maquette.
_BULLES = [
    [(141, 190), (260, 190), (330, 296), (188, 433), (61, 296)],
    [(514, 190), (632, 190), (702, 296), (561, 433), (435, 296)],
    [(887, 190), (1006, 190), (1077, 296), (934, 433), (807, 296)],
    [(1259, 190), (1377, 190), (1437, 296), (1303, 433), (1180, 296)],
    [(141, 718), (260, 718), (330, 824), (188, 961), (61, 824)],
    [(514, 718), (632, 718), (702, 824), (560, 961), (435, 824)],
    [(887, 718), (1006, 718), (1077, 824), (934, 961), (807, 824)],
    [(1259, 718), (1377, 718), (1437, 824), (1303, 961), (1180, 824)],
]
_RB_PX = 36.0   # plus petit rayon mesuré -> taille uniforme qui tient partout
# plage de chaque bulle, dans le même ordre horaire
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
# série : coin bas-gauche du carton (sur l'eau, peu d'encre), calé sur la grille
_POS_SER = (0.13, 0.955)
_SER = []
for _r in range(_ROWS):
    for _c in range(_COLS):
        _SER.append((_c * _CW + _POS_SER[0] * _CW, _r * _CH + _POS_SER[1] * _CH))

MARGE = 4.5 * mm
_AVW = PAGE_W - 2 * MARGE
_AVH = PAGE_H - 2 * MARGE
def _x(px): return MARGE + px / _IMG_W * _AVW
def _y(py): return (PAGE_H - MARGE) - py / _IMG_H * _AVH

def _fond():
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "bateau_pirate_fond.png")
_IMG_FOND = _fond()

# ⚠️ 26/10 (sceau Maeva : « tous les chiffres ont le même pt ») : une SEULE
#    taille pour les 5 chiffres = celle qui tient dans la PLUS PETITE bulle.
def _taille(rb_px):
    rb_pt = rb_px / _IMG_W * _AVW
    t = 40.0
    while t > 8:
        w = stringWidth("88", POLICE, t); h = t * 0.70
        if ((w / 2) ** 2 + (h / 2) ** 2) ** 0.5 <= rb_pt * 0.98:
            break
        t -= 0.5
    return t
_T = _taille(_RB_PX)   # taille uniforme (tient dans la plus petite bulle)

def _gen_carton(rng):
    """Un numéro par plage, dans l'ordre horaire des 5 bulles."""
    return [rng.randint(a, b) for (a, b) in PLAGES]

def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 709)
    serie = int(serie_start); faites = 0
    try: page_dep = max(1, int(page_start))
    except Exception: page_dep = 1
    while faites < n_:
        try: c.drawImage(_IMG_FOND, MARGE, MARGE, _AVW, _AVH, preserveAspectRatio=False, mask="auto")
        except Exception: pass
        for k in range(CARTES_PAGE):
            if faites >= n_: break
            vals = _gen_carton(rng)
            col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else GRIS
            c.setFillColor(col); c.setFont(POLICE, _T)
            for (px, py), v in zip(_BULLES[k], vals):
                c.drawCentredString(_x(px), _y(py) - _T * 0.36, str(v))
            # série discrète, coin bas-gauche (petit cartouche blanc pour la lisibilité)
            sx, sy = _SER[k]
            c.setFillColor(colors.white)
            c.rect(_x(sx) - 15, _y(sy) - 6, 30, 13, fill=1, stroke=0)
            c.setFillColor(colors.Color(0.30, 0.30, 0.30)); c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(_x(sx), _y(sy) - 9 * 0.34, "%03d" % serie)
            serie += 1; faites += 1
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont("Helvetica", 6)
            nfe = page_dep + (faites - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 7 * mm, "%03d" % nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
