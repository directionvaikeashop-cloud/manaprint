# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TRIPLE BO90 (format A4)
7 LANGUETTES PLEINE LARGEUR/page — façon modèle TRIPLE BO90, chiffres 32 pts (calibre POW) : le pavé-titre à gauche
(TRIPLE / BO90) et 3 GRANDES CASES, chacune avec 3 numéros TRIÉS (2 en haut,
1 en bas) : case 1 = 1-15 · case 2 = 61-75 · case 3 = 76-90.
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
COLS_PAGE = 1
ROWS_PAGE = 7
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

NB_NUMS = 9
# le modèle (8 billets lus) : 3 cases de 3 numéros TRIÉS chacune —
# lecture haut-gauche, haut-droit puis bas-centre ; case 1 = 1-15,
# case 2 = 61-75, case 3 = 76-90 (les tranches 16-60 sont absentes)
CASE_X0 = 21.0        # après le pavé-titre de la languette
CASE_W = 48.0
CASE_GAP = 1.5
CASE_Y0, CASE_H = 3.0, 28.0
Y_HAUT, Y_BAS = 23.0, 10.5     # lignes des numéros (centres, en mm de carte)
FX_HG, FX_HD, FX_B = 0.27, 0.73, 0.50   # fractions de case
TAILLE_CHIFFRE = 32            # le calibre POW


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── le pavé-titre de la languette : TRIPLE / BO90 empilés (façon modèle) ──
    gris_trait = colors.Color(0.60, 0.60, 0.60)
    c.setFillColor(colors.Color(0.55, 0.55, 0.55))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x0 + 10.5 * mm, y0 + 22.0 * mm, "TRIPLE")
    c.drawCentredString(x0 + 10.5 * mm, y0 + 15.0 * mm, "BO90")

    # ── les 3 grandes cases arrondies ──
    c.setStrokeColor(gris_trait); c.setLineWidth(0.7)
    for k in range(3):
        cx0 = x0 + (CASE_X0 + k * (CASE_W + CASE_GAP)) * mm
        c.roundRect(cx0, y0 + CASE_Y0 * mm, CASE_W * mm, CASE_H * mm, 1.8 * mm, stroke=1, fill=0)

    # en-tête : nom + signature + N° de carte
    titre = "TRIPLE BO90 9 boules"
    if titre_jeu and titre_jeu.strip().upper() != titre.upper():
        titre += "  —  " + titre_jeu.strip()
    titre += "  by TUKEA " + (telephone or "")
    c.setFillColor(col); c.setFont(POLICE, 4.6)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 3.0 * mm, titre[:64])
    c.setFillColor(col); c.setFont(POLICE, 5.5)
    c.drawCentredString(x0 + 10.5 * mm, y0 + 8.5 * mm, "Carte N° %05d" % serie)

    # le téléphone en pied gauche (comme les billets du fenua)
    c.setFillColor(colors.Color(0.45, 0.45, 0.45)); c.setFont(POLICE, 4.5)
    c.drawString(x0 + 2.5 * mm, y0 + 2.2 * mm, "Tèl : " + (telephone or ""))

    # ── les 9 numéros : 3 par case (2 en haut, 1 en bas), triés ──
    taille = TAILLE_CHIFFRE
    for i, n in enumerate(nums):
        k, j = divmod(i, 3)
        cx0 = CASE_X0 + k * (CASE_W + CASE_GAP)
        fx, cyc = ((FX_HG, Y_HAUT), (FX_HD, Y_HAUT), (FX_B, Y_BAS))[j]
        ccx = x0 + (cx0 + CASE_W * fx) * mm
        cy = y0 + cyc * mm
        if _sec:
            _sec.chiffre_micro(c, n, ccx, cy - taille * 0.36, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(ccx, cy - taille * 0.36, str(n))

    # QR de vérification (anti-duplication) — CENTRÉ dans le blanc du bout de bande
    if _sec and evenement_id:
        try:
            _q = 8.5 * mm
            fin_cases = (CASE_X0 + 3 * CASE_W + 2 * CASE_GAP) * mm
            qx = x0 + (fin_cases + CARD_W) / 2 - _q / 2
            qy = y0 + (CARD_H - _q) / 2
            _sec.carton_qr(c, qx, qy, _q, evenement_id, serie)
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
    rng = random.Random(967000 + int(serie_start))
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
                za = sorted(rng.sample(range(1, 16), 3))   # case 1
                zb = sorted(rng.sample(range(61, 76), 3))  # case 2
                zc = sorted(rng.sample(range(76, 91), 3))  # case 3
                nums = za + zb + zc
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
