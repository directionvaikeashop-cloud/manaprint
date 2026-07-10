# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur BROWN 8 BOULES (format A4)
8 cartes par feuille A4 (2 colonnes × 4 rangées).
Chaque carte : grille 3×5 B·R·O·W·N, 8 numéros placés en quinconce, N° de série au centre.
Plages : B 1-15, R 16-30, O 31-45, W 46-60, N 61-75.
Disposition des numéros :
  rangée haute : B  ·  O  ·  N      (colonnes 0,2,4)
  rangée milieu:    R · (série) · W (colonnes 1,3 + centre = série)
  rangée basse : B  ·  O  ·  N      (colonnes 0,2,4)
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris 40%.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les cartons sortent normalement, simplement sans microtexte.
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
GRIS40 = colors.Color(0.60, 0.60, 0.60)        # chiffres
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)    # lignes de grille



# ══ DEUX GAMMES COMMERCIALES (vision Maeva) ══════════════════════════
# ÉCO      : écriture fine DejaVu ExtraLight, gris 0,50 — économie de toner
# PREMIUM  : écriture grasse Helvetica-Bold, gris 0,55 — style P15
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
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4
LETTERS = ["B", "R", "O", "W", "N"]
# (lettre, min, max, nb de numéros)
PLAGES = [("B", 1, 15, 2), ("R", 16, 30, 1), ("O", 31, 45, 2), ("W", 46, 60, 1), ("N", 61, 75, 2)]

COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """Numéros distincts par colonne (2 pour B/O/N, 1 pour R/W)."""
    return {lettre: sorted(rng.sample(range(a, b + 1), n)) for lettre, a, b, n in PLAGES}


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 5
    cell_w = CARD_W / ncols

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête B R O W N
    hdr_y = y0 + CARD_H - 6 * mm
    c.setFont(POLICE, 11)
    for i, lettre in enumerate(LETTERS):
        c.setFillColor(col)
        c.drawCentredString(x0 + (i + 0.5) * cell_w, hdr_y, lettre)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0 + 1.5 * mm, hdr_y - 2 * mm, x0 + CARD_W - 1.5 * mm, hdr_y - 2 * mm)

    # Grille 3 rangées × 5 colonnes
    grid_top = hdr_y - 2 * mm
    grid_bot = y0 + 2.5 * mm
    grid_h = grid_top - grid_bot
    row_h = grid_h / 3

    # séparateurs colonnes
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
    for i in range(1, ncols):
        c.line(x0 + i * cell_w, grid_bot, x0 + i * cell_w, grid_top)
    # séparateurs rangées
    for r in range(1, 3):
        yy = grid_top - r * row_h
        c.line(x0 + 1.5 * mm, yy, x0 + CARD_W - 1.5 * mm, yy)

    # placement des 8 numéros (motif quinconce) + série au centre
    #   r=0 (haut) : B(0), O(2), N(4)  -> index 0 de la colonne
    #   r=1 (mil.) : R(1), W(3) ; centre (col 2) = série
    #   r=2 (bas)  : B(0), O(2), N(4)  -> index 1 de la colonne
    def cy(r):
        return grid_top - (r + 0.5) * row_h

    def cx(i):
        return x0 + (i + 0.5) * cell_w

    if _sec:  # chiffres "billet de banque" remplis de microtexte
        for (i, lettre) in [(0, "B"), (2, "O"), (4, "N")]:
            _sec.chiffre_micro(c, carte[lettre][0], cx(i), cy(0) - 11, 32, gris_ch, police_ch)
        _sec.chiffre_micro(c, carte["R"][0], cx(1), cy(1) - 11, 32, gris_ch, police_ch)
        _sec.chiffre_micro(c, carte["W"][0], cx(3), cy(1) - 11, 32, gris_ch, police_ch)
    else:
        c.setFont(police_ch, 32)
        # rangée haute
        for (i, lettre) in [(0, "B"), (2, "O"), (4, "N")]:
            c.setFillColor(gris_ch)
            c.drawCentredString(cx(i), cy(0) - 11, str(carte[lettre][0]))
        # rangée milieu : R et W
        c.setFillColor(gris_ch)
        c.drawCentredString(cx(1), cy(1) - 11, str(carte["R"][0]))
        c.drawCentredString(cx(3), cy(1) - 11, str(carte["W"][0]))
    # centre = série
    c.setFillColor(GRIS); c.setFont(POLICE, 6)
    c.drawCentredString(cx(2), cy(1) - 2, "%06d" % serie)
    # rangée basse
    if _sec:
        for (i, lettre) in [(0, "B"), (2, "O"), (4, "N")]:
            _sec.chiffre_micro(c, carte[lettre][1], cx(i), cy(2) - 11, 32, gris_ch, police_ch)
    else:
        c.setFont(police_ch, 32)
        for (i, lettre) in [(0, "B"), (2, "O"), (4, "N")]:
            c.setFillColor(gris_ch)
            c.drawCentredString(cx(i), cy(2) - 11, str(carte[lettre][1]))

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            # 🎯 QR intégré : case vide fixe du quinconce (rangée basse, colonne W)
            _q = 12.5 * mm
            _xq = x0 + 3 * cell_w + (cell_w - _q) / 2
            _yq = grid_bot + (row_h - _q - 3.4 * mm) / 2 + 3.4 * mm
            _sec.carton_qr(c, _xq, _yq, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(680000 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    faites = 0

    for _ in range(nb_pages):
        # En-tête de page
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 10)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        ligne2 = (titre_jeu or "BROWN 8 boules")
        if date_lieu:
            ligne2 += "  ·  " + date_lieu
        ligne2 += "  ·  Page %d" % no_page
        c.setFillColor(GRIS); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 7.5 * mm, ligne2)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, carte, coul, serie, telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=8, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="GRAND LOTO",
                      date_lieu="20 déc 2026", telephone="87 12 34 56")
    with open("test_brown.pdf", "wb") as f:
        f.write(pdf.read())
    print("BROWN 8 boules généré")
