# -*- coding: utf-8 -*-
"""MANAPRINT — PING-PONG GO · 16 numéros (création RANIHEI Sisters & Shop).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « pingpong_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet = 8 PAIRES (une balle ronde + une raquette), 2 numéros par paire
(le plus petit dans la balle, le plus grand sur la raquette), table de ping-pong,
titre PING-PONG GO, ☎ RANI&HEI 87 77 39 19.
Plages (inchangées) = celles de l'OHANA 75 · 2 séries, la lettre posée sur chaque balle (24/11) :
   rangée du haut, gauche + droite    -> B  1-15
   rangée du milieu, gauche + droite  -> I 16-30
   rangée du bas, gauche + droite     -> N 31-45
   paire du centre, en haut           -> G 46-60
   paire du centre, en dessous        -> O 61-75
   -> 16 numéros différents par billet, crieur 1 à 75.
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

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG = {k: _os.path.join(_ICI, "pingpong_v2_%s.png" % k) for k in ("raquette", "table")}
_POLICE_TEL = "Helvetica"
try:      # ☎ de la maquette (police DejaVu déjà présente dans generators/)
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont("DJV_TEL", _os.path.join(_ICI, "DejaVuSans-Bold.ttf")))
    _POLICE_TEL = "DJV_TEL"
except Exception:
    pass

T_NUM = 25
_R_BALLE = 16.15748
_RAQ_W, _RAQ_H = 41.95276, 36.85039
# paire = (centre balle x, centre balle y, raquette x, raquette y)
def _paire(cx, cy, rx, ry):
    return (cx, cy, rx, ry)
_G = [_paire(28.91339, 115.937, 46.77165, 97.22835),
      _paire(28.91339, 75.68504, 46.77165, 56.97638),
      _paire(28.91339, 35.43307, 46.77165, 16.72441)]
_C = [_paire(118.2047, 112.252, 136.063, 93.54331),
      _paire(118.2047, 72.0, 136.063, 53.29134)]
_D = [_paire(207.4961, 115.937, 225.3543, 97.22835),
      _paire(207.4961, 75.68504, 225.3543, 56.97638),
      _paire(207.4961, 35.43307, 225.3543, 16.72441)]
GROUPES = [                      # (paires, plage, lettre — pastille sur la balle, 24/11)
    ([_G[0], _D[0]], (1, 15), "B"),
    ([_G[1], _D[1]], (16, 30), "I"),
    ([_G[2], _D[2]], (31, 45), "N"),
    ([_C[0]], (46, 60), "G"),
    ([_C[1]], (61, 75), "O"),
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
    """[(paire, petit, grand), ...] — 16 numéros tous différents."""
    out = []
    for paires, (lo, hi), let in GROUPES:
        t = rng.sample(range(lo, hi + 1), 2 * len(paires))
        for i, p in enumerate(paires):
            a, b = sorted(t[2 * i:2 * i + 2])
            out.append((p, a, b, let))
    return out


def _billet(c, ox, oy, serie, tirage, col):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setLineWidth(0.7)
    c.roundRect(2.834646, 2.834646, 274.9607, 143.1497, 6.803, stroke=1, fill=0)
    c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 4.6)
    c.drawString(9.637795, 137.7638, "N° %06d" % serie)
    for (cx, cy, rx, ry), a, b, let in tirage:
        c.setStrokeColor(NOIR); c.setLineWidth(0.8)
        c.circle(cx, cy, _R_BALLE, stroke=1, fill=0)
        _image(c, "raquette", rx, ry, _RAQ_W, _RAQ_H)
        c.setFillColor(col)
        # 24/11 : chiffres à 25 pt (balle et raquette), centrés dans leur rond
        # dans la balle : 25 pt de haut, resserré en largeur si besoin pour ne JAMAIS toucher le rond
        _w = c.stringWidth(str(a), "Helvetica-Bold", T_NUM)
        _k = min(1.0, 21.5 / _w)
        _t = c.beginText(); _t.setFont("Helvetica-Bold", T_NUM); _t.setHorizScale(_k * 100); _t.setFillColor(col)
        _t.setTextOrigin(cx - _w * _k / 2.0, cy - T_NUM * 0.717 / 2.0); _t.textOut(str(a)); _t.setHorizScale(100)
        c.drawText(_t)
        c.setFont("Helvetica-Bold", T_NUM)
        c.drawCentredString(rx + _RAQ_W / 2.0, ry + 10.835 + 22 * 0.717 / 2.0 - T_NUM * 0.717 / 2.0, str(b))
        # lettre B I N G O : pastille blanche posée sur le bord haut-gauche de la balle
        lx, ly = cx - 14.2, cy + 13.8
        c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.6)
        c.circle(lx, ly, 4.8, stroke=1, fill=1)
        c.setFillColor(col); c.setFont("Helvetica-Bold", 7.2); c.drawCentredString(lx, ly - 2.6, let)
    _image(c, "table", 111.9685, 28.45276, 56.69291, 20.01969)
    t = c.beginText(96.00612, 18.4252); t.setFont("Helvetica", 11); t.setCharSpace(0.5)
    t.setFillColor(NOIR); t.textOut("PING-PONG GO"); t.setCharSpace(0); c.drawText(t)
    c.setFillColor(NOIR)
    c.setFont(_POLICE_TEL, 6)
    c.drawString(104.8819, 6.519685, "☎" if _POLICE_TEL != "Helvetica" else "Tel")
    c.setFont("Helvetica-Bold", 6); c.drawString(115.937, 6.519685, "RANI&HEI   87 77 39 19")
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 1515)
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
    open("test_pingpong.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("PING-PONG GO genere")
