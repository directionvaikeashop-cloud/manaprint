# -*- coding: utf-8 -*-
"""MANAPRINT — GUN · 5 boules (création RANIHEI SISTERS & SHOP, maquette CANVA de Maeva).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « gun_canva2_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : le stand de tir en perspective, 5 cercles « viseur » en haut, 4 impacts,
le viseur central, le titre GUN, le pistolet, « RANIHEI SISTERS & SHOP · 87 77 39 19 ».
Plages (inchangées), une par cercle de gauche à droite, la lettre posée sur le bord
de chaque cercle (24/11) : B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75 -> crieur 1 à 75.
Chiffres gras 28 pt comme la maquette. Seul ajout : le N° de série, discret, sous GUN.
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
POLICE_NUM, T_NUM = "Helvetica-Bold", 28  # comme la maquette (gras 28 pt)

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG = {k: _os.path.join(_ICI, "gun_v2_%s.png" % k)
        for k in ("fond", "impact1", "impact2", "impact3", "impact4", "pistolet")}

_CX = [35.14961, 87.30709, 139.748, 192.7559, 244.9134]   # centres des 5 cercles
_CY = 118.2047
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
    return [rng.randint(lo, hi) for lo, hi in PLAGES]


def _billet(c, ox, oy, serie, nums, col):
    c.saveState()
    c.translate(ox, oy)
    c.saveState()
    p = c.beginPath(); p.rect(0, 0, CELL_W, CELL_H)
    c.clipPath(p, stroke=0, fill=0)
    _image(c, "fond", 0, 0, CELL_W, CELL_H)
    _image(c, "impact1", 16.72441, 64.88801, 36.85039, 43.13737)
    _image(c, "impact2", 68.88189, 66.22386, 36.85039, 40.46566)
    _image(c, "impact3", 121.3228, 66.75197, 36.85039, 39.40945)
    _image(c, "impact4", 174.3307, 66.75197, 36.85039, 39.40945)
    c.restoreState()
    # titre GUN
    t = c.beginText(11.33858, 35.43307); t.setFont("Helvetica", 30); t.setCharSpace(5)
    t.setFillColor(NOIR); t.textOut("GUN"); t.setCharSpace(0); c.drawText(t)
    # viseur central
    c.setStrokeColor(NOIR); c.setLineWidth(0.5)
    c.circle(130.3937, 63.98365, 10.20472, stroke=1, fill=0)
    c.circle(130.3937, 63.98365, 4.535433, stroke=1, fill=0)
    c.line(116.2205, 63.98365, 144.5669, 63.98365); c.line(130.3937, 49.81042, 130.3937, 78.15688)
    # pied
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 5.2)
    c.drawString(26.30012, 13.03937, "RANIHEI SISTERS & SHOP")
    c.drawString(45.7925, 6.23622, "87 77 39 19")
    c.setFillColor(colors.Color(0.30, 0.30, 0.30)); c.setFont("Helvetica-Bold", 5.2)
    c.drawString(26.30012, 21.5, "N\u00b0 %06d" % serie)      # seul ajout : le n° de série
    _image(c, "pistolet", 175.748, 11.33858, 96.37795, 63.42779)
    # 5 cercles viseur + chiffres + lettre B I N G O
    for cx, n, let in zip(_CX, nums, LETTRES):
        c.setStrokeColor(NOIR); c.setFillColor(colors.white); c.setLineWidth(0.9)
        c.circle(cx, _CY, 20.69291, stroke=1, fill=1)
        c.setLineWidth(0.35); c.circle(cx, _CY, 18.14173, stroke=1, fill=0)
        c.setFillColor(col); c.setFont(POLICE_NUM, T_NUM)
        c.drawCentredString(cx, 108.1807, str(n))
        lx, ly = cx - 15.6, _CY + 14.6
        c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.6)
        c.circle(lx, ly, 4.8, stroke=1, fill=1)
        c.setFillColor(col); c.setFont("Helvetica-Bold", 7.2); c.drawCentredString(lx, ly - 2.6, let)
    c.setStrokeColor(NOIR); c.setLineWidth(0.5)
    c.rect(0.708661, 0.708661, 279.2126, 147.4016, stroke=1, fill=0)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 4848)
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
    open("test_gun.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("GUN genere")
