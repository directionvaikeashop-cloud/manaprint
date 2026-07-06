"""
MANAPRINT — Générateur ALOHA 75 (format A4)
12 cartes par feuille (2 colonnes × 6 rangées).
Chaque carte : 5 colonnes A·L·O·H·A, 2 numéros par colonne.
Plages : A 1-15, L 16-30, O 31-45, H 46-60, A 61-75.
Couleur arc-en-ciel (chiffres noirs) ou gris 40%. Personnalisation + téléphone responsable.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les cartons sortent normalement, simplement sans microtexte.
try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None


RAINBOW = [
    "#E53935", "#FF7043", "#FB8C00", "#F9A825",
    "#43A047", "#00ACC1", "#1E88E5", "#3949AB",
    "#8E24AA", "#D81B60", "#6D4C41", "#546E7A",
]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)

PAGE_W, PAGE_H = A4

COLS_PAGE = 2   # 2 cartes par rangée
ROWS_PAGE = 6   # 6 rangées
MARGIN_X = 8 * mm
MARGIN_TOP = 12 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

LETTERS = ["A", "L", "O", "H", "A"]
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
HDR_H = 4 * mm
FOOT_H = 3.5 * mm


def _gen_carte():
    """5 colonnes, 2 numéros distincts triés par colonne."""
    return [sorted(random.sample(range(lo, hi + 1), 2)) for (lo, hi) in RANGES]


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre, telephone="", titre_jeu="", nom_jeu="ALOHA 75"):
    col = colors.HexColor(couleur_hex)
    ncols = len(LETTERS)
    cell_w = CARD_W / ncols

    # Bordure
    c.setStrokeColor(col)
    c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # Mini-bandeau : nom du jeu + nom du tournoi (sécurité, sur chaque grille)
    bandeau = nom_jeu
    if titre_jeu:
        bandeau += "  —  " + titre_jeu
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 2.5 * mm, bandeau[:60])

    # Header lettres
    hdr_y = y0 + CARD_H - HDR_H - 2.5 * mm
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", 8)
    for i, lettre in enumerate(LETTERS):
        c.drawCentredString(x0 + (i + 0.5) * cell_w, hdr_y + 1.4 * mm, lettre)
    c.setStrokeColor(col)
    c.setLineWidth(0.4)
    c.line(x0, hdr_y, x0 + CARD_W, hdr_y)

    # Zone des numéros (2 lignes)
    zone_h = (CARD_H - 2.5 * mm) - HDR_H - FOOT_H
    for i, nums in enumerate(carte):
        cx = x0 + (i + 0.5) * cell_w
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, nums[0], cx, y0 + FOOT_H + zone_h * 0.55, 26, encre, "Helvetica-Bold")
            _sec.chiffre_micro(c, nums[1], cx, y0 + FOOT_H + zone_h * 0.12, 26, encre, "Helvetica-Bold")
        else:
            c.setFillColor(encre)
            c.setFont("Helvetica-Bold", 26)
            c.drawCentredString(cx, y0 + FOOT_H + zone_h * 0.55, str(nums[0]))
            c.drawCentredString(cx, y0 + FOOT_H + zone_h * 0.12, str(nums[1]))
        if i > 0:
            c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))
            c.setLineWidth(0.3)
            c.line(x0 + i * cell_w, y0 + FOOT_H, x0 + i * cell_w, hdr_y)

    # Pied : N° série à gauche + responsable à droite (sur chaque grille)
    c.setStrokeColor(col)
    c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, f"N° {serie:06d}")
    if telephone:
        c.drawRightString(x0 + CARD_W - 1.5 * mm, y0 + 1.3 * mm, f"Resp. {telephone}")


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    serie = serie_start
    no_page = 1
    encre = NOIR if couleur else GRIS40

    for _ in range(nb_pages):
        # En-tête de page
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        titre_aff = titre_jeu if titre_jeu else "ALOHA 75"
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
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre, telephone, titre_jeu, "ALOHA 75")
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="GRAND LOTO",
                      date_lieu="20 déc 2026", telephone="87 12 34 56")
    with open("test_aloha.pdf", "wb") as f:
        f.write(pdf.read())
    print("ALOHA 75 généré")
