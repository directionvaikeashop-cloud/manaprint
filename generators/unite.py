# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur UNITÉ (format A4)

💗 NÉ LE 15/08 (sceau Maeva) — LE QUATRIÈME JEU DE RANIHEI, rien qu'à elle.
Cinq cœurs entourés de rameaux, disposés en V.

RÈGLE (sceau Maeva 15/08, relevée sur sa maquette 12·24·38·55·69) :
cinq numéros, un par cœur —
  1 · cœur en HAUT à GAUCHE   : 1-15
  2 · cœur en HAUT à DROITE   : 16-25
  3 · cœur au MILIEU à GAUCHE : 26-40
  4 · cœur au MILIEU à DROITE : 41-60
  5 · cœur au CENTRE, en bas  : 61-75
⚠️ Les cinq plages ne se chevauchent pas : les numéros sont donc
toujours différents.
⚠️ Le sac du crieur va de 1 à 75.

8 cartes par feuille A4 (2 colonnes × 4 rangées).
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgn
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgv
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les cartons sortent normalement, simplement sans microtexte.
try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None


try:
    pdfmetrics.registerFont(TTFont("DJL", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    POLICE = "DJL"
except Exception:
    POLICE = "Helvetica"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)


# ══ DEUX GAMMES COMMERCIALES (vision Maeva) ══════════════════════════
# ÉCO      : écriture fine DejaVu ExtraLight, gris 0,50 — économie de toner
# PREMIUM  : écriture grasse Helvetica-Bold, gris 0,55 — style P15
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TF
try:
    _pm.registerFont(_TF("DJLECO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    _POLICE_ECO = "DJLECO"
except Exception:
    _POLICE_ECO = "Helvetica"
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)
_POLICE_P15 = "Helvetica-Bold"
_GRIS_P15 = colors.Color(0.55, 0.55, 0.55)

def _style_chiffres(style):
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4
LETTRES = "ING"
# (min, max, nombre) par lettre — le N saute sa case centrale
COLONNES = [(16, 30, 3), (31, 45, 2), (46, 60, 3)]

# ═══ 💗 LES CINQ CŒURS ═══
# Rangés : haut-gauche · haut-droite · milieu-gauche · milieu-droite · centre
_RATIO_UNITE = 1.5
COEURS = [[0.1662, 0.8123], [0.8409, 0.8125], [0.3289, 0.5195], [0.6756, 0.5201], [0.5015, 0.2491]]
LARG_COEUR = 0.2092
HAUT_COEUR = 0.2918

# 💗 les cinq cœurs et leur plage, dans l'ordre du dessin
PLAGES = [
    ("haut-gauche", (1, 15)),
    ("haut-droite", (16, 25)),
    ("milieu-gauche", (26, 40)),
    ("milieu-droite", (41, 60)),
    ("centre", (61, 75)),
]

import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_un


def _choisir_image(motif_img, ratio_attendu):
    """Retrouve le dessin, quel que soit son nom de fichier."""
    dossier = _os2.path.dirname(_os2.path.abspath(__file__))
    exact = _os2.path.join(dossier, motif_img + ".png")
    candidats = []
    try:
        for f in _os2.listdir(dossier):
            if motif_img in f and f.lower().endswith(".png"):
                candidats.append(_os2.path.join(dossier, f))
    except Exception:
        return exact
    if not candidats:
        return exact
    meilleur, ecart = candidats[0], 9e9
    for chemin in candidats:
        try:
            from PIL import Image as _Im
            with _Im.open(chemin) as im:
                e = abs(im.width / float(im.height) - ratio_attendu)
        except Exception:
            continue
        if e < ecart:
            meilleur, ecart = chemin, e
    return meilleur


_IMAGE_UNITE = _choisir_image("unite_coeurs", _RATIO_UNITE)

PAGE_W, PAGE_H = A4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm
# ⚠️ ON RESPECTE LE RATIO DU DESSIN : la largeur commande, la hauteur suit.
COLS_PAGE = 2
ROWS_PAGE = 4
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = CARD_W / _RATIO_UNITE
MARGE_G = MARGIN_X
# ⚠️ le bloc est CENTRÉ en hauteur, sinon les cartes s'entassent en bas.
_TOTAL_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_B = MARGIN_BOT + max(0, (PAGE_H - MARGIN_TOP - MARGIN_BOT - _TOTAL_H) / 2)
GRIS_CLAIR = colors.Color(0.62, 0.62, 0.62)


def _gen_carte(rng):
    """💗 Cinq numéros, un par cœur, dans sa plage. Ils sont forcément
    tous différents : les cinq plages ne se chevauchent pas."""
    return [rng.randint(lo, hi) for _nom, (lo, hi) in PLAGES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, telephone="",
                    style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)

    # ═══ LA PLAQUE AUX CŒURS ═══
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_UNITE):
        try:
            c.drawImage(_IMAGE_UNITE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    # ⚠️ un CŒUR se resserre vers sa pointe : le chiffre se pose dans sa
    #    partie large, un peu au-dessus du milieu.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_c = _pw * LARG_COEUR
    _ht_c = _ph * HAUT_COEUR
    _t_num = 48.0
    while _t_num > 6 and (_lg_un("88", _POLICE_NUM, _t_num) > _lg_c * 0.66
                          or _t_num * 0.72 > _ht_c * 0.56):
        _t_num -= 0.5

    for _k, _n in enumerate(nums[:5]):
        _bx, _by = COEURS[_k]
        _nx = _px + _bx * _pw
        _ny = _py + (_by + HAUT_COEUR * 0.06) * _ph - _t_num * 0.34
        c.setFillColor(gris_ch)
        c.setFont(_POLICE_NUM, _t_num)
        c.drawCentredString(_nx, _ny, str(_n))

    # ═══ LA SÉRIE, en bas à gauche ═══
    c.setFillColor(gris_ch)
    _tb = 11.0
    _bl = "S\u00c9RIE %03d" % serie
    while _tb > 3.4 and _lg_un(_bl, "Helvetica-Bold", _tb) > _pw * 0.20:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.135, _py + _ph * 0.055, _bl)


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    rng = random.Random()
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    serie = int(serie_start)
    no_page = max(1, int(page_start))
    faites = 0
    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 5 * mm, "Page %d" % no_page)
        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGE_G + col_i * (CARD_W + GUTTER_X)
                y0 = MARGE_B + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                coul = (couleur_perso or "#000000") if couleur else "#000000"
                _dessiner_carte(c, x0, y0, _gen_carte(rng), coul, serie,
                                telephone, style, evenement_id)
                serie += 1
                faites += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf
