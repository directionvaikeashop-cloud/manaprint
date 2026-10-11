# -*- coding: utf-8 -*-
"""
MANAPRINT — Generateur LUNES 75 (format A4 PORTRAIT)

REFAIT LE 11/10 (sceau Maeva) : nouvelle maquette LUNES 75 (12 cartons,
2 colonnes x 4 rangees = 8 cases). Reprise TELLE QUELLE, posee comme UNE
SEULE image de fond (impression rapide). 12 cartons par feuille.

REGLE INCHANGEE (LUNES 75 - 8 boules, le 31-45 n'existe pas) :
  colonne GAUCHE : 4 numeros 1-30  (tries haut -> bas)
  colonne DROITE : 4 numeros 46-75 (tries haut -> bas)
N de serie dans le pied (case "N"). Chiffres NOIRS (Latin Modern), au max.
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

PAGE_W, PAGE_H = A4
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

CELL_W, CELL_H = 55.69, 45.6
PLAGES = [(1, 30), (46, 75)]   # gauche, droite — le 31-45 n'existe pas

CARTONS = [
    dict(L=[(58.81,754.05),(58.81,704.49),(58.81,655.06),(58.81,605.50)], R=[(117.49,754.05),(117.49,704.49),(117.49,655.06),(117.49,605.50)], SER=(126.98,570.46)),
    dict(L=[(198.51,754.05),(198.51,704.49),(198.51,655.06),(198.51,605.50)], R=[(257.19,754.05),(257.19,704.49),(257.19,655.06),(257.19,605.50)], SER=(266.67,570.46)),
    dict(L=[(338.20,754.05),(338.20,704.49),(338.20,655.06),(338.20,605.50)], R=[(396.89,754.05),(396.89,704.49),(396.89,655.06),(396.89,605.50)], SER=(406.37,570.46)),
    dict(L=[(477.90,754.05),(477.90,704.49),(477.90,655.06),(477.90,605.50)], R=[(536.59,754.05),(536.59,704.49),(536.59,655.06),(536.59,605.50)], SER=(546.07,570.46)),
    dict(L=[(58.81,488.14),(58.81,438.58),(58.81,389.15),(58.81,339.59)], R=[(117.49,488.14),(117.49,438.58),(117.49,389.15),(117.49,339.59)], SER=(126.98,304.55)),
    dict(L=[(198.51,488.14),(198.51,438.58),(198.51,389.15),(198.51,339.59)], R=[(257.19,488.14),(257.19,438.58),(257.19,389.15),(257.19,339.59)], SER=(266.67,304.55)),
    dict(L=[(338.20,488.14),(338.20,438.58),(338.20,389.15),(338.20,339.59)], R=[(396.89,488.14),(396.89,438.58),(396.89,389.15),(396.89,339.59)], SER=(406.37,304.55)),
    dict(L=[(477.90,488.14),(477.90,438.58),(477.90,389.15),(477.90,339.59)], R=[(536.59,488.14),(536.59,438.58),(536.59,389.15),(536.59,339.59)], SER=(546.07,304.55)),
    dict(L=[(58.81,222.23),(58.81,172.67),(58.81,123.24),(58.81,73.68)], R=[(117.49,222.23),(117.49,172.67),(117.49,123.24),(117.49,73.68)], SER=(126.98,38.64)),
    dict(L=[(198.51,222.23),(198.51,172.67),(198.51,123.24),(198.51,73.68)], R=[(257.19,222.23),(257.19,172.67),(257.19,123.24),(257.19,73.68)], SER=(266.67,38.64)),
    dict(L=[(338.20,222.23),(338.20,172.67),(338.20,123.24),(338.20,73.68)], R=[(396.89,222.23),(396.89,172.67),(396.89,123.24),(396.89,73.68)], SER=(406.37,38.64)),
    dict(L=[(477.90,222.23),(477.90,172.67),(477.90,123.24),(477.90,73.68)], R=[(536.59,222.23),(536.59,172.67),(536.59,123.24),(536.59,73.68)], SER=(546.07,38.64)),
]


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("lunes75_fond.png","lunes_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "lunes75_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"lunes75_fond.png")
_IMG_FOND=_fond()

_w88=max(_sw("88",POLICE_NUM,1.0),0.01)
_T_NUM = min(CELL_W*0.64/_w88, CELL_H*0.82)

def _gen_carte(rng):
    g=sorted(rng.sample(range(1,31),4))    # gauche 1-30
    d=sorted(rng.sample(range(46,76),4))   # droite 46-75
    return g,d

def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                style="", motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+6)
    n_=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,0,0,PAGE_W,PAGE_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n_: break
            g,d=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for (cx,cy),val in zip(pos["L"], g):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            for (cx,cy),val in zip(pos["R"], d):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.5)
            c.drawString(pos["SER"][0], pos["SER"][1], "%06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, PAGE_H-10, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
