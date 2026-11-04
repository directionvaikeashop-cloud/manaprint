# -*- coding: utf-8 -*-
"""MANAPRINT — ARCHER (RANIHEI & SISTERS), maquette fournie par Maeva (03/11).
8 cartons / feuille A4 PORTRAIT (grille 2 colonnes x 4 rangees).
Chaque carton = une scene de tir a l'arc avec 4 CIBLES alignees (la grande a
gauche, 3 plus petites a droite). Un numero au centre de chaque cible :
   cible 1 (grande, gauche) : 1-20
   cible 2                  : 21-40
   cible 3                  : 41-60
   cible 4 (petite, droite) : 61-90
   -> crieur 1 a 90.
La maquette (carton complet) est reprise TELLE QUELLE comme image de fond,
repetee 8 fois ; on ajoute seulement les chiffres, le n° de position (1-8)
et la serie."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4
CARTES_PAGE = 8
POLICE = "Helvetica-Bold"
GRIS = colors.Color(0.18, 0.18, 0.18)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

# carton-modele (523 x 386). Cibles : (x, y, rayon_blanc_px) -- centre blanc
# ou s'inscrit le chiffre.
_IMG_W, _IMG_H = 523.0, 386.0
# cibles : (x, y, rayon_blanc_px, hfac, wfac) — hfac/wfac = part du disque
# occupee par le chiffre. 03/11 : anneau epais interieur RETIRE de chaque
# cible -> centre blanc agrandi jusqu'au cercle fin exterieur ; chiffres
# nettement plus gros.
_CIBLES = [
    (104, 214, 62, 0.86, 0.94),   # grande cible gauche   -> 1-20
    (218, 218, 42, 0.86, 0.94),   # 2e cible              -> 21-40
    (306, 218, 35, 0.86, 0.94),   # 3e cible              -> 41-60
    (384, 218, 31, 0.86, 0.94),   # petite cible droite   -> 61-90
]
# 03/11 (choix Maeva) : tailles de police FIXES par cible (pt).
_PT_CIBLES = [35.0, 33.0, 30.0, 27.0]
PLAGES = [(1, 20), (21, 40), (41, 60), (61, 90)]
_BADGE = (66, 72, 37)                          # pastille n° de position (1-8)


def _taille_max(r_blanc_px, scale, hfac=0.78, wfac=0.86):
    """Plus grande taille de police (pt) pour que « 88 » (pire cas) tienne dans
    le disque blanc de rayon r_blanc_px, avec une marge pour ne pas toucher
    l'anneau de la cible."""
    d = 2 * r_blanc_px * scale                 # diametre en pt
    t = d * hfac / 0.717
    while t > 5 and stringWidth("88", POLICE, t) > d * wfac:
        t -= 0.5
    return t


# grille 2 x 4, bloc centre (meme methode que MONTRE / CARBASS)
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


def _fond():
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "archer_carton.png")
_IMG_FOND = _fond()


def _origine(idx):
    col = idx % 2
    rang = idx // 2
    x = _X0 + col * (_CW + _GAP_X)
    y = PAGE_H - _YTOP - (rang + 1) * _CH - rang * _GAP_Y
    return x, y


def _px(x0, px):
    return x0 + px / _IMG_W * _CW


def _py(y0, py):
    return y0 + _CH * (1 - py / _IMG_H)


def _numeros(rng):
    """1 numero par cible, tire dans sa plage."""
    return [rng.randint(a, b) for a, b in PLAGES]


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 523)
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
            # n° de position (1-8) dans la pastille : on efface le "1" du modele
            bx, by, br = _BADGE
            c.setFillColor(colors.white)
            c.circle(_px(x0, bx), _py(y0, by), (br - 9) / _IMG_W * _CW, stroke=0, fill=1)
            c.setFillColor(GRIS)
            tb = _taille_max(br - 11, _scale)
            c.setFont(POLICE, tb)
            c.drawCentredString(_px(x0, bx), _py(y0, by) - tb * 0.35, str(idx + 1))
            # les 4 chiffres du jeu, centres dans les cibles
            if couleur:
                col = col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])
            else:
                col = GRIS
            c.setFillColor(col)
            for (px, py, rb, hf, wf), num, t in zip(_CIBLES, _numeros(rng), _PT_CIBLES):
                s = str(num)
                c.setFont(POLICE, t)
                c.drawCentredString(_px(x0, px), _py(y0, py) - t * 0.35, s)
            # serie discrete, bas du carton
            c.setFillColor(colors.Color(0.55, 0.55, 0.55))
            c.setFont("Helvetica", 6)
            c.drawCentredString(x0 + _CW / 2.0, y0 + 3, "N° %05d" % serie)
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
