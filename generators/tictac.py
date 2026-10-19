# -*- coding: utf-8 -*-
"""MANAPRINT — TIC TAC (RANIHEI & SISTERS) — maquette « horloge » créée par Maeva (18/10).

🕐 La maquette « TIC TAC » (A4 PAYSAGE, 8 cartons = 2 rangées × 4 colonnes ;
chaque carton : en-tête « RANIHEI & SISTERS / TIC TAC », case N°, et un cadran
d'horloge avec 8 pastilles) est reprise TELLE QUELLE, posée comme UNE SEULE image
de fond. On n'ajoute QUE les chiffres (et le N° de série) ; rien n'est redessiné.

REGLE — 8 boules réparties de 1-90 dans le SENS HORAIRE (départ à 12h) :
  12h : 1-11 · 1h30 : 12-22 · 3h : 23-34 · 4h30 : 35-45 ·
  6h : 46-56 · 7h30 : 57-68 · 9h : 69-79 · 10h30 : 80-90.
Le tirage couvre 1-90 en continu. Chiffres pleins -> impression Konica rapide.
"""
import io
import os as _os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = landscape(A4)        # 841.9 × 595.3
CARTES_PAGE = 8
POLICE = "Helvetica-Bold"
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
NOIR = colors.Color(0, 0, 0)

# plages par position horaire (0 = 12h, puis sens horaire)
BANDS = [(1, 11), (12, 22), (23, 34), (35, 45),
         (46, 56), (57, 68), (69, 79), (80, 90)]

# ── Géométrie mesurée sur la maquette (image 1491×1055 px, A4 paysage) ──
_IMG_W, _IMG_H = 1491, 1055
_SX = PAGE_W / _IMG_W
_SY = PAGE_H / _IMG_H

PASTILLES = [
    [(198,192,37), (288,228,37), (310,306,34), (282,384,37), (196,422,38), (112,384,36), (88,308,34), (110,228,36)],
    [(586,192,34), (670,230,32), (692,308,37), (664,384,33), (586,422,34), (506,384,32), (480,308,37), (504,228,32)],
    [(948,192,32), (1034,230,36), (1054,308,34), (1028,384,37), (948,422,34), (868,384,36), (842,308,33), (866,228,32)],
    [(1312,192,37), (1394,230,32), (1412,308,33), (1386,384,36), (1310,420,33), (1234,384,33), (1210,308,36), (1230,230,36)],
    [(198,708,37), (288,744,36), (310,822,38), (282,898,33), (196,936,34), (112,898,37), (88,822,33), (110,744,33)],
    [(586,708,36), (668,744,36), (692,822,33), (664,898,37), (584,936,37), (504,896,37), (480,820,37), (504,744,32)],
    [(950,708,32), (1034,744,32), (1056,822,34), (1030,898,37), (946,936,36), (866,898,33), (842,822,36), (864,744,37)],
    [(1312,708,37), (1392,744,36), (1414,822,32), (1386,898,32), (1310,936,36), (1234,898,32), (1206,822,36), (1230,744,32)],
]
NBOXES = [[332, 85, 40, 55], [703, 85, 41, 55], [1068, 85, 49, 55], [1418, 85, 56, 55], [332, 602, 40, 54], [703, 602, 41, 54], [1068, 602, 49, 54], [1418, 602, 56, 54]]  # case N° : (x0,y0,w,h) px, [723, 123], [1092, 123], [1446, 123], [352, 639], [723, 639], [1092, 639], [1446, 639]]


def _x(px):
    return px / _IMG_W * PAGE_W


def _y(py):
    return PAGE_H - py / _IMG_H * PAGE_H


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    p = _os.path.join(d, "tictac_fond.png")
    if _os.path.exists(p):
        return p
    try:
        for f in _os.listdir(d):
            if "tictac_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "tictac_fond.png")
_IMG_FOND = _fond()


def _taille(r_px):
    """Chiffres à 30 pt, réduits seulement si une pastille est trop petite."""
    wlim = 2 * r_px * _SX * 0.98
    hlim = 2 * r_px * _SY * 0.98
    t = 30.0
    while t > 6 and (stringWidth("88", POLICE, t) > wlim or t * 0.70 > hlim):
        t -= 0.5
    return t


def _taille_serie(w_px):
    """Taille du N° de série pour qu'il tienne dans la case (marge)."""
    wlim = w_px * _SX * 0.78
    t = 11.0
    while t > 5 and stringWidth("00000", "Helvetica-Bold", t) > wlim:
        t -= 0.5
    return t


def _gen_carton(rng):
    return [rng.randint(a, b) for (a, b) in BANDS]


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                **_ignore):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 909)
    serie = int(serie_start)
    faites = 0
    try:
        page_dep = max(1, int(page_start))
    except Exception:
        page_dep = 1

    while faites < n_:
        try:
            c.drawImage(_IMG_FOND, 0, 0, PAGE_W, PAGE_H,
                        preserveAspectRatio=False, mask="auto")
        except Exception:
            pass
        for k in range(CARTES_PAGE):
            if faites >= n_:
                break
            nums = _gen_carton(rng)
            col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col)
            for i, (px, py, r) in enumerate(PASTILLES[k]):
                t = _taille(r)
                c.setFont(POLICE, t)
                c.drawCentredString(_x(px), _y(py) - t * 0.34, str(nums[i]))
            # N° de série : centré dans la case N° (bas de la case, sous « N° »)
            bx0, by0, bw, bh = NBOXES[k]
            ts = _taille_serie(bw)
            c.setFillColor(NOIR)
            c.setFont("Helvetica-Bold", ts)
            c.drawCentredString(_x(bx0 + bw / 2.0),
                                _y(by0 + bh * 0.72) - ts * 0.34, "%05d" % serie)
            serie += 1
            faites += 1
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(colors.Color(0.45, 0.45, 0.45))
            c.setFont("Helvetica", 6.0)
            nfe = page_dep + (faites - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 9 * mm, "%03d" % nfe)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf
