# -*- coding: utf-8 -*-
"""MANAPRINT — MÉLODIE · 10 boules (création RANIHEI SISTERS & SHOP, maquette CANVA de Maeva).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « melodie_canva_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : cadre de feuillages et de baies, titre MÉLODIE, N° de série,
« RANIHEI SISTERS & SHOP · 87 77 39 19 », deux portées avec leurs clés de sol,
10 ronds (2 rangées x 5 colonnes).
RÈGLE (inchangée) — 2 numéros par colonne (le petit en haut), la lettre sur le rond du haut (24/11) :
   B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75 -> crieur 1 à 75.
Chiffres comme la maquette : gras 25 pt.
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
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
POLICE_NUM, T_NUM = "Helvetica-Bold", 25  # comme la maquette (gras 25 pt)

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG = {k: _os.path.join(_ICI, "melodie_v2_%s.png" % k) for k in ("fond", "portee_haut", "portee_bas")}

_CX = [57.54331, 98.92913, 140.315, 181.7008, 223.0866]
_CY = [87.87402, 47.05512]          # rangée du haut, rangée du bas
_RX, _RY = 18.42519, 17.85828
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
LETTRES = "BINGO"

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0


def _image(c, cle, x, y, w, h):
    try:
        c.drawImage(_IMG[cle], x, y, w, h, preserveAspectRatio=False, mask="auto")
    except Exception:
        pass


def _numeros(rng):
    """[[haut, bas] par colonne] — le plus petit en haut."""
    return [sorted(rng.sample(range(lo, hi + 1), 2)) for lo, hi in PLAGES]


def _billet(c, ox, oy, serie, nums, col):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setLineWidth(0.6)
    c.roundRect(2.267717, 2.267717, 276.0945, 144.2835, 3.134, stroke=1, fill=0)
    c.saveState()
    p = c.beginPath(); p.roundRect(2.834646, 2.834646, 274.9606, 143.1497, 2.977)
    c.clipPath(p, stroke=0, fill=0)
    _image(c, "fond", 0, 0, CELL_W, CELL_H)
    c.restoreState()
    _image(c, "portee_haut", 22.67717, 71.71498, 235.2756, 32.31808)
    _image(c, "portee_bas", 22.67717, 30.84636, 235.2756, 32.41752)
    for k, (cx, paire, let) in enumerate(zip(_CX, nums, LETTRES)):
        for cy, n in zip(_CY, paire):
            c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.9)
            c.ellipse(cx - _RX, cy - _RY, cx + _RX, cy + _RY, stroke=1, fill=1)
            s = str(n); w = c.stringWidth(s, POLICE_NUM, T_NUM)
            t = c.beginText(cx - w / 2.0, cy - 8.95); t.setFont(POLICE_NUM, T_NUM); t.setFillColor(col)
            t.textOut(s); c.drawText(t)
        lx, ly = cx - 15.2, _CY[0] + 13.6
        c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.6)
        c.circle(lx, ly, 4.6, stroke=1, fill=1)
        c.setFillColor(col); c.setFont("Helvetica-Bold", 7.0); c.drawCentredString(lx, ly - 2.5, let)
    c.setFillColor(colors.white); c.rect(26.92913, 114.2362, 226.7717, 21.54331, stroke=0, fill=1)
    t = c.beginText(29.76378, 120.4724); t.setFont("Helvetica", 17); t.setCharSpace(1.6)
    t.setFillColor(NOIR); t.textOut("M\u00c9LODIE"); t.setCharSpace(0); c.drawText(t)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 5)
    c.drawString(188.3845, 128.4094, "RANIHEI SISTERS & SHOP"); c.drawString(225.8699, 119.3386, "87 77 39 19")
    t = c.beginText(133.2283, 120.4724); t.setFont("Helvetica-Bold", 6); t.setFillColor(colors.Color(.35, .35, .35))
    t.textOut("N\u00b0 %06d" % serie); c.drawText(t)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 7171)
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
    open("test_melodie.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("MELODIE genere")
