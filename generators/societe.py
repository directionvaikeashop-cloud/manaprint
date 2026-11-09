# -*- coding: utf-8 -*-
"""MANAPRINT — SOCIÉTÉ 7 boules · NOUVELLE MAQUETTE fournie par Maeva (08/11/2026).
8 cartons / feuille A4 PORTRAIT (grille 2 colonnes x 4 rangées).
Chaque carton = « SOCIÉTÉ – 2KEA & Associé – Papeete », la pastille
« Carte N° », la carte des îles (Bora Bora, Moorea, Tahaa, Huahine, Raiatea,
Tahiti) et 7 CASES : 3 à gauche, 3 à droite, 1 en bas au centre.
Jeu inchangé : 7 numéros tirés de 1 à 75, rangés du plus petit au plus grand
(la gauche de haut en bas, puis la case du bas, puis la droite de haut en bas).
La maquette (carton complet) est reprise TELLE QUELLE comme image de fond,
répétée 8 fois ; on ajoute seulement les 7 chiffres et le numéro de carte."""
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
NB_NUMS = 7
PLAGE = (1, 75)
POLICE = "Helvetica-Bold"
GRIS = colors.Color(0.18, 0.18, 0.18)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

# le n° de carte, dans le style de la pastille (gras italique)
try:
    pdfmetrics.registerFont(TTFont("SOCSERIE", "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"))
    _POLICE_SERIE = "SOCSERIE"
except Exception:
    _POLICE_SERIE = "Helvetica-BoldOblique"

# carton-modèle (519 x 350 px)
_IMG_W, _IMG_H = 519.0, 350.0
# les 7 cases : (x0, y0, x1, y1) en px, dans l'ORDRE de lecture
_CASES = [
    (22, 75, 127, 145),    # gauche haut
    (23, 156, 128, 229),   # gauche milieu
    (23, 241, 128, 315),   # gauche bas
    (194, 257, 322, 328),  # bas centre
    (391, 75, 496, 145),   # droite haut
    (392, 156, 496, 229),  # droite milieu
    (390, 241, 496, 315),  # droite bas
]
# n° de carte : là où était « 00003 » dans la pastille
# (x gauche, ligne de base, hauteur des chiffres — en px)
_SERIE_X, _SERIE_BASE, _SERIE_HCAP = 279.0, 65.0, 16.0

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
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "societe_carton.png")
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


def _taille_case():
    """Une seule taille pour les 7 cases : la plus grande qui laisse « 88 »
    (pire cas) DANS la plus petite case, sans toucher le bord."""
    w = min(x1 - x0 for x0, y0, x1, y1 in _CASES) * _SCALE
    h = min(y1 - y0 for x0, y0, x1, y1 in _CASES) * _SCALE
    t = h * 0.70 / 0.717
    while t > 6 and stringWidth("88", POLICE, t) > w * 0.78:
        t -= 0.5
    return t
_T_NUM = _taille_case()


def _numeros(rng):
    """7 numéros DIFFÉRENTS de 1 à 75, du plus petit au plus grand."""
    return sorted(rng.sample(range(PLAGE[0], PLAGE[1] + 1), NB_NUMS))


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(940000 + int(serie_start))
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

    # taille du n° : hauteur des anciens chiffres, mais jamais plus large que
    # la place qui reste dans la pastille (bord droit à x=357 px)
    t_serie = _SERIE_HCAP * _SCALE / 0.729
    while t_serie > 4 and stringWidth("00000", _POLICE_SERIE, t_serie) > (348 - _SERIE_X) * _SCALE:
        t_serie -= 0.25
    no_page = page_dep
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
            # n° de carte dans la pastille « Carte N° »
            c.setFillColor(colors.black)
            c.setFont(_POLICE_SERIE, t_serie)
            c.drawString(_px(x0, _SERIE_X), _py(y0, _SERIE_BASE), "%05d" % serie)
            # les 7 chiffres, centrés dans leurs cases
            c.setFillColor(col)
            c.setFont(POLICE, _T_NUM)
            for (bx0, by0, bx1, by1), num in zip(_CASES, _numeros(rng)):
                cx = _px(x0, (bx0 + bx1) / 2.0)
                cy = _py(y0, (by0 + by1) / 2.0)
                c.drawCentredString(cx, cy - _T_NUM * 0.717 / 2.0, str(num))
            serie += 1
            faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_societe.pdf", "wb").write(generer_pdf(nb_cartes=8, couleur=False).read())
    print("SOCIÉTÉ genere")
