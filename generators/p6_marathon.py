"""
MANAPRINT — Générateur P6 MARATHON (format A4)
6 cartes par feuille (2 colonnes × 3 rangées).
Chaque carte : 5 colonnes B·I·N·G·O, grille 5×5, case centrale "MARATHON" libre.
Plages : B 1-15, I 16-30, N 31-45, G 46-60, O 61-75.
N° série dans le header (colonne N). Responsable sur chaque grille.
Couleur arc-en-ciel (chiffres noirs) ou gris 40%.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

RAINBOW = [
    "#E53935", "#FF7043", "#FB8C00", "#F9A825",
    "#43A047", "#00ACC1", "#1E88E5", "#3949AB",
    "#8E24AA", "#D81B60", "#6D4C41", "#546E7A",
]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)

PAGE_W, PAGE_H = A4

COLS_PAGE = 2
ROWS_PAGE = 3
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

LETTERS = ["B", "I", "N", "G", "O"]
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
HDR_H = 4.5 * mm
FOOT_H = 3 * mm
GRID_N = 5  # 5x5


def _gen_carte():
    """5 colonnes × 5 numéros distincts triés. Case centrale (col N, ligne 2) = MARATHON."""
    cols = []
    for (lo, hi) in RANGES:
        cols.append(sorted(random.sample(range(lo, hi + 1), GRID_N)))
    return cols


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre, telephone="", titre_jeu=""):
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / GRID_N

    # Bordure
    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.8 * mm, stroke=1, fill=0)

    # Mini-bandeau : nom du jeu + nom du tournoi (sécurité)
    bandeau = "P6 MARATHON"
    if titre_jeu:
        bandeau += "  —  " + titre_jeu
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 2.3 * mm, bandeau[:60])

    # Header : lettres B I N G O centrées dans chaque colonne
    hdr_y = y0 + CARD_H - HDR_H - 2.3 * mm
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", 10)
    for i, lettre in enumerate(LETTERS):
        cx = x0 + (i + 0.5) * cell_w
        c.drawCentredString(cx, hdr_y + 1.4 * mm, lettre)

    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_y, x0 + CARD_W, hdr_y)

    # Grille 5×5
    zone_h = CARD_H - HDR_H - FOOT_H - 2.3 * mm
    cell_h = zone_h / GRID_N
    for ci, nums in enumerate(carte):
        cx = x0 + (ci + 0.5) * cell_w
        for ri in range(GRID_N):
            cy = y0 + FOOT_H + (GRID_N - 1 - ri) * cell_h + cell_h * 0.30
            # case centrale (colonne N=2, ligne du milieu ri=2) = MARATHON
            if ci == 2 and ri == 2:
                c.setFillColor(col); c.setFont("Helvetica-Bold", 5)
                c.drawCentredString(cx, cy + cell_h * 0.14, "MARA")
                c.drawCentredString(cx, cy - cell_h * 0.14, "THON")
            else:
                c.setFillColor(encre); c.setFont("Helvetica-Bold", 27)
                c.drawCentredString(cx, cy, str(nums[ri]))
        if ci > 0:
            c.setStrokeColor(colors.Color(0.85, 0.85, 0.85)); c.setLineWidth(0.3)
            c.line(x0 + ci * cell_w, y0 + FOOT_H, x0 + ci * cell_w, hdr_y)

    # Pied : N° série + responsable sur chaque grille
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, f"N° {serie:06d}")
    if telephone:
        c.drawRightString(x0 + CARD_W - 1.5 * mm, y0 + 1.3 * mm, f"Resp. {telephone}")


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    serie = serie_start
    no_page = 1
    encre = NOIR if couleur else GRIS40

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        titre_aff = titre_jeu if titre_jeu else "P6 MARATHON"
        ligne2 = titre_aff
        if date_lieu: ligne2 += "  ·  " + date_lieu
        ligne2 += f"  ·  Page {no_page}"
        c.setFillColor(GREY); c.setFont("Helvetica", 7)
        y2 = (PAGE_H - 8.5 * mm) if nom_evenement else (PAGE_H - 6 * mm)
        c.drawCentredString(PAGE_W / 2, y2, ligne2)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#999999")
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre, telephone, titre_jeu)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="GRAND LOTO",
                      date_lieu="20 déc 2026", telephone="87 12 34 56")
    with open("test_p6.pdf", "wb") as f:
        f.write(pdf.read())
    print("P6 MARATHON généré")
