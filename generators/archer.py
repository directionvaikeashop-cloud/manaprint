# -*- coding: utf-8 -*-
"""MANAPRINT — ARCHER · 4 cibles (création RANIHEI & SISTERS).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « archer_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : rond avec la place du billet sur la feuille (1 à 12), titre ARCHER et sa
flèche, paysage (montagnes, église, palme, herbes, hibiscus), 4 cibles sur pied
(la grande à gauche), l'arbalète, « RANIHEI & SISTERS ».
Plages (inchangées) :
   cible 1 (grande, gauche) : 1-20
   cible 2                  : 21-40
   cible 3                  : 41-60
   cible 4 (droite)         : 61-90
   -> crieur 1 à 90. Chiffres gras 30 pt comme la maquette (le maximum).
Seul ajout : le N° de série, discret, à droite du rond (suivi des rames).
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
POLICE_NUM, T_NUM = "Helvetica-Bold", 30  # comme la maquette (gras 30 pt)

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG = {k: _os.path.join(_ICI, "archer_v2_%s.png" % k)
        for k in ("paysage", "palme", "herbes", "eglise", "cible", "arbalete", "hibiscus")}

# cibles : (x, y, l, h) de l'image, (centre x du chiffre, ligne de base), plage
CIBLES = [
    ((15.86195, 21.38609, 61.8194, 80.53382), (46.77165, 61.54346), (1, 20)),
    ((83.29033, 44.81803, 48.8524, 63.64136), (107.7165, 74.29937), (21, 40)),
    ((132.0824, 45.81115, 47.64617, 62.06997), (155.9055, 74.29937), (41, 60)),
    ((178.0399, 46.80427, 46.43994, 60.49858), (201.2598, 74.29937), (61, 90)),
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


def _numeros(rng):
    return [rng.randint(lo, hi) for _b, _p, (lo, hi) in CIBLES]


def _billet(c, ox, oy, serie, nums, col, place=1):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setLineWidth(0.7)
    c.roundRect(2.834646, 2.834646, 274.9607, 143.1497, 6.803, stroke=1, fill=0)
    # le dessin, découpé dans le cadre arrondi intérieur
    c.saveState()
    p = c.beginPath(); p.roundRect(3.685039, 3.685039, 273.2598, 141.4488, 6.236)
    c.clipPath(p, stroke=0, fill=0)
    _image(c, "paysage", 5.669291, 62.81693, 269.2913, 48.58465)
    _image(c, "palme", 4.251969, 62.3622, 30.00172, 41.10236)
    _image(c, "herbes", 5.669291, 12.75591, 269.2913, 52.44094)
    _image(c, "eglise", 214.0157, 65.74803, 58.11024, 76.83465)
    for (bx, by, bw, bh), _p, _pl in CIBLES:
        _image(c, "cible", bx, by, bw, bh)
    _image(c, "arbalete", 162.9921, -1.517369, 113.3858, 70.96619)
    _image(c, "hibiscus", 7.370079, 5.021372, 42.51969, 39.48256)
    c.restoreState()
    # rond + place du billet sur la feuille
    c.setStrokeColor(NOIR); c.setLineWidth(0.6)
    c.circle(25.51181, 124.4409, 14.74016, stroke=1, fill=0)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(25.51181, 120.5029, str(place))
    # N° de série (seul ajout)
    c.setFont("Helvetica-Bold", 5.5); c.setFillColor(colors.Color(0.35, 0.35, 0.35))
    c.drawString(44.5, 134.2, "N\u00b0 %06d" % serie)
    # titre + flèche
    t = c.beginText(80.63849, 122.1732); t.setFont("Helvetica", 21); t.setCharSpace(1.6)
    t.setFillColor(NOIR); t.textOut("ARCHER"); t.setCharSpace(0); c.drawText(t)
    c.setStrokeColor(NOIR); c.setLineWidth(0.6); c.line(85.03937, 114.2362, 167.2441, 114.2362)
    pf = c.beginPath(); pf.moveTo(181.4173, 114.2362); pf.lineTo(167.2441, 118.2047); pf.lineTo(167.2441, 110.2677); pf.close()
    c.setFillColor(NOIR); c.drawPath(pf, stroke=0, fill=1)
    c.setLineWidth(0.5)
    for x in (72.28346, 76.8189, 81.35433):
        c.line(x, 117.3543, x + 4.25197, 114.2362); c.line(x + 4.25197, 114.2362, x, 111.1181)
    c.line(72.28346, 114.2362, 85.03937, 114.2362)
    # chiffres dans les cibles
    c.setFillColor(col); c.setFont(POLICE_NUM, T_NUM)
    for (_b, (nx, ny), _pl), n in zip(CIBLES, nums):
        c.drawCentredString(nx, ny, str(n))
    # bandeau RANIHEI & SISTERS
    c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.5)
    c.roundRect(58.11024, 7.086614, 96.37796, 15.87402, 7.93701, stroke=1, fill=1)
    c.setFillColor(NOIR); c.setFont("Helvetica-BoldOblique", 7.2)
    c.drawString(71.49453, 12.75591, "RANIHEI & SISTERS")
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 9091)
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
            _billet(c, ox, oy, serie, _numeros(rng), col, idx + 1)
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
    open("test_archer.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("ARCHER genere")
