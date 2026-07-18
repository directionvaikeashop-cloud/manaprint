# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur NGO 8 BOULES (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : grille 3 colonnes (B-N-O) × 3 rangées.
La case CENTRALE (colonne du milieu, rangée du milieu) est toujours VIDE
et accueille le QR de vérification. => 8 numéros par carton.
Colonnes : N=31-45, G=46-60, O=61-75 (colonnes N, G, O du bingo).
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
GRIS = colors.Color(0.42, 0.42, 0.42)
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
# (min, max) par colonne — NGO 8 boules (colonnes B, N, O du bingo)
PLAGES = [(31, 45), (46, 60), (61, 75)]

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
    """8 numéros : col1 = 3 nums, col3 = 3 nums, col2 (milieu) = 2 nums.
    La case centrale (col2, rangée 1) est vide -> accueille le QR."""
    col1 = sorted(rng.sample(range(PLAGES[0][0], PLAGES[0][1] + 1), 3))
    col3 = sorted(rng.sample(range(PLAGES[2][0], PLAGES[2][1] + 1), 3))
    col2n = sorted(rng.sample(range(PLAGES[1][0], PLAGES[1][1] + 1), 2))
    col2 = [col2n[0], None, col2n[1]]  # centre vide
    grille = [
        [col1[0], col2[0], col3[0]],
        [col1[1], None,    col3[1]],   # centre vide
        [col1[2], col2[2], col3[2]],
    ]
    return grille


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 3

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête (titre)
    hdr_y = y0 + CARD_H - 3.5 * mm
    titre = "NGO 8 boules"
    if titre_jeu and "NGO" not in titre_jeu.strip().upper():
        titre = "NGO 8 boules \u00b7 " + titre_jeu.strip()   # le nom du jeu TOUJOURS affiché (décision Maeva)
    elif titre_jeu:
        titre = titre_jeu.strip()
    if telephone:
        titre += " by TUKEA " + telephone
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y, titre[:64])

    # En-tête colonnes N - G - O
    cell_w = CARD_W / ncols
    lettres_y = hdr_y - 4 * mm
    for i, lettre in enumerate(["N", "G", "O"]):
        c.setFillColor(col); c.setFont(POLICE, 6.5)
        c.drawCentredString(x0 + (i + 0.5) * cell_w, lettres_y, lettre)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, lettres_y - 1.5 * mm, x0 + CARD_W, lettres_y - 1.5 * mm)

    # Zone grille 3×3
    grid_top = lettres_y - 1.5 * mm
    grid_bot = y0 + 5 * mm
    grid_h = grid_top - grid_bot
    row_h = grid_h / 3

    # séparateurs de grille
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
    for i in range(1, ncols):
        c.line(x0 + i * cell_w, grid_bot, x0 + i * cell_w, grid_top)
    for r in range(1, 3):
        yy = grid_top - r * row_h
        c.line(x0 + 1.5 * mm, yy, x0 + CARD_W - 1.5 * mm, yy)

    # contenu
    for r in range(3):
        for cc in range(3):
            cx = x0 + (cc + 0.5) * cell_w
            cyc = grid_top - (r + 0.5) * row_h
            val = grille[r][cc]
            if val is None:
                # case centrale vide (r==1, cc==1) -> QR ; les autres None restent vides
                if r == 1 and cc == 1 and _sec and evenement_id:
                    try:
                        _q = min(cell_w, row_h) - 2.5 * mm
                        _q = max(5.0 * mm, _q)
                        _sec.carton_qr(c, cx - _q / 2, cyc - _q / 2, _q, evenement_id, serie)
                    except Exception:
                        pass
                continue
            if _sec:
                _sec.chiffre_micro(c, val, cx, cyc - 11, 32, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, 32)
                c.drawCentredString(cx, cyc - 11, str(val))

    # Pied : N° SÉRIE (comme la référence NGO)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + 4.5 * mm, x0 + CARD_W, y0 + 4.5 * mm)
    c.setFillColor(GRIS_CLAIR); c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 2 * mm, y0 + 1.5 * mm, "N° SÉRIE")
    c.setFillColor(col); c.setFont("Helvetica", 6)
    c.drawRightString(x0 + CARD_W - 2 * mm, y0 + 1.5 * mm, "%06d" % serie)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(700000 + int(serie_start))
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
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="NGO 8 boules",
                      telephone="87048221")
    with open("test_bno.pdf", "wb") as f:
        f.write(pdf.read())
    print("NGO 8 boules généré")
