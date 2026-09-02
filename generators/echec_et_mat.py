# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur ÉCHEC ET MAT (format A4)

♟️ NÉ LE 15/08 (sceau Maeva) — LE SECOND JEU DE RANIHEI, rien qu'à elle.
Une languette, six pièces d'échecs, un rond sous chacune.

RÈGLE (sceau Maeva 15/08) : six numéros, TOUS DIFFÉRENTS —
  1 · ♔ le ROI      : 76-90 (la plage royale)
  2 · ♕ la DAME     : 61-75  (le O)
  3 · ♗ le FOU      : 46-60  (le G)
  4 · ♖ la TOUR     : 31-45  (le N)
  5 · ♘ le CAVALIER : 16-30  (le I)
  6 · ♙ le PION     : 1-15   (le B)
⚠️ Le sac du crieur va de 1 à 90.

⭐⭐ DESSIN REFAIT PAR MAEVA LE 28/08 (deuxième version) — tout en contours,
   RANIHEI SISTERS & SHOP et le téléphone remontés en tête, « 6 BOULES » et la
   couronne sous le titre, et surtout DES RONDS BEAUCOUP PLUS GROS :
   0,0714 → 0,1186 de la largeur. Le ratio passe de 2,6966 à 1,7094.
   Résultat : à 12 cartes par feuille les chiffres montent de 16 à 21,5 pt.

12 languettes par feuille A4 — 2 colonnes × 6 rangées (sceau Maeva 28/08 :
elle est passée de 5 à 12 cartons par feuille, chiffres à 14,5 pt).
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

# ═══ ♟️ LA LANGUETTE D'ÉCHECS ═══
# Les six ronds, sous leurs pièces, de gauche à droite.
_RATIO_TICKET = 1.7094
CERCLES = [[0.1357, 0.2179], [0.2904, 0.2179], [0.4371, 0.2179],
           [0.5761, 0.2179], [0.7186, 0.2179], [0.8636, 0.2167]]
LARG_CERCLE = 0.1186
HAUT_CERCLE = 0.2234

# ♟️ les six pièces et leur plage — une seule chacune
BOULES = [
    ("\u2654 ROI", (76, 90)),
    ("\u2655 DAME", (61, 75)),
    ("\u2657 FOU", (46, 60)),
    ("\u2656 TOUR", (31, 45)),
    ("\u2658 CAVALIER", (16, 30)),
    ("\u2659 PION", (1, 15)),
]

import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_ec


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


_IMAGE_TICKET = _choisir_image("echec_pieces", _RATIO_TICKET)

PAGE_W, PAGE_H = A4
MARGIN_X = 6 * mm
MARGIN_TOP = 6 * mm
MARGIN_BOT = 6 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 2 * mm
# ⚠️⚠️ ON RESPECTE LE RATIO DU DESSIN : les deux côtés se calculent ENSEMBLE
# et la grille est centrée dans les DEUX sens. Sinon le dessin s'aplatit.
COLS_PAGE = 2
ROWS_PAGE = 6
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
    """♟️ Six numéros, un par pièce, dans sa plage. Ils sont forcément
    tous différents : les six plages ne se chevauchent pas."""
    return [rng.randint(lo, hi) for _nom, (lo, hi) in BOULES]


def _dessiner_ticket(c, x0, y0, nums, couleur_hex, serie, telephone="",
                     style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)

    # ═══ LA PLAQUE ═══
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
    _POLICE_NUM = "Helvetica-Bold"
    _lg_c = _pw * LARG_CERCLE
    _ht_c = _ph * HAUT_CERCLE
    _t_num = 40.0
    while _t_num > 6 and (_lg_ec("88", _POLICE_NUM, _t_num) > _lg_c * 0.92
                          or _t_num * 0.72 > _ht_c * 0.80):
        _t_num -= 0.5

    for _k, _n in enumerate(nums[:6]):
        _bx, _by = CERCLES[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        c.setFillColor(gris_ch)
        c.setFont(_POLICE_NUM, _t_num)
        c.drawCentredString(_nx, _ny, str(_n))

    # ═══ LA SÉRIE, discrète au pied ═══
    c.setFillColor(gris_ch)
    _tb = 8.0
    _bl = "N\u00b0 %05d" % serie
    while _tb > 3.2 and _lg_ec(_bl, "Helvetica-Bold", _tb) > _pw * 0.13:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.8679, _py + _ph * 0.7497 - _tb * 0.34, _bl)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
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
