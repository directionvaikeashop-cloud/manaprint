# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur POMARE (format A4)

👑 NÉ LE 15/08 (sceau Maeva) — LE TROISIÈME JEU DE RANIHEI, rien qu'à elle.
⭐ DESSIN REFAIT PAR MAEVA LE 28/08 (version définitive) — la couronne royale
à sept pointes, un rond au bout de chacune, le bandeau laissé NU, « POMARE »
en tête, l'étoile « 7 BOULES » et, en bas à gauche, RANIHEI SISTERS & SHOP
avec UNE PASTILLE PRÊTE POUR LE NUMÉRO.
⚠️ Maeva a retiré les deux hibiscus et la gravure « H-TMH » : c'est là que
   partait l'encre (9,03 % → 6,90 % par feuille).
⚠️ La pastille est CONSERVÉE : seul le faux numéro qu'elle contenait a été
   effacé, et le PDF écrit le vrai exactement dedans.

RÈGLE (sceau Maeva 15/08, relevée sur sa maquette 12·24·37·84·41·27·7) :
sept numéros, les pointes vont PAR PAIRES, de l'extérieur vers le centre —
  1er pic, à GAUCHE et à DROITE : 1-15
  2e  pic, à GAUCHE et à DROITE : 16-30
  3e  pic, à GAUCHE et à DROITE : 31-45
  et AU MILIEU, la pointe la plus haute : 76-90
⚠️ Les deux numéros d'une même paire sont toujours DIFFÉRENTS.
⚠️ Le sac du crieur va de 1 à 90.

6 cartes par feuille A4 (2 colonnes × 3 rangées).
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

# ═══ 👑 LA COURONNE ET SES SEPT POINTES ═══
# Les ronds, de gauche à droite : 1G · 2G · 3G · MILIEU · 3D · 2D · 1D
_RATIO_COURONNE = 1.4127
RONDS = [[0.0818, 0.4490],   # 1G
         [0.1975, 0.6176],   # 2G
         [0.3600, 0.7255],   # 3G
         [0.5232, 0.8587],   # MILIEU, la pointe la plus haute
         [0.6775, 0.7245],   # 3D
         [0.8375, 0.6130],   # 2D
         [0.9232, 0.4379]]   # 1D
DIAM_ROND = 0.0893   # le plus petit des sept
HAUT_ROND = 0.1352

# 👑 les sept pointes et leur plage, dans l'ordre du dessin
POINTES = [
    ("1G", (1, 15)),
    ("2G", (16, 30)),
    ("3G", (31, 45)),
    ("MILIEU", (76, 90)),
    ("3D", (31, 45)),
    ("2D", (16, 30)),
    ("1D", (1, 15)),
]

import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_po


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


_IMAGE_COURONNE = _choisir_image("pomare_couronne", _RATIO_COURONNE)

PAGE_W, PAGE_H = A4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 2 * mm
# ⚠️⚠️ ON RESPECTE LE RATIO DU DESSIN : la largeur commande, la hauteur
# suit. Avec 95 mm de large, la carte fait 67 mm de haut — il en tient
# donc HUIT par feuille (2 colonnes × 4 rangées).
COLS_PAGE = 2
ROWS_PAGE = 4
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = CARD_W / _RATIO_COURONNE
MARGE_G = MARGIN_X
# ⚠️ le bloc des cartes est CENTRÉ en hauteur : sinon elles s'entassent
# en bas et laissent un grand vide au-dessus.
_TOTAL_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_B = MARGIN_BOT + max(0, (PAGE_H - MARGIN_TOP - MARGIN_BOT - _TOTAL_H) / 2)
GRIS_CLAIR = colors.Color(0.62, 0.62, 0.62)


def _gen_carte(rng):
    """👑 Sept numéros. Les paires gauche/droite partagent leur plage :
    on tire donc les DEUX d'un coup pour qu'ils soient différents."""
    nums = [None] * 7
    for gauche, droite in ((0, 6), (1, 5), (2, 4)):
        lo, hi = POINTES[gauche][1]
        a, b = rng.sample(range(lo, hi + 1), 2)
        nums[gauche], nums[droite] = a, b
    lo, hi = POINTES[3][1]
    nums[3] = rng.randint(lo, hi)
    return nums


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, telephone="",
                    style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)

    # ═══ LA PLAQUE À LA COURONNE ═══
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_COURONNE):
        try:
            c.drawImage(_IMAGE_COURONNE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_c = _pw * DIAM_ROND
    _ht_c = _ph * HAUT_ROND
    _t_num = 40.0
    while _t_num > 6 and (_lg_po("88", _POLICE_NUM, _t_num) > _lg_c * 0.88
                          or _t_num * 0.72 > _ht_c * 0.76):
        _t_num -= 0.5

    for _k, _n in enumerate(nums[:7]):
        _bx, _by = RONDS[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        c.setFillColor(gris_ch)
        c.setFont(_POLICE_NUM, _t_num)
        c.drawCentredString(_nx, _ny, str(_n))

    # ═══ LA SÉRIE, dans sa boîte au pied ═══
    c.setFillColor(gris_ch)
    _tb = 10.0
    _bl = "N\u00b0 %06d" % serie
    while _tb > 3.4 and _lg_po(_bl, "Helvetica-Bold", _tb) > _pw * 0.205:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.2438, _py + _ph * 0.0589 - _tb * 0.34, _bl)


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
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
