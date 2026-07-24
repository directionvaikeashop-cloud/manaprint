# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur AUSTRALES (format A4)
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
_AUSTRALES_IMG = None


def _charger_australes():
    """L'illustration des Australes (licence à fournir par Maeva),
    pâlie en filigrane. Anti-panne : archipel vectoriel maison en secours."""
    global _AUSTRALES_IMG
    if _AUSTRALES_IMG is not None:
        return _AUSTRALES_IMG
    try:
        from PIL import Image as _Image
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "australes_archipel.png")
        brut = _Image.open(chemin)
        if brut.mode in ("RGBA", "LA", "P"):
            brut = brut.convert("RGBA")
            fondb = _Image.new("RGBA", brut.size, (255, 255, 255, 255))
            brut = _Image.alpha_composite(fondb, brut)
        img = brut.convert("L")
        img = img.point(lambda p: int(255 - (255 - p) * 0.45))
        _AUSTRALES_IMG = img.convert("RGB")
    except Exception:
        _AUSTRALES_IMG = False
    return _AUSTRALES_IMG


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
# ordre de LECTURE : les numéros triés s'y posent du plus petit au plus grand
# ordre de LECTURE EN COLONNES : la montée descend la gauche puis la droite
POSITIONS = [(0.16, 0.74), (0.16, 0.48), (0.155, 0.30), (0.46, 0.15), (0.84, 0.76), (0.84, 0.52), (0.84, 0.30)]
TAILLE_CHIFFRE = 32


def _dessiner_fond(c, x0, y0, w, h):
    """Les AUSTRALES : l'illustration sous licence en filigrane —
    et l'archipel vectoriel maison en roue de secours si l'image manque."""
    img = _charger_australes()
    if img:
        from reportlab.lib.utils import ImageReader
        iw, ih = img.size
        zone_w, zone_h = w * 0.94, h * 0.78
        ratio = min(zone_w / iw, zone_h / ih)
        dw, dh = iw * ratio, ih * ratio
        c.drawImage(ImageReader(img), x0 + (w - dw) / 2, y0 + h * 0.05 + (zone_h - dh) / 2, dw, dh,
                    mask=[238, 255, 238, 255, 238, 255])
        return
    # ── repli : les VRAIES îles Australes, dessinées maison ──
    # (la géographie est un fait du monde : la chaîne du sud, de Maria
    #  jusqu'aux rochers de Marotiri, avec Rapa la lointaine)
    ILES = [
        # (nom, x, y, largeur mm, hauteur mm, côté de l'étiquette : g/d/b/h)
        ("Maria",    0.300, 0.80, 1.3, 0.9, "d"),
        ("Rimatara", 0.340, 0.68, 1.8, 1.3, "b"),
        ("Rurutu",   0.400, 0.74, 2.0, 1.5, "h"),
        ("Tubuai",   0.470, 0.62, 2.6, 1.7, "d"),
        ("Raivavae", 0.530, 0.54, 2.2, 1.4, "b"),
        ("Rapa",     0.620, 0.28, 2.0, 1.6, "h"),
        ("Marotiri", 0.680, 0.22, 1.0, 0.8, "b"),
    ]
    import math as _math
    for nomile, px, py, lw, lh, cote in ILES:
        cx, cy = x0 + w * px, y0 + h * (0.10 + py * 0.72)
        c.setFillColor(PALE)
        if nomile == "Marotiri":
            # les rochers : trois pointes éparses
            for dx, dy, r in ((-0.8, 0.3, 0.35), (0.4, -0.2, 0.30), (1.0, 0.5, 0.25)):
                c.circle(cx + dx * mm, cy + dy * mm, r * mm, stroke=0, fill=1)
        else:
            # île haute pleine : deux ellipses organiques
            c.ellipse(cx - lw * mm / 2, cy - lh * mm / 2, cx + lw * mm / 2, cy + lh * mm / 2, stroke=0, fill=1)
            c.ellipse(cx - lw * mm * 0.25, cy - lh * mm * 0.10, cx + lw * mm * 0.58, cy + lh * mm * 0.60, stroke=0, fill=1)
        c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont(POLICE, 3.2)
        if cote == "g":
            c.drawRightString(cx - lw * mm / 2 - 0.8 * mm, cy - 1.0, nomile)
        elif cote == "d":
            c.drawString(cx + lw * mm / 2 + 0.8 * mm, cy - 1.0, nomile)
        elif cote == "b":
            c.drawCentredString(cx, cy - lh * mm / 2 - 1.6 * mm, nomile)
        else:
            c.drawCentredString(cx, cy + lh * mm / 2 + 0.7 * mm, nomile)


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
    titre = "AUSTRALES 7 boules"
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
                nums = sorted(rng.sample(range(1, 76), NB_NUMS))  # ordre chronologique 1 -> 75
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
