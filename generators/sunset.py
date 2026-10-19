# -*- coding: utf-8 -*-
"""MANAPRINT — SUNSET (RANIHEI SISTERS & SHOP) — maquette « coucher de soleil » (18/10).

🌅 La maquette « SUNSET » (A4 PAYSAGE, 8 cartons = 2 rangées × 4 colonnes ;
chaque carton : en-tête « RANIHEI SISTERS & SHOP », scène plage/palmiers/SUNSET,
et 5 bulles en quinconce — 3 en haut, 2 en bas) est reprise TELLE QUELLE, posée
comme UNE SEULE image de fond. On n'ajoute QUE les chiffres (et un petit N° de
série) ; rien n'est redessiné.

REGLE — 1-90, 2 boules par bulle (comme OHANA 90) séparées par « / » :
  5 plages fixes de 18, ordre lecture —
  haut :  bulle1 1-18 · bulle2 19-36 · bulle3 37-54
  bas  :  bulle4 55-72 · bulle5 73-90
Le tirage couvre 1-90 en continu. Chiffres pleins -> impression Konica rapide.
"""
import io
import os as _os
import math
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
GRIS = colors.Color(0.45, 0.45, 0.45)

# plages par bulle (ordre : haut G-C-D, puis bas G-D)
BANDS = [(1, 18), (19, 36), (37, 54), (55, 72), (73, 90)]

# ── Géométrie mesurée sur la maquette (image 1491×1055 px, A4 paysage) ──
_IMG_W, _IMG_H = 1491, 1055
_SX = PAGE_W / _IMG_W
_SY = PAGE_H / _IMG_H

PASTILLES = [
    [(93,332,45), (193,334,45), (293,332,45), (137,437,48), (250,437,48)],
    [(470,331,45), (570,334,45), (670,332,45), (513,437,48), (624,437,48)],
    [(839,332,45), (937,334,45), (1037,332,46), (881,436,48), (992,437,48)],
    [(1206,332,45), (1305,334,45), (1406,331,45), (1248,437,48), (1359,437,48)],
    [(91,855,46), (192,858,46), (294,856,46), (137,961,48), (248,962,48)],
    [(467,855,46), (568,858,45), (668,856,46), (511,961,48), (622,962,48)],
    [(838,856,46), (937,858,45), (1037,857,46), (881,961,48), (992,962,48)],
    [(1205,855,46), (1305,858,45), (1405,855,46), (1248,961,48), (1359,961,48)],
]

_CW, _CH = _IMG_W / 4, _IMG_H / 2
_SER_REL_Y = 505   # N° de série discret, bas de carton


def _x(px):
    return px / _IMG_W * PAGE_W


def _y(py):
    return PAGE_H - py / _IMG_H * PAGE_H


def _fond():
    d = _os.path.dirname(_os.path.abspath(__file__))
    p = _os.path.join(d, "sunset_fond.png")
    if _os.path.exists(p):
        return p
    try:
        for f in _os.listdir(d):
            if "sunset_fond" in f.lower() and f.lower().endswith(".png"):
                return _os.path.join(d, f)
    except Exception:
        pass
    return _os.path.join(d, "sunset_fond.png")
_IMG_FOND = _fond()


_OFF_F = 0.42   # décalage vertical de chaque chiffre (en fraction de la taille)


def _taille(r_px):
    """Plus grand chiffre en FRACTION dont les 2 nombres restent DANS le cercle."""
    rp = r_px * _SY          # rayon de la bulle en points (bulle quasi ronde)
    lim = rp * 0.90          # coin du chiffre doit rester sous ce rayon
    t = 34.0
    while t > 5:
        w = stringWidth("88", POLICE, t)
        h = t * 0.70
        corner = math.hypot(w / 2.0, _OFF_F * t + h / 2.0)
        if corner <= lim:
            return t
        t -= 0.5
    return t


def _gen_carton(rng):
    paires = []
    for a, b in BANDS:
        x, y = rng.sample(range(a, b + 1), 2)
        paires.append(tuple(sorted((x, y))))
    return paires


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                **_ignore):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 313)
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
            paires = _gen_carton(rng)
            col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col)
            for i, (px, py, r) in enumerate(PASTILLES[k]):
                a, b = paires[i]
                t = _taille(r)
                cx = _x(px)
                cyc = _y(py)
                off = t * _OFF_F
                c.setFont(POLICE, t)
                # chiffre du HAUT (plus petit)
                c.drawCentredString(cx, cyc + off - t * 0.34, str(a))
                # chiffre du BAS (plus grand)
                c.drawCentredString(cx, cyc - off - t * 0.34, str(b))
                # barre de fraction
                hw = stringWidth("88", POLICE, t) / 2.0 + 2.0
                c.setLineWidth(max(1.1, t * 0.055))
                c.setStrokeColor(col)
                c.line(cx - hw, cyc, cx + hw, cyc)
            # N° de série discret (bas-centre)
            ccell = k % 2 if False else k % 4
            rcell = k // 4
            sx = (k % 4) * _CW + _CW / 2.0
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
