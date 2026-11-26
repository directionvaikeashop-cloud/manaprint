# -*- coding: utf-8 -*-
"""MANAPRINT — MONTRE · 5 boules (création RANIHEI SISTERS & SHOP).
NOUVELLE MAQUETTE CANVA de Maeva (25/11/2026, « montre_canva_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Le dessin du billet (cadre, montre au bord pointillé, boutons, ondes, fleur, palmiers,
cases, bulle, pastille de position) vient de la maquette : image noir & blanc 600 dpi
(montre_v2_dessin.png), enregistrée UNE fois par document -> fichier léger, impression d'une traite.
On y pose : MONTRE, RANIHEI SISTERS & SHOP, 87 77 39 19, le n° de position (1-12),
le N° de série et les 5 chiffres.
RÈGLE (Maeva 25/11) — une plage par case, dans l'ordre de lecture :
   HAUT gauche 1-18 · HAUT droite 19-40 · BAS gauche 41-50 · BAS milieu 51-75 · bulle 76-90
   -> crieur 1 à 90, jamais deux fois le même chiffre sur un billet.
   La plage est écrite dans une petite pastille sur le bord de chaque case (25/11) :
   en haut à gauche des cases, sous la bulle.
Chiffres comme la maquette (gras 30 pt) ; dans la bulle 25 pt pour rester DANS le rond.
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
_IMG = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "montre_v2_dessin.png")

# (centre x, ligne de base, taille) des 5 cases, dans l'ordre : haut g, haut d, bas g, bas milieu, bulle
CASES = [(122.1709, 75.43323, 30), (200.9718, 75.43323, 30),
         (106.5826, 38.58283, 30), (162.1417, 38.58283, 30),
         (222.2362, 49.32283 - 0.716 * 25 / 2.0, 25)]

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0
_DEJA = set()


PLAGES = [(1, 18), (19, 40), (41, 50), (51, 75), (76, 90)]   # haut g, haut d, bas g, bas milieu, bulle
# centre de la pastille de plage : sur le bord haut de chaque case, sous la bulle
PASTILLES = [(106.0, 102.0472), (184.8, 102.0472), (97.5, 65.19685), (153.0, 65.19685),
             (222.2362, 30.89764)]


def _numeros(rng):
    for _ in range(400):
        t = tuple(rng.randint(lo, hi) for lo, hi in PLAGES)
        if t not in _DEJA:
            break
    _DEJA.add(t)
    return t


def _txt(c, s, x, y, police, taille, col, esp=0, centre=False):
    w = c.stringWidth(s, police, taille) + (esp * (len(s) - 1) if esp else 0)
    t = c.beginText(x - w / 2.0 if centre else x, y); t.setFont(police, taille)
    if esp:
        t.setCharSpace(esp)
    t.setFillColor(col); t.textOut(s)
    if esp:
        t.setCharSpace(0)
    c.drawText(t)


def _billet(c, ox, oy, serie, position, nums, col):
    if not getattr(c, "_montre_modele", False):     # le dessin : une seule fois par document
        c.beginForm("MONTRE_DESSIN", 0, 0, CELL_W, CELL_H)
        c.drawImage(_IMG, 0, 0, CELL_W, CELL_H)
        c.endForm()
        c._montre_modele = True
    c.saveState()
    c.translate(ox, oy)
    c.doForm("MONTRE_DESSIN")
    _txt(c, "MONTRE", 121.7442, 115.937, "Helvetica", 17, NOIR, esp=1.2)
    _txt(c, "RANIHEI SISTERS & SHOP", 128.3653, 106.5827, "Helvetica-Bold", 5, NOIR, esp=0.12)
    _txt(c, "87 77 39 19", 137.6233, 18.14173, "Helvetica-BoldOblique", 8.5, NOIR, esp=0.3)
    _txt(c, str(position), 24.9437, 118.504, "Helvetica-Bold", 15 if position < 10 else 13, NOIR, centre=True)
    _txt(c, "N° %05d" % serie, 24.9437, 96.0, "Helvetica", 5.5, NOIR, centre=True)
    for (cx, y, t), v in zip(CASES, nums):
        _txt(c, str(v), cx, y, POLICE_NUM, t, col, centre=True)
    for (px, py), (lo, hi) in zip(PASTILLES, PLAGES):
        s = "%d-%d" % (lo, hi)
        w = c.stringWidth(s, "Helvetica-Bold", 5.6) + 5
        c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.6)
        c.roundRect(px - w / 2.0, py - 3.6, w, 7.2, 3.6, stroke=1, fill=1)
        _txt(c, s, px, py - 1.95, "Helvetica-Bold", 5.6, col, centre=True)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 528)
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
            _billet(c, ox, oy, serie, idx + 1, _numeros(rng), col)
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
    open("test_montre.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("MONTRE genere")
