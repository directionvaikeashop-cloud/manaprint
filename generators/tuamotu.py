# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TUAMOTU (format A4)
8 cartes/page — archipel dessiné maison avec ses îles, 6 grands numéros.
Numéros tirés dans 1-75 · QR de sécurité · série · microtexte · Tèl par défaut 89 22 23 05.
Dessins vectoriels originaux MANAPRINT.
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
_TUAMOTU_IMG = None


def _charger_tuamotu():
    """L'illustration des Tuamotu (licence à fournir par Maeva),
    pâlie en filigrane. Anti-panne : archipel vectoriel maison en secours."""
    global _TUAMOTU_IMG
    if _TUAMOTU_IMG is not None:
        return _TUAMOTU_IMG
    try:
        from PIL import Image as _Image
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "tuamotu_archipel.png")
        brut = _Image.open(chemin)
        if brut.mode in ("RGBA", "LA", "P"):
            brut = brut.convert("RGBA")
            fondb = _Image.new("RGBA", brut.size, (255, 255, 255, 255))
            brut = _Image.alpha_composite(fondb, brut)
        img = brut.convert("L")
        img = img.point(lambda p: int(255 - (255 - p) * 0.18))
        _TUAMOTU_IMG = img.convert("RGB")
    except Exception:
        _TUAMOTU_IMG = False
    return _TUAMOTU_IMG


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
POSITIONS = [(0.16, 0.74), (0.16, 0.48), (0.155, 0.24), (0.84, 0.76), (0.84, 0.52), (0.84, 0.33), (0.40, 0.15), (0.66, 0.15)]
TAILLE_CHIFFRE = 32


def _dessiner_fond(c, x0, y0, w, h):
    """Les TUAMOTU : l'illustration sous licence en filigrane —
    et l'archipel vectoriel maison en roue de secours si l'image manque."""
    img = _charger_tuamotu()
    if img:
        from reportlab.lib.utils import ImageReader
        iw, ih = img.size
        zone_w, zone_h = w * 0.52, h * 0.80
        ratio = min(zone_w / iw, zone_h / ih)
        dw, dh = iw * ratio, ih * ratio
        c.drawImage(ImageReader(img), x0 + (w - dw) / 2, y0 + h * 0.10, dw, dh,
                    mask=[238, 255, 238, 255, 238, 255])
        c.setFillColor(colors.Color(0.62, 0.62, 0.62)); c.setFont(POLICE, 3.2)
        c.drawCentredString(x0 + w / 2, y0 + 0.9 * mm, "Illustration : Designed by Freepik")
        return
    # ── repli : les VRAIS ATOLLS des Tuamotu, dessinés maison en anneaux ──
    # (la géographie est un fait du monde : positions et noms réels — le lagon
    #  dans son récif, dessiné en anneau comme la nature les a faits)
    ATOLLS = [
        # (nom, x, y, largeur mm, hauteur mm, côté de l'étiquette : g/d/b/h)
        ("Mataiva",  0.295, 0.70, 1.8, 1.1, "h"),
        ("Tikehau",  0.340, 0.565, 2.2, 1.4, "h"),
        ("Rangiroa", 0.420, 0.585, 4.6, 2.2, "d"),
        ("Manihi",   0.475, 0.745, 2.0, 1.2, "d"),
        ("Pukapuka", 0.680, 0.885, 1.5, 1.0, "g"),
        ("Fakarava", 0.445, 0.415, 2.8, 1.9, "b"),
        ("Anaa",     0.485, 0.275, 2.0, 1.2, "g"),
        ("Makemo",   0.560, 0.425, 3.0, 1.5, "d"),
        ("Hao",      0.665, 0.30, 3.4, 1.3, "g"),
    ]
    for nomatoll, px, py, lw, lh, cote in ATOLLS:
        cx, cy = x0 + w * px, y0 + h * (0.10 + py * 0.72)
        # l'anneau du récif (le lagon au centre reste blanc)
        c.setStrokeColor(PALE); c.setLineWidth(1.1)
        c.ellipse(cx - lw * mm / 2, cy - lh * mm / 2, cx + lw * mm / 2, cy + lh * mm / 2, stroke=1, fill=0)
        # quelques motu du récif (petits points sur l'anneau)
        for ang in (25, 130, 250, 330):
            import math as _math
            mx = cx + (lw * mm / 2) * _math.cos(_math.radians(ang))
            my = cy + (lh * mm / 2) * _math.sin(_math.radians(ang))
            c.setFillColor(PALE)
            c.circle(mx, my, 0.28 * mm, stroke=0, fill=1)
        c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont(POLICE, 3.2)
        if cote == "g":
            c.drawRightString(cx - lw * mm / 2 - 0.8 * mm, cy - 1.0, nomatoll)
        elif cote == "d":
            c.drawString(cx + lw * mm / 2 + 0.8 * mm, cy - 1.0, nomatoll)
        elif cote == "b":
            c.drawCentredString(cx, cy - lh * mm / 2 - 1.6 * mm, nomatoll)
        else:  # "h" : au-dessus
            c.drawCentredString(cx, cy + lh * mm / 2 + 0.7 * mm, nomatoll)


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    _dessiner_fond(c, x0, y0, CARD_W, CARD_H)

    # en-tête : nom du jeu toujours affiché + titre client + notre signature
    hdr_y = y0 + CARD_H - 4.2 * mm
    titre = "TUAMOTU 8 boules"
    if titre_jeu and titre_jeu.strip().upper() != titre.upper():
        titre += "  —  " + titre_jeu.strip()
    titre += "  by TUKEA " + (telephone or "")
    c.setFillColor(col); c.setFont(POLICE, 4.6)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y, titre[:64])
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y - 4.2 * mm, "Carte N° %05d" % serie)

    # le téléphone en pied gauche (comme les billets du fenua)
    c.setFillColor(colors.Color(0.45, 0.45, 0.45)); c.setFont(POLICE, 4.5)
    c.drawString(x0 + 2.5 * mm, y0 + 2.2 * mm, "Tèl : " + (telephone or ""))


    for i, (px, py) in enumerate(POSITIONS[:len(nums)]):
        cx = x0 + CARD_W * px
        cy = y0 + CARD_H * py

        if _sec:
            _sec.chiffre_micro(c, nums[i], cx, cy - TAILLE_CHIFFRE * 0.36, TAILLE_CHIFFRE, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, TAILLE_CHIFFRE)
            c.drawCentredString(cx, cy - TAILLE_CHIFFRE * 0.36, str(nums[i]))

    # QR de vérification (anti-duplication) — bas-droit
    if _sec and evenement_id:
        try:
            _q = 10 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.5 * mm, y0 + 2.2 * mm, _q, evenement_id, serie)
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
    rng = random.Random(940000 + int(serie_start))
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
                nums = rng.sample(range(1, 76), NB_NUMS)
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
