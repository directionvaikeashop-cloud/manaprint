# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur CALLER (format A4)
12 billets/page — le POUCE DU COOL dessiné maison au centre-droit (façon POINTS),
le titre CALLER en gris, 6 grands numéros SANS cases : 2×1-15 · 2×46-60 · 2×61-75.
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
_CALLER_IMG = None


def _charger_caller():
    """L'illustration du pouce du cool (image de Maeva),
    pâlie en filigrane. Anti-panne : pouce vectoriel maison en secours."""
    global _CALLER_IMG
    if _CALLER_IMG is not None:
        return _CALLER_IMG
    try:
        from PIL import Image as _Image
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "caller_pouce.png")
        brut = _Image.open(chemin)
        if brut.mode in ("RGBA", "LA", "P"):
            brut = brut.convert("RGBA")
            fondb = _Image.new("RGBA", brut.size, (255, 255, 255, 255))
            brut = _Image.alpha_composite(fondb, brut)
        img = brut.convert("L")
        img = img.point(lambda p: int(255 - (255 - p) * 0.32))  # bien lisible
        _CALLER_IMG = img.convert("RGB")
    except Exception:
        _CALLER_IMG = False
    return _CALLER_IMG


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

NB_NUMS = 6
# chemin décodé sur le billet modèle POINTS (3/7/46/57/66/69) :
# gauche-haut puis gauche-bas = 2 triés dans 1-15 · sommet puis bas-centre =
# 2 triés dans 46-60 · centre (sur le pouce) puis bas-droit = 2 triés dans
# 61-75 (16-30 et 31-45 absentes du modèle)
POSITIONS = [(0.15, 0.62), (0.15, 0.30), (0.52, 0.76), (0.40, 0.13), (0.62, 0.45), (0.69, 0.13)]
TAILLE_CHIFFRE = 32


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── le titre CALLER en gris, haut-gauche (façon modèle) ──
    c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont(POLICE, 9)
    c.drawString(x0 + 3.0 * mm, y0 + CARD_H * 0.80, "CALLER")

    # ── le POUCE DU COOL : l'image de Maeva en filigrane,
    #    et le pouce maison en roue de secours si elle manque ──
    img = _charger_caller()
    if img:
        from reportlab.lib.utils import ImageReader
        iw, ih = img.size
        zone_w, zone_h = CARD_W * 0.58, CARD_H * 0.50
        ratio = min(zone_w / iw, zone_h / ih)
        dw, dh = iw * ratio, ih * ratio
        c.drawImage(ImageReader(img), x0 + CARD_W * 0.56 - dw / 2, y0 + CARD_H * 0.44 - dh / 2,
                    dw, dh, mask=[238, 255, 238, 255, 238, 255])
    else:
        _pouce_maison(c, x0, y0)
    _suite_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu, telephone, style, evenement_id, col, police_ch, gris_ch)


def _pouce_maison(c, x0, y0):
    gris_pouce = colors.Color(0.72, 0.72, 0.72)
    c.setStrokeColor(gris_pouce); c.setLineWidth(0.7)
    hx, hy = x0 + CARD_W * 0.55, y0 + CARD_H * 0.42
    # les quatre doigts repliés (courbes empilées, la plus haute un peu plus large)
    for k in range(4):
        dw2 = (12.2 - k * 0.7) * mm
        dh2 = 4.0 * mm
        dy = (7.2 - k * 4.6) * mm
        c.ellipse(hx - dw2, hy + dy - dh2 / 2, hx + dw2 * 0.35, hy + dy + dh2 / 2, stroke=1, fill=0)
    # le pouce levé (ellipse allongée inclinée)
    c.saveState()
    c.translate(hx + 6.0 * mm, hy + 13.5 * mm)
    c.rotate(72)
    c.ellipse(-9.5 * mm, -3.4 * mm, 9.5 * mm, 3.4 * mm, stroke=1, fill=0)
    c.restoreState()
    # la manchette à droite du poing
    c.roundRect(hx + 7.5 * mm, hy - 9.5 * mm, 6.5 * mm, 15.5 * mm, 1.5 * mm, stroke=1, fill=0)


def _suite_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu, telephone, style, evenement_id, col, police_ch, gris_ch):
    # en-tête : nom + signature + N° de carte
    titre = "CALLER 6 boules"
    if titre_jeu and titre_jeu.strip().upper() != titre.upper():
        titre += "  —  " + titre_jeu.strip()
    titre += "  by TUKEA " + (telephone or "")
    c.setFillColor(col); c.setFont(POLICE, 4.4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 3.6 * mm, titre[:64])
    c.setFillColor(col); c.setFont(POLICE, 5.2)
    c.drawString(x0 + 2.6 * mm, y0 + CARD_H - 7.8 * mm, "Carte N° %05d" % serie)

    # le téléphone en pied gauche (comme les billets du fenua)
    c.setFillColor(colors.Color(0.45, 0.45, 0.45)); c.setFont(POLICE, 4.2)
    c.drawString(x0 + 2.6 * mm, y0 + 2.0 * mm, "Tèl : " + (telephone or ""))

    # les 6 grands numéros NUS (façon modèle), chacun sur un halo blanc
    # pour rester net même posé sur le pouce
    for i, (px, py) in enumerate(POSITIONS[:len(nums)]):
        ccx = x0 + CARD_W * px
        cy = y0 + CARD_H * py
        c.setFillColor(colors.white)
        c.rect(ccx - 7.6 * mm, cy - 6.0 * mm, 15.2 * mm, 12.0 * mm, stroke=0, fill=1)
        if _sec:
            _sec.chiffre_micro(c, nums[i], ccx, cy - TAILLE_CHIFFRE * 0.36, TAILLE_CHIFFRE, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, TAILLE_CHIFFRE)
            c.drawCentredString(ccx, cy - TAILLE_CHIFFRE * 0.36, str(nums[i]))

    # QR de vérification (anti-duplication) — HAUT-DROIT, dans la zone blanche
    if _sec and evenement_id:
        try:
            _q = 8.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.2 * mm, y0 + CARD_H - _q - 9.8 * mm, _q, evenement_id, serie)
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
    rng = random.Random(959000 + int(serie_start))
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
                zg = sorted(rng.sample(range(1, 16), 2))   # gauche : haut puis bas
                zc = sorted(rng.sample(range(46, 61), 2))  # sommet puis bas-centre
                zd = sorted(rng.sample(range(61, 76), 2))  # centre puis bas-droit
                nums = [zg[0], zg[1], zc[0], zc[1], zd[0], zd[1]]
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
