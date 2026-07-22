# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur FEU (format A4)
12 billets/page — les lettres F·E·U en grand contour posées en diagonale (façon FIU),
5 cases arrondies, chaque case tire dans SA zone : 16-30 · 61-75 · 46-60 · 1-15 · 31-45.
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
# chaque case a SA zone, aux places du modèle FIU (lues sur 12 billets) :
# à côté du F = 16-30 · haut-droit = 61-75 · milieu-droit = 46-60 ·
# gauche-bas = 1-15 · bas-centre = 31-45 — le 1-75 entier est couvert
PLAGES = [(16, 30), (61, 75), (46, 60), (1, 15), (31, 45)]
POSITIONS = [(0.44, 0.75), (0.82, 0.75), (0.74, 0.52), (0.14, 0.30), (0.38, 0.19)]
# les lettres F, E, U en diagonale : (lettre, x gauche, y ligne de base)
LETTRES = [("F", 0.06, 0.60), ("E", 0.30, 0.37), ("U", 0.58, 0.09)]
TAILLE_LETTRE = 50
TAILLE_CHIFFRE = 32


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # F · E · U en grandes lettres ÉVIDÉES posées en diagonale (façon modèle)
    c.saveState()
    c.setStrokeColor(colors.Color(0.62, 0.62, 0.62)); c.setLineWidth(0.8)
    for lettre, fx, fy in LETTRES:
        to = c.beginText(x0 + CARD_W * fx, y0 + CARD_H * fy)
        to.setTextRenderMode(1)
        to.setFont("Helvetica-Bold", TAILLE_LETTRE)
        to.textOut(lettre)
        c.drawText(to)
    c.restoreState()

    # en-tête : nom + signature + N° de carte
    titre = "FEU 5 boules"
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

    # les 5 cases arrondies, chaque numéro dans SA zone
    case_w, case_h = 13.5 * mm, 13.0 * mm
    for i, (px, py) in enumerate(POSITIONS[:len(nums)]):
        ccx = x0 + CARD_W * px
        cy = y0 + CARD_H * py
        c.setStrokeColor(colors.Color(0.62, 0.62, 0.62)); c.setLineWidth(0.7)
        c.roundRect(ccx - case_w / 2, cy - case_h / 2, case_w, case_h, 2.6 * mm, stroke=1, fill=0)
        if _sec:
            _sec.chiffre_micro(c, nums[i], ccx, cy - TAILLE_CHIFFRE * 0.36, TAILLE_CHIFFRE, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, TAILLE_CHIFFRE)
            c.drawCentredString(ccx, cy - TAILLE_CHIFFRE * 0.36, str(nums[i]))

    # QR de vérification (anti-duplication) — bas-droit
    if _sec and evenement_id:
        try:
            _q = 8.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.2 * mm, y0 + 1.8 * mm, _q, evenement_id, serie)
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
    rng = random.Random(955000 + int(serie_start))
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
                nums = [rng.randint(a, b) for (a, b) in PLAGES]  # un numéro par plage, ordre du billet
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
