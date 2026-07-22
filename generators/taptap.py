# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TAP TAP (format A4)
8 billets larges/page — les lettres T·A·P T·A·P éparpillées (façon PAM PAM),
5 grands numéros en CERCLES : 1-15 · 46-60 · 2×61-75 · 76-90 (tirage dans 1-90).
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
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

NB_NUMS = 5
# chemin décodé sur le billet modèle (8/47/66/69/85, plage 1-90) :
# bas-gauche = 1-15 · haut-gauche = 46-60 · centre puis bas-droite = 2 triés
# dans 61-75 · haut-droite = 76-90 (les tranches 16-30 et 31-45 sont absentes)
POSITIONS = [(0.15, 0.26), (0.26, 0.72), (0.49, 0.48), (0.71, 0.26), (0.85, 0.72)]
RAYONS_MM =  [8.0, 8.0, 8.0, 8.0, 8.0]
TAILLES_CH = [32, 32, 32, 32, 32]
# les 6 lettres éparpillées, grises, façon modèle : (lettre, x, y ligne de base)
LETTRES = [("T", 0.55, 0.79), ("A", 0.68, 0.62), ("P", 0.87, 0.44),
           ("T", 0.20, 0.48), ("A", 0.32, 0.27), ("P", 0.50, 0.10)]
TAILLE_CHIFFRE = 32


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── les lettres T·A·P T·A·P éparpillées, grises (façon modèle) ──
    gris_trait = colors.Color(0.60, 0.60, 0.60)
    c.setFillColor(colors.Color(0.58, 0.58, 0.58))
    c.setFont("Helvetica-Bold", 16)
    for lettre, fx, fy in LETTRES:
        c.drawCentredString(x0 + CARD_W * fx, y0 + CARD_H * fy, lettre)

    # en-tête : nom + signature + N° de carte
    titre = "TAP TAP 5 boules"
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
        r = RAYONS_MM[i] * mm
        taille = TAILLES_CH[i]
        ccx = x0 + CARD_W * px
        cy = y0 + CARD_H * py
        c.setFillColor(colors.white); c.setStrokeColor(gris_trait); c.setLineWidth(0.7)
        c.ellipse(ccx - r, cy - r, ccx + r, cy + r, stroke=1, fill=1)
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
    rng = random.Random(957000 + int(serie_start))
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
                za = rng.randint(1, 15)                    # bas-gauche
                zb = rng.randint(46, 60)                   # haut-gauche
                zc = sorted(rng.sample(range(61, 76), 2))  # centre puis bas-droite
                zd = rng.randint(76, 90)                   # haut-droite
                nums = [za, zb, zc[0], zc[1], zd]
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
