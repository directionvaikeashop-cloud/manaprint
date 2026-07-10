# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur WOW 4 (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : grille 2 colonnes (W, O) × 2 rangées = 4 numéros.
En-têtes de colonnes avec plages affichées : W (30-44) et O (45-60).
Numéro de série EN PIED ("N° SÉRIE ... 000001").
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris (2 gammes ÉCO/PREMIUM).
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne
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

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GREY = colors.Color(0.60, 0.60, 0.60)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)


# ══ DEUX GAMMES COMMERCIALES ══════════════════════════
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TF
try:
    _pm.registerFont(_TF("DJLECO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    _POLICE_ECO = "DJLECO"
except Exception:
    _POLICE_ECO = "Helvetica"
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)
_POLICE_P15 = "Helvetica-Bold"
_GRIS_P15 = colors.Color(0.55, 0.55, 0.55)

def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4
# En-têtes de colonnes W / O avec leurs plages
LETTERS = ["W", "O"]
RANGES = [(30, 44), (45, 60)]

COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """2 colonnes (W, O) × 2 numéros triés. grille[rangée][colonne]."""
    w = sorted(rng.sample(range(RANGES[0][0], RANGES[0][1] + 1), 2))
    o = sorted(rng.sample(range(RANGES[1][0], RANGES[1][1] + 1), 2))
    grille = [
        [w[0], o[0]],
        [w[1], o[1]],
    ]
    return grille


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 2

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête colonnes W / O avec plages
    hdr_y = y0 + CARD_H - 5 * mm
    cell_w = CARD_W / ncols
    for i, lettre in enumerate(LETTERS):
        cx = x0 + (i + 0.5) * cell_w
        c.setFillColor(col); c.setFont(POLICE, 7)
        c.drawCentredString(cx, hdr_y, lettre)
        lo, hi = RANGES[i]
        c.setFillColor(GREY); c.setFont(POLICE, 4)
        c.drawCentredString(cx, hdr_y - 2.6 * mm, "%d - %d" % (lo, hi))
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_y - 3.8 * mm, x0 + CARD_W, hdr_y - 3.8 * mm)

    # Zone des numéros (2 colonnes × 2 rangées)
    grid_top = hdr_y - 3.8 * mm
    grid_bot = y0 + 21 * mm  # 📏 bande dédiée en bas : le QR y vit, la grille au-dessus
    grid_h = grid_top - grid_bot
    row_h = grid_h / 2

    # séparateur de colonnes
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
    c.line(x0 + cell_w, grid_bot, x0 + cell_w, grid_top)
    c.line(x0 + 1.5 * mm, grid_top - row_h, x0 + CARD_W - 1.5 * mm, grid_top - row_h)

    # contenu
    for r in range(2):
        for cc in range(2):
            cx = x0 + (cc + 0.5) * cell_w
            cyc = grid_top - (r + 0.5) * row_h
            val = grille[r][cc]
            if _sec:
                _sec.chiffre_micro(c, val, cx, cyc - 11, 32, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, 32)
                c.drawCentredString(cx, cyc - 11, str(val))

    # Pied : N° SÉRIE
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + 4.5 * mm, x0 + CARD_W, y0 + 4.5 * mm)
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 2 * mm, y0 + 1.5 * mm, "N° SÉRIE")
    c.setFillColor(col); c.setFont("Helvetica", 6)
    c.drawRightString(x0 + CARD_W - 2 * mm, y0 + 1.5 * mm, "%06d" % serie)

    # QR de vérification par grille — coin bas-droit (au-dessus du pied)
    if _sec and evenement_id:
        try:
            # 🎯 QR dans la bande dédiée (aucun chiffre dérangé)
            _q = 13.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.0 * mm, y0 + 6.0 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(400000 + int(serie_start))
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
                grille = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, grille, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="WOW 4",
                      telephone="89.22.23.05")
    with open("test_wow.pdf", "wb") as f:
        f.write(pdf.read())
    print("WOW 4 généré")
