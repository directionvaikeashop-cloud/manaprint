# -*- coding: utf-8 -*-
"""MANAPRINT — LA JOIE 5 boules (maquette CANVA de Maeva).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « joie_canva_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : cadre arrondi, pastille « N° » + série, titre LA JOIE, la fleur de tiare,
les colonnes I · G · O avec leurs plages, le soleil qui rit, 5 cases en escalier,
« La chance en toute joie ! » souligné.
LA RÈGLE DU JEU (inchangée) : I 16-30 (1 case) · G 46-60 (2 cases, le petit en haut)
· O 61-75 (2 cases, le petit en haut). Le crieur sort 16-30 et 46-75.
Chiffres comme la maquette : écriture à empattements (Times), 28 pt.
Garde-fou : jamais deux billets identiques dans un même document.
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
POLICE_NUM, T_NUM = "Times-Roman", 28     # comme la maquette (Liberation Serif 28 pt)

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG = {k: _os.path.join(_ICI, "joie_v2_%s.png" % k) for k in ("soleil", "tiare")}

_BW, _BH, _BR = 48.75591, 27.2126, 5.1
CASES = [(89.00787, 64.34646),                       # I
         (140.0315, 64.34646), (140.0315, 35.43307),  # G (haut, bas)
         (191.0551, 35.43307), (191.0551, 6.519685)]  # O (haut, bas)
COLONNES = [("I", "16-30", 110.9536, 106.736), ("G", "46-60", 159.548, 157.7596),
            ("O", "61-75", 210.5716, 208.7833)]

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0
_DEJA = set()


def _image(c, cle, x, y, w, h):
    try:
        c.drawImage(_IMG[cle], x, y, w, h, preserveAspectRatio=False, mask="auto")
    except Exception:
        pass


def _numeros(rng):
    for _ in range(400):
        t = (rng.randint(16, 30),) + tuple(sorted(rng.sample(range(46, 61), 2))) \
            + tuple(sorted(rng.sample(range(61, 76), 2)))
        if t not in _DEJA:
            break
    _DEJA.add(t)
    return list(t)


def _billet(c, ox, oy, serie, nums, col):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setFillColor(colors.white); c.setLineWidth(0.7)
    c.roundRect(2.267717, 2.267717, 276.0945, 144.2835, 3.134, stroke=1, fill=1)
    _image(c, "soleil", 6.23622, 51.40789, 73.70079, 50.25508)
    _image(c, "tiare", 227.9055, 102.6846, 42.51969, 37.06343)
    t = c.beginText(109.8345, 123.5906); t.setFont("Helvetica", 20); t.setCharSpace(2)
    t.setFillColor(NOIR); t.textOut("LA JOIE"); t.setCharSpace(0); c.drawText(t)
    c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.6)
    c.roundRect(11.90551, 123.0236, 59.52756, 15.30709, 1.88, stroke=1, fill=1)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 6.3); c.drawString(15.87402, 127.8425, "N\u00b0")
    c.setFillColor(colors.Color(.45, .45, .45)); c.setFont("Helvetica", 7.2)
    c.drawRightString(67.6, 127.8425, "%05d" % serie)
    for let, pl, xl, xp in COLONNES:
        c.setFillColor(NOIR); c.setFont("Times-Bold", 12.5); c.drawString(xl, 106.5827, let)
        c.setFillColor(colors.Color(.25, .25, .25)); c.setFont("Helvetica-Bold", 5.2); c.drawString(xp, 97.51181, pl)
    for (bx, by), n in zip(CASES, nums):
        c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.9)
        c.roundRect(bx, by, _BW, _BH, _BR, stroke=1, fill=1)
        # chiffre posé en objet texte : il reste EXACTEMENT dans sa case (même tout en bas du billet)
        _s = str(n); _w = c.stringWidth(_s, POLICE_NUM, T_NUM)
        _t = c.beginText(bx + (_BW - _w) / 2.0, by + 4.3663); _t.setFont(POLICE_NUM, T_NUM)
        _t.setFillColor(col); _t.textOut(_s); c.drawText(_t)
    c.setFillColor(colors.Color(.15, .15, .15)); c.setFont("Helvetica-BoldOblique", 6.2)
    c.drawString(30.19188, 27.2126, "La chance"); c.drawString(25.20433, 18.70866, "en toute joie !")
    c.setStrokeColor(NOIR); c.setLineWidth(0.7); c.line(19.84252, 13.03937, 72.28346, 15.02362)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 3131)
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
    open("test_joie.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("JOIE genere")
