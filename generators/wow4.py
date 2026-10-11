# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur WOW 4 (format A4 PORTRAIT)

REFAIT LE 11/10 (sceau Maeva) : nouvelle maquette « WOW · 4 boules » (12
cartons, 4 cases carrées 2x2 par carton). Reprise TELLE QUELLE, posée comme
UNE SEULE image de fond (impression rapide). 12 cartons par feuille.

RÈGLE INCHANGÉE (WOW 4) :
  colonne de GAUCHE (W) : 2 numéros 30-44 (triés, haut -> bas)
  colonne de DROITE (O) : 2 numéros 45-60 (triés, haut -> bas)
N° de série dans le bas du cadre. Chiffres NOIRS (Latin Modern), au plus grand.
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

CELL_W, CELL_H = 77.73, 66.4
RANGES = {"W": (30, 44), "O": (45, 60)}

CARTONS = [
    dict(W=[(70.60,760.92),(70.60,689.82)], O=[(152.77,760.92),(152.77,689.82)], SER=(113.80,650.60)),
    dict(W=[(257.54,760.92),(257.54,689.82)], O=[(338.58,760.92),(338.58,689.82)], SER=(299.05,650.60)),
    dict(W=[(443.92,760.92),(443.92,689.82)], O=[(525.24,760.92),(525.24,689.82)], SER=(484.30,650.60)),
    dict(W=[(70.60,558.34),(70.31,487.25)], O=[(152.77,558.34),(152.77,487.25)], SER=(113.80,447.47)),
    dict(W=[(257.54,558.34),(257.54,487.25)], O=[(338.58,558.34),(338.58,487.25)], SER=(299.05,447.47)),
    dict(W=[(443.92,558.34),(443.92,487.25)], O=[(525.24,558.34),(525.24,487.25)], SER=(484.30,447.47)),
    dict(W=[(70.31,354.36),(70.60,283.55)], O=[(152.77,354.36),(152.77,283.55)], SER=(113.80,243.76)),
    dict(W=[(257.54,354.36),(257.54,283.55)], O=[(338.58,354.36),(338.58,283.55)], SER=(299.05,243.76)),
    dict(W=[(443.92,354.36),(443.92,283.55)], O=[(525.24,354.36),(525.24,283.55)], SER=(484.30,243.76)),
    dict(W=[(70.60,152.07),(70.60,80.97)], O=[(152.77,152.07),(152.77,80.97)], SER=(113.80,41.76)),
    dict(W=[(257.54,152.07),(257.54,80.97)], O=[(338.58,152.35),(338.58,80.97)], SER=(299.05,41.76)),
    dict(W=[(443.92,152.35),(443.92,80.97)], O=[(525.24,152.07),(525.24,80.97)], SER=(484.30,41.76)),
]


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("wow4_boules_fond.png","wow4_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "wow4_boules_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"wow4_boules_fond.png")
_IMG_FOND=_fond()

# chiffres au plus grand qui tient dans la case
_w88=max(_sw("88",POLICE_NUM,1.0),0.01)
_T_NUM = min(CELL_W*0.70/_w88, CELL_H*0.74)

def _gen_carte(rng):
    w=sorted(rng.sample(range(30,45),2))   # gauche 30-44
    o=sorted(rng.sample(range(45,61),2))   # droite 45-60
    return w,o

def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                style="", motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+4)
    n=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n:
        try: c.drawImage(_IMG_FOND,0,0,PAGE_W,PAGE_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n: break
            w,o=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for (cx,cy),val in zip(pos["W"], w):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            for (cx,cy),val in zip(pos["O"], o):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            c.drawCentredString(pos["SER"][0], pos["SER"][1], "N° %06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, PAGE_H-10, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
