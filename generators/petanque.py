# -*- coding: utf-8 -*-
"""MANAPRINT — PÉTANQUE · 7 boules (création 2KEA & Associé).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « petanque_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : N° de série souligné, boules de pétanque (haut-gauche), cochonnet (haut-droite),
titre PÉTANQUE, 7 ovales 2 · 3 · 2, herbes en bas, « Voir plus loin.. Gagner ensemble ! »
et « 2KEA & Associé – Papeete ».
Les 7 ovales lus par COLONNE de gauche à droite : 1 · 2 · 1 · 2 · 1, une lettre par colonne
   (comme le CARBASS) : B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75 ou ★ ÉTOILE 76-90
   (les deux d'une colonne : le petit en haut) -> crieur 1 à 90.
Le tout est réduit pour garder 6 mm de marge d'impression (Konica / Sharp)."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors

PAGE_W, PAGE_H = landscape(A4)            # 841.89 x 595.28
COLS, RANGS = 3, 4
CARTES_PAGE = COLS * RANGS                # 12
CELL_W, CELL_H = 280.6299, 148.8189       # case de la maquette (pt)
# 24/11 : B I N G O comme le CARBASS — la dernière colonne : O 61-75 ou ★ ÉTOILE 76-90
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 90)]
LETTRES = "BINGO"
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
NOIR = colors.black
POLICE_NUM, T_NUM = "Helvetica-Bold", 28  # comme la maquette (Arial/Liberation gras 28 pt)

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG = {k: _os.path.join(_ICI, "petanque_v2_%s.png" % k)
        for k in ("boules", "cochonnet", "herbe_g", "herbe_d")}

# ovales (centre x, centre y, demi-largeur, demi-hauteur) dans la case, groupés par colonne
_RX, _RY = 31.18, 14.74
COLONNES = [
    [(86.45669, 59.24409)],                          # col 1 : 1-18
    [(130.6772, 89.85827), (122.7402, 28.62992)],    # col 2 : 19-36 (haut, bas)
    [(154.7717, 59.24409)],                          # col 3 : 37-54
    [(199.5591, 89.85827), (198.1417, 28.62992)],    # col 4 : 55-72 (haut, bas)
    [(226.2047, 59.24409)],                          # col 5 : 73-90
]

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0


def _ovale(c, cx, cy):
    c.ellipse(cx - _RX, cy - _RY, cx + _RX, cy + _RY, stroke=1, fill=0)


def _image(c, cle, x, y, w, h):
    try:
        c.drawImage(_IMG[cle], x, y, w, h, preserveAspectRatio=False, mask="auto")
    except Exception:
        pass


def _billet(c, ox, oy, serie, nums, col):
    c.saveState()
    c.translate(ox, oy)
    # cadre arrondi
    c.setStrokeColor(NOIR); c.setLineWidth(0.7)
    c.roundRect(2.834646, 2.834646, 274.9607, 143.1497, 6.236, stroke=1, fill=0)
    # N° + série soulignée
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 7.5)
    c.drawString(10.20472, 131.2441, "N°")
    c.drawString(23.81102, 131.2441, "%06d" % serie)
    c.setLineWidth(0.4); c.line(23.81102, 129.8268, 48.83788, 129.8268)
    # dessins
    _image(c, "boules", 8.503937, 89.29134, 70.86614, 36.85039)
    _image(c, "cochonnet", 235.2756, 107.6988, 35.43307, 30.91535)
    _image(c, "herbe_g", 9.637795, 14.13921, 36.85039, 37.7348)
    _image(c, "herbe_d", 235.2756, 22.90612, 38.26772, 16.77892)
    # titre
    t = c.beginText(102.516, 113.6693); t.setFont("Helvetica", 22); t.setCharSpace(0.8)
    t.setFillColor(NOIR); t.textOut("PÉTANQUE"); t.setCharSpace(0); c.drawText(t)
    # 7 ovales + chiffres
    c.setLineWidth(0.8)
    lettres = [LETTRES[i] for i, colonne in enumerate(COLONNES) for _p in colonne]
    for (cx, cy), n, let in zip([p for colonne in COLONNES for p in colonne], nums, lettres):
        c.setStrokeColor(NOIR); _ovale(c, cx, cy)
        c.setFillColor(col); c.setFont(POLICE_NUM, T_NUM)
        c.drawCentredString(cx + 5.5, cy - 10.0, str(n))
        lx = cx - _RX + 8.5
        if let == "O" and n >= 76:
            _etoile(c, lx, cy + 0.5, 5.2, col)
        else:
            c.setFont("Helvetica-Bold", 10); c.drawCentredString(lx, cy - 3.6, let)
    # pied
    c.setFillColor(NOIR)
    c.setFont("Helvetica-Oblique", 4.8); c.drawString(10.20472, 6.519685, "Voir plus loin.. Gagner ensemble !")
    c.setFont("Helvetica-Bold", 4.8); c.drawString(209.3307, 6.519685, "2KEA & Associé – Papeete")
    c.restoreState()


def _etoile(c, x, y, R, col):
    import math
    p = c.beginPath()
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        rr = R if k % 2 == 0 else R * 0.42
        (p.moveTo if k == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
    p.close(); c.setFillColor(col); c.drawPath(p, stroke=0, fill=1)


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
    rng = random.Random(int(serie_start) * 100003 + 7373)
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
    open("test_petanque.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("PETANQUE genere")
