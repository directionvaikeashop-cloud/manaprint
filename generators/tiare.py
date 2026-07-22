# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TIARE 5 boules (format A4)
12 cartes/page — coquillage en éventail original, 6 numéros en boules.
Numéros tirés dans 50-90 (le jeu de fin de partie) · QR de sécurité · série · microtexte · Tèl par défaut 89 22 23 05.
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
_TIARE_IMG = None


def _charger_tiare():
    """L'illustration de la fleur (licence pngtree, fournie par Maeva), pâlie en filigrane.
    Anti-panne : si le fichier manque, retour à la tiare vectorielle maison."""
    global _TIARE_IMG
    if _TIARE_IMG is not None:
        return _TIARE_IMG
    try:
        from PIL import Image as _Image
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "tiare_fleur.png")
        brut = _Image.open(chemin)
        # fond transparent -> aplati sur BLANC (sinon pavé noir !)
        if brut.mode in ("RGBA", "LA", "P"):
            brut = brut.convert("RGBA")
            fondb = _Image.new("RGBA", brut.size, (255, 255, 255, 255))
            brut = _Image.alpha_composite(fondb, brut)
        img = brut.convert("L")
        # les traits noirs deviennent gris très pâle (filigrane)
        img = img.point(lambda p: int(255 - (255 - p) * 0.18))
        _TIARE_IMG = img.convert("RGB")
    except Exception:
        _TIARE_IMG = False
    return _TIARE_IMG


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

NB_NUMS = 5
# ordre de LECTURE : haut, milieu, bas — la montée 50 -> 90
POSITIONS = [(0.22, 0.72), (0.78, 0.72), (0.19, 0.34), (0.81, 0.38), (0.52, 0.16)]
TAILLE_CHIFFRE = 32


def _dessiner_fond(c, x0, y0, w, h):
    """La fleur TIARE : l'illustration sous licence en filigrane —
    et la tiare Tahiti vectorielle maison en roue de secours si l'image manque."""
    img = _charger_tiare()
    if img:
        from reportlab.lib.utils import ImageReader
        iw, ih = img.size
        zone_w, zone_h = w * 0.72, h * 0.66
        ratio = min(zone_w / iw, zone_h / ih)
        dw, dh = iw * ratio, ih * ratio
        c.drawImage(ImageReader(img), x0 + (w - dw) / 2, y0 + h * 0.14, dw, dh,
                    mask=[238, 255, 238, 255, 238, 255])
        c.setFillColor(colors.Color(0.62, 0.62, 0.62)); c.setFont(POLICE, 3.2)
        c.drawCentredString(x0 + w / 2, y0 + 0.9 * mm, "Illustration : pngtree.com")
        return
    # ── repli : la tiare Tahiti vectorielle maison ──
    # (6 pétales allongés en hélice, cœur doux — dessin original MANAPRINT)
    bx, by = x0 + w * 0.50, y0 + h * 0.46
    R = h * 0.30
    c.setStrokeColor(PALE); c.setLineWidth(1.0); c.setFillColor(colors.white)
    for i in range(6):
        c.saveState()
        c.translate(bx, by)
        c.rotate(i * 60 + 12)
        p = c.beginPath()
        p.moveTo(0, 0)
        p.curveTo(-R * 0.30, R * 0.30, -R * 0.34, R * 0.78, -R * 0.06, R)
        p.curveTo(R * 0.22, R * 0.86, R * 0.20, R * 0.34, 0, 0)
        c.drawPath(p, stroke=1, fill=1)
        # la nervure centrale du pétale
        pn = c.beginPath()
        pn.moveTo(0, R * 0.12)
        pn.curveTo(-R * 0.06, R * 0.40, -R * 0.08, R * 0.66, -R * 0.05, R * 0.86)
        c.drawPath(pn, stroke=1, fill=0)
        c.restoreState()
    c.setFillColor(PALE)
    c.circle(bx, by, R * 0.14, stroke=0, fill=1)
    # la tige délicate
    c.setStrokeColor(PALE); c.setLineWidth(1.6); c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(bx + R * 0.05, by - R * 0.2)
    p.curveTo(bx + R * 0.12, by - R * 0.8, bx + R * 0.02, by - R * 1.3, bx + R * 0.10, y0 + h * 0.06)
    c.drawPath(p, stroke=1, fill=0)


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
    titre = "TIARE 50-90"
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
        # case arrondie (façon billet du fenua)
        _l = TAILLE_CHIFFRE * 1.15
        c.setStrokeColor(colors.Color(0.55, 0.55, 0.55)); c.setLineWidth(1.0)
        c.setFillColor(colors.white)
        c.roundRect(cx - _l * 0.72, cy - _l * 0.62, _l * 1.44, _l * 1.1, 2.4 * mm, stroke=1, fill=1)
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


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif=""):
    telephone = (telephone or "").strip() or "89 22 23 05"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    rng = random.Random(930000 + int(serie_start))
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
                nums = sorted(rng.sample(range(50, 91), NB_NUMS))  # ordre chronologique 50 -> 90
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
