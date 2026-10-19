# -*- coding: utf-8 -*-
"""MANAPRINT — ROYAL · 6 BOULES — maquette « collier » créée par Maeva (17/10).

👑 La maquette « ROYAL » (A4 portrait, 10 cartons = 2 colonnes × 5 rangées ;
chaque carton : en-tête « ROYAL / 6 BOULES », logo 2Kea&Associé, et un collier
à 6 pierres rondes) est reprise TELLE QUELLE, posée comme UNE SEULE image de
fond. On n'ajoute QUE les chiffres (et le N° de série) ; rien n'est redessiné.

REGLE — 6 boules sur 4 plages :
  • pierre extérieure GAUCHE  : 1-30
  • paire GAUCHE (2 pierres)  : 31-40
  • paire DROITE (2 pierres)  : 41-50
  • pierre extérieure DROITE  : 51-90
Le tirage couvre 1-90 en continu. Chiffres pleins -> impression Konica rapide.
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
CARTES_PAGE = 10
POLICE = "Helvetica-Bold"
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
NOIR = colors.Color(0, 0, 0)

PLAGE = {"A": (1, 30), "B": (31, 40), "C": (41, 50), "D": (51, 90)}

_IMG_W, _IMG_H = 1024, 1536
_SX = PAGE_W / _IMG_W
_SY = PAGE_H / _IMG_H

CARTONS = [
    [(106,111,31,'A'), (205,140,30,'B'), (221,214,30,'B'), (313,214,31,'C'), (327,140,30,'C'), (425,112,31,'D')],
    [(604,111,31,'A'), (702,141,30,'B'), (718,214,30,'B'), (809,214,31,'C'), (824,141,31,'C'), (922,111,31,'D')],
    [(106,413,31,'A'), (205,443,30,'B'), (222,516,31,'B'), (312,515,32,'C'), (326,443,30,'C'), (425,413,31,'D')],
    [(603,413,32,'A'), (703,442,30,'B'), (717,515,31,'B'), (809,516,30,'C'), (824,443,30,'C'), (922,413,32,'D')],
    [(106,717,31,'A'), (205,747,31,'B'), (222,820,31,'B'), (313,820,30,'C'), (327,747,30,'C'), (424,717,30,'D')],
    [(604,717,31,'A'), (702,747,30,'B'), (718,820,30,'B'), (808,820,31,'C'), (824,747,30,'C'), (922,718,31,'D')],
    [(106,1019,31,'A'), (205,1049,30,'B'), (222,1122,31,'B'), (313,1122,31,'C'), (326,1049,30,'C'), (424,1019,30,'D')],
    [(603,1020,32,'A'), (702,1050,30,'B'), (717,1123,31,'B'), (809,1123,32,'C'), (824,1051,30,'C'), (922,1021,31,'D')],
    [(106,1322,31,'A'), (205,1353,31,'B'), (221,1427,30,'B'), (312,1426,32,'C'), (325,1353,30,'C'), (424,1322,31,'D')],
    [(604,1324,32,'A'), (702,1354,30,'B'), (717,1427,30,'B'), (809,1427,31,'C'), (824,1354,30,'C'), (922,1325,31,'D')],
]
SER_CENTERS = [[86, 24], [586, 25], [86, 325], [586, 325], [86, 630], [586, 630], [86, 931], [586, 933], [86, 1235], [586, 1237]]


def _x(px):
    return px / _IMG_W * PAGE_W


def _y(py):
    return PAGE_H - py / _IMG_H * PAGE_H


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    p = _os.path.join(d, "royal_fond.png")
    if _os.path.exists(p):
        return p
    try:
        for f in _os.listdir(d):
            if "royal_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "royal_fond.png")
_IMG_FOND = _fond()


def _taille(r_px):
    """Chiffres à 30 pt (cible), réduits seulement si la pierre est trop petite."""
    wlim = 2 * r_px * _SX * 0.96
    hlim = 2 * r_px * _SY * 0.96
    t = 30.0
    while t > 6 and (stringWidth("88", POLICE, t) > wlim or t * 0.70 > hlim):
        t -= 0.5
    return t


def _gen_carton(rng):
    return {
        "A": rng.sample(range(1, 31), 1),
        "B": sorted(rng.sample(range(31, 41), 2)),
        "C": sorted(rng.sample(range(41, 51), 2)),
        "D": rng.sample(range(51, 91), 1),
    }


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                **_ignore):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 777)
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
            carton = CARTONS[k]
            nums = _gen_carton(rng)
            col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else NOIR
            groupes = {"A": [], "B": [], "C": [], "D": []}
            for idx, (px, py, r, grp) in enumerate(carton):
                groupes[grp].append((py, idx))
            for grp in groupes:
                groupes[grp].sort()
            c.setFillColor(col)
            for grp, slots in groupes.items():
                vals = nums[grp]
                for j, (py, idx) in enumerate(slots):
                    px, py2, r, g2 = carton[idx]
                    val = vals[j] if j < len(vals) else vals[-1]
                    t = _taille(r)
                    c.setFont(POLICE, t)
                    c.drawCentredString(_x(px), _y(py2) - t * 0.34, str(val))
            # N° de série : cadre propre + numéro
            scx, scy = SER_CENTERS[k]
            lx, rx = _x(scx - 36), _x(scx + 36)
            ty, by = _y(scy - 12), _y(scy + 12)
            c.setLineWidth(1.1)
            c.setStrokeColor(NOIR)
            c.setFillColor(colors.white)
            c.roundRect(lx, by, rx - lx, ty - by, 4, stroke=1, fill=1)
            c.setFillColor(NOIR)
            c.setFont("Helvetica-Bold", 11.0)
            c.drawCentredString((lx + rx) / 2, _y(scy) - 11.0 * 0.34, "%05d" % serie)
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
