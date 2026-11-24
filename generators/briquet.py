# -*- coding: utf-8 -*-
"""MANAPRINT — BRIQUET · 7 boules (création 2KEA & Associé).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « briquet_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : N° de série souligné, le briquet (haut-gauche), titre BRIQUET, la flamme
(haut-droite), 7 gouttes 2 · 3 · 2, « Voir plus loin.. Gagner ensemble ! » et
« 2KEA & Associé – Papeete ».
Plages B I N G O (inchangées), lues par COLONNE de gauche à droite, la lettre posée
dans la pointe de chaque goutte (24/11, comme le CARBASS) :
   colonne 1 : goutte du milieu gauche      -> B  1-15
   colonne 2 : gouttes haut + bas gauche    -> I 16-30 (le plus petit en haut)
   colonne 3 : goutte du centre             -> N 31-45
   colonne 4 : gouttes haut + bas droite    -> G 46-60 (le plus petit en haut)
   colonne 5 : goutte du milieu droit       -> O 61-75
   -> crieur 1 à 75.
Le tout est réduit pour garder 6 mm de marge d'impression (Konica / Sharp)."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors

PAGE_W, PAGE_H = landscape(A4)
COLS, RANGS = 3, 4
CARTES_PAGE = COLS * RANGS                # 12
CELL_W, CELL_H = 280.6299, 148.8189
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
LETTRES = "BINGO"
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
NOIR = colors.black
POLICE_NUM, T_NUM = "Helvetica-Bold", 22  # comme la maquette (gras 22 pt)

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG = {k: _os.path.join(_ICI, "briquet_v2_%s.png" % k) for k in ("briquet", "flamme", "goutte")}

_GW, _GH = 42.51969, 40.25197          # goutte
COLONNES = [                            # coin bas-gauche de chaque goutte, par colonne
    [(33.16535, 44.50394)],                          # B
    [(83.62205, 78.51969), (75.11811, 9.92126)],     # I (haut, bas)
    [(121.3228, 44.50394)],                          # N
    [(170.9291, 78.51969), (167.5276, 9.92126)],     # G (haut, bas)
    [(209.4803, 44.50394)],                          # O
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


def _billet(c, ox, oy, serie, nums, col):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setLineWidth(0.7)
    c.roundRect(2.834646, 2.834646, 274.9607, 143.1497, 6.803, stroke=1, fill=0)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(9.637795, 134.6457, "N\u00b0")
    c.drawString(22.67717, 134.6457, "%06d" % serie)
    c.setLineWidth(0.4); c.line(22.67717, 133.2283, 44.36711, 133.2283)
    _image(c, "briquet", 9.070866, 87.80598, 31.1811, 40.03654)
    _image(c, "flamme", 248.0315, 104.8819, 19.84252, 35.43307)
    t = c.beginText(118.7734, 124.4409); t.setFont("Helvetica", 21); t.setCharSpace(0.6)
    t.setFillColor(NOIR); t.textOut("BRIQUET"); t.setCharSpace(0); c.drawText(t)
    gouttes = [(p, LETTRES[i]) for i, colonne in enumerate(COLONNES) for p in colonne]
    for ((gx, gy), let), n in zip(gouttes, nums):
        _image(c, "goutte", gx, gy, _GW, _GH)
        c.setFillColor(col); c.setFont(POLICE_NUM, T_NUM)
        c.drawCentredString(gx + _GW / 2.0, gy + 6.615, str(n))
        c.setFont("Helvetica-Bold", 7); c.drawCentredString(gx + _GW / 2.0, gy + 25.3, let)
    c.setFillColor(NOIR)
    c.setFont("Helvetica-Oblique", 4.8); c.drawString(10.20472, 5.952756, "Voir plus loin.. Gagner ensemble !")
    c.setFont("Helvetica-Bold", 4.8); c.drawString(209.3307, 5.952756, "2KEA & Associ\u00e9 \u2013 Papeete")
    c.restoreState()


def _numeros(rng):
    """Un tirage par colonne dans sa plage ; deux numéros différents, le petit en haut."""
    out = []
    for colonne, (lo, hi) in zip(COLONNES, PLAGES):
        out.extend(sorted(rng.sample(range(lo, hi + 1), len(colonne))))
    return out


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 8181)
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
        # en-tête de rame personnalisée + n° de feuille, dans la marge
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
        # traits de coupe en pointillés
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
    open("test_briquet.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("BRIQUET genere")
