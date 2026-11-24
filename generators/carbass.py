# -*- coding: utf-8 -*-
"""MANAPRINT — CARBASS (TUKEA / 2KEA & Associé), NOUVELLE maquette de Maeva (24/11).
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : titre CARBASS en lettres noires fines (maquette du 24/11), TUKEA 89 22 23 05, voiture sono (coffre ouvert) + 5 cercles.
Une lettre et une plage par bulle (24/11) :
  haut-gauche B 1-15 · haut-droite I 16-30 · bas-gauche N 31-45 · bas-droite G 46-60 ·
  bas-centre O 61-75 ou ★ ÉTOILE 76-90 (le 90 s'annonce étoile) -> crieur 1 à 90.
La maquette (billet complet) est reprise TELLE QUELLE comme image de fond
(carbass_carton_v2.png), les cercles et les chiffres sont posés par-dessus."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors

PAGE_W, PAGE_H = landscape(A4)          # 842 x 595
COLS, RANGS = 3, 4
CARTES_PAGE = COLS * RANGS               # 12
POLICE = "Helvetica-Bold"
TAILLE_MAX = 30                          # règle Maeva : 30 pt maximum
GRIS = colors.Color(0.0, 0.0, 0.0)       # chiffres noirs (la gamme ÉCO de la plateforme les grise)
TRAIT = colors.Color(0.30, 0.30, 0.30)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

# billet-modèle 384 x 202 (unités de la maquette) — cercles mesurés sur la maquette
_IMG_W, _IMG_H = 384.0, 202.0
_CERCLES = [            # (x, y, rayon) dans l'ordre de pose des numéros croissants
    (51.8, 81.2, 31.5),    # haut-gauche
    (332.8, 81.2, 31.5),   # haut-droite
    (39.3, 153.5, 31.5),   # bas-gauche
    (345.5, 153.5, 31.5),  # bas-droite
    (192.2, 165.2, 31.5),  # bas-centre (sur la voiture)
]

_MARGE = 3 * mm
_CELL_W = (PAGE_W - 2 * _MARGE) / COLS
_CELL_H = (PAGE_H - 2 * _MARGE) / RANGS
_PAD = 1.2 * mm
if (_CELL_W - 2 * _PAD) / (_CELL_H - 2 * _PAD) > _IMG_W / _IMG_H:
    _CH = _CELL_H - 2 * _PAD
    _CW = _CH * _IMG_W / _IMG_H
else:
    _CW = _CELL_W - 2 * _PAD
    _CH = _CW * _IMG_H / _IMG_W
_K = _CW / _IMG_W        # points par unité de maquette

_IMG_FOND = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "carbass_carton_v2.png")


def _origine(idx):
    col, rang = idx % COLS, idx // COLS
    cx = _MARGE + col * _CELL_W + (_CELL_W - _CW) / 2.0
    cy = PAGE_H - _MARGE - (rang + 1) * _CELL_H + (_CELL_H - _CH) / 2.0
    return cx, cy


# 24/11 : chaque bulle porte sa lettre B I N G O et sa plage ; le 76-90 s'annonce ÉTOILE (★)
_PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 90)]   # haut-g B · haut-d I · bas-g N · bas-d G · centre O/★


def _numeros(rng):
    return [rng.randint(a, b) for a, b in _PLAGES]


def _lettre(i, num):
    if i == 4:
        return "\u2605" if num >= 76 else "O"
    return "BING"[i]


def _etoile(c, x, y, R, col):
    import math
    p = c.beginPath()
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        rr = R if k % 2 == 0 else R * 0.42
        (p.moveTo if k == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
    p.close(); c.setFillColor(col); c.drawPath(p, stroke=0, fill=1)


def _coupes(c):
    c.saveState()
    c.setStrokeColor(colors.Color(0.55, 0.55, 0.55)); c.setLineWidth(0.5); c.setDash(3, 3)
    for i in range(1, COLS):
        x = _MARGE + i * _CELL_W
        c.line(x, _MARGE, x, PAGE_H - _MARGE)
    for j in range(1, RANGS):
        y = _MARGE + j * _CELL_H
        c.line(_MARGE, y, PAGE_W - _MARGE, y)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 509)
    serie = int(serie_start)
    faits = 0
    try:
        page_dep = max(1, int(page_start))
    except Exception:
        page_dep = 1
    col_imposee = None
    if couleur and couleur_perso:
        try:
            col_imposee = colors.HexColor(couleur_perso)
        except Exception:
            col_imposee = None

    while faits < n_:
        _coupes(c)
        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            x0, y0 = _origine(idx)
            try:
                c.drawImage(_IMG_FOND, x0, y0, _CW, _CH, preserveAspectRatio=False, mask="auto")
            except Exception:
                pass
            # titre CARBASS (lettres noires fines, comme la maquette)
            _t = 27.0 / 0.718 * _K
            _w = c.stringWidth("CARBASS", "Helvetica", _t)
            _cs = max(0.0, (192 * _K - _w) / 6.0)
            _to = c.beginText(x0 + 17 * _K, y0 + (_IMG_H - 36) * _K)
            _to.setFont("Helvetica", _t); _to.setCharSpace(_cs); _to.setFillColor(colors.black)
            _to.textOut("CARBASS"); _to.setCharSpace(0); c.drawText(_to)
            col = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else GRIS
            for i, ((px, py, pr), num) in enumerate(zip(_CERCLES, _numeros(rng))):
                cx = x0 + px * _K
                cy = y0 + (_IMG_H - py) * _K
                r = pr * _K
                c.setFillColor(colors.white); c.setStrokeColor(TRAIT); c.setLineWidth(0.9)
                c.circle(cx, cy, r, stroke=1, fill=1)
                txt = str(num)
                taille = 24
                while c.stringWidth(txt, POLICE, taille) > 1.55 * r and taille > 12:
                    taille -= 1
                c.setFillColor(col); c.setFont(POLICE, taille)
                c.drawCentredString(cx, cy - r * 0.62, txt)
                let = _lettre(i, num)
                if let == "\u2605":
                    _etoile(c, cx, cy + r * 0.56, r * 0.25, col)
                else:
                    c.setFont(POLICE, 11); c.drawCentredString(cx, cy + r * 0.38, let)
            c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont("Helvetica", 5.5)
            c.drawString(x0 + 5, y0 + 4, "N° %05d" % serie)
            serie += 1
            faits += 1
        nfe = page_dep + (faits - 1) // CARTES_PAGE
        c.setFillColor(colors.Color(0.5, 0.5, 0.5)); c.setFont("Helvetica", 6)
        c.drawRightString(PAGE_W - _MARGE, 2.5, "page %d" % nfe)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf
