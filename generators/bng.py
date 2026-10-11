# -*- coding: utf-8 -*-
"""
MANAPRINT — Generateur BNG (format A4 PAYSAGE)

REFAIT LE 11/10 (sceau Maeva) : nouvelle maquette BNG (16 cartons 4x4,
colonnes B / N / G). Reprise TELLE QUELLE, posee comme UNE SEULE image de
fond (impression rapide). 16 cartons par feuille.

REGLE INCHANGEE (BNG 5 boules) :
  B : 2 numeros 1-15   (triés, haut -> bas)
  N : 1 numero  31-45
  G : 2 numeros 46-60  (triés, haut -> bas)
N de serie en bas du cadre. Chiffres NOIRS (Latin Modern), au plus grand.
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

CELL_W, CELL_H = 50.16, 34.56
RANGES = {"B": (1, 15), "N": (31, 45), "G": (46, 60)}

CARTONS = [
    dict(B=[(51.00,532.15),(51.00,483.90)], N=[(114.12,507.90)], G=[(177.47,532.15),(177.47,483.90)], SER=(114.24,455.34)),
    dict(B=[(255.47,532.15),(255.47,483.90)], N=[(318.59,507.90)], G=[(381.95,532.15),(381.95,483.90)], SER=(318.71,455.34)),
    dict(B=[(460.18,532.15),(460.18,483.90)], N=[(523.30,507.90)], G=[(586.66,532.15),(586.66,483.90)], SER=(523.42,455.34)),
    dict(B=[(664.66,532.15),(664.66,483.90)], N=[(727.77,507.90)], G=[(791.13,532.15),(791.13,483.90)], SER=(727.89,455.34)),
    dict(B=[(51.00,388.61),(51.00,340.36)], N=[(114.12,364.37)], G=[(177.47,388.61),(177.47,340.36)], SER=(114.24,311.80)),
    dict(B=[(255.47,388.61),(255.47,340.36)], N=[(318.59,364.37)], G=[(381.95,388.61),(381.95,340.36)], SER=(318.71,311.80)),
    dict(B=[(460.18,388.61),(460.18,340.36)], N=[(523.30,364.37)], G=[(586.66,388.61),(586.66,340.36)], SER=(523.42,311.80)),
    dict(B=[(664.66,388.61),(664.66,340.36)], N=[(727.77,364.37)], G=[(791.13,388.61),(791.13,340.36)], SER=(727.89,311.80)),
    dict(B=[(51.00,245.31),(51.00,197.07)], N=[(114.12,221.07)], G=[(177.47,245.31),(177.47,197.07)], SER=(114.24,168.50)),
    dict(B=[(255.47,245.31),(255.47,197.07)], N=[(318.59,221.07)], G=[(381.95,245.31),(381.95,197.07)], SER=(318.71,168.50)),
    dict(B=[(460.18,245.31),(460.18,197.07)], N=[(523.30,221.07)], G=[(586.66,245.31),(586.66,197.07)], SER=(523.42,168.50)),
    dict(B=[(664.66,245.31),(664.66,197.07)], N=[(727.77,221.07)], G=[(791.13,245.31),(791.13,197.07)], SER=(727.89,168.50)),
    dict(B=[(51.00,102.01),(51.00,53.77)], N=[(114.12,77.77)], G=[(177.47,102.01),(177.47,53.77)], SER=(114.24,25.20)),
    dict(B=[(255.47,102.01),(255.47,53.77)], N=[(318.59,77.77)], G=[(381.95,102.01),(381.95,53.77)], SER=(318.71,25.20)),
    dict(B=[(460.18,102.01),(460.18,53.77)], N=[(523.30,77.77)], G=[(586.66,102.01),(586.66,53.77)], SER=(523.42,25.20)),
    dict(B=[(664.66,102.01),(664.66,53.77)], N=[(727.77,77.77)], G=[(791.13,102.01),(791.13,53.77)], SER=(727.89,25.20)),
]


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("bng_fond.png","bng_maquette_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "bng_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"bng_fond.png")
_IMG_FOND=_fond()

_w88=max(_sw("88",POLICE_NUM,1.0),0.01)
_T_NUM = min(CELL_W*0.84/_w88, CELL_H*0.95)

def _gen_carte(rng):
    b=sorted(rng.sample(range(1,16),2))    # B 1-15
    n=[rng.randint(31,45)]                 # N 31-45
    g=sorted(rng.sample(range(46,61),2))   # G 46-60
    return b,n,g

def generer_pdf(nb_cartes=16, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                style="", motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+5)
    n_=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,0,0,PAGE_W,PAGE_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n_: break
            b,nn,g=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for (cx,cy),val in zip(pos["B"], b):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            for (cx,cy),val in zip(pos["N"], nn):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            for (cx,cy),val in zip(pos["G"], g):
                c.drawCentredString(cx, cy-_T_NUM*0.34, str(val))
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            c.drawCentredString(pos["SER"][0], pos["SER"][1], "N %06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, PAGE_H-10, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
