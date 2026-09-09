# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TIFAI (format A4)

🐢 NÉ LE 02/09 (sceau Maeva) — SIX TORTUES SUR LE SABLE.
Un carton « CRÉATION TUKEA · 89 22 23 05 » : le titre TIFAI sous un lys,
l'étoile « 6 BOULES », et six tortues de mer alignées. Chacune porte SA
PAIRE DE LETTRES au-dessus de sa carapace, et sa carapace porte l'ovale
où viennent les DEUX chiffres, séparés par une barre À PLAT comme une
fraction : un chiffre AU-DESSUS, un chiffre AU-DESSOUS.

RÈGLE — DOUZE numéros, tous différents, DEUX par tortue (un par lettre) :
  1 · BO : B 1-15  +  O 61-75
  2 · IG : I 16-30 +  G 46-60
  3 · NB : N 31-45 +  B 1-15
  4 · GI : G 46-60 +  I 16-30
  5 · OB : O 61-75 +  B 1-15
  6 · ON : O 61-75 +  N 31-45
⚠️ TIFAI reprend la convention de HUNTER, à UNE DIFFÉRENCE PRÈS : la 6e
   n'est pas l'ÉTOILE (76-90) mais « ON ». Il n'y a donc PAS de plage
   76-90 : LE SAC DU CRIEUR VA DE 1 À 75.
⚠️ Le sac est servi tout entier — chaque tranche de quinze est tirée :
   B ×3 · I ×2 · N ×2 · G ×2 · O ×3, soit douze numéros sur soixante-quinze.
⭐ DESSIN AGRANDI PAR MAEVA LE 03/09 : les carapaces sont plus grandes et
   l'ovale passe de 0,0736 à 0,1079 de la largeur (+47 %).
⭐⭐ BARRE MISE À PLAT (idée de Maeva, 03/09) — LE VRAI GAIN EST LÀ :
   avec la barre OBLIQUE, chaque chiffre ne disposait que d'une MOITIÉ de
   largeur, d'où 13,5 pt. À PLAT, chacun prend TOUTE la largeur de l'ovale
   et n'en perd que la moitié en hauteur : on monte à 18 pt.
   ⚠️ Les barres obliques ont donc été EFFACÉES du dessin ; c'est le PDF
      qui trace lui-même le trait horizontal, entre les deux chiffres.
   ⚠️ 9 pt → 13,5 pt (ovale agrandi) → 18 pt (barre à plat) : le premier
      carton était deux fois moins lisible que celui-ci.

8 cartons par feuille A4 (2 colonnes × 4 rangées).
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

# ═══ 🎯 LE TICKET DE RANIHEI ═══
# Les six cercles, alignés de gauche à droite.
_RATIO_TICKET = 1.5301
CERCLES = [[0.0932, 0.3388],   # 1 · BO
           [0.2550, 0.3383],   # 2 · IG
           [0.4171, 0.3388],   # 3 · NB
           [0.5782, 0.3383],   # 4 · GI
           [0.7361, 0.3383],   # 5 · OB
           [0.8964, 0.3383]]   # 6 · ON
LARG_CERCLE = 0.1079   # le plus petit des six ovales de carapace
HAUT_CERCLE = 0.1945

# 🎲 LES SIX BULLES — DEUX CHIFFRES CHACUNE (sceau Maeva 15/08)
# ⚠️⚠️ Chaque lettre de la paire donne SON chiffre : « BO » = un chiffre
# du B (1-15) ET un chiffre du O (61-75). La barre oblique du dessin les
# sépare : le premier en haut-gauche, le second en bas-droite.
# ⚠️ L'ÉTOILE tire ses DEUX chiffres dans sa plage réservée 76-90.
BOULES = [
    ("BO", [(1, 15), (61, 75)]),
    ("IG", [(16, 30), (46, 60)]),
    ("NB", [(31, 45), (1, 15)]),
    ("GI", [(46, 60), (16, 30)]),
    ("OB", [(61, 75), (1, 15)]),
    ("ON", [(61, 75), (31, 45)]),
]

import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_hu


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


_IMAGE_TICKET = _choisir_image("tifai_tortues", _RATIO_TICKET)

PAGE_W, PAGE_H = A4
MARGIN_X = 6 * mm
MARGIN_TOP = 6 * mm
MARGIN_BOT = 6 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 2 * mm
# ⚠️⚠️ ON RESPECTE LE RATIO du dessin (1,5351) : les deux côtés se calculent
# ENSEMBLE et le bloc est centré dans les DEUX sens, sinon les tortues
# s'aplatissent. 8 cartons par feuille : 2 colonnes × 4 rangées.
COLS_PAGE = 2
ROWS_PAGE = 4
_DISPO_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
_DISPO_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_TICKET)
CARD_H = CARD_W / _RATIO_TICKET
_TOTAL_W = COLS_PAGE * CARD_W + (COLS_PAGE - 1) * GUTTER_X
_TOTAL_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_G = (PAGE_W - _TOTAL_W) / 2
MARGE_B = MARGIN_BOT + max(0, (PAGE_H - MARGIN_TOP - MARGIN_BOT - _TOTAL_H) / 2)
GRIS_CLAIR = colors.Color(0.62, 0.62, 0.62)


def _gen_carte(rng):
    """🎯 DOUZE numéros, tous différents : DEUX par bulle — un pour chaque
    lettre de sa paire. « BO » donne un B (1-15) puis un O (61-75)."""
    pris = set()
    bulles = []
    for _nom, plages in BOULES:
        paire = []
        for lo, hi in plages:
            libres = [v for v in range(lo, hi + 1) if v not in pris]
            n = rng.choice(libres)
            pris.add(n)
            paire.append(n)
        bulles.append(paire)
    return bulles


def _dessiner_ticket(c, x0, y0, nums, couleur_hex, serie, telephone="",
                     style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)

    # ═══ LA PLAQUE DU TICKET ═══
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_TICKET):
        try:
            c.drawImage(_IMAGE_TICKET, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    # ⚠️⚠️ DEUX chiffres par bulle : ils se placent de part et d'autre de
    # la barre oblique — le premier en HAUT-GAUCHE, le second en BAS-DROITE.
    # Chacun ne dispose donc que d'une moitié du cercle.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_c = _pw * LARG_CERCLE
    _ht_c = _ph * HAUT_CERCLE
    _t_num = 34.0
    # ⭐ BARRE À PLAT : chaque chiffre prend toute la largeur DISPONIBLE.
    # ⚠️⚠️ ATTENTION — l'ovale se RÉTRÉCIT en haut et en bas. Mesuré sur le
    # dessin : 10,46 mm au centre, mais seulement 7,83 mm à la hauteur du
    # sommet du chiffre. C'est CETTE largeur-là qui commande, pas la
    # largeur maximale : 0,80 faisait mordre les chiffres sur la carapace.
    while _t_num > 6 and (_lg_hu("88", _POLICE_NUM, _t_num) > _lg_c * 0.68
                          or _t_num * 0.72 > _ht_c * 0.34):
        _t_num -= 0.5

    for _k, _paire in enumerate(nums[:6]):
        _bx, _by = CERCLES[_k]
        _cx = _px + _bx * _pw
        _cy = _py + _by * _ph
        # ── LA BARRE À PLAT, tracée par le PDF ──
        _demi = _lg_c * 0.36
        c.setStrokeColor(gris_ch)
        c.setLineWidth(max(0.6, _t_num * 0.045))
        c.line(_cx - _demi, _cy, _cx + _demi, _cy)
        # ── un chiffre AU-DESSUS, un chiffre AU-DESSOUS ──
        _dy = _ht_c * 0.215
        for _i, _n in enumerate(_paire[:2]):
            _ny = (_cy + _dy) if _i == 0 else (_cy - _dy)
            c.setFillColor(gris_ch)
            c.setFont(_POLICE_NUM, _t_num)
            c.drawCentredString(_cx, _ny - _t_num * 0.34, str(_n))

    # ═══ LA SÉRIE, dans le pied du ticket ═══
    c.setFillColor(gris_ch)
    _tb = 9.0
    _bl = "N\u00b0 %05d" % serie
    while _tb > 3.2 and _lg_hu(_bl, "Helvetica-Bold", _tb) > _pw * 0.17:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.0879, _py + _ph * 0.1355 - _tb * 0.34, _bl)


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
                _dessiner_ticket(c, x0, y0, _gen_carte(rng), coul, serie,
                                 telephone, style, evenement_id)
                serie += 1
                faites += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf
