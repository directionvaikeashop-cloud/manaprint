# -*- coding: utf-8 -*-
"""MANAPRINT — BROWN 8 boules (maquette CANVA de Maeva, 25/11/2026, « brown_canva_12_A4 »).
Reprise TELLE QUELLE : 12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées),
traits de coupe en pointillés. Chaque billet : cadre arrondi, pastille « N° » + série,
titre BROWN, l'hibiscus, la bande B I N G O, 5 colonnes séparées par des filets gris,
8 cases à coins ronds.
RÈGLE (inchangée) :
   B 1-15 (2 cases) · I 16-30 (1, au milieu) · N 31-45 (2) · G 46-60 (1, au milieu) · O 61-75 (2)
   le plus petit en haut dans chaque colonne -> crieur 1 à 75.
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
_IMG_FLEUR = _os.path.join(_ICI, "brown8_v2_hibiscus.png")

_X0, _PAS = 10.99843, 53.17795             # bord gauche de la 1re case, pas entre colonnes
_BW, _BH, _BR = 45.92126, 40.8189, 6.24
_Y_HAUT, _Y_MILIEU, _Y_BAS = 55.84252, 32.88189, 9.92126
COLONNES = [  # (plage, nombre de cases)
    ((1, 15), 2), ((16, 30), 1), ((31, 45), 2), ((46, 60), 1), ((61, 75), 2)]
LETTRES = [("B", 30.7093), ("I", 85.88676), ("N", 137.0652), ("G", 189.9927), ("O", 243.1706)]

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0
_DEJA = set()


def _numeros(rng):
    for _ in range(400):
        t = tuple(tuple(sorted(rng.sample(range(lo, hi + 1), n))) for (lo, hi), n in COLONNES)
        if t not in _DEJA:
            break
    _DEJA.add(t)
    return t


def _billet(c, ox, oy, serie, nums, col):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setFillColor(colors.white); c.setLineWidth(0.7)
    c.roundRect(2.267717, 2.267717, 276.0945, 144.2835, 5.67, stroke=1, fill=1)
    c.setLineWidth(0.6)
    c.roundRect(11.90551, 122.4567, 59.52756, 15.87402, 3.4, stroke=1, fill=1)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 6.3); c.drawString(15.87402, 127.2756, "N\u00b0")
    t = c.beginText(44.00571, 127.2756); t.setFont("Helvetica", 7.2); t.setFillColor(GRIS)
    t.textOut("%06d" % serie); c.drawText(t)
    t = c.beginText(108.4243, 123.0236); t.setFont("Helvetica", 21); t.setCharSpace(2.2)
    t.setFillColor(NOIR); t.textOut("BROWN"); t.setCharSpace(0); c.drawText(t)
    try:
        c.drawImage(_IMG_FLEUR, 238.1102, 113.2806, 32.31496, 28.1682, preserveAspectRatio=False, mask="auto")
    except Exception:
        pass
    c.setStrokeColor(GRIS); c.setLineWidth(0.4)
    c.line(7.370079, 99.2126, 273.2598, 99.2126); c.line(7.370079, 113.9528, 273.2598, 113.9528)
    for x in (60.54803, 113.726, 166.9039, 220.0819):
        c.line(x, 6.80315, x, 113.9528)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 9)
    for let, x in LETTRES:
        c.drawString(x, 102.6142, let)
    for k, ((_pl, n), valeurs) in enumerate(zip(COLONNES, nums)):
        bx = _X0 + k * _PAS
        ys = [_Y_HAUT, _Y_BAS] if n == 2 else [_Y_MILIEU]
        for by, v in zip(ys, valeurs):
            c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.9)
            c.roundRect(bx, by, _BW, _BH, _BR, stroke=1, fill=1)
            s = str(v); w = c.stringWidth(s, POLICE_NUM, T_NUM)
            tt = c.beginText(bx + (_BW - w) / 2.0, by + 10.50945); tt.setFont(POLICE_NUM, T_NUM)
            tt.setFillColor(col); tt.textOut(s); c.drawText(tt)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 8888)
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
    open("test_brown8.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("BROWN genere")
