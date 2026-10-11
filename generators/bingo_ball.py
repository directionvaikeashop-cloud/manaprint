# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur BINGO BALL (format A4 PAYSAGE)

REFAIT LE 10/10 (sceau Maeva) : maquette « BINGO BALL · 7 BOULES » en croix,
reprise TELLE QUELLE, posée comme UNE SEULE image de fond (impression rapide).
12 cartons/feuille. Règle inchangée (7 boules) :
  ligne de 5 : B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75
  colonne centrale : 1 en HAUT + le N + 1 en BAS (les 3 dans 31-45)
  N° de série dans le blanc en bas à gauche. Chiffres NOIRS Latin Modern au max.
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

CELL_W, CELL_H = 36.18, 40.84
FOND_X, FOND_Y, FOND_W, FOND_H = 24.09, 0.00, 793.65, 595.28

CARTONS = [
    dict(B=(58.90, 478.52), I=(95.08, 478.52), N=(132.08, 478.52), G=(169.08, 478.52), O=(206.08, 478.52), TOP=(131.53, 519.36), BOT=(131.53, 435.77)),
    dict(B=(255.41, 478.52), I=(290.76, 478.52), N=(327.21, 478.25), G=(363.39, 478.52), O=(398.75, 478.52), TOP=(326.94, 519.36), BOT=(326.94, 435.77)),
    dict(B=(444.24, 478.52), I=(479.87, 478.52), N=(515.77, 478.52), G=(552.22, 478.52), O=(588.13, 478.52), TOP=(515.77, 519.36), BOT=(515.77, 435.77)),
    dict(B=(635.27, 478.52), I=(672.27, 478.52), N=(708.99, 478.25), G=(746.26, 478.52), O=(783.26, 478.52), TOP=(709.26, 519.36), BOT=(708.99, 435.77)),
    dict(B=(58.90, 290.24), I=(95.08, 290.24), N=(132.08, 290.24), G=(169.08, 290.24), O=(206.08, 290.24), TOP=(131.53, 331.07), BOT=(131.53, 247.76)),
    dict(B=(255.41, 290.24), I=(290.76, 290.24), N=(327.21, 290.24), G=(363.39, 290.24), O=(399.02, 290.24), TOP=(326.94, 331.07), BOT=(326.94, 247.76)),
    dict(B=(444.24, 290.24), I=(479.87, 290.24), N=(515.77, 290.24), G=(552.22, 290.24), O=(588.13, 290.24), TOP=(515.77, 331.07), BOT=(515.77, 247.76)),
    dict(B=(635.27, 290.24), I=(672.27, 290.24), N=(708.99, 290.24), G=(746.26, 290.24), O=(782.99, 290.24), TOP=(708.99, 331.07), BOT=(708.99, 247.76)),
    dict(B=(58.63, 102.78), I=(94.80, 102.78), N=(132.08, 102.50), G=(169.08, 102.78), O=(206.08, 102.78), TOP=(131.53, 143.61), BOT=(131.53, 59.47)),
    dict(B=(255.13, 102.78), I=(290.76, 102.78), N=(327.21, 102.50), G=(363.39, 102.78), O=(398.75, 102.78), TOP=(326.94, 143.61), BOT=(326.94, 59.47)),
    dict(B=(443.97, 102.78), I=(479.60, 102.78), N=(515.77, 102.78), G=(551.95, 102.78), O=(587.58, 102.78), TOP=(515.50, 143.61), BOT=(515.50, 59.75)),
    dict(B=(635.27, 102.78), I=(672.27, 102.78), N=(708.99, 102.78), G=(745.99, 102.78), O=(782.99, 102.78), TOP=(708.99, 143.61), BOT=(708.99, 59.75)),
]

def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("bingo_ball_fond.png","bingoball_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "bingo_ball_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"bingo_ball_fond.png")
_IMG_FOND=_fond()

_T_NUM = min(CELL_W*0.88/max(_sw("88",POLICE_NUM,1.0),0.01), CELL_H*0.90)

def _gen_carte(rng):
    tn=rng.sample(range(31,46),3)
    return {"B":rng.randint(1,15),"I":rng.randint(16,30),"N":tn[1],
            "G":rng.randint(46,60),"O":rng.randint(61,75),"TOP":tn[0],"BOT":tn[2]}

def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                motif="", **_ignore):
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+7)
    n=max(1,int(nb_cartes)); serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    ordre=("B","I","N","G","O","TOP","BOT")
    while faites<n:
        try: c.drawImage(_IMG_FOND, FOND_X, FOND_Y, FOND_W, FOND_H, preserveAspectRatio=True, mask="auto")
        except Exception: pass
        for pos in CARTONS:
            if faites>=n: break
            carte=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col); c.setFont(POLICE_NUM,_T_NUM)
            for cle in ordre:
                cx,cy=pos[cle]
                c.drawCentredString(cx, cy-_T_NUM*0.35, str(carte[cle]))
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            c.drawString(pos["B"][0]-CELL_W*0.40, pos["BOT"][1]-2, "N° %06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, PAGE_H-10, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
