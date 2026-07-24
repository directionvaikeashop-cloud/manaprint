# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur LOSANGE (format A4)
6 losanges/page (2×3) — 8 numéros par carte : flanc gauche 3 triés 1-30,
flanc droit 3 triés 46-75, haut+bas 2 triés 31-45. Texte central, QR, microtexte.
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


PAGE_W, PAGE_H = A4
COLS_PAGE = 2
ROWS_PAGE = 3
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

NB_NUMS = 8
TAILLE_CHIFFRE = 32
# positions en fraction de carte : (fx, fy) — haut, fg1, fd1, g, d, fg2, fd2, bas
POS = [(0.50, 0.770), (0.315, 0.615), (0.685, 0.615), (0.185, 0.465), (0.815, 0.465),
       (0.325, 0.330), (0.675, 0.330), (0.50, 0.180)]


def _gen_nums(rng):
    """8 numéros : gauche 3 triés 1-30, droite 3 triés 46-75, haut+bas 2 triés 31-45."""
    g = sorted(rng.sample(range(1, 31), 3))
    d = sorted(rng.sample(range(46, 76), 3))
    n = sorted(rng.sample(range(31, 46), 2))
    #      haut  fg1   fd1   g     d     fg2   fd2   bas
    return [n[0], g[0], d[0], g[1], d[1], g[2], d[2], n[1]]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # le LOSANGE (carré sur pointe) — sommets avec marge
    cx, cyc = x0 + CARD_W / 2, y0 + CARD_H / 2
    ht, hb = y0 + CARD_H - 1.5 * mm, y0 + 1.5 * mm
    xg, xd = x0 + 2.0 * mm, x0 + CARD_W - 2.0 * mm
    c.setStrokeColor(col); c.setLineWidth(1.0)
    p = c.beginPath()
    p.moveTo(cx, ht); p.lineTo(xd, cyc); p.lineTo(cx, hb); p.lineTo(xg, cyc); p.close()
    c.drawPath(p, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.6 * mm)

    # texte central (esprit du modèle)
    c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont(POLICE, 4.6)
    c.drawCentredString(cx, cyc + 1.6 * mm, "Le jeu LOSANGE pour 8 boules by 2KEA")
    c.setFont(POLICE, 4.6)
    c.drawCentredString(cx, cyc - 1.2 * mm, "N° %06d" % serie)
    if telephone:
        c.setFont(POLICE, 4.0)
        c.drawCentredString(cx, cyc - 3.8 * mm, "Tèl : " + telephone)
    if titre_jeu:
        c.setFillColor(col); c.setFont(POLICE, 5.0)
        c.drawCentredString(cx, cyc + 4.4 * mm, titre_jeu.strip()[:36])

    # les 8 numéros à leur poste
    for i, (fx, fy) in enumerate(POS):
        nx, ny = x0 + CARD_W * fx, y0 + CARD_H * fy
        if _sec:
            _sec.chiffre_micro(c, nums[i], nx, ny - TAILLE_CHIFFRE * 0.36, TAILLE_CHIFFRE, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, TAILLE_CHIFFRE)
            c.drawCentredString(nx, ny - TAILLE_CHIFFRE * 0.36, str(nums[i]))

    # QR de vérification — DANS le losange, sous le texte central (décision Maeva)
    if _sec and evenement_id:
        try:
            _q = 8.5 * mm
            _sec.carton_qr(c, cx - _q / 2, cyc - 14.6 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif=""):
    telephone = (telephone or "").strip() or "89 22 23 05"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    rng = random.Random(979000 + int(serie_start))
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
                nums = _gen_nums(rng)
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


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True, nom_evenement="TEST", telephone="89.22.23.05")
    with open("test_losange.pdf", "wb") as f:
        f.write(pdf.read())
    print("LOSANGE généré")
