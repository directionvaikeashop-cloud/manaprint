# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur OPOA (format A4)
8 billets larges/page — les lettres O·P·O·A éparpillées en vague (façon AVERA),
la MONTAGNE de Maeva en filigrane pleine grille, 7 numéros en BOULES DE
BINGO à double cercle (façon VALIDER) : 2×1-15 · 2×31-45 · 2×46-60 · 61-75.
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
_MONT_IMG = None


def _charger_montagne():
    """La montagne au trait de Maeva, pâlie une fois pour vivre en filigrane
    derrière la grille. Anti-panne : billet sans décor si l'image manque."""
    global _MONT_IMG
    if _MONT_IMG is not None:
        return _MONT_IMG
    try:
        from PIL import Image as _Image
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "opoa_montagne.png")
        brut = _Image.open(chemin)
        if brut.mode in ("RGBA", "LA", "P"):
            brut = brut.convert("RGBA")
            fondb = _Image.new("RGBA", brut.size, (255, 255, 255, 255))
            brut = _Image.alpha_composite(fondb, brut)
        img = brut.convert("L")
        img = img.point(lambda p: int(255 - (255 - p) * 0.30))
        _MONT_IMG = img.convert("RGB")
    except Exception:
        _MONT_IMG = False
    return _MONT_IMG


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

NB_NUMS = 7
# le billet modèle AVERA (34/55 haut · 3/35/70 milieu · 15/57 bas) :
# 1-15 = petit au milieu-gauche puis grand en bas-gauche ; 31-45 = petit en
# haut-centre-gauche puis grand au centre ; 46-60 = petit en haut-centre-droit
# puis grand en bas-droit ; 61-75 = 1 seul au milieu-droit (16-30 et 76-90 absents)
POSITIONS = [(0.12, 0.50), (0.24, 0.21), (0.33, 0.72), (0.50, 0.56), (0.67, 0.72), (0.72, 0.21), (0.88, 0.50)]
LETTRES = [("O", 0.29, 0.50), ("P", 0.41, 0.35), ("O", 0.53, 0.23), ("A", 0.65, 0.37)]
R_MM = 9.0   # boules de bingo à double cercle, façon VALIDER
TAILLE_CHIFFRE = 24


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── la montagne en filigrane pleine grille (passe derrière tout) ──
    gris_trait = colors.Color(0.60, 0.60, 0.60)
    img = _charger_montagne()
    if img:
        from reportlab.lib.utils import ImageReader
        iw, ih = img.size
        zw = CARD_W * 0.94
        zh = zw * ih / float(iw)
        zh = min(zh, CARD_H * 0.70)
        zw2 = zh * iw / float(ih)
        c.drawImage(ImageReader(img), x0 + (CARD_W - zw2) / 2, y0 + (CARD_H - 12 * mm - zh) / 2 + 2.5 * mm,
                    zw2, zh, mask=[238, 255, 238, 255, 238, 255])

    # ── les lettres O·P·O·A éparpillées en vague, grises (façon modèle) ──
    c.setFillColor(colors.Color(0.58, 0.58, 0.58))
    c.setFont("Helvetica-Bold", 16)
    for lettre, fx, fy in LETTRES:
        c.drawCentredString(x0 + CARD_W * fx, y0 + CARD_H * fy, lettre)

    # en-tête : nom + signature + N° de carte
    titre = "OPOA 7 boules"
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
    for i, (px, py) in enumerate(POSITIONS[:len(nums)]):
        r = R_MM * mm
        taille = TAILLE_CHIFFRE
        ccx = x0 + CARD_W * px
        cy = y0 + CARD_H * py
        # la boule de bingo : grand rond blanc + double cercle intérieur (façon VALIDER)
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
    rng = random.Random(962000 + int(serie_start))
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
                za = sorted(rng.sample(range(1, 16), 2))   # milieu-gauche puis bas-gauche
                zb = sorted(rng.sample(range(31, 46), 2))  # haut-centre-g puis centre
                zc = sorted(rng.sample(range(46, 61), 2))  # haut-centre-d puis bas-droit
                zd = rng.randint(61, 75)                   # milieu-droit
                nums = [za[0], za[1], zb[0], zb[1], zc[0], zc[1], zd]
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
