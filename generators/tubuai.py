# -*- coding: utf-8 -*-
"""MANAPRINT — TUBUAI (RANIHEI SISTERS & SHOP), maquette fournie par Maeva (31/10).
8 cartons / feuille A4 PORTRAIT (grille 2 colonnes x 4 rangées).
Chaque carton : scène sous-marine (pieuvre ORAVA + requin TUAI) + 6 cercles
autour = LES PLAGES DU BINGO 90 (6 plages de 15) :
  gauche  haut->bas : 1-15 · 16-30 · 31-45
  droite  haut->bas : 46-60 · 61-75 · 76-90
  -> crieur 1 à 90 sans trou.
La maquette (carton complet, 6 cercles) est reprise TELLE QUELLE comme image de
fond, répétée 8 fois ; on ajoute seulement les chiffres dans les cercles."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

PAGE_W, PAGE_H = A4                 # portrait (595 x 842)
CARTES_PAGE = 8
POLICE = "Helvetica-Bold"
GRIS = colors.Color(0.20, 0.20, 0.20)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

# le carton-modèle (523 x 355) — les 6 cercles ne sont PAS en rangée :
#   (x, y, rayon, (plage_min, plage_max))  — centres mesurés sur la maquette.
_IMG_W, _IMG_H = 523.0, 355.0
_CERCLES = [
    (118,  94, 36, (1, 15)),     # haut-gauche
    ( 58, 152, 37, (16, 30)),    # milieu-gauche (bord)
    (146, 278, 37, (31, 45)),    # bas-gauche
    (430,  96, 36, (46, 60)),    # haut-droite
    (470, 170, 34, (61, 75)),    # milieu-droite (bord)
    (414, 280, 34, (76, 90)),    # bas-droite
]

# grille 2 x 4 : carton dimensionné pour tenir en hauteur ET largeur, bloc centré.
_MARGE = 14
_GAP_X = 10
_GAP_Y = 8
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
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "tubuai_carton.png")
_IMG_FOND = _fond()


def _origine(idx):
    col = idx % 2
    rang = idx // 2
    x = _X0 + col * (_CW + _GAP_X)
    y = PAGE_H - _YTOP - (rang + 1) * _CH - rang * _GAP_Y
    return x, y


def _numeros(rng):
    """Un numéro tiré dans chaque plage (ordre des cercles ci-dessus)."""
    return [rng.randint(a, b) for (_x, _y, _r, (a, b)) in _CERCLES]


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 631)
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
            if couleur:
                col = col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])
            else:
                col = GRIS
            c.setFillColor(col)
            nums = _numeros(rng)
            for (px, py, pr, _pl), num in zip(_CERCLES, nums):
                r_pt = pr / _IMG_W * _CW
                taille = r_pt * 1.35          # tient dans le plus petit cercle
                c.setFont(POLICE, taille)
                cx = x0 + px / _IMG_W * _CW
                cy = y0 + _CH * (1 - py / _IMG_H)
                c.drawCentredString(cx, cy - taille * 0.35, str(num))
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
