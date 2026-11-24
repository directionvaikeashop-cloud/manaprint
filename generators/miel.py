# -*- coding: utf-8 -*-
"""MANAPRINT — MIEL · 6 boules (création TUKEA / 2KEA & Associé).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « miel_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : N° de série, TUKEA entre deux fleurs de lys, ☎ 89 22 23 05,
6 pots de miel (un numéro par pot), bol de miel + abeilles en bas.
Plages B I G O (inchangées), la lettre posée sur le couvercle de chaque pot (24/11), lues par COLONNE de gauche à droite :
   pots de gauche (haut + bas)  -> B  1-15 (le plus petit en haut)
   pot milieu gauche            -> I 16-30
   pot milieu droit             -> G 46-60
   pots de droite (haut + bas)  -> O 61-75 (le plus petit en haut)
   -> crieur 1 à 75 SANS le N (31-45).
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
POLICE_NUM, T_NUM = "Helvetica-Bold", 26  # comme la maquette (gras 26 pt, les chiffres prennent la place du pot)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG = {k: _os.path.join(_ICI, "miel_v2_%s.png" % k) for k in ("pot", "lys", "bol")}

_POLICE_TEL = "Helvetica"
try:      # ☎ de la maquette (police DejaVu déjà présente dans generators/)
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont("DJV_TEL", _os.path.join(_ICI, "DejaVuSans-Bold.ttf")))
    _POLICE_TEL = "DJV_TEL"
except Exception:
    pass

_POT_W, _POT_H = 51.02362, 48.18898
_HG, _HD = (9.92126, 87.02362), (219.685, 87.02362)
_MG, _MD = (63.77953, 51.30709), (165.8268, 51.30709)
_BG, _BD = (9.92126, 4.535433), (219.685, 4.535433)
COLONNES = [               # (pots, plage, lettre affichée sur le couvercle — 24/11, comme le CARBASS)
    ([_HG, _BG], (1, 15), "B"),
    ([_MG], (16, 30), "I"),
    ([_MD], (46, 60), "G"),
    ([_HD, _BD], (61, 75), "O"),
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
    """[(pot, numéro), ...] : chaque colonne tire dans sa plage, le plus petit en haut."""
    out = []
    for pots, (lo, hi), let in COLONNES:
        out.extend((p, n, let) for p, n in zip(pots, sorted(rng.sample(range(lo, hi + 1), len(pots)))))
    return out


def _billet(c, ox, oy, serie, tirage, col):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setLineWidth(0.7)
    c.roundRect(2.834646, 2.834646, 274.9607, 143.1497, 6.803, stroke=1, fill=0)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 4.6)
    c.drawString(10.20472, 138.6142, "N° %05d" % serie)
    for (px, py), n, let in tirage:
        _image(c, "pot", px, py, _POT_W, _POT_H)
        c.setFillColor(col); c.setFont(POLICE_NUM, T_NUM)
        c.drawCentredString(px + _POT_W / 2.0, py + 8.04, str(n))
        # lettre B I G O sur le couvercle (pastille blanche sur le nœud)
        lx, ly = px + _POT_W / 2.0, py + 41.0
        c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.6)
        c.circle(lx, ly, 5.4, stroke=1, fill=1)
        c.setFillColor(col); c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(lx, ly - 2.85, let)
    _image(c, "lys", 77.83011, 115.6535, 18.14173, 21.25984)
    _image(c, "lys", 184.6581, 115.6535, 18.14173, 21.25984)
    t = c.beginText(101.6411, 118.2047); t.setFont("Helvetica", 22); t.setCharSpace(1)
    t.setFillColor(NOIR); t.textOut("TUKEA"); t.setCharSpace(0); c.drawText(t)
    c.setFillColor(NOIR); c.setFont(_POLICE_TEL, 9); c.drawString(104.502, 104.0315, "\u260e" if _POLICE_TEL != "Helvetica" else "Tel")
    c.setFont("Helvetica-Bold", 10.5); c.drawString(120.6594, 104.0315, "89 22 23 05")
    _image(c, "bol", 87.87402, 5.385827, 104.8819, 48.31122)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 4242)
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
    open("test_miel.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("MIEL genere")
