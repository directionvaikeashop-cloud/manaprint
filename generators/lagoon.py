# -*- coding: utf-8 -*-
"""MANAPRINT — LAGOON 5 boules (maquette CANVA de Maeva).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « lagoon_canva_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : cadre arrondi, pastille « N° » + série, titre LAGOON, cocotier sur son îlot,
l'ATOLL avec son lagon au centre (pirogue, cocotiers), 5 ronds à pointillés sur la couronne.
Plages (inchangées : 5 tranches de 10, crieur 1 à 50), une par rond :
   rond du haut          : 1-10
   rond de gauche        : 11-20
   rond en bas à gauche  : 21-30
   rond en bas à droite  : 31-40
   rond de droite        : 41-50
Chiffres comme la maquette : écriture à empattements (Times), 26 pt.
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
POLICE_NUM, T_NUM = "Times-Roman", 26     # comme la maquette (Liberation Serif 26 pt)

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG = {k: _os.path.join(_ICI, "lagoon_v2_%s.png" % k) for k in ("atoll", "cocotier")}

_R, _R_PT = 17.00787, 15.02362
RONDS = [   # (centre x, centre y, plage)
    (170.3073, 111.604, (1, 10)),
    (100.9447, 57.88666, (11, 20)),
    (140.1020 - 0.0, 25.75324, (21, 30)),
    (222.6482, 26.35953, (31, 40)),
    (252.8613, 61.52441, (41, 50)),
]

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0


def _image(c, cle, x, y, w, h):
    try:
        c.drawImage(_IMG[cle], x, y, w, h, preserveAspectRatio=False, mask="auto")
    except Exception:
        pass


_DEJA = set()   # garde-fou : pas deux billets identiques dans un même document (10^5 combinaisons)


def _numeros(rng):
    for _ in range(400):
        t = tuple(rng.randint(lo, hi) for _x, _y, (lo, hi) in RONDS)
        if t not in _DEJA:
            break
    _DEJA.add(t)
    return list(t)


def _billet(c, ox, oy, serie, nums, col):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setFillColor(colors.white); c.setLineWidth(0.7)
    c.roundRect(2.267717, 2.267717, 276.0945, 144.2835, 3.134, stroke=1, fill=1)
    _image(c, "atoll", 79.37008, 6.80315, 192.7559, 130.3937)
    _image(c, "cocotier", 6.80315, 9.070866, 52.07846, 63.77953)
    for (cx, cy, _pl), n in zip(RONDS, nums):
        c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.9)
        c.circle(cx, cy, _R, stroke=1, fill=1)
        c.saveState()
        c.setLineCap(1); c.setLineWidth(0.5); c.setDash([0, 2.6], 0)
        c.circle(cx, cy, _R_PT, stroke=1, fill=0)
        c.restoreState()
        c.setFillColor(col); c.setFont(POLICE_NUM, T_NUM)
        c.drawCentredString(cx, cy - 8.58, str(n))
    t = c.beginText(10.38773, 89.5748); t.setFont("Helvetica", 13.5); t.setCharSpace(1.3)
    t.setFillColor(NOIR); t.textOut("LAGOON"); t.setCharSpace(0); c.drawText(t)
    c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.6)
    c.roundRect(11.90551, 123.0236, 59.52756, 15.30709, 1.88, stroke=1, fill=1)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 6.3); c.drawString(15.87402, 127.8425, "N\u00b0")
    c.setFillColor(colors.Color(.45, .45, .45)); c.setFont("Helvetica", 7.2)
    c.drawString(44.00571, 127.8425, "%06d" % serie)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 5050)
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
    open("test_lagoon.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("LAGOON genere")
