# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur CHANCE (format A4)
8 billets larges/page — le titre CHANCE en italique élégant (façon MĀROI) et
6 numéros nichés DANS DES TRÈFLES à 4 feuilles : 2×1-15 · 2×31-45 · 2×76-90.
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
_TREFLE_SVG = None


def _charger_trefle_svg():
    """Le trèfle PROFESSIONNEL : dessin au trait OpenMoji (CC BY-SA 4.0)
    rendu en VECTORIEL par svglib — net à toutes les tailles.
    Anti-panne : le trèfle dessiné maison prend le relais si besoin."""
    global _TREFLE_SVG
    if _TREFLE_SVG is not None:
        return _TREFLE_SVG
    try:
        from svglib.svglib import svg2rlg
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "chance_trefle.svg")
        d = svg2rlg(chemin)

        def _griser(objet):
            for attr, val in (("strokeColor", colors.Color(0.50, 0.50, 0.50)),
                              ("strokeWidth", 1.1)):
                if hasattr(objet, attr) and getattr(objet, attr) is not None:
                    setattr(objet, attr, val)
            if hasattr(objet, "fillColor") and getattr(objet, "fillColor") is not None:
                objet.fillColor = colors.Color(0.50, 0.50, 0.50)
            for enfant in getattr(objet, "contents", []) or []:
                _griser(enfant)

        _griser(d)
        _TREFLE_SVG = d
    except Exception:
        _TREFLE_SVG = False
    return _TREFLE_SVG


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

NB_NUMS = 6
# le billet modèle MĀROI (3/6/36/34/85/89) : colonne gauche = 2 triés dans
# 1-15 (haut puis bas), le duo du milieu = 2 triés dans 31-45 (le PETIT en
# bas-droite comme le 34, le GRAND en haut-gauche comme le 36), colonne
# droite = 2 triés dans 76-90 (haut puis bas)
POSITIONS = [(0.13, 0.66), (0.13, 0.28), (0.58, 0.33), (0.35, 0.585), (0.86, 0.66), (0.86, 0.33)]
# géométrie du trèfle : le dessin OpenMoji n'occupe qu'une partie de sa
# boîte SVG — on cadre sur le CONTENU réel mesuré (fractions de boîte) :
# encre x 0.294..0.792, y 0.110..0.869 (du haut), coeur des feuilles (0.539, 0.361)
CX0, CX1, CY0, CY1 = 0.294, 0.792, 0.110, 0.869
COEUR_X, COEUR_Y = 0.539, 0.361
CONTENU_H_MM = 24.0   # hauteur du trèfle visible (le dessin, pas la boîte)
# secours maison (si svglib ou le .svg manquent)
TREFLE_R0 = 6.4
TREFLE_H = 4.8
TREFLE_W = 7.6
TAILLE_CHIFFRE = 18


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── le titre C H A N C E en italique élégant, haut-centre (façon modèle) ──
    gris_trait = colors.Color(0.60, 0.60, 0.60)
    c.setFillColor(colors.Color(0.55, 0.55, 0.55))
    c.setFont("Times-BoldItalic", 13)
    titre_esp = " ".join("CHANCE")
    c.drawCentredString(x0 + CARD_W * 0.50, y0 + CARD_H * 0.80, titre_esp)

    # en-tête : nom + signature + N° de carte
    titre = "CHANCE 6 boules"
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
    c.setFillColor(colors.Color(0.62, 0.62, 0.62)); c.setFont(POLICE, 3.2)
    c.drawRightString(x0 + CARD_W - 13.0 * mm, y0 + 2.2 * mm, "Motif : OpenMoji (CC BY-SA 4.0)")

    # ── les 5 grands numéros en CERCLES ──
    svg = _charger_trefle_svg()
    if svg:
        from reportlab.graphics import renderPDF
        # échelle pour que le CONTENU fasse CONTENU_H_MM de haut
        ech = (CONTENU_H_MM * mm) / (float(svg.height) * (CY1 - CY0))
        b_w = svg.width * ech          # la boîte, plus grande que le dessin
        b_h = svg.height * ech
    for i, (px, py) in enumerate(POSITIONS[:len(nums)]):
        taille = TAILLE_CHIFFRE
        ccx = x0 + CARD_W * px
        cy = y0 + CARD_H * py
        if svg:
            # la boîte est posée pour que le CENTRE DU DESSIN tombe sur (ccx, cy)
            ox = ccx - (CX0 + CX1) / 2.0 * b_w
            oy = cy - (1.0 - (CY0 + CY1) / 2.0) * b_h
            c.saveState()
            c.translate(ox, oy)
            c.scale(ech, ech)
            renderPDF.draw(svg, c, 0, 0)
            c.restoreState()
            # le coeur des 4 feuilles (mesuré sur le dessin)
            ccx_ch = ox + COEUR_X * b_w
            cy_ch = oy + (1.0 - COEUR_Y) * b_h
        else:
            _trefle_maison(c, ccx, cy, gris_trait)
            ccx_ch, cy_ch = ccx, cy
        # le MÉDAILLON au coeur du trèfle : rond blanc finement cerclé,
        # le chiffre y trône sans croquer les feuilles
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.Color(0.58, 0.58, 0.58)); c.setLineWidth(0.5)
        c.ellipse(ccx_ch - 5.4 * mm, cy_ch - 5.4 * mm, ccx_ch + 5.4 * mm, cy_ch + 5.4 * mm, stroke=1, fill=1)
        if _sec:
            _sec.chiffre_micro(c, nums[i], ccx_ch, cy_ch - taille * 0.36, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(ccx_ch, cy_ch - taille * 0.36, str(nums[i]))


    # QR de vérification (anti-duplication) — bas-droit
    if _sec and evenement_id:
        try:
            _q = 8.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.2 * mm, y0 + 1.8 * mm, _q, evenement_id, serie)
        except Exception:
            pass

def _trefle_maison(c, ccx, cy, gris_trait):
    """Le trèfle à 4 feuilles redessiné au propre : quatre coeurs galbés
    pointant vers le centre (pointes sur la clairière du chiffre) et la
    tige courbée en bas-gauche, façon dessin de Maeva."""
    import math as _math
    c.setStrokeColor(gris_trait)
    c.setLineWidth(0.8)
    c.setLineJoin(1)
    for ang in (45, 135, 225, 315):
        a = _math.radians(ang)
        ux, uy = _math.cos(a), _math.sin(a)
        vx, vy = -uy, ux

        def P(t, s):
            """point à t mm du bout de la pointe (vers l'extérieur) et s mm de côté"""
            r = TREFLE_R0 + t
            return (ccx + (r * ux + s * vx) * mm, cy + (r * uy + s * vy) * mm)

        h, w = TREFLE_H, TREFLE_W
        p = c.beginPath()
        p.moveTo(*P(0, 0))
        # flanc gauche : de la pointe au lobe gauche
        p.curveTo(*P(0.28 * h, 0.62 * w), *P(0.86 * h, 0.72 * w), *P(1.06 * h, 0.30 * w))
        # le creux entre les deux lobes
        p.curveTo(*P(1.12 * h, 0.10 * w), *P(0.94 * h, 0.06 * w), *P(0.90 * h, 0.0))
        p.curveTo(*P(0.94 * h, -0.06 * w), *P(1.12 * h, -0.10 * w), *P(1.06 * h, -0.30 * w))
        # flanc droit : retour à la pointe
        p.curveTo(*P(0.86 * h, -0.72 * w), *P(0.28 * h, -0.62 * w), *P(0, 0))
        c.drawPath(p, stroke=1, fill=0)
    # la tige : deux courbes parallèles vers le bas-gauche, façon modèle
    a = _math.radians(252)
    ux, uy = _math.cos(a), _math.sin(a)
    vx, vy = -uy, ux
    r0, r1 = TREFLE_R0 - 1.2, TREFLE_R0 + TREFLE_H + 1.6
    for cote in (-0.55, 0.55):
        p = c.beginPath()
        p.moveTo(ccx + (r0 * ux + cote * vx) * mm, cy + (r0 * uy + cote * vy) * mm)
        p.curveTo(ccx + ((r0 + 3.2) * ux + (cote + 1.1) * vx) * mm, cy + ((r0 + 3.2) * uy + (cote + 1.1) * vy) * mm,
                  ccx + ((r1 - 2.4) * ux + (cote + 2.4) * vx) * mm, cy + ((r1 - 2.4) * uy + (cote + 2.4) * vy) * mm,
                  ccx + (r1 * ux + (cote + 2.9) * vx) * mm, cy + (r1 * uy + (cote + 2.9) * vy) * mm)
        c.drawPath(p, stroke=1, fill=0)
    # le petit bout de la tige
    c.line(ccx + (r1 * ux + (0.55 + 2.9) * vx) * mm, cy + (r1 * uy + (0.55 + 2.9) * vy) * mm,
           ccx + (r1 * ux + (-0.55 + 2.9) * vx) * mm, cy + (r1 * uy + (-0.55 + 2.9) * vy) * mm)


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif=""):
    telephone = (telephone or "").strip() or "89 22 23 05"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    rng = random.Random(961000 + int(serie_start))
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
                zc = sorted(rng.sample(range(31, 46), 2))  # milieu : petit en bas-droite, grand en haut-gauche
                zd = sorted(rng.sample(range(76, 91), 2))  # droite : haut puis bas
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
