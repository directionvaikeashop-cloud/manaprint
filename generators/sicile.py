# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur SICILE (format A4)

👑 NÉ LE 02/09 (sceau Maeva) — LA COURONNE À CINQ PIERRES.
Un diadème à cinq pointes, chacune sertie d'un ovale, le bandeau perlé et son
médaillon au centre, « SICILE · 5 BOULES » en tête, « TUKEA · 89 22 23 05 »
au pied. Le dessin est de Maeva, tout en contours.

RÈGLE — cinq numéros, une plage par ovale, de gauche à droite :
  ovale 1 (gauche)        : 1-15
  ovale 2                 : 16-30
  ovale 3 (le plus haut)  : 31-45
  ovale 4                 : 46-60
  ovale 5 (droite)        : 61-75
⚠️ Les cinq plages se suivent SANS TROU ni chevauchement : tout le sac de
   1 à 75 sert, et les cinq numéros sont forcément différents.
⚠️ Le sac du crieur va de 1 à 75.

⚠️ Le dessin est en PAYSAGE (ratio 1,4141) — 8 cartes par feuille A4 (2×4).
   Le ratio commande : on calcule les deux côtés ENSEMBLE et on centre dans
   les deux sens, sinon la couronne s'aplatit.
⚠️ Les ovales ne sont PAS tous de la même taille : celui du centre est le
   plus grand, ceux des bords les plus petits. LARG_OVALE retient le PLUS
   PETIT — le chiffre tient alors dans les cinq sans jamais déborder.
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
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_si

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

# ═══ 👑 LES CINQ OVALES, de gauche à droite ═══
# (relevés sur le dessin recadré — fractions de la carte, repère bas-gauche)
_RATIO_SICILE = 1.4141
OVALES = [
    [0.1664, 0.3641],   # 1 · pointe de GAUCHE
    [0.3254, 0.4500],   # 2
    [0.4993, 0.5152],   # 3 · la pointe du MILIEU, la plus haute
    [0.6711, 0.4505],   # 4
    [0.8293, 0.3641],   # 5 · pointe de DROITE
]
LARG_OVALE = 0.0986   # le plus petit des cinq (ceux des bords)
HAUT_OVALE = 0.1949

# 👑 une plage par ovale, dans l'ordre du dessin (sceau Maeva 02/09)
PLAGES = [
    (1, 15),
    (16, 30),
    (31, 45),
    (46, 60),
    (61, 75),
]

# la bande blanche du bas, à gauche de la signature TUKEA
_SERIE_X = 0.1014
_SERIE_Y = 0.0828
_SERIE_LARG = 0.143


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


_IMAGE_SICILE = _choisir_image("sicile_couronne", _RATIO_SICILE)

PAGE_W, PAGE_H = A4
MARGIN_X = 6 * mm
MARGIN_TOP = 6 * mm
MARGIN_BOT = 6 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 2 * mm
# ⚠️ ON RESPECTE LE RATIO : les deux côtés se calculent ENSEMBLE, sinon la
# couronne s'aplatit. Le bloc est centré dans les DEUX sens.
COLS_PAGE = 2
ROWS_PAGE = 4
_DISPO_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
_DISPO_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_SICILE)
CARD_H = CARD_W / _RATIO_SICILE
_TOTAL_W = COLS_PAGE * CARD_W + (COLS_PAGE - 1) * GUTTER_X
_TOTAL_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_G = (PAGE_W - _TOTAL_W) / 2
MARGE_B = MARGIN_BOT + max(0, (PAGE_H - MARGIN_TOP - MARGIN_BOT - _TOTAL_H) / 2)


def _gen_carte(rng):
    """👑 Cinq numéros, un par ovale.

    Les cinq plages ne se chevauchent pas : un simple tirage par ovale suffit,
    les cinq numéros sont forcément différents.
    """
    return [rng.randint(lo, hi) for (lo, hi) in PLAGES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, telephone="",
                    style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)

    # ═══ LA COURONNE AUX CINQ PIERRES ═══
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_SICILE):
        try:
            c.drawImage(_IMAGE_SICILE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_o = _pw * LARG_OVALE
    _ht_o = _ph * HAUT_OVALE
    _t_num = 48.0
    while _t_num > 6 and (_lg_si("88", _POLICE_NUM, _t_num) > _lg_o * 0.86
                          or _t_num * 0.72 > _ht_o * 0.74):
        _t_num -= 0.5

    for _k, _n in enumerate(nums[:5]):
        _ox, _oy = OVALES[_k]
        _nx = _px + _ox * _pw
        _ny = _py + _oy * _ph - _t_num * 0.34
        c.setFillColor(gris_ch)
        c.setFont(_POLICE_NUM, _t_num)
        c.drawCentredString(_nx, _ny, str(_n))

    # ═══ LA SÉRIE, discrète en bas à gauche ═══
    c.setFillColor(gris_ch)
    _tb = 8.0
    _bl = "N\u00b0 %05d" % serie
    while _tb > 3.2 and _lg_si(_bl, "Helvetica-Bold", _tb) > _pw * _SERIE_LARG:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _SERIE_X * _pw,
                        _py + _SERIE_Y * _ph - _tb * 0.34, _bl)


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
