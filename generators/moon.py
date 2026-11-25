# -*- coding: utf-8 -*-
"""MANAPRINT — MOON (maquette CANVA de Maeva, 25/11/2026, « moon_canva_12_A4 »).
Reprise TELLE QUELLE : 12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées),
traits de coupe en pointillés. Chaque billet : cadre arrondi, pastille « N° » + série,
titre MOON entre deux étoiles, le croissant de lune, les étoiles des côtés le long de
deux filets pointillés, 8 cases à coins ronds (2 rangées x 4 colonnes).
RÈGLE (inchangée), 2 numéros par colonne, le petit en haut :
   M 1-15 · O 16-30 · O 46-60 · N 61-75   ->   le 31-45 n'existe pas, crieur 1-30 et 46-75.
Chiffres comme la maquette : écriture à empattements (Times), 30 pt (le maximum).
Le tout est réduit pour garder 6 mm de marge d'impression (Konica / Sharp)."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors

PAGE_W, PAGE_H = landscape(A4)
COLS, RANGS = 3, 4
CARTES_PAGE = COLS * RANGS                # 12
CELL_W, CELL_H = 280.6299, 148.8189
NOIR = colors.black
GRIS = colors.Color(.45, .45, .45)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
POLICE_NUM, T_NUM = "Times-Roman", 30     # comme la maquette (Liberation Serif 30 pt)

_ICI = _os.path.dirname(_os.path.abspath(__file__))
def _png(k):
    return _os.path.join(_ICI, "moon_v2_%s.png" % k)
DECOR = [  # (image, x, y, l, h) — relevés sur la maquette
    ("etoile_g1", 3.541513, 17.00787, 11.62564, 11.33858), ("etoile_g2", 3.544478, 52.44094, 11.6197, 11.33858),
    ("etoile_g3", 4.459725, 87.87402, 9.789211, 11.33858), ("etoile_d1", 266.2451, 17.00787, 10.061, 11.33858),
    ("etoile_d2", 265.5013, 52.44094, 11.54856, 11.33858), ("etoile_d3", 266.315, 87.87402, 9.92126, 11.33858),
    ("etoile_d2", 77.29659, 125.5748, 9.816273, 9.637795), ("etoile_d3", 194.2087, 125.5748, 8.433071, 9.637795),
    ("lune", 244.7861, 115.937, 23.37141, 27.2126),
]
_X0, _PAS = 29.76378, 56.69291
_BW, _BH, _BR = 50.45669, 45.35428, 6.24
_Y_HAUT, _Y_BAS = 60.66142, 9.070866
PLAGES = [(1, 15), (16, 30), (46, 60), (61, 75)]     # M · O · O · N

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0
_DEJA = set()


def _numeros(rng):
    for _ in range(400):
        t = tuple(tuple(sorted(rng.sample(range(lo, hi + 1), 2))) for lo, hi in PLAGES)
        if t not in _DEJA:
            break
    _DEJA.add(t)
    return t


def _billet(c, ox, oy, serie, nums, col):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setFillColor(colors.white); c.setLineWidth(0.7)
    c.roundRect(2.267717, 2.267717, 276.0945, 144.2835, 5.67, stroke=1, fill=1)
    c.setLineWidth(0.35); c.setDash(1, 1)
    c.line(15.87402, 7.937008, 15.87402, 115.0866); c.line(264.7559, 7.937008, 264.7559, 115.0866)
    c.setDash()
    for k, x, y, w, h in DECOR:
        try:
            c.drawImage(_png(k), x, y, w, h, preserveAspectRatio=False, mask="auto")
        except Exception:
            pass
    t = c.beginText(105.9066, 123.5906); t.setFont("Helvetica", 20); t.setCharSpace(2.2)
    t.setFillColor(NOIR); t.textOut("MOON"); t.setCharSpace(0); c.drawText(t)
    c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.6)
    c.roundRect(20.97638, 123.0236, 49.88976, 15.30709, 3.4, stroke=1, fill=1)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 6); c.drawString(24.37795, 127.8425, "N\u00b0")
    t = c.beginText(45.34048, 127.8425); t.setFont("Helvetica", 6.8); t.setFillColor(GRIS)
    t.textOut("%06d" % serie); c.drawText(t)
    for k, paire in enumerate(nums):
        bx = _X0 + k * _PAS
        for by, v in zip((_Y_HAUT, _Y_BAS), paire):
            c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.9)
            c.roundRect(bx, by, _BW, _BH, _BR, stroke=1, fill=1)
            s = str(v); w = c.stringWidth(s, POLICE_NUM, T_NUM)
            tt = c.beginText(bx + (_BW - w) / 2.0, by + 12.77716); tt.setFont(POLICE_NUM, T_NUM)
            tt.setFillColor(col); tt.textOut(s); c.drawText(tt)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 3030)
    _DEJA.clear()
    serie = int(serie_start)
    faits = 0
    try:
        no_page = max(1, int(page_start))
    except Exception:
        no_page = 1
    col_imposee = None
    if couleur and couleur_perso:
        try:
            col_imposee = colors.HexColor(couleur_perso)
        except Exception:
            col_imposee = None

    while faits < n_:
        entete = "  ·  ".join(t for t in ((nom_evenement or "").strip(), (date_lieu or "").strip()) if t)
        if entete:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - DECAL_Y / 2.0 - 2.5, entete)
        c.setFillColor(colors.Color(0.5, 0.5, 0.5)); c.setFont("Helvetica", 6)
        c.drawRightString(PAGE_W - DECAL_X, DECAL_Y / 2.0 - 2, "page %d" % no_page)

        c.saveState()
        c.translate(DECAL_X, DECAL_Y); c.scale(ECHELLE, ECHELLE)
        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ox = (idx % COLS) * CELL_W
            oy = (RANGS - 1 - idx // COLS) * CELL_H
            col = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else NOIR
            _billet(c, ox, oy, serie, _numeros(rng), col)
            serie += 1
            faits += 1
        c.setStrokeColor(colors.Color(0.5, 0.5, 0.5)); c.setLineWidth(0.3); c.setDash(2, 2)
        for i in (1, 2):
            c.line(i * CELL_W, 0, i * CELL_W, RANGS * CELL_H)
        for j in (1, 2, 3):
            c.line(0, j * CELL_H, COLS * CELL_W, j * CELL_H)
        c.restoreState()
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_moon.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("MOON genere")
