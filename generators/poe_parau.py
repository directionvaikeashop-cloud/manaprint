# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur POE PARAU 6 boules (format A4)
12 cartes/page — coquillage en éventail original, 6 numéros en boules.
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
_NACRE_IMG = None


def _charger_nacre():
    """L'illustration du coquillage (licence Freepik), pâlie en filigrane.
    Anti-panne : si le fichier manque, retour à la gravure vectorielle maison."""
    global _NACRE_IMG
    if _NACRE_IMG is not None:
        return _NACRE_IMG
    try:
        from PIL import Image as _Image
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "nacre_poe_parau.png")
        brut = _Image.open(chemin)
        # fond transparent -> aplati sur BLANC (sinon pavé noir !)
        if brut.mode in ("RGBA", "LA", "P"):
            brut = brut.convert("RGBA")
            fondb = _Image.new("RGBA", brut.size, (255, 255, 255, 255))
            brut = _Image.alpha_composite(fondb, brut)
        img = brut.convert("L")
        # les traits noirs deviennent gris très pâle (filigrane)
        img = img.point(lambda p: int(255 - (255 - p) * 0.18))
        _NACRE_IMG = img.convert("RGB")
    except Exception:
        _NACRE_IMG = False
    return _NACRE_IMG


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
POSITIONS = [(0.20, 0.72), (0.58, 0.72), (0.86, 0.59), (0.15, 0.42), (0.40, 0.22), (0.84, 0.34)]
TAILLE_CHIFFRE = 32


def _dessiner_fond(c, x0, y0, w, h):
    """La nacre POE PARAU : l'illustration sous licence en filigrane —
    et la gravure vectorielle maison en roue de secours si l'image manque."""
    img = _charger_nacre()
    if img:
        from reportlab.lib.utils import ImageReader
        iw, ih = img.size
        zone_w, zone_h = w * 0.76, h * 0.70
        ratio = min(zone_w / iw, zone_h / ih)
        dw, dh = iw * ratio, ih * ratio
        c.drawImage(ImageReader(img), x0 + (w - dw) / 2, y0 + h * 0.07, dw, dh,
                    mask=[238, 255, 238, 255, 238, 255])
        # mention de licence (formule gratuite Freepik)
        c.setFillColor(colors.Color(0.62, 0.62, 0.62)); c.setFont(POLICE, 3.2)
        c.drawCentredString(x0 + w / 2, y0 + 0.9 * mm, "Illustration : Designed by Freepik")
        return
    # ── repli : la gravure vectorielle maison ──
    bx, by = x0 + w * 0.50, y0 + h * 0.10
    R = h * 0.50
    c.setStrokeColor(PALE)

    NERVURES = 9
    a0, a1 = 32, 148   # l'ouverture de l'éventail (degrés)

    # ── le contour festonné : une bosse entre chaque paire de nervures ──
    c.setLineWidth(1.0)
    for i in range(NERVURES - 1):
        ang_a = math.radians(a0 + (a1 - a0) * i / (NERVURES - 1))
        ang_b = math.radians(a0 + (a1 - a0) * (i + 1) / (NERVURES - 1))
        xa, ya = bx + R * math.cos(ang_a), by + R * math.sin(ang_a)
        xb, yb = bx + R * math.cos(ang_b), by + R * math.sin(ang_b)
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        # la bosse : point médian poussé vers l'extérieur
        norme = math.hypot(mx - bx, my - by)
        fx, fy = bx + (mx - bx) / norme * R * 1.075, by + (my - by) / norme * R * 1.075
        p = c.beginPath()
        p.moveTo(xa, ya)
        p.curveTo(fx, fy, fx, fy, xb, yb)
        c.drawPath(p, stroke=1, fill=0)

    # ── les nervures : doubles lignes légèrement galbées ──
    c.setLineWidth(0.8)
    for i in range(NERVURES):
        ang = math.radians(a0 + (a1 - a0) * i / (NERVURES - 1))
        xe, ye = bx + R * math.cos(ang), by + R * math.sin(ang)
        for de in (-1.1, 1.1):
            px = -math.sin(ang) * de
            py = math.cos(ang) * de
            p = c.beginPath()
            p.moveTo(bx + px, by + py)
            p.curveTo(bx + (xe - bx) * 0.4 + px * 2.2, by + (ye - by) * 0.4 + py * 2.2,
                      bx + (xe - bx) * 0.75 + px * 1.6, by + (ye - by) * 0.75 + py * 1.6,
                      xe, ye)
            c.drawPath(p, stroke=1, fill=0)

    # ── les hachures de gravure : petits traits le long des nervures ──
    c.setLineWidth(0.45)
    for i in range(NERVURES - 1):
        ang_m = math.radians(a0 + (a1 - a0) * (i + 0.5) / (NERVURES - 1))
        for k in range(7):
            rr = R * (0.40 + 0.078 * k)
            hx, hy = bx + rr * math.cos(ang_m), by + rr * math.sin(ang_m)
            lg = R * 0.045 * (1 + 0.5 * (k % 2))
            c.line(hx - math.cos(ang_m) * lg / 2, hy - math.sin(ang_m) * lg / 2,
                   hx + math.cos(ang_m) * lg / 2, hy + math.sin(ang_m) * lg / 2)

    # ── la charnière et ses oreillettes ──
    c.setLineWidth(0.9)
    c.setFillColor(colors.white)
    c.rect(bx - R * 0.13, by - R * 0.075, R * 0.26, R * 0.075, stroke=1, fill=1)
    for s in (-1, 1):
        c.rect(bx + s * R * 0.13, by - R * 0.045, s * R * 0.085, R * 0.045, stroke=1, fill=1)

    # ── la petite perle POE, nichée à la charnière (signature du jeu) ──
    pr = R * 0.085
    for k, g in ((1.0, 0.82), (0.80, 0.88), (0.60, 0.93)):
        c.setFillColor(colors.Color(g, g, g))
        c.circle(bx - pr * (1 - k) * 0.4, by + R * 0.055 + pr * (1 - k) * 0.4, pr * k, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.circle(bx - pr * 0.25, by + R * 0.055 + pr * 0.25, pr * 0.35, stroke=0, fill=1)


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
    titre = "POE PARAU 6 boules"
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
        # boule ombrée en relief (dégradé simulé par anneaux)
        r_b = TAILLE_CHIFFRE * 0.72
        cyb = cy - TAILLE_CHIFFRE * 0.14
        for k, g in ((1.0, 0.84), (0.90, 0.88), (0.78, 0.92), (0.62, 0.96)):
            c.setFillColor(colors.Color(g, g, g))
            c.circle(cx - r_b * (1 - k) * 0.5, cyb + r_b * (1 - k) * 0.5, r_b * k, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.circle(cx - r_b * 0.22, cyb + r_b * 0.22, r_b * 0.44, stroke=0, fill=1)
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
