# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur 100 FRANCS (format A4)
12 billets/page (3×4, façon YAKARI carré) — 7 numéros chacun DANS UNE PIÈCE DE 100 FRANCS
(l'image de Maeva, chiffre sur médaillon blanc au centre de la pièce),
en couronne façon YAKARI : 3×46-60 à gauche · 3×61-75 à droite · 76-90 au centre.
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
_PIECE_IMG = None


def _charger_piece():
    """La pièce de 100 francs de Maeva (découpée en disque), pâlie une fois
    pour que le chiffre reste roi. Anti-panne : boule à double cercle."""
    global _PIECE_IMG
    if _PIECE_IMG is not None:
        return _PIECE_IMG
    try:
        from PIL import Image as _Image
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "francs_piece.png")
        brut = _Image.open(chemin)
        if brut.mode in ("RGBA", "LA", "P"):
            brut = brut.convert("RGBA")
            fondb = _Image.new("RGBA", brut.size, (255, 255, 255, 255))
            brut = _Image.alpha_composite(fondb, brut)
        img = brut.convert("L")
        img = img.point(lambda p: int(255 - (255 - p) * 0.34))
        _PIECE_IMG = img.convert("RGB")
    except Exception:
        _PIECE_IMG = False
    return _PIECE_IMG


PAGE_W, PAGE_H = A4
COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

NB_NUMS = 7
# le billet modèle YAKARI (47/67 haut · 49/84/71 milieu · 50/75 bas) :
# colonne GAUCHE = 3 triés dans 46-60 (haut, milieu, bas), colonne DROITE =
# 3 triés dans 61-75 (haut, milieu, bas), CENTRE = 1 dans 76-90
POSITIONS = [(0.22, 0.73), (0.22, 0.47), (0.22, 0.21), (0.78, 0.73), (0.78, 0.47), (0.78, 0.21), (0.50, 0.47)]
PIECE_MM = 16.0        # diamètre de chaque pièce de 100 F
MEDAILLON_MM = 4.9     # rayon du médaillon blanc au coeur de la pièce
TAILLE_CHIFFRE = 19


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    gris_trait = colors.Color(0.60, 0.60, 0.60)
    img = _charger_piece()
    if img:
        from reportlab.lib.utils import ImageReader
        lecteur = ImageReader(img)

    # en-tête : nom + signature + N° de carte
    titre = "100 FRANCS 7 boules"
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
        taille = TAILLE_CHIFFRE
        ccx = x0 + CARD_W * px
        cy = y0 + CARD_H * py
        d = PIECE_MM * mm
        if img:
            # la pièce de 100 F, et le chiffre sur son médaillon blanc au centre
            c.drawImage(lecteur, ccx - d / 2, cy - d / 2, d, d,
                        mask=[240, 255, 240, 255, 240, 255])
        else:
            # secours : boule à double cercle façon VALIDER
            r = d / 2
            c.setFillColor(colors.white); c.setStrokeColor(gris_trait); c.setLineWidth(0.7)
            c.ellipse(ccx - r, cy - r, ccx + r, cy + r, stroke=1, fill=1)
            ri = r * 0.80
            c.setLineWidth(0.45)
            c.ellipse(ccx - ri, cy + 0.7 * mm - ri, ccx + ri, cy + 0.7 * mm + ri, stroke=1, fill=0)
        rm = MEDAILLON_MM * mm
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.Color(0.58, 0.58, 0.58)); c.setLineWidth(0.45)
        c.ellipse(ccx - rm, cy - rm, ccx + rm, cy + rm, stroke=1, fill=1)
        if _sec:
            _sec.chiffre_micro(c, nums[i], ccx, cy - taille * 0.36, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(ccx, cy - taille * 0.36, str(nums[i]))

    # QR de vérification (anti-duplication) — bas-droit
    if _sec and evenement_id:
        try:
            _q = 8.5 * mm
            # QR au BAS-CENTRE : les pièces occupent les deux coins du bas
            _sec.carton_qr(c, x0 + (CARD_W - _q) / 2, y0 + 1.8 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif=""):
    telephone = (telephone or "").strip() or "89 22 23 05"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    rng = random.Random(963000 + int(serie_start))
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
                zg = sorted(rng.sample(range(46, 61), 3))  # colonne gauche, haut vers bas
                zd = sorted(rng.sample(range(61, 76), 3))  # colonne droite, haut vers bas
                zc = rng.randint(76, 90)                   # le centre
                nums = [zg[0], zg[1], zg[2], zd[0], zd[1], zd[2], zc]
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
