# -*- coding: utf-8 -*-
"""MANAPRINT — KAPUNKA (RANIHEI & SISTERS) — maquette « main » créée par Maeva (18/10).

🌺 La maquette « KAPUNKA » (A4 portrait, 8 cartons = 2 colonnes × 4 rangées ;
chaque carton : en-tête « RANIHEI & SISTERS / Jeux de bingo, création et vente /
87 77 39 19 / KAPUNKA », fleurs d'hibiscus, et une main tenant 5 pastilles en arc)
est reprise TELLE QUELLE, posée comme UNE SEULE image de fond. On n'ajoute QUE les
chiffres (et un petit N° de série) ; rien n'est redessiné.

REGLE — 5 boules, plages B·I·N·G·O de gauche à droite :
  pastille 1 (gauche) : 1-15 · 2 : 16-30 · 3 (centre) : 31-45 ·
  4 : 46-60 · 5 (droite) : 61-75.
Le tirage couvre 1-75 en continu. Chiffres pleins -> impression Konica rapide.
"""
import io
import os as _os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4
CARTES_PAGE = 8
POLICE = "Helvetica-Bold"
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
NOIR = colors.Color(0, 0, 0)
GRIS = colors.Color(0.45, 0.45, 0.45)

# plages gauche -> droite
BANDS = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

# ── Géométrie mesurée sur la maquette (image 1024×1536 px) ──
_IMG_W, _IMG_H = 1024, 1536
_SX = PAGE_W / _IMG_W
_SY = PAGE_H / _IMG_H

PASTILLES = [
    [(107,246,41), (177,297,36), (257,316,38), (335,296,36), (406,246,41)],
    [(617,246,41), (686,297,36), (765,315,38), (844,296,36), (915,246,41)],
    [(106,624,41), (177,676,36), (256,696,38), (335,675,36), (406,624,41)],
    [(616,624,41), (686,675,36), (765,696,38), (844,675,36), (915,624,41)],
    [(107,1005,41), (176,1056,36), (256,1076,38), (335,1056,35), (405,1005,41)],
    [(617,1005,41), (687,1056,36), (766,1076,38), (845,1056,35), (915,1005,41)],
    [(106,1381,41), (176,1435,36), (256,1456,38), (335,1435,36), (405,1382,41)],
    [(616,1381,41), (686,1435,36), (765,1456,38), (844,1435,36), (915,1382,41)],
]

# N° de série : discret, bas-centre de chaque carton
_CW, _CH = _IMG_W / 2, _IMG_H / 4
_SER_REL_Y = 366


def _x(px):
    return px / _IMG_W * PAGE_W


def _y(py):
    return PAGE_H - py / _IMG_H * PAGE_H


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    p = _os.path.join(d, "kapunka_fond.png")
    if _os.path.exists(p):
        return p
    try:
        for f in _os.listdir(d):
            if "kapunka_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "kapunka_fond.png")
_IMG_FOND = _fond()


def _taille(r_px):
    """Plus grand chiffre (pire cas « 88 ») qui tient dans la pastille."""
    wlim = 2 * r_px * _SX * 0.74
    hlim = 2 * r_px * _SY * 0.78
    t = 40.0
    while t > 6 and (stringWidth("88", POLICE, t) > wlim or t * 0.70 > hlim):
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
    rng = random.Random(int(serie_start) * 100003 + 211)
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
            # N° de série discret (bas-centre)
            ccell = k % 2
            rcell = k // 2
            sx = ccell * _CW + _CW / 2.0
            sy = rcell * _CH + _SER_REL_Y
            c.setFillColor(GRIS)
            c.setFont("Helvetica-Bold", 8.0)
            c.drawCentredString(_x(sx), _y(sy) - 8.0 * 0.34, "N° %05d" % serie)
            serie += 1
            faites += 1
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(GRIS)
            c.setFont("Helvetica", 6.0)
            nfe = page_dep + (faites - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 9 * mm, "%03d" % nfe)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf
