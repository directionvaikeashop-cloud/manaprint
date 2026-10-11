# -*- coding: utf-8 -*-
"""
MANAPRINT — Generateur 60 BOULES (format A4 PORTRAIT)

REFAIT LE 11/10 (sceau Maeva) : nouvelle maquette JEU 60 (12 cartons,
4 colonnes x 2 rangees = 8 cases). Reprise TELLE QUELLE, posee comme UNE
SEULE image de fond (impression rapide). 12 cartons par feuille.
L'image n'est pas au ratio A4 : on la pose en gardant ses proportions
(ajustee en largeur, centree verticalement) — AUCUNE deformation.

REGLE INCHANGEE (60 BOULES - 8 boules) :
  colonne 1 : 2 numeros 1-15   (tries haut -> bas)
  colonne 2 : 2 numeros 16-30
  colonne 3 : 2 numeros 31-45
  colonne 4 : 2 numeros 46-60
N de serie dans le pied (N SERIE). Chiffres NOIRS (Latin Modern), au max.
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
FOND_X, FOND_Y, FOND_W, FOND_H = 0.0, 36.15, 595.28, 769.59
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

CELL_W, CELL_H = 64.0, 39.27
PLAGES = [(1,15),(16,30),(31,45),(46,60)]

CARTONS = [
    dict(C=[[(61.79,739.63),(61.52,700.77)], [(125.21,739.63),(125.21,700.50)], [(188.89,739.63),(188.89,700.77)], [(252.30,739.63),(252.30,700.77)]], SER=(184.00,671.90)),
    dict(C=[[(342.97,739.63),(342.97,700.77)], [(406.65,739.63),(406.65,700.50)], [(470.07,739.63),(470.07,700.77)], [(533.75,739.63),(533.75,700.77)]], SER=(465.35,671.90)),
    dict(C=[[(61.79,618.20),(61.52,579.07)], [(125.21,618.20),(125.21,579.07)], [(188.89,618.20),(188.89,579.07)], [(252.30,618.20),(252.30,579.07)]], SER=(184.00,550.47)),
    dict(C=[[(342.97,618.20),(342.97,579.07)], [(406.65,618.20),(406.65,579.07)], [(470.07,618.20),(470.07,579.07)], [(533.75,618.20),(533.75,579.07)]], SER=(465.35,550.47)),
    dict(C=[[(61.52,495.96),(61.79,457.10)], [(125.21,495.96),(125.21,457.10)], [(188.89,495.96),(188.89,457.10)], [(252.30,496.23),(252.30,457.10)]], SER=(184.00,428.50)),
    dict(C=[[(342.97,496.23),(342.97,457.10)], [(406.65,496.23),(406.65,457.10)], [(470.07,495.96),(470.07,457.10)], [(533.75,495.96),(533.75,457.10)]], SER=(465.35,428.50)),
    dict(C=[[(61.52,374.53),(61.52,335.67)], [(125.21,374.53),(125.21,335.67)], [(188.89,374.53),(188.89,335.67)], [(252.30,374.53),(252.30,335.67)]], SER=(183.97,307.07)),
    dict(C=[[(342.97,374.53),(342.97,335.67)], [(406.65,374.53),(406.65,335.67)], [(470.07,374.53),(470.07,335.67)], [(533.75,374.53),(533.75,335.67)]], SER=(465.35,307.07)),
    dict(C=[[(61.52,252.29),(61.52,213.17)], [(125.21,252.29),(125.21,213.17)], [(188.89,252.29),(188.89,213.17)], [(252.30,252.29),(252.30,213.17)]], SER=(183.97,184.56)),
    dict(C=[[(342.97,252.29),(342.97,213.17)], [(406.65,252.29),(406.65,213.17)], [(470.07,252.29),(470.07,213.17)], [(533.75,252.29),(533.75,213.17)]], SER=(465.35,184.56)),
    dict(C=[[(61.52,130.32),(61.79,90.93)], [(125.21,130.32),(125.21,90.93)], [(188.89,130.32),(188.89,90.93)], [(252.30,130.05),(252.30,90.93)]], SER=(184.00,62.05)),
    dict(C=[[(342.97,130.32),(342.97,90.93)], [(406.65,130.32),(406.65,90.93)], [(470.07,130.32),(470.07,90.93)], [(533.75,130.32),(533.75,90.93)]], SER=(465.35,62.05)),
]


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("boules60_fond.png","jeu60_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "boules60_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"boules60_fond.png")
_IMG_FOND=_fond()

_w88=max(_sw("88",POLICE_NUM,1.0),0.01)
_T_NUM = min(CELL_W*0.80/_w88, CELL_H*0.92)

def _gen_carte(rng):
    return [sorted(rng.sample(range(lo,hi+1),2)) for lo,hi in PLAGES]

def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                style="", motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+60)
    n_=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,FOND_X,FOND_Y,FOND_W,FOND_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n_: break
            nums=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for colpts,colnums in zip(pos["C"], nums):
                for (cx,cy),val in zip(colpts, colnums):
                    c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,7.0)
            c.drawString(pos["SER"][0], pos["SER"][1], "%06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, PAGE_H-10, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
