# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur VANIRA (format A4)

🌸 NÉ LE 10/09 (sceau Maeva) — LA GOUSSE DE VANILLE DE RANIHEI.
Un carton bordé d'un filet arrondi : une fleur de vanille en haut à gauche,
le titre « VANIRA » en lettres creuses, un grand V dessiné dans lequel
SEPT BOULES descendent puis remontent, « RANIHEI SISTERS & SHOP » et le
téléphone au pied, une seconde fleur en bas à droite.

RÈGLE — sept numéros, tous différents. ON SUIT LE V, de la boule du haut à
gauche jusqu'à celle du haut à droite (sceau Maeva 10/09) :
  1 · haut GAUCHE      : 1-15
  2 · on descend       : 16-30
  3 · on descend       : 31-45
  4 · LE CREUX du V    : 84-90
  5 · on remonte       : 76-83
  6 · on remonte       : 61-75
  7 · haut DROITE      : 46-60
⚠️ VÉRIFIÉ : les sept plages se suivent SANS TROU NI CHEVAUCHEMENT — les
   quatre-vingt-dix boules du sac servent toutes. C'est net, rien à
   corriger de ce côté.
⚠️ Le sac du crieur va de 1 à 90.

⚠️ Le carton est légèrement en largeur (ratio 1,3393) — 8 par feuille A4
   (2 colonnes × 4 rangées), comme la planche dessinée par Maeva.
⭐ Le dessin ne prévoyait PAS de place pour le numéro de série : il est
   posé dans la bande blanche du pied, à droite du téléphone. Le NUMÉRO DE
   PAGE est au CENTRE, en haut de feuille.
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

_RATIO_CARTON = 1.3393

# ═══ 🌸 LES SEPT BOULES ═══ (fractions du carton, repère bas-gauche)
#     dans l'ORDRE DU V : on descend à gauche, le creux, on remonte à droite
BOULES = [
    (0.2771, 0.6557),   # 1 · haut GAUCHE
    (0.3621, 0.5089),   # 2
    (0.4371, 0.3532),   # 3
    (0.5325, 0.2115),   # 4 · LE CREUX
    (0.6279, 0.3549),   # 5
    (0.7042, 0.5128),   # 6
    (0.7887, 0.6719),   # 7 · haut DROITE
]
DIAM_BOULE = 0.1225   # la plus petite des sept
HAUT_BOULE = 0.1590

# 🌸 la plage de chaque boule, dans le même ordre — sceau Maeva 10/09
PLAGES = [
    (1, 15),     # 1 · haut gauche
    (16, 30),    # 2
    (31, 45),    # 3
    (84, 90),    # 4 · le creux
    (76, 83),    # 5
    (61, 75),    # 6
    (46, 60),    # 7 · haut droite
]

# ⭐ la place du numéro de série : la bande blanche du pied, à droite du
#    téléphone (le dessin n'en prévoyait pas)
# ⚠️ DEUX ESSAIS RATÉS avant celui-ci, notés pour ne pas les refaire :
#    • x 0,48 → le numéro tombait SUR la pointe du V, qui descend jusqu'en bas
#    • y 0,035 → il touchait le bas du « 87 77 39 19 »
#    Mesure ligne par ligne : le cadre s'arrête à y 0,007 et le téléphone
#    commence à y 0,056 ; la bande VRAIMENT libre est 0,011 → 0,051.
SERIE_X = 0.3433
SERIE_Y = 0.0180
SERIE_LARG = 0.150


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


_IMAGE_CARTON = _choisir_image("vanira_carton", _RATIO_CARTON)

PAGE_W, PAGE_H = A4
MARGIN_X = 5 * mm
MARGIN_TOP = 6 * mm
MARGIN_BOT = 5 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 3 * mm
# ⚠️ ON RESPECTE LE RATIO : les deux côtés ensemble, puis on centre.
COLS_PAGE = 2
ROWS_PAGE = 4
_DISPO_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
_DISPO_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_CARTON)
CARD_H = CARD_W / _RATIO_CARTON
_TOTAL_W = COLS_PAGE * CARD_W + (COLS_PAGE - 1) * GUTTER_X
_TOTAL_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_G = (PAGE_W - _TOTAL_W) / 2
MARGE_B = MARGIN_BOT + max(0, (PAGE_H - MARGIN_TOP - MARGIN_BOT - _TOTAL_H) / 2)


def _gen_carte(rng):
    """🌸 Sept numéros, un par boule, tous différents.

    Les sept plages ne se chevauchent pas : un simple tirage par boule
    suffit, les sept numéros sont forcément distincts.
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

    # ═══ LA SÉRIE, dans le pied, à droite du téléphone ═══
    _bl = "N\u00b0 %05d" % serie
    _tb = 6.0
    while _tb > 3.0 and _lg_vn(_bl, "Helvetica-Bold", _tb) > _pw * SERIE_LARG:
        _tb -= 0.25
    c.setFillColor(gris_ch)
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + SERIE_X * _pw, _py + SERIE_Y * _ph, _bl)


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
