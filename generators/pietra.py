# -*- coding: utf-8 -*-
"""
8 billets larges/page — façon PAKIRAGI : 8 grands numéros en ELLIPSES en
couronne (colonne g. = 2 triés 1-15, centre-g = 2 triés 16-30, centre-d =
2 triés 46-60, colonne d. = 2 triés 61-75), le titre P·I·E·T·R·A au centre
et la CHÂTAIGNE DE MAEVA (bogue et feuilles, dessin au trait) en filigrane
pleine grille derrière la couronne — clin d'oeil à la bière corse à la
châtaigne, aucun élément de la marque. Châtaigne maison en secours.
"""
import io
import math
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)
PALE = colors.Color(0.86, 0.86, 0.86)
PALE2 = colors.Color(0.90, 0.90, 0.90)

try:
    pdfmetrics.registerFont(TTFont("DJLECO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    _POLICE_ECO = "DJLECO"
except Exception:
    _POLICE_ECO = "Helvetica"
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)


def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return "Helvetica-Bold", colors.Color(0.55, 0.55, 0.55)
    return _POLICE_ECO, _GRIS_ECO


import os as _os
_CHATAIGNE_IMG = None


def _charger_chataigne():
    """La châtaigne au trait de Maeva, pâlie une fois pour vivre en filigrane
    derrière la couronne. Anti-panne : châtaigne maison au centre."""
    global _CHATAIGNE_IMG
    if _CHATAIGNE_IMG is not None:
        return _CHATAIGNE_IMG or None
    try:
        from PIL import Image
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "pietra_chataigne.png")
        img = Image.open(chemin).convert("L")
        img = img.point(lambda v: int(255 - (255 - v) * 0.30))
        _CHATAIGNE_IMG = img
    except Exception:
        _CHATAIGNE_IMG = False
    return _CHATAIGNE_IMG or None


PAGE_W, PAGE_H = A4
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

NB_NUMS = 8
# le billet modèle PAKIRAGI (7/9 · 16/25 · 52/54 · 67/71) : colonne gauche =
# 2 triés 1-15 (haut/bas), centre-gauche = 2 triés 16-30 (haut/bas),
# centre-droit = 2 triés 46-60 (haut/bas), colonne droite = 2 triés 61-75
POSITIONS = [(0.12, 0.62), (0.12, 0.28), (0.375, 0.72), (0.375, 0.20),
             (0.625, 0.72), (0.625, 0.20), (0.88, 0.62), (0.88, 0.28)]
RX_MM, RY_MM = 8.5, 6.5        # les grandes ellipses du modèle
TAILLE_CHIFFRE = 28


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    gris_trait = colors.Color(0.60, 0.60, 0.60)

    # en-tête : nom + signature + N° de carte
    titre = "PIETRA 8 boules"
    if titre_jeu and titre_jeu.strip().upper() != titre.upper():
        titre += "  —  " + titre_jeu.strip()
    titre += "  by TUKEA " + (telephone or "")
    c.setFillColor(col); c.setFont(POLICE, 4.6)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 4.2 * mm, titre[:64])
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 8.4 * mm, "Carte N° %05d" % serie)

    # le téléphone en pied gauche (comme les billets du fenua)
    c.setFillColor(colors.Color(0.45, 0.45, 0.45)); c.setFont(POLICE, 4.5)
    c.drawString(x0 + 2.5 * mm, y0 + 2.2 * mm, "Tèl : " + (telephone or ""))

    # ── la châtaigne de Maeva en filigrane pleine grille (derrière tout) ──
    img = _charger_chataigne()
    if img:
        from reportlab.lib.utils import ImageReader
        iw, ih = img.size
        zw = CARD_W * 0.94
        zh = zw * ih / float(iw)
        zh = min(zh, CARD_H * 0.70)
        zw2 = zh * iw / float(ih)
        c.drawImage(ImageReader(img), x0 + (CARD_W - zw2) / 2, y0 + (CARD_H - 12 * mm - zh) / 2 + 2.5 * mm,
                    zw2, zh, mask=[238, 255, 238, 255, 238, 255])
    else:
        _chataigne_maison(c, x0 + CARD_W * 0.50, y0 + CARD_H * 0.575, gris_trait)

    # ── le titre P I E T R A au centre, sur son halo (façon PAKIRAGI) ──
    c.setFillColor(colors.white)
    c.roundRect(x0 + CARD_W * 0.50 - 15.5 * mm, y0 + CARD_H * 0.42 - 2.4 * mm,
                31 * mm, 7.6 * mm, 2.0 * mm, stroke=0, fill=1)
    c.setFillColor(colors.Color(0.55, 0.55, 0.55))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(x0 + CARD_W * 0.50, y0 + CARD_H * 0.42, " ".join("PIETRA"))

    # ── les 8 grands numéros en ELLIPSES, en couronne comme le modèle ──
    for i, (px, py) in enumerate(POSITIONS[:len(nums)]):
        taille = TAILLE_CHIFFRE
        ccx = x0 + CARD_W * px
        cy = y0 + CARD_H * py
        c.setFillColor(colors.white)
        c.setStrokeColor(gris_trait); c.setLineWidth(0.7)
        c.ellipse(ccx - RX_MM * mm, cy - RY_MM * mm, ccx + RX_MM * mm, cy + RY_MM * mm, stroke=1, fill=1)
        if _sec:
            _sec.chiffre_micro(c, nums[i], ccx, cy - taille * 0.36, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(ccx, cy - taille * 0.36, str(nums[i]))

    # QR de vérification (anti-duplication) — bas-droit
    if _sec and evenement_id:
        try:
            _q = 8.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.2 * mm, y0 + 1.8 * mm, _q, evenement_id, serie)
        except Exception:
            pass

def _chataigne_maison(c, ccx, cy, gris_trait):
    """La châtaigne redessinée au propre : le fruit galbé pointé vers le
    haut et sa base plate — secours si l'image de Maeva manque."""
    c.setStrokeColor(gris_trait)
    c.setLineWidth(0.8)
    c.setLineJoin(1)
    h = 4.5   # demi-hauteur en mm
    w = 4.2   # demi-largeur
    p = c.beginPath()
    p.moveTo(ccx - w * mm, cy - h * 0.55 * mm)
    p.curveTo(ccx - w * 1.05 * mm, cy + h * 0.35 * mm, ccx - w * 0.45 * mm, cy + h * 0.85 * mm, ccx, cy + h * mm)
    p.curveTo(ccx + w * 0.45 * mm, cy + h * 0.85 * mm, ccx + w * 1.05 * mm, cy + h * 0.35 * mm, ccx + w * mm, cy - h * 0.55 * mm)
    c.drawPath(p, stroke=1, fill=0)
    # la base plate, légèrement bombée
    p = c.beginPath()
    p.moveTo(ccx - w * mm, cy - h * 0.55 * mm)
    p.curveTo(ccx - w * 0.5 * mm, cy - h * 0.95 * mm, ccx + w * 0.5 * mm, cy - h * 0.95 * mm, ccx + w * mm, cy - h * 0.55 * mm)
    c.drawPath(p, stroke=1, fill=0)
    # la petite pointe du sommet
    c.line(ccx, cy + h * mm, ccx + 0.7 * mm, cy + (h + 1.1) * mm)


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif=""):
    telephone = (telephone or "").strip() or "89 22 23 05"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    rng = random.Random(966000 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    faites = 0
    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 9)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 7.2 * mm, "%03d" % no_page)
        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                za = sorted(rng.sample(range(1, 16), 2))   # colonne gauche, haut puis bas
                zb = sorted(rng.sample(range(16, 31), 2))  # centre-gauche, haut puis bas
                zc = sorted(rng.sample(range(46, 61), 2))  # centre-droit, haut puis bas
                zd = sorted(rng.sample(range(61, 76), 2))  # colonne droite, haut puis bas
                nums = [za[0], za[1], zb[0], zb[1], zc[0], zc[1], zd[0], zd[1]]
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, nums, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf
