# -*- coding: utf-8 -*-
"""MANAPRINT — BRIQUET · 7 boules (création 2KEA & Associé), maquette Maeva 08/11/2026.
8 cartons / feuille A4 PORTRAIT (grille 2 colonnes x 4 rangées).
Chaque carton = « N° ______ », « BRIQUET », le briquet, la flamme, et
7 FLAMMES où l'on pose un numéro chacune.
Plages B I N G O, lues par COLONNE de gauche à droite (sceau Maeva) :
   colonne 1 : 1 flamme  (milieu gauche)            -> B  1-15
   colonne 2 : 2 flammes (haut et bas, à gauche)     -> I 16-30
   colonne 3 : 1 flamme  (centre)                    -> N 31-45
   colonne 4 : 2 flammes (haut et bas, à droite)     -> G 46-60
   colonne 5 : 1 flamme  (milieu droit)              -> O 61-75
   -> crieur 1 à 75 (BINGO complet).
Dans une colonne de 2, le plus petit numéro est en haut.
La maquette (carton complet) est reprise TELLE QUELLE comme image de fond,
répétée 8 fois ; on ajoute seulement les 7 chiffres et le numéro de série."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4
CARTES_PAGE = 8
COLS_PAGE, ROWS_PAGE = 2, 4
POLICE = "Helvetica-Bold"
GRIS = colors.Color(0.18, 0.18, 0.18)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

# le n° de série, dans le style du « N° » de la maquette (gras condensé)
try:
    pdfmetrics.registerFont(TTFont("BRQSERIE", "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"))
    _POLICE_SERIE = "BRQSERIE"
except Exception:
    _POLICE_SERIE = "Helvetica-Bold"

# carton-modèle (518 x 371 px)
_IMG_W, _IMG_H = 518.0, 371.0
# contour de chaque flamme (x0, y0, x1, y1) en px
_FL_MILIEU_G = (41, 152, 160, 262)
_FL_HAUT_G = (131, 63, 246, 172)
_FL_BAS_G = (119, 241, 233, 346)
_FL_CENTRE = (203, 152, 320, 262)
_FL_HAUT_D = (294, 64, 406, 170)
_FL_BAS_D = (287, 241, 404, 344)
_FL_MILIEU_D = (365, 153, 484, 262)
# colonnes B I N G O : (flammes de haut en bas, plage)
COLONNES = [
    ([_FL_MILIEU_G], (1, 15)),                 # B
    ([_FL_HAUT_G, _FL_BAS_G], (16, 30)),       # I
    ([_FL_CENTRE], (31, 45)),                  # N
    ([_FL_HAUT_D, _FL_BAS_D], (46, 60)),       # G
    ([_FL_MILIEU_D], (61, 75)),                # O
]
# le chiffre se pose dans le « ventre » blanc de la flamme
_VENTRE_Y = 0.64          # hauteur du centre du ventre, en part de la flamme
_VENTRE_L = 66.0          # largeur blanche utile (px) entre les reflets gris
_VENTRE_H = 41.0          # hauteur blanche utile (px)
# n° de série : à la place de « 000003 », au-dessus du soulignement
_SERIE_X, _SERIE_BASE, _SERIE_HCAP, _SERIE_XMAX = 68.0, 44.0, 26.0, 168.0

# grille 2 x 4, bloc centré (même méthode que ARCHER / MONTRE)
_MARGE = 12
_GAP_X = 8
_GAP_Y = 6
_avail_w = PAGE_W - 2 * _MARGE
_avail_h = PAGE_H - 2 * _MARGE
_cw_w = (_avail_w - _GAP_X) / 2.0
_ch_w = _cw_w * (_IMG_H / _IMG_W)
if 4 * _ch_w + 3 * _GAP_Y <= _avail_h:
    _CW, _CH = _cw_w, _ch_w
else:
    _CH = (_avail_h - 3 * _GAP_Y) / 4.0
    _CW = _CH * (_IMG_W / _IMG_H)
_BLOC_W = 2 * _CW + _GAP_X
_BLOC_H = 4 * _CH + 3 * _GAP_Y
_X0 = (PAGE_W - _BLOC_W) / 2.0
_YTOP = (PAGE_H - _BLOC_H) / 2.0
_SCALE = _CW / _IMG_W


def _fond():
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "briquet_carton.png")
_IMG_FOND = _fond()


def _origine(idx):
    col = idx % COLS_PAGE
    rang = idx // COLS_PAGE
    x = _X0 + col * (_CW + _GAP_X)
    y = PAGE_H - _YTOP - (rang + 1) * _CH - rang * _GAP_Y
    return x, y


def _px(x0, px):
    return x0 + px / _IMG_W * _CW


def _py(y0, py):
    return y0 + _CH * (1 - py / _IMG_H)


def _taille_flamme():
    """La plus grande taille où « 88 » (pire cas) tient dans le ventre blanc."""
    w = _VENTRE_L * _SCALE
    h = _VENTRE_H * _SCALE
    t = h / 0.717
    while t > 6 and stringWidth("88", POLICE, t) > w:
        t -= 0.5
    return t
_T_NUM = _taille_flamme()


def _numeros(rng):
    """[(flamme, numéro), ...] : chaque colonne tire dans sa plage, numéros
    différents, le plus petit en haut."""
    sortie = []
    for flammes, (lo, hi) in COLONNES:
        tires = sorted(rng.sample(range(lo, hi + 1), len(flammes)))
        sortie.extend(zip(flammes, tires))
    return sortie


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 811)
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

    t_serie = _SERIE_HCAP * _SCALE / 0.729
    while t_serie > 4 and stringWidth("000000", _POLICE_SERIE, t_serie) > (_SERIE_XMAX - _SERIE_X) * _SCALE:
        t_serie -= 0.25

    while faits < n_:
        # en-tête de page (rame personnalisée) + n° de feuille
        entete = "  ·  ".join(t for t in ((nom_evenement or "").strip(),
                                          (date_lieu or "").strip()) if t)
        if entete:
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - _YTOP / 2.0 - 3, entete)
        c.setFillColor(colors.Color(0.6, 0.6, 0.6))
        c.setFont("Helvetica", 6)
        c.drawRightString(PAGE_W - 14, PAGE_H - _YTOP / 2.0 - 3, "%03d" % no_page)

        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            x0, y0 = _origine(idx)
            try:
                c.drawImage(_IMG_FOND, x0, y0, _CW, _CH,
                            preserveAspectRatio=False, mask="auto")
            except Exception:
                pass
            if couleur:
                col = col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])
            else:
                col = GRIS
            # n° de série, sur le soulignement à côté de « N° »
            c.setFillColor(colors.black)
            c.setFont(_POLICE_SERIE, t_serie)
            c.drawString(_px(x0, _SERIE_X), _py(y0, _SERIE_BASE), "%06d" % serie)
            # les 7 chiffres, au centre du ventre de chaque flamme
            c.setFillColor(col)
            c.setFont(POLICE, _T_NUM)
            for (fx0, fy0, fx1, fy1), num in _numeros(rng):
                cx = _px(x0, (fx0 + fx1) / 2.0)
                cy = _py(y0, fy0 + _VENTRE_Y * (fy1 - fy0))
                c.drawCentredString(cx, cy - _T_NUM * 0.717 / 2.0, str(num))
            serie += 1
            faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_briquet.pdf", "wb").write(generer_pdf(nb_cartes=8, couleur=False).read())
    print("BRIQUET genere")
