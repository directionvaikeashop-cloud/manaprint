# -*- coding: utf-8 -*-
"""MANAPRINT — MONTRE (RANIHEI SISTERS & SHOP), maquette fournie par Maeva (03/11).
8 cartons / feuille A4 PORTRAIT (grille 2 colonnes x 4 rangées).
Chaque carton = une montre digitale. 5 cases :
  HAUT (écran, 2 cases) : 2 chiffres MULTIPLES DE 5 (5,10,…,75)  -> ex. 25:75
  BAS  (2 rectangles + 1 bulle) :
     bas-gauche  : 1-12
     bas-milieu  : 13-60
     bulle droite: 61-90
  -> crieur 1 à 90.
La maquette (carton complet) est reprise TELLE QUELLE comme image de fond,
répétée 8 fois ; on ajoute les chiffres, le n° de position (1-8) et la série."""
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

# carton-modèle (528 x 372). Cases : (x, y, rayon_inscrit).
_IMG_W, _IMG_H = 528.0, 372.0
# cases : (x, y, largeur_px, hauteur_px, forme)  — forme 'r'=rectangle, 'c'=cercle
_CASES = [
    (216, 173, 111, 63, "r"),   # HAUT-gauche  (multiple de 5)
    (380, 173, 114, 62, "r"),   # HAUT-droite  (multiple de 5)
    (194, 261,  84, 61, "r"),   # BAS-gauche   (1-12)
    (314, 261,  78, 61, "r"),   # BAS-milieu   (13-60)
    (408, 261,  75, 71, "c"),   # BULLE droite (61-90)
]


def _taille_max(texte, w_px, h_px, forme, scale):
    """Plus grande taille de police (pt) pour que `texte` (pire cas 2 chiffres)
    remplisse la case, avec une petite marge. Rectangle : large marge ; cercle :
    marge plus forte pour ne pas toucher l'anneau."""
    wpt, hpt = w_px * scale, h_px * scale
    if forme == "c":
        hfac, wfac = 0.74, 0.84
    else:
        hfac, wfac = 0.82, 0.88
    # limite par la hauteur (hauteur de chiffre ~ 0.717 * taille)
    t = hpt * hfac / 0.717
    # limite par la largeur (on dimensionne pour « 88 », le plus large)
    ref = "8" * max(1, len(texte))
    while t > 6 and stringWidth(ref, POLICE, t) > wpt * wfac:
        t -= 0.5
    return t
_MULT5 = [n for n in range(5, 76, 5)]          # 5,10,…,75
_BADGE = (71, 62, 41)                          # pastille n° de position (1-8)

# grille 2 x 4, bloc centré (même méthode que CARBASS / TUBUAI)
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
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "montre_carton.png")
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
    """2 multiples de 5 distincts (haut) · 1-12 · 13-60 · 61-90."""
    h = rng.sample(_MULT5, 2)
    return [h[0], h[1], rng.randint(1, 12), rng.randint(13, 60), rng.randint(61, 90)]


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 528)
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
            # n° de position (1-8) dans la pastille : on efface le "1" du modèle
            bx, by, br = _BADGE
            c.setFillColor(colors.white)
            c.circle(_px(x0, bx), _py(y0, by), (br - 9) / _IMG_W * _CW, stroke=0, fill=1)
            c.setFillColor(GRIS)
            tb = (br * 0.9) / _IMG_W * _CW
            c.setFont(POLICE, tb)
            c.drawCentredString(_px(x0, bx), _py(y0, by) - tb * 0.35, str(idx + 1))
            # les 5 chiffres du jeu
            if couleur:
                col = col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])
            else:
                col = GRIS
            c.setFillColor(col)
            _scale = _CW / _IMG_W
            for (px, py, pw, ph, forme), num in zip(_CASES, _numeros(rng)):
                s = str(num)
                t = _taille_max(s, pw, ph, forme, _scale)
                c.setFont(POLICE, t)
                c.drawCentredString(_px(x0, px), _py(y0, py) - t * 0.35, s)
            # série discrète, bas du carton
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
