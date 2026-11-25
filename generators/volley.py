# -*- coding: utf-8 -*-
"""MANAPRINT — VOLLEY-BALL · 5 numéros (création RANIHEI, maquette CANVA de Maeva).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « volley_canva2_12_A4 », le petit joueur accroupi décalé vers le milieu) reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : N° de série, titre VOLLEY-BALL, ballon, salle et filet, la smasheuse,
les deux contreurs, les deux joueurs accroupis, « RANI & HEI – 87 77 39 19 ».
Plages (inchangées), un numéro par joueur, écrit sur 2 chiffres (« 09 ») comme la maquette,
la lettre B I N G O posée à côté de chaque numéro, et le dessin BLANCHI sous chaque numéro (24/11) :
   joueuse accroupie à gauche -> B  1-15 (24 pt)
   petit joueur accroupi      -> I 16-30 (20 pt)
   smasheuse qui saute        -> N 31-45 (28 pt)
   contreur de gauche         -> G 46-60 (28 pt)
   contreur de droite         -> O 61-75 (28 pt)
   -> crieur 1 à 75.
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
POLICE_NUM = "Helvetica-Bold"

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG = {k: _os.path.join(_ICI, "volley_v2_%s.png" % k)
        for k in ("fond", "ballon", "contreurs", "accroupie", "accroupi", "smasheuse")}

# (lettre, plage, centre x du numéro, ligne de base, taille) — mesurés sur la maquette
JOUEURS = [
    ("B", (1, 15), 38.831, 21.17178, 24),
    ("I", (16, 30), 138.895, 23.73764, 20),
    ("N", (31, 45), 93.539, 76.99962, 28),
    ("G", (46, 60), 193.602, 31.36183, 28),
    ("O", (61, 75), 246.61, 31.36183, 28),
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
    return [rng.randint(lo, hi) for _l, (lo, hi), _x, _y, _t in JOUEURS]


def _billet(c, ox, oy, serie, nums, col):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setLineWidth(0.7)
    c.roundRect(2.834646, 2.834646, 274.9607, 143.1497, 6.803, stroke=1, fill=0)
    c.saveState()
    p = c.beginPath(); p.roundRect(3.685039, 3.685039, 273.2598, 141.4488, 6.236)
    c.clipPath(p, stroke=0, fill=0)
    _image(c, "fond", 0, 0, 280.6299, 148.8189)
    c.setFillColor(colors.white)
    c.rect(39.68504, 118.7717, 113.3858, 26.07874, stroke=0, fill=1)
    c.rect(158.7402, 118.7717, 116.2205, 26.07874, stroke=0, fill=1)
    _image(c, "ballon", 226.7717, 115.0866, 24.94488, 25.22835)
    _image(c, "contreurs", 172.9134, 15.59055, 96.37795, 102.0472)
    _image(c, "accroupie", 5.102362, 11.33858, 62.3622, 40.53543)
    _image(c, "accroupi", 107.7165, 11.33858, 62.3622, 40.53543)
    _image(c, "smasheuse", 48.18898, 38.83465, 102.0472, 85.03937)
    c.restoreState()
    for (let, _pl, nx, ny, tn), n in zip(JOUEURS, nums):
        txt = "%02d" % n
        # 24/11 (Maeva : « blanchi là où il y a les chiffres ») : réserve blanche sous le numéro
        _w = c.stringWidth(txt, POLICE_NUM, tn)
        c.setFillColor(colors.white)
        c.roundRect(nx - _w / 2.0 - 2.2, ny - 2.4, _w + 4.4, tn * 0.717 + 4.8, 2.5, stroke=0, fill=1)
        c.setFillColor(col); c.setFont(POLICE_NUM, tn)
        c.drawCentredString(nx, ny, txt)
        # lettre B I N G O : pastille blanche contre le haut-gauche du numéro (24/11)
        lw = c.stringWidth(txt, POLICE_NUM, tn)
        lx, ly = nx - lw / 2.0 - 3.2, ny + tn * 0.717 + 1.0
        c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.6)
        c.circle(lx, ly, 4.8, stroke=1, fill=1)
        c.setFillColor(col); c.setFont("Helvetica-Bold", 7.2); c.drawCentredString(lx, ly - 2.6, let)
    t = c.beginText(63.44379, 127.2756); t.setFont("Helvetica", 12.5); t.setCharSpace(0.8)
    t.setFillColor(NOIR); t.textOut("VOLLEY-BALL"); t.setCharSpace(0); c.drawText(t)
    c.setFillColor(colors.white); c.rect(56.69291, 4.535433, 167.2441, 11.90551, stroke=0, fill=1)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 5.2)
    c.drawString(109.6774, 6.80315, "RANI & HEI \u2013 87 77 39 19")
    c.setFillColor(colors.white); c.rect(7.370079, 130.6772, 53.85827, 14.74016, stroke=0, fill=1)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(9.637795, 134.6457, "N\u00b0 %06d" % serie)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 6262)
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
    open("test_volley.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("VOLLEY genere")
