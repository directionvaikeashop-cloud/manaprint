# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur SPEED 90 (format A4)

⚡ NÉ LE 10/09 (sceau Maeva) — LA LANGUETTE DE RANIHEI SISTERS SHOP.
Un bandeau allongé, encadré d'un filet à l'ancienne : la boîte
« SPEED 90 — SÉRIE … » en tête, puis DOUZE CASES OCTOGONALES rangées en
SIX COLONNES DE DEUX, avec le médaillon dentelé « RANIHEI SISTERS SHOP »
au milieu, entre la 3e et la 4e colonne.

⚠️⚠️ LA RÈGLE EST CELLE D'OHANA 90 · 12 BOULES (sceau Maeva) : seule la
   MISE EN PAGE change, le tirage est le même. DOUZE numéros, DEUX par
   famille de quinze, chaque famille dans SA colonne :
     colonne 1 : 1-15   ·   colonne 4 : 46-60
     colonne 2 : 16-30  ·   colonne 5 : 61-75
     colonne 3 : 31-45  ·   colonne 6 : 76-90
   Dans chaque colonne, le plus petit EN HAUT, le plus grand en dessous.
⚠️ Les six familles se suivent SANS TROU : tout le sac de 1 à 90 sert.
⚠️ Le sac du crieur va de 1 à 90.

⚠️⚠️ LA FEUILLE EST EN PAYSAGE — A4 COUCHÉ (sceau Maeva 10/09), avec HUIT
   languettes : 2 colonnes × 4 rangées.
   ⭐ C'est le meilleur des deux mondes, et c'est la feuille couchée qui le
      permet : une languette aussi allongée (ratio 3,08) épouse mal une page
      debout. Comparé au portrait, on gagne SUR LES DEUX TABLEAUX —
        portrait 1 × 7 : 7 languettes, chiffres à 23,5 pt
        PAYSAGE  2 × 4 : 8 languettes, CHIFFRES À 28,5 pt
      une languette de plus par feuille ET cinq points de chiffre en plus.
   ⚠️ Étapes précédentes, pour ne pas les refaire : portrait 2 × 8 donnait
      16 languettes mais seulement 19,5 pt ; portrait 1 × 7 donnait 23,5 pt
      mais 7 languettes seulement.
⭐ Le NUMÉRO DE SÉRIE s'écrit dans la boîte du titre, à la place du « 001 »
   que portait le dessin (celui-ci a été effacé, « SPEED 90 — SÉRIE » est
   gardé). Le NUMÉRO DE PAGE est au CENTRE, en haut de feuille.
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
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_sp

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les languettes sortent normalement, simplement sans microtexte.
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

_RATIO_LANGUETTE = 3.0837

# ═══ ⚡ LES DOUZE CASES ═══ (fractions de la languette, repère bas-gauche)
COLONNES = [0.1016, 0.2248, 0.3484, 0.6570, 0.7784, 0.9009]
LIGNES = [0.5870, 0.2349]          # le haut, puis le bas
LARG_CASE = 0.1098
HAUT_CASE = 0.3109

# ⚡ une famille de quinze par colonne — la règle d'OHANA 90 · 12 boules
FAMILLES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 90)]

# ⭐ la place du numéro de série, dans la boîte du titre
SERIE_X = 0.3460
SERIE_Y = 0.8167
SERIE_LARG = 0.071


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


_IMAGE_LANGUETTE = _choisir_image("speed90_languette", _RATIO_LANGUETTE)

PAGE_W, PAGE_H = landscape(A4)
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
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_LANGUETTE)
CARD_H = CARD_W / _RATIO_LANGUETTE
_TOTAL_W = COLS_PAGE * CARD_W + (COLS_PAGE - 1) * GUTTER_X
_TOTAL_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_G = (PAGE_W - _TOTAL_W) / 2
MARGE_B = MARGIN_BOT + max(0, (PAGE_H - MARGIN_TOP - MARGIN_BOT - _TOTAL_H) / 2)


def _gen_carte(rng):
    """⚡ Douze numéros : DEUX par famille de quinze, triés.

    C'est exactement le tirage d'OHANA 90 · 12 boules. On rend une liste de
    six paires, une par colonne, chacune rangée du plus petit au plus grand.
    """
    return [sorted(rng.sample(range(lo, hi + 1), 2)) for (lo, hi) in FAMILLES]


def _dessiner_languette(c, x0, y0, paires, serie, style="eco"):
    police_ch, gris_ch = _style_chiffres(style)
    _pw = CARD_W - 0.4 * mm
    _ph = CARD_H - 0.4 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.2 * mm
    if _os2.path.exists(_IMAGE_LANGUETTE):
        try:
            c.drawImage(_IMAGE_LANGUETTE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_c = _pw * LARG_CASE
    _ht_c = _ph * HAUT_CASE
    _t_num = 40.0
    while _t_num > 6 and (_lg_sp("88", _POLICE_NUM, _t_num) > _lg_c * 0.72
                          or _t_num * 0.72 > _ht_c * 0.60):
        _t_num -= 0.5

    for ic, paire in enumerate(paires):
        for il, valeur in enumerate(paire):      # 0 = en haut, 1 = en bas
            _nx = _px + COLONNES[ic] * _pw
            _ny = _py + LIGNES[il] * _ph - _t_num * 0.34
            c.setFillColor(gris_ch)
            c.setFont(_POLICE_NUM, _t_num)
            c.drawCentredString(_nx, _ny, str(valeur))

    # ═══ LA SÉRIE, dans la boîte du titre ═══
    _bl = "%03d" % serie
    _tb = 11.0
    while _tb > 3.0 and _lg_sp(_bl, "Helvetica-Bold", _tb) > _pw * SERIE_LARG:
        _tb -= 0.25
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", _tb)
    # ⚠️ SERIE_Y est déjà la LIGNE DE BASE du texte du dessin : on ne
    #    retranche donc rien, sinon le numéro descend sous la boîte.
    c.drawCentredString(_px + SERIE_X * _pw, _py + SERIE_Y * _ph, _bl)


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
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
                _dessiner_languette(c, x0, y0, _gen_carte(rng), serie, style)
                serie += 1
                faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf
