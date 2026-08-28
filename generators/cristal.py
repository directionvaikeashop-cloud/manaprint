# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur LES 7 BOULES DE CRISTAL (format A4)

🔮 NÉ LE 27/08 (sceau Maeva) — LE SEPTIÈME JEU DE RANIHEI, rien qu'à elle.
Une languette : sept boules de cristal posées sur leurs socles ouvragés,
« RANIHEI SISTERS & SHOP · 87 77 39 19 ».

RÈGLE — sept numéros, une plage par boule, de gauche à droite :
  1re boule : 1-15
  2e  boule : 16-30
  3e  boule : 31-40
  4e  boule : 76-90
  5e  boule : 41-50
  6e  boule : 51-60
  7e  boule : 61-75
⚠️ Les sept plages se suivent SANS TROU ni chevauchement : tout le sac de
   1 à 90 sert, et les sept numéros sont forcément différents.
⚠️ Le sac du crieur va de 1 à 90.

⚠️ Le dessin est une LANGUETTE (ratio 2,7119) — 16 cartes par feuille A4
   (2 colonnes × 8 rangées, sceau Maeva 27/08). Le ratio commande : on calcule
   les deux côtés ENSEMBLE et on centre dans les deux sens, sinon les boules
   s'ovalisent.
"""
import io
import os as _os2
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_cr

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

GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.62, 0.62, 0.62)


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

# ═══ 🔮 LES SEPT BOULES, de gauche à droite ═══
# (relevées sur le dessin — fractions de la carte, repère bas-gauche)
_RATIO_CRISTAL = 2.7119
BOULES = [
    [0.1141, 0.4788],
    [0.2426, 0.4778],
    [0.3707, 0.4778],
    [0.4980, 0.4788],
    [0.6254, 0.4788],
    [0.7531, 0.4788],
    [0.8801, 0.4778],
]
LARG_BOULE = 0.1156
HAUT_BOULE = 0.2966
# le chiffre descend un cheveu sous le milieu : le haut de la boule porte
# le reflet et l'étincelle du dessin
_DESCENTE = 0.0

# 🔮 une plage par boule, dans l'ordre du dessin (sceau Maeva 27/08)
PLAGES = [
    (1, 15),
    (16, 30),
    (31, 40),
    (76, 90),
    (41, 50),
    (51, 60),
    (61, 75),
]

# la mention « SÉRIE : 001 » a été effacée du dessin — le PDF écrit le vrai
# numéro exactement à sa place
_SERIE_X = 0.8854
_SERIE_Y = 0.8140
_SERIE_LARG = 0.128


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


_IMAGE_CRISTAL = _choisir_image("cristal_boules", _RATIO_CRISTAL)

PAGE_W, PAGE_H = A4
MARGIN_X = 6 * mm
MARGIN_TOP = 6 * mm
MARGIN_BOT = 6 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 2 * mm
# ⚠️ ON RESPECTE LE RATIO : les deux côtés se calculent ENSEMBLE, sinon les
# boules deviennent des œufs. On centre ensuite dans les deux sens.
COLS_PAGE = 2
ROWS_PAGE = 8
_DISPO_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
_DISPO_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_CRISTAL)
CARD_H = CARD_W / _RATIO_CRISTAL
_TOTAL_W = COLS_PAGE * CARD_W + (COLS_PAGE - 1) * GUTTER_X
_TOTAL_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_G = (PAGE_W - _TOTAL_W) / 2
MARGE_B = MARGIN_BOT + max(0, (PAGE_H - MARGIN_TOP - MARGIN_BOT - _TOTAL_H) / 2)


def _gen_carte(rng):
    """🔮 Sept numéros, un par boule.

    Les sept plages ne se chevauchent pas : un simple tirage par boule suffit,
    les sept numéros sont forcément différents.
    """
    return [rng.randint(lo, hi) for (lo, hi) in PLAGES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, telephone="",
                    style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)

    # ═══ LA LANGUETTE AUX SEPT BOULES ═══
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_CRISTAL):
        try:
            c.drawImage(_IMAGE_CRISTAL, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_b = _pw * LARG_BOULE
    _ht_b = _ph * HAUT_BOULE
    _t_num = 48.0
    while _t_num > 6 and (_lg_cr("88", _POLICE_NUM, _t_num) > _lg_b * 0.80
                          or _t_num * 0.72 > _ht_b * 0.70):
        _t_num -= 0.5

    for _k, _n in enumerate(nums[:7]):
        _bx, _by = BOULES[_k]
        _nx = _px + _bx * _pw
        _ny = _py + (_by - HAUT_BOULE * _DESCENTE) * _ph - _t_num * 0.34
        c.setFillColor(gris_ch)
        c.setFont(_POLICE_NUM, _t_num)
        c.drawCentredString(_nx, _ny, str(_n))

    # ═══ LA SÉRIE, à la place que le dessin lui réserve (en haut à droite) ═══
    c.setFillColor(colors.black)
    _tb = 12.0
    _bl = "S\u00c9RIE : %03d" % serie
    while _tb > 3.2 and _lg_cr(_bl, "Helvetica-Bold", _tb) > _pw * _SERIE_LARG:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _SERIE_X * _pw,
                        _py + _SERIE_Y * _ph - _tb * 0.34, _bl)


def generer_pdf(nb_cartes=16, serie_start=1, theme="", couleur=True,
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
