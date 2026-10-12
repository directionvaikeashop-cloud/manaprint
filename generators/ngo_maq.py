# -*- coding: utf-8 -*-
"""
MANAPRINT — Generateur NGO (format A4 PAYSAGE)

REFAIT LE 11/10 (sceau Maeva) : nouvelle maquette NGO (16 cartons 4x4,
en-tete N G O, grille 3x3 case centrale VIDE). Reprise TELLE QUELLE, posee
comme UNE SEULE image de fond. L'image n'est pas au ratio A4 : posee en
gardant ses proportions (ajustee en largeur, centree) — AUCUNE deformation.

REGLE INCHANGEE (NGO 8 boules) :
  colonne N : 3 numeros 31-45 (tries haut -> bas)
  colonne G : 2 numeros 46-60 (HAUT et BAS ; centre VIDE)
  colonne O : 3 numeros 61-75 (tries haut -> bas)
N de serie dans la case centrale (la case signature). Chiffres NOIRS (Latin Modern).
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
CARTES_PAGE = 16
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

CELL_W, CELL_H = 60.84, 33.98

CARTONS = [
    dict(N=[(53.99,531.68),(53.99,497.97),(53.99,463.71)], G=[(114.83,531.68),(114.83,463.71)], O=[(176.49,531.68),(176.49,497.97),(176.49,463.71)], SER=(114.83,497.97)),
    dict(N=[(257.88,531.68),(257.88,497.97),(257.88,463.71)], G=[(318.72,531.68),(318.72,463.71)], O=[(380.39,531.68),(380.39,497.97),(380.39,463.71)], SER=(318.72,497.97)),
    dict(N=[(459.59,531.68),(459.59,497.97),(459.59,463.71)], G=[(520.43,531.68),(520.43,463.71)], O=[(582.09,531.68),(582.09,497.97),(582.09,463.71)], SER=(520.43,497.97)),
    dict(N=[(662.93,531.68),(662.93,497.97),(662.93,463.71)], G=[(723.77,531.68),(723.77,463.71)], O=[(785.43,531.68),(785.43,497.97),(785.43,463.71)], SER=(723.77,497.97)),
    dict(N=[(53.99,392.46),(53.99,358.75),(53.99,324.49)], G=[(114.83,392.46),(114.83,324.49)], O=[(176.49,392.46),(176.49,358.75),(176.49,324.49)], SER=(114.83,358.75)),
    dict(N=[(257.88,392.46),(257.88,358.75),(257.88,324.49)], G=[(318.72,392.46),(318.72,324.49)], O=[(380.39,392.46),(380.39,358.75),(380.39,324.49)], SER=(318.72,358.75)),
    dict(N=[(459.59,392.46),(459.59,358.75),(459.59,324.49)], G=[(520.43,392.46),(520.43,324.49)], O=[(582.09,392.46),(582.09,358.75),(582.09,324.49)], SER=(520.43,358.75)),
    dict(N=[(662.93,392.46),(662.93,358.75),(662.93,324.49)], G=[(723.77,392.46),(723.77,324.49)], O=[(785.43,392.46),(785.43,358.75),(785.43,324.49)], SER=(723.77,358.75)),
    dict(N=[(53.99,254.34),(53.99,220.63),(53.99,186.37)], G=[(114.83,254.34),(114.83,186.37)], O=[(176.49,254.34),(176.49,220.63),(176.49,186.37)], SER=(114.83,220.63)),
    dict(N=[(257.88,254.34),(257.88,220.63),(257.88,186.37)], G=[(318.72,254.34),(318.72,186.37)], O=[(380.39,254.34),(380.39,220.63),(380.39,186.37)], SER=(318.72,220.63)),
    dict(N=[(459.59,254.34),(459.59,220.63),(459.59,186.37)], G=[(520.43,254.34),(520.43,186.37)], O=[(582.09,254.34),(582.09,220.63),(582.09,186.37)], SER=(520.43,220.63)),
    dict(N=[(662.93,254.34),(662.93,220.63),(662.93,186.37)], G=[(723.77,254.34),(723.77,186.37)], O=[(785.43,254.34),(785.43,220.63),(785.43,186.37)], SER=(723.77,220.63)),
    dict(N=[(53.99,116.21),(53.99,82.51),(53.99,48.25)], G=[(114.83,116.21),(114.83,48.25)], O=[(176.49,116.21),(176.49,82.51),(176.49,48.25)], SER=(114.83,82.51)),
    dict(N=[(257.88,116.21),(257.88,82.51),(257.88,48.25)], G=[(318.72,116.21),(318.72,48.25)], O=[(380.39,116.21),(380.39,82.51),(380.39,48.25)], SER=(318.72,82.51)),
    dict(N=[(459.59,116.21),(459.59,82.51),(459.59,48.25)], G=[(520.43,116.21),(520.43,48.25)], O=[(582.09,116.21),(582.09,82.51),(582.09,48.25)], SER=(520.43,82.51)),
    dict(N=[(662.93,116.21),(662.93,82.51),(662.93,48.25)], G=[(723.77,116.21),(723.77,48.25)], O=[(785.43,116.21),(785.43,82.51),(785.43,48.25)], SER=(723.77,82.51)),
]


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("ngo_fond.png","ngo8_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "ngo_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"ngo_fond.png")
_IMG_FOND=_fond()

_w88=max(_sw("88",POLICE_NUM,1.0),0.01)
_T_NUM = min(CELL_W*0.80/_w88, CELL_H*0.92)
_T_SER = 7.0

def _gen_carte(rng):
    n=sorted(rng.sample(range(31,46),3))   # N 31-45
    g=sorted(rng.sample(range(46,61),2))   # G 46-60 (haut/bas)
    o=sorted(rng.sample(range(61,76),3))   # O 61-75
    return n,g,o

def generer_pdf(nb_cartes=16, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                style="", motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+9)
    n_=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,FOND_X,FOND_Y,FOND_W,FOND_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n_: break
            n,g,o=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for (cx,cy),val in zip(pos["N"], n):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            for (cx,cy),val in zip(pos["G"], g):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            for (cx,cy),val in zip(pos["O"], o):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,_T_SER)
            c.drawCentredString(pos["SER"][0], pos["SER"][1]-_T_SER*0.34, "%06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, PAGE_H-10, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
