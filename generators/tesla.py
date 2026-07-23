# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TESLA — le 100e jeu (format A4)
8 billets larges/page — LA VOITURE de Maeva en grand au centre (façon
CHAPCHAP : les numéros vivent DANS la voiture) : roue gauche = 1-15,
pare-brise g. + badge de calandre = 2 triés 16-30, pare-brise d. + roue
droite = 2 triés 46-60, chacun dans une BOULE DE BINGO à double cercle
(façon VALIDER). Titre T·E·S·L·A, mention « 100e jeu ».
QR de sécurité · série · microtexte · Tèl par défaut 89 22 23 05.
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
_VOITURE_IMG = None


def _charger_voiture():
    """La voiture au trait de Maeva, pâlie une fois : les chiffres restent
    rois dans leurs médaillons. Anti-panne : boules à double cercle."""
    global _VOITURE_IMG
    if _VOITURE_IMG is not None:
        return _VOITURE_IMG
    try:
        from PIL import Image as _Image
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "tesla_voiture.png")
        brut = _Image.open(chemin)
        if brut.mode in ("RGBA", "LA", "P"):
            brut = brut.convert("RGBA")
            fondb = _Image.new("RGBA", brut.size, (255, 255, 255, 255))
            brut = _Image.alpha_composite(fondb, brut)
        img = brut.convert("L")
        img = img.point(lambda p: int(255 - (255 - p) * 0.30))
        _VOITURE_IMG = img.convert("RGB")
    except Exception:
        _VOITURE_IMG = False
    return _VOITURE_IMG


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

NB_NUMS = 5
# façon CHAPCHAP : chaque numéro habite un élément de la voiture, en
# fractions de L'IMAGE (x du bord gauche, y du HAUT de l'image) —
# chrono : roue g. -> pare-brise g. -> badge calandre -> pare-brise d. -> roue d.
POS_IMG = [(0.135, 0.84), (0.345, 0.19), (0.50, 0.53), (0.655, 0.19), (0.865, 0.84)]
IMG_W_MM = 73.0        # largeur de la voiture sur le billet
IMG_H_MAX_MM = 39.0    # plafond de hauteur (le titre vit au-dessus)
R_MM = 8.0             # boules de bingo à double cercle, façon VALIDER
TAILLE_CHIFFRE = 20


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── le titre T·E·S·L·A et la fierté du 100e jeu ──
    gris_trait = colors.Color(0.60, 0.60, 0.60)
    c.setFillColor(colors.Color(0.55, 0.55, 0.55))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H * 0.80, "T E S L A")
    c.setFont("Helvetica", 5.5)
    c.setFillColor(colors.Color(0.62, 0.62, 0.62))
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H * 0.755, "· 100e jeu ·")

    # ── la voiture de Maeva, en grand — l'image porte les numéros ──
    img = _charger_voiture()
    if img:
        from reportlab.lib.utils import ImageReader
        iw, ih = img.size
        zw = IMG_W_MM * mm
        zh = zw * ih / float(iw)
        if zh > IMG_H_MAX_MM * mm:
            zh = IMG_H_MAX_MM * mm
            zw = zh * iw / float(ih)
        ix = x0 + (CARD_W - zw) / 2
        iy = y0 + 9.5 * mm
        c.drawImage(ImageReader(img), ix, iy, zw, zh, mask=[238, 255, 238, 255, 238, 255])
    else:
        zw = IMG_W_MM * mm; zh = IMG_H_MAX_MM * mm
        ix = x0 + (CARD_W - zw) / 2
        iy = y0 + 9.5 * mm

    # en-tête : nom + signature + N° de carte
    titre = "TESLA 5 boules"
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

    # ── les 5 grands numéros en CERCLES ──
    for i, (fx, fy) in enumerate(POS_IMG[:len(nums)]):
        taille = TAILLE_CHIFFRE
        ccx = ix + zw * fx
        cy = iy + zh * (1.0 - fy)
        r = R_MM * mm
        # la boule de bingo sur l'élément de la voiture (façon VALIDER)
        c.setFillColor(colors.white); c.setStrokeColor(gris_trait); c.setLineWidth(0.7)
        c.ellipse(ccx - r, cy - r, ccx + r, cy + r, stroke=1, fill=1)
        ri = r * 0.80
        c.setLineWidth(0.45)
        c.ellipse(ccx - ri, cy + 0.7 * mm - ri, ccx + ri, cy + 0.7 * mm + ri, stroke=1, fill=0)
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


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif=""):
    telephone = (telephone or "").strip() or "89 22 23 05"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    rng = random.Random(964000 + int(serie_start))
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
                za = rng.randint(1, 15)                    # la roue gauche
                zb = sorted(rng.sample(range(16, 31), 2))  # pare-brise g. puis badge
                zc = sorted(rng.sample(range(46, 61), 2))  # pare-brise d. puis roue d.
                nums = [za, zb[0], zb[1], zc[0], zc[1]]
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
