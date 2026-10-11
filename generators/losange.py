# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur LOSANGE (format A4 PORTRAIT)

REFAIT LE 11/10 (sceau Maeva) : nouvelle maquette LOSANGE · 8 BOULES en
couronne. Reprise TELLE QUELLE, posée comme UNE SEULE image de fond
(impression rapide). 12 cartons par feuille.

RÈGLE INCHANGÉE (8 boules) :
  flanc GAUCHE : 3 numéros 1-30 (triés, haut -> bas)
  flanc DROIT  : 3 numéros 46-75 (triés, haut -> bas)
  HAUT + BAS   : 2 numéros 31-45 (triés)
N° de série dans le carré pointillé central. Chiffres NOIRS (Latin Modern).
"""
import io
import os as _os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as _sw

PAGE_W, PAGE_H = A4            # portrait
CARTES_PAGE = 12
try:
    pdfmetrics.registerFont(TTFont("LMROMAN", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    POLICE_NUM = "LMROMAN"
except Exception:
    POLICE_NUM = "Times-Bold"
POLICE_PETIT = "Helvetica"
RAINBOW = ["#E53935","#FB8C00","#F9A825","#43A047","#00ACC1",
           "#1E88E5","#3949AB","#8E24AA","#D81B60","#6D4C41"]
NOIR = colors.Color(0,0,0)
GRIS = colors.Color(0.45,0.45,0.45)

R_PT = 21.45
# Cadrage vertical : on descend tout le contenu pour que le blanc soit
# davantage en HAUT qu'en bas (demande Maeva 11/10).
DECAL_Y = -28.0
# ordre des 8 cercles : TOP, UL, UR, L, R, LL, LR, BOT
CARTONS = [
    dict(C=[(101.25, 806.15), (60.90, 777.64), (142.06, 777.73), (34.20, 739.34), (168.01, 739.43), (59.68, 699.62), (142.91, 699.34), (101.25, 671.48)], SER=(101.28, 718.51)),
    dict(C=[(296.76, 806.15), (256.41, 777.64), (337.57, 777.73), (229.71, 739.34), (363.52, 739.43), (255.19, 699.62), (338.42, 699.34), (296.76, 671.48)], SER=(296.79, 718.51)),
    dict(C=[(493.11, 806.43), (452.77, 777.92), (533.93, 778.01), (426.06, 739.62), (559.88, 739.71), (451.55, 699.90), (534.77, 699.62), (493.11, 671.77)], SER=(493.15, 718.80)),
    dict(C=[(100.40, 611.91), (60.06, 583.40), (141.21, 583.49), (33.35, 545.10), (167.17, 545.19), (58.83, 505.38), (142.06, 505.10), (100.40, 477.24)], SER=(100.44, 524.28)),
    dict(C=[(296.76, 611.63), (256.41, 583.12), (337.57, 583.21), (229.71, 544.81), (363.52, 544.91), (255.19, 505.10), (338.42, 504.82), (296.76, 476.96)], SER=(296.79, 523.99)),
    dict(C=[(492.83, 611.63), (452.49, 583.12), (533.64, 583.21), (425.78, 544.81), (559.60, 544.91), (451.26, 505.10), (534.49, 504.82), (492.83, 476.96)], SER=(492.87, 523.99)),
    dict(C=[(100.68, 416.55), (60.34, 388.03), (141.50, 388.12), (33.63, 349.73), (167.45, 349.82), (59.12, 310.02), (142.34, 309.73), (100.68, 281.88)], SER=(100.72, 328.91)),
    dict(C=[(296.47, 416.55), (256.13, 388.03), (337.29, 388.12), (229.42, 349.73), (363.24, 349.82), (254.91, 310.02), (338.13, 309.73), (296.47, 281.88)], SER=(296.51, 328.91)),
    dict(C=[(492.83, 416.55), (452.49, 388.03), (533.64, 388.12), (425.78, 349.73), (559.60, 349.82), (451.26, 310.02), (534.49, 309.73), (492.83, 281.88)], SER=(492.87, 328.91)),
    dict(C=[(100.12, 222.31), (59.77, 193.79), (140.93, 193.89), (33.07, 155.49), (166.89, 155.58), (58.55, 115.78), (141.78, 115.49), (100.12, 87.64)], SER=(100.15, 134.67)),
    dict(C=[(296.47, 221.74), (256.13, 193.23), (337.29, 193.32), (229.42, 154.93), (363.24, 155.02), (254.91, 115.21), (338.13, 114.93), (296.47, 87.07)], SER=(296.51, 134.10)),
    dict(C=[(493.39, 222.31), (453.05, 193.79), (534.21, 193.89), (426.34, 155.49), (560.16, 155.58), (451.83, 115.78), (535.05, 115.49), (493.39, 87.64)], SER=(493.43, 134.67)),
]


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("losange_fond.png","losange8_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "losange_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"losange_fond.png")
_IMG_FOND=_fond()

_a=_sw("88",POLICE_NUM,1.0)/2.0
_T_NUM = R_PT*0.86/max((_a*_a+0.35*0.35)**0.5,0.01)

def _gen_carte(rng):
    g=sorted(rng.sample(range(1,31),3))      # gauche 1-30
    d=sorted(rng.sample(range(46,76),3))     # droite 46-75
    tb=sorted(rng.sample(range(31,46),2))    # haut/bas 31-45
    # ordre: TOP, UL, UR, L, R, LL, LR, BOT
    return [tb[0], g[0], d[0], g[1], d[1], g[2], d[2], tb[1]]

def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+13)
    n=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n:
        try: c.drawImage(_IMG_FOND,0,DECAL_Y,PAGE_W,PAGE_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n: break
            nums=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for (cx,cy),val in zip(pos["C"],nums):
                c.drawCentredString(cx, cy+DECAL_Y-_T_NUM*0.33, str(val))
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            c.drawCentredString(pos["SER"][0], pos["SER"][1]+DECAL_Y, "N° %06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, PAGE_H-10, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
