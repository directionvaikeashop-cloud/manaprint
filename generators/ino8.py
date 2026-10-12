# -*- coding: utf-8 -*-
"""
MANAPRINT — Generateur INO 8 BOULES (format A4 PAYSAGE)

REFAIT LE 11/10 (sceau Maeva) : nouvelle maquette INO (16 cartons 4x4,
en-tete I N O, grille 3x3 case centrale VIDE). Reprise TELLE QUELLE, posee
comme UNE SEULE image de fond. L'image n'est pas au ratio A4 : posee en
gardant ses proportions (ajustee en largeur, centree) — AUCUNE deformation.

REGLE INCHANGEE (INO 8 boules — le 46-60 n'existe pas) :
  colonne I : 3 numeros 16-30 (tries haut -> bas)
  colonne N : 2 numeros 31-45 (HAUT et BAS ; centre VIDE)
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

CELL_W, CELL_H = 60.29, 33.98

CARTONS = [
    dict(I=[(54.54,531.68),(54.54,497.70),(54.54,463.44)], N=[(115.10,531.68),(115.10,463.44)], O=[(176.49,531.68),(176.49,497.70),(176.49,463.44)], SER=(115.10,497.70)),
    dict(I=[(258.43,531.68),(258.43,497.70),(258.43,463.44)], N=[(319.00,531.68),(319.00,463.44)], O=[(380.39,531.68),(380.39,497.70),(380.39,463.44)], SER=(319.00,497.70)),
    dict(I=[(459.59,531.68),(459.59,497.70),(459.59,463.44)], N=[(520.15,531.68),(520.15,463.44)], O=[(581.54,531.68),(581.54,497.70),(581.54,463.44)], SER=(520.15,497.70)),
    dict(I=[(662.93,531.68),(662.93,497.70),(662.93,463.44)], N=[(723.50,531.68),(723.50,463.44)], O=[(784.89,531.68),(784.89,497.70),(784.89,463.44)], SER=(723.50,497.70)),
    dict(I=[(54.54,393.01),(54.54,359.03),(54.54,324.77)], N=[(115.10,393.01),(115.10,324.77)], O=[(176.49,393.01),(176.49,359.03),(176.49,324.77)], SER=(115.10,359.03)),
    dict(I=[(258.43,393.01),(258.43,359.03),(258.43,324.77)], N=[(319.00,393.01),(319.00,324.77)], O=[(380.39,393.01),(380.39,359.03),(380.39,324.77)], SER=(319.00,359.03)),
    dict(I=[(459.59,393.01),(459.59,359.03),(459.59,324.77)], N=[(520.15,393.01),(520.15,324.77)], O=[(581.54,393.01),(581.54,359.03),(581.54,324.77)], SER=(520.15,359.03)),
    dict(I=[(662.93,393.01),(662.93,359.03),(662.93,324.77)], N=[(723.50,393.01),(723.50,324.77)], O=[(784.89,393.01),(784.89,359.03),(784.89,324.77)], SER=(723.50,359.03)),
    dict(I=[(54.54,254.89),(54.54,220.90),(54.54,186.65)], N=[(115.10,254.89),(115.10,186.65)], O=[(176.49,254.89),(176.49,220.90),(176.49,186.65)], SER=(115.10,220.90)),
    dict(I=[(258.43,254.89),(258.43,220.90),(258.43,186.65)], N=[(319.00,254.89),(319.00,186.65)], O=[(380.39,254.89),(380.39,220.90),(380.39,186.65)], SER=(319.00,220.90)),
    dict(I=[(459.59,254.89),(459.59,220.90),(459.59,186.65)], N=[(520.15,254.89),(520.15,186.65)], O=[(581.54,254.89),(581.54,220.90),(581.54,186.65)], SER=(520.15,220.90)),
    dict(I=[(662.93,254.89),(662.93,220.90),(662.93,186.65)], N=[(723.50,254.89),(723.50,186.65)], O=[(784.89,254.89),(784.89,220.90),(784.89,186.65)], SER=(723.50,220.90)),
    dict(I=[(54.54,117.31),(54.54,83.33),(54.54,49.07)], N=[(115.10,117.31),(115.10,49.07)], O=[(176.49,117.31),(176.49,83.33),(176.49,49.07)], SER=(115.10,83.33)),
    dict(I=[(258.43,117.31),(258.43,83.33),(258.43,49.07)], N=[(319.00,117.31),(319.00,49.07)], O=[(380.39,117.31),(380.39,83.33),(380.39,49.07)], SER=(319.00,83.33)),
    dict(I=[(459.59,117.31),(459.59,83.33),(459.59,49.07)], N=[(520.15,117.31),(520.15,49.07)], O=[(581.54,117.31),(581.54,83.33),(581.54,49.07)], SER=(520.15,83.33)),
    dict(I=[(662.93,117.31),(662.93,83.33),(662.93,49.07)], N=[(723.50,117.31),(723.50,49.07)], O=[(784.89,117.31),(784.89,83.33),(784.89,49.07)], SER=(723.50,83.33)),
]


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("ino8_fond.png","ino_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "ino8_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"ino8_fond.png")
_IMG_FOND=_fond()

_w88=max(_sw("88",POLICE_NUM,1.0),0.01)
_T_NUM = min(CELL_W*0.80/_w88, CELL_H*0.92)
_T_SER = 7.0

def _gen_carte(rng):
    i=sorted(rng.sample(range(16,31),3))   # I 16-30
    n=sorted(rng.sample(range(31,46),2))   # N 31-45 (haut/bas)
    o=sorted(rng.sample(range(61,76),3))   # O 61-75
    return i,n,o

def generer_pdf(nb_cartes=16, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                style="", motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+8)
    n_=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,FOND_X,FOND_Y,FOND_W,FOND_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n_: break
            i,nn,o=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for (cx,cy),val in zip(pos["I"], i):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            for (cx,cy),val in zip(pos["N"], nn):
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
