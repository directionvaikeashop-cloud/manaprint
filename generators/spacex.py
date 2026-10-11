# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur SPACE (fusées, format A4 PAYSAGE)

REFAIT LE 10/10 (sceau Maeva) : maquette SPACE fusée verticale, 4 cercles
EMPILÉS. Reprise TELLE QUELLE, posée comme UNE SEULE image de fond
(impression rapide). 15 fusées par feuille (5 × 3).

RÈGLE : 4 numéros par fusée, UN PAR TRANCHE, de HAUT en BAS :
  cercle du haut 1-19 · 2e 20-39 · 3e 40-69 · cercle du bas 70-90.
Chiffres NOIRS (Latin Modern) à 30 pt, centrés, N° de série en bas à gauche.
"""
import io
import os as _os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PAGE_W, PAGE_H = landscape(A4)
CARTES_PAGE = 15
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

R_PT = 19.13
_T_NUM = 30.0      # taille demandee par Maeva (10/10)
FOND_X, FOND_Y, FOND_W, FOND_H = 24.09, 0.00, 793.70, 595.28
TRANCHES = [(1,19),(20,39),(40,69),(70,90)]

CARTONS = [
    dict(C=[(129.06, 531.42), (129.06, 494.69), (129.06, 460.71), (129.06, 421.24)], SER=(30.44, 403.80)),
    dict(C=[(291.86, 530.87), (291.86, 496.34), (291.86, 461.26), (291.31, 421.24)], SER=(189.18, 403.80)),
    dict(C=[(439.86, 531.97), (440.40, 495.24), (439.86, 460.16), (440.40, 423.98)], SER=(347.92, 403.80)),
    dict(C=[(588.40, 535.25), (588.95, 494.14), (588.95, 461.26), (588.95, 421.79)], SER=(506.66, 403.80)),
    dict(C=[(738.59, 533.61), (738.59, 497.43), (739.14, 461.80), (738.59, 422.34)], SER=(665.40, 403.80)),
    dict(C=[(129.06, 345.60), (129.61, 311.62), (129.06, 276.53), (129.06, 234.88)], SER=(30.44, 205.37)),
    dict(C=[(291.31, 349.98), (290.76, 309.42), (291.86, 274.89), (291.31, 235.97)], SER=(189.18, 205.37)),
    dict(C=[(440.95, 349.44), (442.05, 310.52), (437.66, 273.79), (439.86, 234.33)], SER=(347.92, 205.37)),
    dict(C=[(588.95, 345.05), (591.14, 310.52), (588.95, 272.15), (588.95, 234.88)], SER=(506.66, 205.37)),
    dict(C=[(738.59, 346.15), (738.59, 311.62), (739.69, 274.34), (739.14, 234.33)], SER=(665.40, 205.37)),
    dict(C=[(129.61, 163.62), (126.87, 126.35), (129.06, 87.43), (129.06, 52.90)], SER=(30.44, 6.94)),
    dict(C=[(291.31, 163.07), (291.31, 129.09), (291.31, 87.43), (291.31, 50.15)], SER=(189.18, 6.94)),
    dict(C=[(439.86, 163.07), (440.40, 127.99), (439.86, 87.98), (440.40, 50.15)], SER=(347.92, 6.94)),
    dict(C=[(588.95, 163.07), (588.95, 129.09), (588.95, 89.62), (588.40, 53.44)], SER=(506.66, 6.94)),
    dict(C=[(739.14, 161.97), (736.95, 126.35), (738.59, 87.98), (739.14, 50.15)], SER=(665.40, 6.94)),
]

def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("spacex_fond.png","space_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "space" in f.lower() and "fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"spacex_fond.png")
_IMG_FOND=_fond()

def _gen_carte(rng):
    return [rng.randint(a,b) for (a,b) in TRANCHES]

def generer_pdf(nb_cartes=15, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+11)
    n=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n:
        try: c.drawImage(_IMG_FOND, FOND_X, FOND_Y, FOND_W, FOND_H, preserveAspectRatio=True, mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n: break
            nums=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for (cx,cy),val in zip(pos["C"],nums):
                c.drawCentredString(cx, cy-_T_NUM*0.33, str(val))
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,5.5)
            c.drawString(pos["SER"][0], pos["SER"][1], "N\u00b0 %06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, PAGE_H-10, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
