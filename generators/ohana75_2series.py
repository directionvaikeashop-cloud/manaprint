# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur OHANA 75 · 2 SÉRIES (format A4)
2 cartes (séries) par feuille A4, séparées par un trait de découpe.
Chaque carte : grille 5×5 B·I·N·G·O, 2 numéros par case (un grand entouré + un petit),
case centrale FREE avec le N° de série. Règle MARATHON.
Plages : B 1-15, I 16-30, N 31-45, G 46-60, O 61-75.
Couleur arc-en-ciel (par carte) ou gris (économie d'encre). Personnalisation + responsable.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Police fine (look OHANA) avec repli Helvetica
try:
    pdfmetrics.registerFont(TTFont("DJL", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    POLICE = "DJL"
except Exception:
    POLICE = "Helvetica"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
NOIR = colors.black
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS40 = colors.Color(0.60, 0.60, 0.60)   # gris 40% (économie d'encre) — pour les chiffres
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)

PAGE_W, PAGE_H = A4
PLAGES = [("B", 1, 15), ("I", 16, 30), ("N", 31, 45), ("G", 46, 60), ("O", 61, 75)]

MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_Y = 7 * mm   # espace de découpe entre les 2 cartes

CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - GUTTER_Y) / 2


def _gen_carte(rng):
    """Pour chaque colonne : 5 cases (4 pour N) de 2 numéros distincts, triés dans la case."""
    carte = {}
    for lettre, a, b in PLAGES:
        n_cases = 4 if lettre == "N" else 5
        nums = rng.sample(range(a, b + 1), n_cases * 2)
        carte[lettre] = [sorted(nums[i * 2:i * 2 + 2]) for i in range(n_cases)]
    return carte


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", no_page=1):
    col = colors.HexColor(couleur_hex)
    ncols = 5
    cell_w = CARD_W / ncols

    # Bordure carte
    c.setStrokeColor(col)
    c.setLineWidth(1.0)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2 * mm, stroke=1, fill=0)

    # Bandeau haut (sécurité : nom du jeu + tournoi + n° carte, sur chaque grille)
    bandeau = "OHANA 75"
    if titre_jeu:
        bandeau += "  —  " + titre_jeu
    c.setFillColor(GRIS); c.setFont(POLICE, 6)
    c.drawString(x0 + 4 * mm, y0 + CARD_H - 5 * mm, bandeau[:60])
    c.drawRightString(x0 + CARD_W - 4 * mm, y0 + CARD_H - 5 * mm,
                      "Page %d  ·  Carte N° %05d" % (no_page, serie))

    # En-tête des colonnes B I N G O
    hdr_base = y0 + CARD_H - 14 * mm
    for i, (lettre, a, b) in enumerate(PLAGES):
        cx = x0 + (i + 0.5) * cell_w
        if lettre == "G":
            c.setFillColor(col); c.setFont(POLICE, 5.5)
            c.drawCentredString(cx, hdr_base + 6.5 * mm, "MARATHON")
        c.setFillColor(col); c.setFont(POLICE, 16)
        c.drawCentredString(cx, hdr_base + 0.5 * mm, lettre)
    # ligne sous l'en-tête
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.line(x0 + 2 * mm, hdr_base - 2 * mm, x0 + CARD_W - 2 * mm, hdr_base - 2 * mm)

    # Grille des numéros
    grid_top = hdr_base - 2 * mm
    grid_bot = y0 + 6 * mm
    grid_h = grid_top - grid_bot
    row_h = grid_h / 5
    r_cercle = min(cell_w, row_h) * 0.35

    for j in range(5):          # rangées (0 = haut)
        cy = grid_top - (j + 0.5) * row_h
        for i, (lettre, a, b) in enumerate(PLAGES):
            cell_x = x0 + i * cell_w
            cxc = cell_x + cell_w * 0.33   # centre du rond (gros numéro)
            cx2 = cell_x + cell_w * 0.74   # petit numéro

            # séparateurs de colonnes
            if i > 0:
                c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
                c.line(cell_x, grid_bot, cell_x, grid_top)

            # Case centrale = FREE + série
            if i == 2 and j == 2:
                c.setFillColor(col); c.setFont(POLICE, 7)
                c.drawCentredString(cell_x + cell_w / 2, cy + 3.2 * mm, "FREE")
                c.setFillColor(GRIS); c.setFont(POLICE, 6)
                c.drawCentredString(cell_x + cell_w / 2, cy - 0.3 * mm, "%05d" % serie)
                c.setFillColor(col); c.setFont(POLICE, 7)
                c.drawCentredString(cell_x + cell_w / 2, cy - 4 * mm, "SPACE")
                continue

            # 2 numéros de la case
            idx = j if i != 2 else (j if j < 2 else j - 1)  # N saute la case centrale
            paire = carte[lettre][idx]
            n1, n2 = paire[0], paire[1]

            # Gros numéro entouré
            c.setStrokeColor(col); c.setLineWidth(1.0)
            c.circle(cxc, cy, r_cercle, stroke=1, fill=0)
            c.setFillColor(GRIS40); c.setFont(POLICE, 32)
            c.drawCentredString(cxc, cy - 11, str(n1))
            # Petit numéro
            c.setFillColor(GRIS40); c.setFont(POLICE, 28)
            c.drawCentredString(cx2, cy - 10, str(n2))

        # séparateur de rangée
        if j > 0:
            yy = grid_top - j * row_h
            c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
            c.line(x0 + 2 * mm, yy, x0 + CARD_W - 2 * mm, yy)

    # Pied : série + responsable
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.line(x0 + 2 * mm, grid_bot, x0 + CARD_W - 2 * mm, grid_bot)
    c.setFillColor(GRIS); c.setFont(POLICE, 5.5)
    c.drawString(x0 + 4 * mm, y0 + 2 * mm, "N° %06d" % serie)
    if telephone:
        c.drawRightString(x0 + CARD_W - 4 * mm, y0 + 2 * mm, "Resp. " + telephone)


def generer_pdf(nb_cartes=2, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = 2
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(750000 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    encre = NOIR if couleur else GRIS
    faites = 0

    for _ in range(nb_pages):
        # En-tête de page (événement)
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont(POLICE, 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 6 * mm, nom_evenement)
        ligne2 = (titre_jeu or "OHANA 75 — 2 séries")
        if date_lieu:
            ligne2 += "  ·  " + date_lieu
        c.setFillColor(GRIS); c.setFont(POLICE, 6.5)
        if nom_evenement:
            c.drawCentredString(PAGE_W / 2, PAGE_H - 9 * mm, ligne2)

        for slot in range(par_page):
            if faites >= nb_cartes:
                break
            # carte du haut (slot 0) puis du bas (slot 1)
            y0 = MARGIN_BOT + (1 - slot) * (CARD_H + GUTTER_Y)
            x0 = MARGIN_X
            carte = _gen_carte(rng)
            coul = (couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
            _dessiner_carte(c, x0, y0, carte, coul, serie, encre, telephone, titre_jeu, no_page)
            serie += 1
            faites += 1

        # trait de découpe pointillé entre les 2 cartes
        c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.5); c.setDash(3, 3)
        yc = MARGIN_BOT + CARD_H + GUTTER_Y / 2
        c.line(MARGIN_X, yc, PAGE_W - MARGIN_X, yc)
        c.setDash()

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


# ── Deux variantes pour le registre : Couleur (arc-en-ciel) et Noir & Blanc ──
def generer_couleur(**kwargs):
    """OHANA 75 2 séries — version COULEUR (ronds et lettres arc-en-ciel)."""
    kwargs["couleur"] = True
    return generer_pdf(**kwargs)


def generer_nb(**kwargs):
    """OHANA 75 2 séries — version NOIR & BLANC (tout en gris, économie d'encre)."""
    kwargs["couleur"] = False
    return generer_pdf(**kwargs)


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=2, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="GRAND LOTO OHANA",
                      date_lieu="20 déc 2026", telephone="87 12 34 56")
    with open("test_ohana_2series.pdf", "wb") as f:
        f.write(pdf.read())
    print("OHANA 75 2 séries généré")
