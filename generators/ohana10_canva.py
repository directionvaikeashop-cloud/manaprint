# -*- coding: utf-8 -*-
"""MANAPRINT — OHANA 75 · 10 BOULES (maquette CANVA de Maeva, 25/11/2026, « 10boules_canva_12_A4 »).
Reprise TELLE QUELLE : 12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées),
traits de coupe en pointillés. Chaque billet : cadre arrondi, titre 10 BOULES entre
deux paires de boules, 10 cases à coins ronds (2 rangées x 5 colonnes), pastille « N° ».
Le dessin du billet est rejoué TRAIT POUR TRAIT depuis la maquette (_DESSIN) et
enregistré une seule fois par document (fichier léger).
(Fichier à part : l'ancien ohana75_10boules.py reste pour l'OHANA 10 boules MYSTÈRE.)
RÈGLE (inchangée) — 2 numéros par colonne, le petit en haut :
   1-15 · 16-30 · 31-45 · 46-60 · 61-75 -> crieur 1 à 75.
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

_CX = [38.26772, 89.29134, 140.315, 191.3386, 242.3622]   # centres des 5 colonnes
_Y_HAUT, _Y_BAS = 75.98976, 30.63543                      # lignes de base des chiffres
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

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


def _txt(c, s, x, y, police, taille, col, esp=0):
    t = c.beginText(x, y); t.setFont(police, taille)
    if esp:
        t.setCharSpace(esp)
    t.setFillColor(col); t.textOut(s)
    if esp:
        t.setCharSpace(0)
    c.drawText(t)


def _billet(c, ox, oy, serie, nums, col):
    if not getattr(c, "_o10_modele", False):      # le dessin : une seule fois par document
        c.beginForm("OHANA10_DESSIN", 0, 0, CELL_W, CELL_H)
        c._code.append("q\n" + _DESSIN + "\nQ")
        c.endForm()
        c._o10_modele = True
    c.saveState()
    c.translate(ox, oy)
    c.doForm("OHANA10_DESSIN")
    _txt(c, "10 BOULES", 86.0132, 125.8583, "Helvetica", 17, NOIR, esp=2)
    _txt(c, "N\u00b0", 11.33858, 9.496063, "Helvetica-Bold", 5, NOIR)
    _txt(c, "%06d" % serie, 32.3369, 9.496063, "Helvetica", 5.6, GRIS)
    for cx, paire in zip(_CX, nums):
        for y, v in zip((_Y_HAUT, _Y_BAS), paire):
            s = str(v); w = c.stringWidth(s, POLICE_NUM, T_NUM)
            _txt(c, s, cx - w / 2.0, y, POLICE_NUM, T_NUM, col)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 1010)
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


_DESSIN = '0 0 0 RG\n.7 w\n1 1 1 rg\nn\n7.937008 2.267717 m\n272.6929 2.267717 l\n275.8269 2.267717 278.3622 4.803024 278.3622 7.937008 c\n278.3622 140.8819 l\n278.3622 144.0159 275.8269 146.5512 272.6929 146.5512 c\n7.937008 146.5512 l\n4.803024 146.5512 2.267717 144.0159 2.267717 140.8819 c\n2.267717 7.937008 l\n2.267717 4.803024 4.803024 2.267717 7.937008 2.267717 c\nh\nB*\n0 0 0 RG\n1 1 1 rg\n.5 w\nn\n42.80315 132.0945 m\n42.80315 136.9476 38.8689 140.8819 34.01575 140.8819 c\n29.1626 140.8819 25.22835 136.9476 25.22835 132.0945 c\n25.22835 127.2413 29.1626 123.3071 34.01575 123.3071 c\n38.8689 123.3071 42.80315 127.2413 42.80315 132.0945 c\nB*\n.3 w\nn\n38.84882 132.0945 m\n38.84882 134.7637 36.68498 136.9276 34.01575 136.9276 c\n31.34652 136.9276 29.18268 134.7637 29.18268 132.0945 c\n29.18268 129.4253 31.34652 127.2614 34.01575 127.2614 c\n36.68498 127.2614 38.84882 129.4253 38.84882 132.0945 c\nS\n.35 w\nn\n31.67148 138.5353 m\n30.15723 137.9842 28.88558 136.9171 28.07986 135.5216 c\nS\n0 0 0 RG\n1 1 1 rg\n.5 w\nn\n62.64567 132.0945 m\n62.64567 136.9476 58.71142 140.8819 53.85827 140.8819 c\n49.00512 140.8819 45.07087 136.9476 45.07087 132.0945 c\n45.07087 127.2413 49.00512 123.3071 53.85827 123.3071 c\n58.71142 123.3071 62.64567 127.2413 62.64567 132.0945 c\nB*\n.3 w\nn\n58.69134 132.0945 m\n58.69134 134.7637 56.5275 136.9276 53.85827 136.9276 c\n51.18904 136.9276 49.0252 134.7637 49.0252 132.0945 c\n49.0252 129.4253 51.18904 127.2614 53.85827 127.2614 c\n56.5275 127.2614 58.69134 129.4253 58.69134 132.0945 c\nS\n.35 w\nn\n51.514 138.5353 m\n49.99975 137.9842 48.7281 136.9171 47.92238 135.5216 c\nS\n0 0 0 RG\n1 1 1 rg\n.5 w\nn\n252.5669 132.0945 m\n252.5669 136.9476 248.6327 140.8819 243.7795 140.8819 c\n238.9264 140.8819 234.9921 136.9476 234.9921 132.0945 c\n234.9921 127.2413 238.9264 123.3071 243.7795 123.3071 c\n248.6327 123.3071 252.5669 127.2413 252.5669 132.0945 c\nB*\n.3 w\nn\n248.6126 132.0945 m\n248.6126 134.7637 246.4488 136.9276 243.7795 136.9276 c\n241.1103 136.9276 238.9465 134.7637 238.9465 132.0945 c\n238.9465 129.4253 241.1103 127.2614 243.7795 127.2614 c\n246.4488 127.2614 248.6126 129.4253 248.6126 132.0945 c\nS\n.35 w\nn\n241.4353 138.5353 m\n239.921 137.9842 238.6494 136.9171 237.8436 135.5216 c\nS\n0 0 0 RG\n1 1 1 rg\n.5 w\nn\n272.4094 132.0945 m\n272.4094 136.9476 268.4752 140.8819 263.622 140.8819 c\n258.7689 140.8819 254.8346 136.9476 254.8346 132.0945 c\n254.8346 127.2413 258.7689 123.3071 263.622 123.3071 c\n268.4752 123.3071 272.4094 127.2413 272.4094 132.0945 c\nB*\n.3 w\nn\n268.4551 132.0945 m\n268.4551 134.7637 266.2913 136.9276 263.622 136.9276 c\n260.9528 136.9276 258.789 134.7637 258.789 132.0945 c\n258.789 129.4253 260.9528 127.2614 263.622 127.2614 c\n266.2913 127.2614 268.4551 129.4253 268.4551 132.0945 c\nS\n.35 w\nn\n261.2778 138.5353 m\n259.7635 137.9842 258.4919 136.9171 257.6862 135.5216 c\nS\n1 1 1 rg\n.5 w\nn\n11.33858 5.669291 m\n51.02362 5.669291 l\n52.59061 5.669291 53.85827 6.936945 53.85827 8.503937 c\n53.85827 13.6063 l\n53.85827 15.17329 52.59061 16.44094 51.02362 16.44094 c\n11.33858 16.44094 l\n9.771591 16.44094 8.503937 15.17329 8.503937 13.6063 c\n8.503937 8.503937 l\n8.503937 6.936945 9.771591 5.669291 11.33858 5.669291 c\nh\nB*\n1 1 1 rg\n0 0 0 RG\n.9 w\nn\n20.40945 65.19685 m\n56.12598 65.19685 l\n59.57337 65.19685 62.3622 67.98569 62.3622 71.43307 c\n62.3622 100.3465 l\n62.3622 103.7938 59.57337 106.5827 56.12598 106.5827 c\n20.40945 106.5827 l\n16.96207 106.5827 14.17323 103.7938 14.17323 100.3465 c\n14.17323 71.43307 l\n14.17323 67.98569 16.96207 65.19685 20.40945 65.19685 c\nh\nB*\n0 0 0 rg\n1 1 1 rg\n0 0 0 RG\n.9 w\nn\n71.43307 65.19685 m\n107.1496 65.19685 l\n110.597 65.19685 113.3858 67.98569 113.3858 71.43307 c\n113.3858 100.3465 l\n113.3858 103.7938 110.597 106.5827 107.1496 106.5827 c\n71.43307 106.5827 l\n67.98569 106.5827 65.19685 103.7938 65.19685 100.3465 c\n65.19685 71.43307 l\n65.19685 67.98569 67.98569 65.19685 71.43307 65.19685 c\nh\nB*\n0 0 0 rg\n1 1 1 rg\n0 0 0 RG\n.9 w\nn\n122.4567 65.19685 m\n158.1732 65.19685 l\n161.6206 65.19685 164.4094 67.98569 164.4094 71.43307 c\n164.4094 100.3465 l\n164.4094 103.7938 161.6206 106.5827 158.1732 106.5827 c\n122.4567 106.5827 l\n119.0093 106.5827 116.2205 103.7938 116.2205 100.3465 c\n116.2205 71.43307 l\n116.2205 67.98569 119.0093 65.19685 122.4567 65.19685 c\nh\nB*\n0 0 0 rg\n1 1 1 rg\n0 0 0 RG\n.9 w\nn\n173.4803 65.19685 m\n209.1969 65.19685 l\n212.6442 65.19685 215.4331 67.98569 215.4331 71.43307 c\n215.4331 100.3465 l\n215.4331 103.7938 212.6442 106.5827 209.1969 106.5827 c\n173.4803 106.5827 l\n170.0329 106.5827 167.2441 103.7938 167.2441 100.3465 c\n167.2441 71.43307 l\n167.2441 67.98569 170.0329 65.19685 173.4803 65.19685 c\nh\nB*\n0 0 0 rg\n1 1 1 rg\n0 0 0 RG\n.9 w\nn\n224.5039 65.19685 m\n260.2205 65.19685 l\n263.6679 65.19685 266.4567 67.98569 266.4567 71.43307 c\n266.4567 100.3465 l\n266.4567 103.7938 263.6679 106.5827 260.2205 106.5827 c\n224.5039 106.5827 l\n221.0566 106.5827 218.2677 103.7938 218.2677 100.3465 c\n218.2677 71.43307 l\n218.2677 67.98569 221.0566 65.19685 224.5039 65.19685 c\nh\nB*\n0 0 0 rg\n1 1 1 rg\n0 0 0 RG\n.9 w\nn\n20.40945 19.84252 m\n56.12598 19.84252 l\n59.57337 19.84252 62.3622 22.63136 62.3622 26.07874 c\n62.3622 54.99213 l\n62.3622 58.43951 59.57337 61.22835 56.12598 61.22835 c\n20.40945 61.22835 l\n16.96207 61.22835 14.17323 58.43951 14.17323 54.99213 c\n14.17323 26.07874 l\n14.17323 22.63136 16.96207 19.84252 20.40945 19.84252 c\nh\nB*\n0 0 0 rg\n1 1 1 rg\n0 0 0 RG\n.9 w\nn\n71.43307 19.84252 m\n107.1496 19.84252 l\n110.597 19.84252 113.3858 22.63136 113.3858 26.07874 c\n113.3858 54.99213 l\n113.3858 58.43951 110.597 61.22835 107.1496 61.22835 c\n71.43307 61.22835 l\n67.98569 61.22835 65.19685 58.43951 65.19685 54.99213 c\n65.19685 26.07874 l\n65.19685 22.63136 67.98569 19.84252 71.43307 19.84252 c\nh\nB*\n0 0 0 rg\n1 1 1 rg\n0 0 0 RG\n.9 w\nn\n122.4567 19.84252 m\n158.1732 19.84252 l\n161.6206 19.84252 164.4094 22.63136 164.4094 26.07874 c\n164.4094 54.99213 l\n164.4094 58.43951 161.6206 61.22835 158.1732 61.22835 c\n122.4567 61.22835 l\n119.0093 61.22835 116.2205 58.43951 116.2205 54.99213 c\n116.2205 26.07874 l\n116.2205 22.63136 119.0093 19.84252 122.4567 19.84252 c\nh\nB*\n0 0 0 rg\n1 1 1 rg\n0 0 0 RG\n.9 w\nn\n173.4803 19.84252 m\n209.1969 19.84252 l\n212.6442 19.84252 215.4331 22.63136 215.4331 26.07874 c\n215.4331 54.99213 l\n215.4331 58.43951 212.6442 61.22835 209.1969 61.22835 c\n173.4803 61.22835 l\n170.0329 61.22835 167.2441 58.43951 167.2441 54.99213 c\n167.2441 26.07874 l\n167.2441 22.63136 170.0329 19.84252 173.4803 19.84252 c\nh\nB*\n0 0 0 rg\n1 1 1 rg\n0 0 0 RG\n.9 w\nn\n224.5039 19.84252 m\n260.2205 19.84252 l\n263.6679 19.84252 266.4567 22.63136 266.4567 26.07874 c\n266.4567 54.99213 l\n266.4567 58.43951 263.6679 61.22835 260.2205 61.22835 c\n224.5039 61.22835 l\n221.0566 61.22835 218.2677 58.43951 218.2677 54.99213 c\n218.2677 26.07874 l\n218.2677 22.63136 221.0566 19.84252 224.5039 19.84252 c\nh\nB*\n0 0 0 rg'


if __name__ == "__main__":
    open("test_ohana10.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("10 BOULES genere")
