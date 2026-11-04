# -*- coding: utf-8 -*-
"""MANAPRINT — WOW 6, nouvelle maquette fournie par Maeva (04/11).
16 cartons / feuille A4 PAYSAGE (grille 4 colonnes x 4 rangees).
Chaque carton : en-tete « W O W 6 » + une grille de 6 cases (2 rangees x
3 colonnes). UN numero par case, 6 numeros UNIQUES tires de 30 a 59
(les plages du jeu WOW 6). Crieur 30 a 59.
La maquette (carton complet) est reprise TELLE QUELLE comme image de fond,
repetee 16 fois ; on ajoute seulement les chiffres et la serie."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = landscape(A4)          # 841.9 x 595.3
CARTES_PAGE = 16
POLICE = "Helvetica-Bold"
GRIS = colors.Color(0.42, 0.42, 0.42)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

PLAGE = (30, 59)                         # les boules du WOW 6

# carton-modele (358 x 236). 6 cases : (x, y, largeur_px, hauteur_px)
_IMG_W, _IMG_H = 358.0, 236.0
_CELL_W, _CELL_H = 113.0, 87.0
_CASES = [
    (63, 95), (177, 95), (291, 95),      # rangee haute : gauche, milieu, droite
    (63, 182), (177, 182), (291, 182),   # rangee basse : gauche, milieu, droite
]


def _taille_max(scale):
    """Plus grande taille (pt) pour que « 88 » tienne dans une case."""
    wpt, hpt = _CELL_W * scale, _CELL_H * scale
    t = hpt * 0.80 / 0.717
    while t > 6 and stringWidth("88", POLICE, t) > wpt * 0.80:
        t -= 0.5
    return t


# grille 4 x 4, bloc centre
_MARGE = 14
_GAP_X = 8
_GAP_Y = 6
_avail_w = PAGE_W - 2 * _MARGE
_avail_h = PAGE_H - 2 * _MARGE
_cw_w = (_avail_w - 3 * _GAP_X) / 4.0
_ch_w = _cw_w * (_IMG_H / _IMG_W)
if 4 * _ch_w + 3 * _GAP_Y <= _avail_h:
    _CW, _CH = _cw_w, _ch_w
else:
    _CH = (_avail_h - 3 * _GAP_Y) / 4.0
    _CW = _CH * (_IMG_W / _IMG_H)
_BLOC_W = 4 * _CW + 3 * _GAP_X
_BLOC_H = 4 * _CH + 3 * _GAP_Y
_X0 = (PAGE_W - _BLOC_W) / 2.0
_YTOP = (PAGE_H - _BLOC_H) / 2.0


def _fond():
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "wow6_carton.png")
_IMG_FOND = _fond()


def _origine(idx):
    col = idx % 4
    rang = idx // 4
    x = _X0 + col * (_CW + _GAP_X)
    y = PAGE_H - _YTOP - (rang + 1) * _CH - rang * _GAP_Y
    return x, y


def _px(x0, px):
    return x0 + px / _IMG_W * _CW


def _py(y0, py):
    return y0 + _CH * (1 - py / _IMG_H)


def _numeros(rng):
    """6 numeros UNIQUES tires de 30 a 59."""
    return rng.sample(range(PLAGE[0], PLAGE[1] + 1), 6)


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 358)
    serie = int(serie_start)
    faits = 0
    try:
        page_dep = max(1, int(page_start))
    except Exception:
        page_dep = 1

    col_imposee = None
    if couleur and couleur_perso:
        try:
            col_imposee = colors.HexColor(couleur_perso)
        except Exception:
            col_imposee = None

    _scale = _CW / _IMG_W
    _t_num = _taille_max(_scale)
    while faits < n_:
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
            c.setFillColor(col)
            c.setFont(POLICE, _t_num)
            for (px, py), num in zip(_CASES, _numeros(rng)):
                c.drawCentredString(_px(x0, px), _py(y0, py) - _t_num * 0.35, str(num))
            # serie discrete, bas du carton
            c.setFillColor(colors.Color(0.55, 0.55, 0.55))
            c.setFont("Helvetica", 5.5)
            c.drawCentredString(x0 + _CW / 2.0, y0 + 2.5, "N° %05d" % serie)
            serie += 1
            faits += 1
        if page_dep > 1 or faits > CARTES_PAGE:
            c.setFillColor(colors.Color(0.6, 0.6, 0.6))
            c.setFont("Helvetica", 6)
            nfe = page_dep + (faits - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 8, PAGE_H - 12, "%03d" % nfe)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf
