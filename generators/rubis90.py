# -*- coding: utf-8 -*-
"""
MANAPRINT — Generateur RUBIS 90 (format A4 PAYSAGE) — nouvelle maquette

REFAIT LE 11/10 (sceau Maeva) : nouvelle maquette RUBIS 90 (9 cartons 3x3,
en-tete N / RUBIS 90, bande R U B I S, grille 5x3 centre B VIDE). Reprise
TELLE QUELLE, posee comme UNE SEULE image de fond. L'image n'est pas au ratio
A4 : posee en gardant ses proportions (ajustee en largeur, centree) — AUCUNE
deformation.

REGLE INCHANGEE (RUBIS 90 - 14 numeros) :
  R : 3 numeros 1-18    U : 3 numeros 19-36
  B : 2 numeros 37-54 (HAUT et BAS ; centre VIDE)
  I : 3 numeros 55-72   S : 3 numeros 73-90
Chaque colonne triee du plus petit en haut au plus grand en bas.
N de serie dans le "N" de l'en-tete. Chiffres NOIRS (Latin Modern).
"""
import io
import os as _os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as _sw

PAGE_W, PAGE_H = landscape(A4)
CARTES_PAGE = 9
FOND_X, FOND_Y, FOND_W, FOND_H = 0.0, 17.01, 841.89, 561.26
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

CELL_W, CELL_H = 48.34, 32.89
RANGES = [(1,18),(19,36),(37,54),(55,72),(73,90)]  # R U B I S

CARTONS = [
    dict(cols=[[(38.09,489.20), (38.09,452.20), (38.09,415.75)], [(89.89,489.20), (89.89,452.20), (89.89,415.75)], [(142.23,489.20), None, (142.23,415.75)], [(194.58,489.20), (194.58,452.20), (194.58,415.75)], [(246.92,489.20), (246.92,452.20), (246.92,415.75)]], SER=(48.23,554.70)),
    dict(cols=[[(317.08,489.20), (317.08,452.20), (317.08,415.75)], [(368.87,489.20), (368.87,452.20), (368.87,415.75)], [(421.22,489.20), None, (421.22,415.75)], [(473.56,489.20), (473.56,452.20), (473.56,415.75)], [(525.91,489.20), (525.91,452.20), (525.91,415.75)]], SER=(327.22,554.70)),
    dict(cols=[[(590.58,489.20), (590.58,452.20), (590.58,415.75)], [(642.38,489.20), (642.38,452.20), (642.38,415.75)], [(694.72,489.20), None, (694.72,415.75)], [(747.07,489.20), (747.07,452.20), (747.07,415.75)], [(799.41,489.20), (799.41,452.20), (799.41,415.75)]], SER=(600.72,554.70)),
    dict(cols=[[(38.64,302.84), (38.64,265.85), (38.64,229.40)], [(90.44,302.84), (90.44,265.85), (90.44,229.40)], [(142.78,302.84), None, (142.78,229.40)], [(195.13,302.84), (195.13,265.85), (195.13,229.40)], [(247.47,302.84), (247.47,265.85), (247.47,229.40)]], SER=(48.78,368.34)),
    dict(cols=[[(317.08,302.84), (317.08,265.85), (317.08,229.40)], [(368.87,302.84), (368.87,265.85), (368.87,229.40)], [(421.22,302.84), None, (421.22,229.40)], [(473.56,302.84), (473.56,265.85), (473.56,229.40)], [(525.91,302.84), (525.91,265.85), (525.91,229.40)]], SER=(327.22,368.34)),
    dict(cols=[[(590.04,302.84), (590.04,265.85), (590.04,229.40)], [(641.83,302.84), (641.83,265.85), (641.83,229.40)], [(694.18,302.84), None, (694.18,229.40)], [(746.52,302.84), (746.52,265.85), (746.52,229.40)], [(798.86,302.84), (798.86,265.85), (798.86,229.40)]], SER=(600.18,368.34)),
    dict(cols=[[(38.09,116.49), (38.09,79.49), (38.09,43.04)], [(89.89,116.49), (89.89,79.49), (89.89,43.04)], [(142.23,116.49), None, (142.23,43.04)], [(194.58,116.49), (194.58,79.49), (194.58,43.04)], [(246.92,116.49), (246.92,79.49), (246.92,43.04)]], SER=(48.23,181.99)),
    dict(cols=[[(317.08,116.49), (317.08,79.49), (317.08,43.04)], [(368.87,116.49), (368.87,79.49), (368.87,43.04)], [(421.22,116.49), None, (421.22,43.04)], [(473.56,116.49), (473.56,79.49), (473.56,43.04)], [(525.91,116.49), (525.91,79.49), (525.91,43.04)]], SER=(327.22,181.99)),
    dict(cols=[[(590.04,116.49), (590.04,79.49), (590.04,43.04)], [(641.83,116.49), (641.83,79.49), (641.83,43.04)], [(694.18,116.49), None, (694.18,43.04)], [(746.52,116.49), (746.52,79.49), (746.52,43.04)], [(798.86,116.49), (798.86,79.49), (798.86,43.04)]], SER=(600.18,181.99)),
]


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("rubis90_fond.png","rubis90_maquette_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "rubis90_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"rubis90_fond.png")
_IMG_FOND=_fond()

_w88=max(_sw("88",POLICE_NUM,1.0),0.01)
_T_NUM = min(CELL_W*0.82/_w88, CELL_H*0.94)
_T_SER = 8.0

def _gen_carte(rng):
    cols=[]
    for ci,(lo,hi) in enumerate(RANGES):
        if ci==2:
            nums=sorted(rng.sample(range(lo,hi+1),2))   # B : 2 (centre vide)
        else:
            nums=sorted(rng.sample(range(lo,hi+1),3))
        cols.append(nums)
    return cols

def generer_pdf(nb_cartes=9, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                style="", motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+90)
    n_=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,FOND_X,FOND_Y,FOND_W,FOND_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n_: break
            data=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for ci, colpts in enumerate(pos["cols"]):
                vals=data[ci]
                # colpts a 3 positions (B: la position centrale est None)
                slot=0
                for p in colpts:
                    if p is None: continue
                    if slot<len(vals):
                        c.drawCentredString(p[0], p[1]-_T_NUM*0.34, str(vals[slot]))
                        slot+=1
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,_T_SER)
            c.drawCentredString(pos["SER"][0], pos["SER"][1]-_T_SER*0.34, "%06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, PAGE_H-10, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
