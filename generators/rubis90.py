# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur RUBIS 90 (format A4)
12 cartes par feuille A4 (2 colonnes × 6 rangées).
Chaque carte : grille 5 colonnes (R-U-B-I-S) × 3 rangées.
La case CENTRALE (colonne B, rangée du milieu) est toujours VIDE (centre libre).
=> 14 numéros par carton.
Colonnes : R=1-18, U=19-36, B=37-54, I=55-72, S=73-90.
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
LETTERS = ["R", "U", "B", "I", "S"]
RANGES = [(1, 18), (19, 36), (37, 54), (55, 72), (73, 90)]

COLS_PAGE = 2   # 2 cartes par rangée
ROWS_PAGE = 6   # 6 rangées
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

HDR_H = 4 * mm
FOOT_H = 3.5 * mm


def _gen_carte(rng):
    """5 colonnes × 3 rangées. 3 numéros triés par colonne, SAUF la colonne B
    (milieu) qui n'a que 2 numéros : la case centrale (B, rangée 1) est vide.
    Retourne une matrice grille[rangée][colonne] (None = case vide)."""
    cols = []
    for ci, (lo, hi) in enumerate(RANGES):
        if ci == 2:  # colonne B : centre libre -> 2 numéros (rangées 0 et 2)
            nums = sorted(rng.sample(range(lo, hi + 1), 2))
            cols.append([nums[0], None, nums[1]])
        else:
            nums = sorted(rng.sample(range(lo, hi + 1), 3))
            cols.append([nums[0], nums[1], nums[2]])
    # transposer en grille[rangée][colonne]
    grille = [[cols[c][r] for c in range(5)] for r in range(3)]
    return grille


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = len(LETTERS)
    cell_w = CARD_W / ncols

    # Bordure
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # Bandeau titre
    bandeau = (titre_jeu or "RUBIS 90")
    if telephone:
        bandeau += " by TUKEA " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.5)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 2.5 * mm, bandeau[:64])

    # En-tête lettres R-U-B-I-S
    hdr_y = y0 + CARD_H - HDR_H - 2.5 * mm
    c.setFillColor(col); c.setFont(POLICE, 6)
    for i, lettre in enumerate(LETTERS):
        c.drawCentredString(x0 + (i + 0.5) * cell_w, hdr_y + 1.2 * mm, lettre)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_y, x0 + CARD_W, hdr_y)

    # Zone des numéros (3 rangées)
    grid_top = hdr_y
    grid_bot = y0 + FOOT_H
    grid_h = grid_top - grid_bot
    row_h = grid_h / 3

    # séparateurs de colonnes
    c.setStrokeColor(colors.Color(0.85, 0.85, 0.85)); c.setLineWidth(0.3)
    for i in range(1, ncols):
        c.line(x0 + i * cell_w, grid_bot, x0 + i * cell_w, grid_top)

    # contenu
    for r in range(3):
        for cc in range(ncols):
            val = grille[r][cc]
            if val is None:
                # case centrale vide -> on y place le QR de vérification
                if _sec and evenement_id:
                    try:
                        cx = x0 + (cc + 0.5) * cell_w
                        cy = grid_top - (r + 0.5) * row_h
                        _q = min(cell_w, row_h) - 2.0 * mm
                        _q = max(5.0 * mm, _q)
                        _sec.carton_qr(c, cx - _q / 2, cy - _q / 2, _q, evenement_id, serie)
                    except Exception:
                        pass
                continue
            cx = x0 + (cc + 0.5) * cell_w
            taille = 34  # gros chiffres au maximum
            cy = grid_top - (r + 0.5) * row_h - taille * 0.36
            if _sec:
                _sec.chiffre_micro(c, val, cx, cy, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cy, str(val))

    # Pied
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, "N° SÉRIE")
    c.setFillColor(col); c.setFont("Helvetica", 6)
    c.drawRightString(x0 + CARD_W - 1.5 * mm, y0 + 1.3 * mm, "%06d" % serie)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(90000 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    faites = 0

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 9)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 7.2 * mm, "Page %d" % no_page)

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
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="RUBIS 90",
                      telephone="89.22.23.05")
    with open("test_rubis.pdf", "wb") as f:
        f.write(pdf.read())
    print("RUBIS 90 généré")
