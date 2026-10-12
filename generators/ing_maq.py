# -*- coding: utf-8 -*-
"""
MANAPRINT — Generateur ING (format A4 PAYSAGE) — nouvelle maquette

REFAIT LE 11/10 (sceau Maeva) : nouvelle maquette ING (16 cartons 4x4,
en-tete I N G, grille 3x3 case centrale VIDE). Reprise TELLE QUELLE, posee
comme UNE SEULE image de fond. L'image n'est pas au ratio A4 : posee en
gardant ses proportions (ajustee en largeur, centree) — AUCUNE deformation.

REGLE INCHANGEE (ING - 8 boules) :
  colonne I : 3 numeros 16-30 (CROISSANTS, haut -> bas)
  colonne N : 2 numeros 31-45 (DECROISSANTS — le plus grand EN HAUT ; centre VIDE)
  colonne G : 3 numeros 46-60 (CROISSANTS, haut -> bas)
N de serie dans la case centrale. Chiffres NOIRS (Latin Modern).
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
    dict(I=[(53.99,531.68),(53.99,498.24),(53.99,464.26)], N=[(114.83,531.68),(114.83,464.26)], G=[(176.49,531.68),(176.49,498.24),(176.49,464.26)], SER=(114.83,498.24)),
    dict(I=[(257.88,531.68),(257.88,498.24),(257.88,464.26)], N=[(318.72,531.68),(318.72,464.26)], G=[(380.39,531.68),(380.39,498.24),(380.39,464.26)], SER=(318.72,498.24)),
    dict(I=[(459.59,531.68),(459.59,498.24),(459.59,464.26)], N=[(520.43,531.68),(520.43,464.26)], G=[(582.09,531.68),(582.09,498.24),(582.09,464.26)], SER=(520.43,498.24)),
    dict(I=[(662.93,531.68),(662.93,498.24),(662.93,464.26)], N=[(723.77,531.68),(723.77,464.26)], G=[(785.43,531.68),(785.43,498.24),(785.43,464.26)], SER=(723.77,498.24)),
    dict(I=[(53.99,392.46),(53.99,359.03),(53.99,325.04)], N=[(114.83,392.46),(114.83,325.04)], G=[(176.49,392.46),(176.49,359.03),(176.49,325.04)], SER=(114.83,359.03)),
    dict(I=[(257.88,392.46),(257.88,359.03),(257.88,325.04)], N=[(318.72,392.46),(318.72,325.04)], G=[(380.39,392.46),(380.39,359.03),(380.39,325.04)], SER=(318.72,359.03)),
    dict(I=[(459.59,392.46),(459.59,359.03),(459.59,325.04)], N=[(520.43,392.46),(520.43,325.04)], G=[(582.09,392.46),(582.09,359.03),(582.09,325.04)], SER=(520.43,359.03)),
    dict(I=[(662.93,392.46),(662.93,359.03),(662.93,325.04)], N=[(723.77,392.46),(723.77,325.04)], G=[(785.43,392.46),(785.43,359.03),(785.43,325.04)], SER=(723.77,359.03)),
    dict(I=[(53.99,254.34),(53.99,220.90),(53.99,186.92)], N=[(114.83,254.34),(114.83,186.92)], G=[(176.49,254.34),(176.49,220.90),(176.49,186.92)], SER=(114.83,220.90)),
    dict(I=[(257.88,254.34),(257.88,220.90),(257.88,186.92)], N=[(318.72,254.34),(318.72,186.92)], G=[(380.39,254.34),(380.39,220.90),(380.39,186.92)], SER=(318.72,220.90)),
    dict(I=[(459.59,254.34),(459.59,220.90),(459.59,186.92)], N=[(520.43,254.34),(520.43,186.92)], G=[(582.09,254.34),(582.09,220.90),(582.09,186.92)], SER=(520.43,220.90)),
    dict(I=[(662.93,254.34),(662.93,220.90),(662.93,186.92)], N=[(723.77,254.34),(723.77,186.92)], G=[(785.43,254.34),(785.43,220.90),(785.43,186.92)], SER=(723.77,220.90)),
    dict(I=[(53.99,116.21),(53.99,82.78),(53.99,48.80)], N=[(114.83,116.21),(114.83,48.80)], G=[(176.49,116.21),(176.49,82.78),(176.49,48.80)], SER=(114.83,82.78)),
    dict(I=[(257.88,116.21),(257.88,82.78),(257.88,48.80)], N=[(318.72,116.21),(318.72,48.80)], G=[(380.39,116.21),(380.39,82.78),(380.39,48.80)], SER=(318.72,82.78)),
    dict(I=[(459.59,116.21),(459.59,82.78),(459.59,48.80)], N=[(520.43,116.21),(520.43,48.80)], G=[(582.09,116.21),(582.09,82.78),(582.09,48.80)], SER=(520.43,82.78)),
    dict(I=[(662.93,116.21),(662.93,82.78),(662.93,48.80)], N=[(723.77,116.21),(723.77,48.80)], G=[(785.43,116.21),(785.43,82.78),(785.43,48.80)], SER=(723.77,82.78)),
]


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("ing_fond.png","ing_maquette_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "ing_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"ing_fond.png")
_IMG_FOND=_fond()

_w88=max(_sw("88",POLICE_NUM,1.0),0.01)
_T_NUM = min(CELL_W*0.80/_w88, CELL_H*0.92)
_T_SER = 7.0

def _gen_carte(rng):
    i=sorted(rng.sample(range(16,31),3))               # I 16-30 croissants
    n=sorted(rng.sample(range(31,46),2), reverse=True) # N 31-45 DECROISSANTS (grand en haut)
    g=sorted(rng.sample(range(46,61),3))               # G 46-60 croissants
    return i,n,g

def generer_pdf(nb_cartes=16, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                style="", motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+11)
    n_=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,FOND_X,FOND_Y,FOND_W,FOND_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n_: break
            i,nn,g=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for (cx,cy),val in zip(pos["I"], i):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            for (cx,cy),val in zip(pos["N"], nn):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            for (cx,cy),val in zip(pos["G"], g):
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
