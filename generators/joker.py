# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur JOKER (format A4)

🃏 NÉ LE 10/09 (sceau Maeva) — LES DEUX BOUFFONS DE RANIHEI SISTERS & SHOP.
Un carton allongé, encadré d'un filet : « RANIHEI SISTERS & SHOP · Tél »
en tête, DEUX JOKERS qui se font face, chacun brandissant DEUX SCEPTRES à
boule, le mot « JOKER » entre eux, et un CARRÉ sous ce mot. « série … » au
pied.

RÈGLE — CINQ numéros, tous différents (sceau Maeva 10/09) :
  🎴 le CARRÉ du centre         : 1-15
  🃏 les DEUX boules du 1er joker (à gauche)  : 16-30
  🃏 les DEUX boules du 2e joker (à droite)   : 60-75
⚠️⚠️ IL Y A UN TROU DANS LE SAC : rien entre 31 et 59. Sur un sac de 1 à
   75, VINGT-NEUF BOULES ne serviraient à personne — près de quatre sur
   dix. Signalé à Maeva le 10/09 ; en attendant sa décision, le crieur est
   réglé sur 1-75.
⚠️ Les deux boules d'un même joker sont tirées D'UN SEUL COUP dans leur
   plage : elles ne peuvent donc jamais porter le même chiffre. Elles sont
   rangées du plus petit à gauche au plus grand à droite.

⚠️⚠️ LA FEUILLE EST EN PAYSAGE — A4 COUCHÉ, avec SIX cartons (2 × 3),
   exactement comme la planche de Maeva.
   ⭐ C'est la feuille couchée qui fait la différence : un carton aussi
      allongé (ratio 2,33) épouse mal une page debout. Sur A4 DEBOUT les
      six cartons n'occupaient que 45 % de la hauteur et les chiffres
      plafonnaient à 14,5 pt ; SUR A4 COUCHÉ on remplit 95 % de la page et
      LES CHIFFRES MONTENT À 20,5 pt (24 pt dans le carré).
⭐ Le NUMÉRO DE SÉRIE s'écrit après le mot « série », à la place du « 001 »
   que portait le dessin. Le NUMÉRO DE PAGE est au CENTRE, en haut.
"""
import io
import os as _os2
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_jk

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

_RATIO_CARTON = 2.3256

# ═══ 🃏 LES CINQ EMPLACEMENTS ═══ (fractions du carton, repère bas-gauche)
#     (x, y, n° de plage)  ·  0 = le carré · 1 = joker de gauche · 2 = joker de droite
PLACES = [
    (0.0732, 0.7010, 1),   # 1er joker, boule de GAUCHE
    (0.3889, 0.6844, 1),   # 1er joker, boule de DROITE
    (0.4825, 0.2666, 0),   # LE CARRÉ, sous le mot « JOKER »
    (0.5768, 0.6836, 2),   # 2e joker, boule de GAUCHE
    (0.9236, 0.7018, 2),   # 2e joker, boule de DROITE
]
LARG_BOULE = 0.0764   # la plus petite des quatre boules
HAUT_BOULE = 0.1794
LARG_CARRE = 0.1079
HAUT_CARRE = 0.2243

# 🃏 la plage de chacun — sceau Maeva 10/09
PLAGES = [(1, 15), (16, 30), (60, 75)]

# ⭐ la place du numéro de série, après le mot « série »
SERIE_X = 0.5168
SERIE_Y = 0.0590
SERIE_LARG = 0.060


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


_IMAGE_CARTON = _choisir_image("joker_carton", _RATIO_CARTON)

PAGE_W, PAGE_H = landscape(A4)
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
    """🃏 Cinq numéros, tous différents.

    Les DEUX boules d'un même joker partagent une plage : on les tire d'un
    seul coup pour qu'elles ne portent jamais le même chiffre, et on range
    la plus petite à gauche.
    """
    valeurs = [None] * len(PLACES)
    par_plage = {}
    for i, (x, y, pl) in enumerate(PLACES):
        par_plage.setdefault(pl, []).append(i)
    for pl, postes in par_plage.items():
        lo, hi = PLAGES[pl]
        tirage = sorted(rng.sample(range(lo, hi + 1), len(postes)))
        # postes rangés de gauche à droite : le plus petit à gauche
        for poste, v in zip(sorted(postes, key=lambda p: PLACES[p][0]), tirage):
            valeurs[poste] = v
    return valeurs


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
    # ⚠️ le CARRÉ est plus grand que les boules : il a sa propre taille.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_b, _ht_b = _pw * LARG_BOULE, _ph * HAUT_BOULE
    _t_boule = 40.0
    while _t_boule > 6 and (_lg_jk("88", _POLICE_NUM, _t_boule) > _lg_b * 0.76
                            or _t_boule * 0.72 > _ht_b * 0.62):
        _t_boule -= 0.5
    _lg_q, _ht_q = _pw * LARG_CARRE, _ph * HAUT_CARRE
    _t_carre = 40.0
    while _t_carre > 6 and (_lg_jk("88", _POLICE_NUM, _t_carre) > _lg_q * 0.62
                            or _t_carre * 0.72 > _ht_q * 0.56):
        _t_carre -= 0.5

    for i, (fx, fy, pl) in enumerate(PLACES):
        _t = _t_carre if pl == 0 else _t_boule
        _nx = _px + fx * _pw
        _ny = _py + fy * _ph - _t * 0.34
        c.setFillColor(gris_ch)
        c.setFont(_POLICE_NUM, _t)
        c.drawCentredString(_nx, _ny, str(nums[i]))

    # ═══ LA SÉRIE, après le mot « série » ═══
    _bl = "%03d" % serie
    _tb = 11.0
    while _tb > 3.0 and _lg_jk(_bl, "Helvetica-Bold", _tb) > _pw * SERIE_LARG:
        _tb -= 0.25
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + SERIE_X * _pw, _py + SERIE_Y * _ph, _bl)


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)
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
