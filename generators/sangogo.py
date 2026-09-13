# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur SANGOGO (format A4)

⚡ NÉ LE 10/09 (sceau Maeva) — LE COMBATTANT DE RANIHEI.
Un carton carré au cadre ouvragé : le titre « SANGOGO » en lettres de
combat, « RANIHEI SISTERS & SHOP » et le téléphone en tête, « LA FORCE DU
JEU ! » à droite, un guerrier debout en posture de puissance, CINQ BOULES
étoilées disposées autour de lui, « SERIE : … » et cinq étoiles au pied.

RÈGLE — cinq numéros, tous différents (sceau Maeva 10/09) :
  1 · boule du HAUT à GAUCHE   : 1-15
  2 · boule du HAUT à DROITE   : 16-30
  3 · boule du MILIEU          : 31-45
  4 · boule du BAS à GAUCHE    : 46-60
  5 · boule du BAS à DROITE    : 61-75
⚠️ VÉRIFIÉ : les cinq plages se suivent SANS TROU NI CHEVAUCHEMENT — les
   soixante-quinze boules du sac servent toutes.
⚠️ Le sac du crieur va de 1 à 75.

⚠️⚠️ SUR L'ORIGINE DU DESSIN : une première version reprenait Son Goku,
   personnage de Toei Animation — impossible à imprimer commercialement
   sans licence. Maeva a refait un personnage à elle (bandeau à triangle,
   symbole « S », tenue à motifs, baskets) et changé le nom. C'est CETTE
   version qui est posée ici. Ne jamais revenir au dessin d'origine.

⚠️ Le carton est presque carré (ratio 1,0490) — 6 par feuille A4 (2 × 3),
   comme la planche dessinée par Maeva.
⭐ Le NUMÉRO DE SÉRIE s'écrit après « SERIE : », à la place du « 001 » du
   dessin. Le NUMÉRO DE PAGE est au CENTRE, en haut de feuille.
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
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_vn

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

_RATIO_CARTON = 1.0490

# ═══ 🌸 LES SEPT BOULES ═══ (fractions du carton, repère bas-gauche)
#     dans l'ORDRE DU V : on descend à gauche, le creux, on remonte à droite
BOULES = [
    (0.1821, 0.5608),   # 1 · HAUT à GAUCHE
    (0.8200, 0.5210),   # 2 · HAUT à DROITE
    (0.4800, 0.3051),   # 3 · le MILIEU
    (0.1800, 0.2906),   # 4 · BAS à GAUCHE
    (0.8183, 0.2714),   # 5 · BAS à DROITE
]
DIAM_BOULE = 0.2083   # la plus petite des cinq
HAUT_BOULE = 0.2150

# 🌸 la plage de chaque boule, dans le même ordre — sceau Maeva 10/09
PLAGES = [
    (1, 15),     # 1 · haut à gauche
    (16, 30),    # 2 · haut à droite
    (31, 45),    # 3 · le milieu
    (46, 60),    # 4 · bas à gauche
    (61, 75),    # 5 · bas à droite
]

# ⭐ la place du numéro de série : la bande blanche du pied, à droite du
#    téléphone (le dessin n'en prévoyait pas)
# ⭐ à la place du « 001 » du dessin, juste après « SERIE : »
SERIE_X = 0.1846
SERIE_Y = 0.0645
SERIE_LARG = 0.075


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


_IMAGE_CARTON = _choisir_image("sangogo_carton", _RATIO_CARTON)

PAGE_W, PAGE_H = A4
MARGIN_X = 5 * mm
MARGIN_TOP = 6 * mm
MARGIN_BOT = 5 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 3 * mm
# ⚠️ ON RESPECTE LE RATIO : les deux côtés ensemble, puis on centre.
COLS_PAGE = 2
ROWS_PAGE = 3
_DISPO_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
_DISPO_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_CARTON)
CARD_H = CARD_W / _RATIO_CARTON
_TOTAL_W = COLS_PAGE * CARD_W + (COLS_PAGE - 1) * GUTTER_X
_TOTAL_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_G = (PAGE_W - _TOTAL_W) / 2
MARGE_B = MARGIN_BOT + max(0, (PAGE_H - MARGIN_TOP - MARGIN_BOT - _TOTAL_H) / 2)


def _gen_carte(rng):
    """⚡ Cinq numéros, un par boule, tous différents.

    Les cinq plages ne se chevauchent pas : un simple tirage par boule
    suffit, les cinq numéros sont forcément distincts.
    """
    return [rng.randint(lo, hi) for (lo, hi) in PLAGES]


def _dessiner_carton(c, x0, y0, nums, serie, style="eco"):
    police_ch, gris_ch = _style_chiffres(style)
    _pw = CARD_W - 0.4 * mm
    _ph = CARD_H - 0.4 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.2 * mm
    if _os2.path.exists(_IMAGE_CARTON):
        try:
            c.drawImage(_IMAGE_CARTON, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_b = _pw * DIAM_BOULE
    _ht_b = _ph * HAUT_BOULE
    _t_num = 40.0
    while _t_num > 6 and (_lg_vn("88", _POLICE_NUM, _t_num) > _lg_b * 0.78
                          or _t_num * 0.72 > _ht_b * 0.62):
        _t_num -= 0.5

    for i, (fx, fy) in enumerate(BOULES):
        _nx = _px + fx * _pw
        _ny = _py + fy * _ph - _t_num * 0.34
        c.setFillColor(gris_ch)
        c.setFont(_POLICE_NUM, _t_num)
        c.drawCentredString(_nx, _ny, str(nums[i]))

    # ═══ LA SÉRIE, après « SERIE : » au pied du carton ═══
    _bl = "%03d" % serie
    _tb = 10.0
    while _tb > 3.0 and _lg_vn(_bl, "Helvetica-Bold", _tb) > _pw * SERIE_LARG:
        _tb -= 0.25
    c.setFillColor(gris_ch)
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + SERIE_X * _pw, _py + SERIE_Y * _ph, _bl)


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
    faits = 0
    for _ in range(nb_pages):
        # ⭐ le numéro de page AU CENTRE, en haut (règle Maeva 03/09)
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 8)
            c.drawString(MARGIN_X, PAGE_H - 4.5 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 4.5 * mm, "Page %d" % no_page)
        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faits >= nb_cartes:
                    break
                x0 = MARGE_G + col_i * (CARD_W + GUTTER_X)
                y0 = MARGE_B + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                _dessiner_carton(c, x0, y0, _gen_carte(rng), serie, style)
                serie += 1
                faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf
