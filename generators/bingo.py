"""
MANAPRINT — Générateur de cartes PDF (ReportLab)
"""
import io
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas

PROGRAMMES = {
    "p6":       {"nom": "Programme P6",      "size": 6, "couleur": (0.18, 0.43, 0.39)},
    "ohana75":  {"nom": "OHANA 75",          "size": 5, "couleur": (0.83, 0.40, 0.24)},
    "quines90": {"nom": "QUINES 90",         "size": 5, "couleur": (0.10, 0.29, 0.26)},
    "petits":   {"nom": "Pack Petits Jeux",  "size": 4, "couleur": (0.55, 0.35, 0.17)},
}

MOTS_DEFAUT = [
    "Himene", "Ori", "Tiare", "Pahu", "Fenua", "Vahine", "Pareu", "Marae",
    "Hei", "Motu", "Reo", "Tama", "Haka", "Mana", "Pape", "Fare", "Tahua",
    "Va'a", "Tumu", "Tapu", "Niau", "Atua", "Hiva", "Tane", "'Ura", "Moana",
    "Honu", "Tiki", "Heiva", "Aroha", "Nui", "Rahi", "Vai", "Ao", "Po",
]


def _grille(mots, size):
    pool = mots[:] if len(mots) >= size * size else (mots * (size * size // len(mots) + 1))
    random.shuffle(pool)
    cells = pool[:size * size]
    if size % 2 == 1:
        cells[(size * size) // 2] = "★"
    return cells


def generer_pdf(programme="ohana75", theme="", mots=None, nb_cartes=1):
    if programme not in PROGRAMMES:
        programme = "ohana75"
    conf = PROGRAMMES[programme]
    size = conf["size"]
    r, g, b = conf["couleur"]
    mots = mots or MOTS_DEFAUT

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    page_w, page_h = A4

    for n in range(nb_cartes):
        cells = _grille(mots, size)

        marge = 20 * mm
        grille_w = page_w - 2 * marge
        cell_size = grille_w / size
        top = page_h - 45 * mm

        c.setFillColorRGB(r, g, b)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(page_w / 2, page_h - 25 * mm, conf["nom"].upper())

        if theme:
            c.setFillColorRGB(0.4, 0.4, 0.4)
            c.setFont("Helvetica-Oblique", 11)
            c.drawCentredString(page_w / 2, page_h - 33 * mm, theme)

        y_grid_top = top
        if size == 5:
            c.setFillColorRGB(r, g, b)
            c.setFont("Helvetica-Bold", 16)
            for i, lettre in enumerate("BINGO"):
                x = marge + i * cell_size + cell_size / 2
                c.drawCentredString(x, top + 4 * mm, lettre)

        for idx, mot in enumerate(cells):
            row = idx // size
            col = idx % size
            x = marge + col * cell_size
            y = y_grid_top - (row + 1) * cell_size

            est_libre = (mot == "★")
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.5)
            if est_libre:
                c.setFillColorRGB(r, g, b)
                c.rect(x, y, cell_size, cell_size, stroke=1, fill=1)
                c.setFillColorRGB(1, 1, 1)
                c.setFont("Helvetica-Bold", 20)
                c.drawCentredString(x + cell_size / 2, y + cell_size / 2 - 6, "★")
            else:
                c.rect(x, y, cell_size, cell_size, stroke=1, fill=0)
                c.setFillColorRGB(0.25, 0.25, 0.25)
                fs = 11 if len(mot) <= 6 else 9 if len(mot) <= 9 else 7
                c.setFont("Helvetica", fs)
                c.drawCentredString(x + cell_size / 2, y + cell_size / 2 - fs / 3, mot)

        c.setFillColorRGB(0.7, 0.7, 0.7)
        c.setFont("Helvetica", 7)
        c.drawCentredString(page_w / 2, 15 * mm, f"manaprint.pf  ·  2KEA  ·  Carte {n + 1}")
        c.showPage()

    c.save()
    buf.seek(0)
    return buf
