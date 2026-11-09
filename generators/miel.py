# -*- coding: utf-8 -*-
"""MANAPRINT — MIEL · 6 boules (création TUKEA / 2KEA & Associé), maquette Maeva 08/11/2026.
8 cartons / feuille A4 PORTRAIT (grille 2 colonnes x 4 rangées).
Chaque carton = « TUKEA », le 89 22 23 05, 6 POTS DE MIEL où l'on pose un
numéro chacun (+ le pot « MIEL » et les abeilles en décor).
Plages B I G O (sceau Maeva 08/11), lues par COLONNE de gauche à droite :
   colonne gauche (haut + bas)  -> B  1-15 (le plus petit en haut)
   pot milieu gauche            -> I 16-30
   pot milieu droit             -> G 46-60
   colonne droite (haut + bas)  -> O 61-75 (le plus petit en haut)
   -> crieur 1 à 75 SANS le N (31-45).
La maquette (carton complet) est reprise TELLE QUELLE comme image de fond,
répétée 8 fois ; on ajoute seulement les 6 chiffres et le numéro de série
(discret, dans le coin haut gauche resté vide)."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4
CARTES_PAGE = 8
COLS_PAGE, ROWS_PAGE = 2, 4
POLICE = "Helvetica-Bold"
NOIR = colors.Color(0.10, 0.10, 0.10)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

# carton-modèle (537 x 360 px)
_IMG_W, _IMG_H = 537.0, 360.0
# ventre blanc de chaque pot (x0, y0, x1, y1) en px
_POT_HG = (40, 77, 148, 153)
_POT_BG = (40, 260, 151, 340)
_POT_MG = (121, 155, 236, 236)
_POT_MD = (303, 156, 419, 237)
_POT_HD = (390, 76, 501, 153)
_POT_BD = (386, 259, 500, 339)
# (pots de haut en bas, plage) — dans une colonne de 2, le plus petit en haut
COLONNES = [
    ([_POT_HG, _POT_BG], (1, 15)),    # B
    ([_POT_MG], (16, 30)),            # I
    ([_POT_MD], (46, 60)),            # G
    ([_POT_HD, _POT_BD], (61, 75)),   # O
]
_VENTRE_Y = 0.54          # centre du chiffre, en part de la hauteur du ventre
# n° de série, coin haut gauche (x gauche, ligne de base) en px
_SERIE_X, _SERIE_BASE = 24.0, 36.0

# grille 2 x 4, bloc centré (même méthode que ARCHER / BRIQUET)
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
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "miel_carton.png")
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


def _taille_pot():
    """La plus grande taille où « 88 » (pire cas) tient dans le plus petit ventre."""
    pots = [p for fl, _ in COLONNES for p in fl]
    w = min(x1 - x0 for x0, y0, x1, y1 in pots) * _SCALE
    h = min(y1 - y0 for x0, y0, x1, y1 in pots) * _SCALE
    t = h * 0.64 / 0.717
    while t > 6 and stringWidth("88", POLICE, t) > w * 0.74:
        t -= 0.5
    return t
_T_NUM = _taille_pot()


def _numeros(rng):
    """[(pot, numéro), ...] : chaque colonne tire dans sa plage, numéros
    différents, le plus petit en haut."""
    sortie = []
    for pots, (lo, hi) in COLONNES:
        tires = sorted(rng.sample(range(lo, hi + 1), len(pots)))
        sortie.extend(zip(pots, tires))
    return sortie


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 6161)
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
                col = NOIR
            # n° de série discret, coin haut gauche
            c.setFillColor(colors.Color(0.45, 0.45, 0.45))
            c.setFont("Helvetica-Bold", 7)
            c.drawString(_px(x0, _SERIE_X), _py(y0, _SERIE_BASE), "N° %05d" % serie)
            # les 6 chiffres, au centre du ventre de chaque pot
            c.setFillColor(col)
            c.setFont(POLICE, _T_NUM)
            for (bx0, by0, bx1, by1), num in _numeros(rng):
                cx = _px(x0, (bx0 + bx1) / 2.0)
                cy = _py(y0, by0 + _VENTRE_Y * (by1 - by0))
                c.drawCentredString(cx, cy - _T_NUM * 0.717 / 2.0, str(num))
            serie += 1
            faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_miel.pdf", "wb").write(generer_pdf(nb_cartes=8, couleur=False).read())
    print("MIEL genere")
