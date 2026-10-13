# -*- coding: utf-8 -*-
"""MANAPRINT — SICILE — maquette RETRAVAILLÉE par Maeva (12/10).

👑 La couronne à cinq pierres. La nouvelle maquette (10 tickets 2×5, en-tête
« SICILE · 5 BOULES », « N° », pastille « 5 BOULES », pied « 2KEA & Associé –
Papeete · 89 22 23 05 ») est reprise TELLE QUELLE, posée comme UNE SEULE image
de fond. Le « N° 00001 » figé a été effacé : le vrai numéro de série est
imprimé dynamiquement.

RÈGLE — cinq numéros, une plage par ovale, de gauche à droite :
  ovale 1 (gauche) : 1-15 · ovale 2 : 16-30 · ovale 3 (centre, le plus grand) :
  31-45 · ovale 4 : 46-60 · ovale 5 (droite) : 61-75.
Tout le sac 1-75 sert, les cinq numéros sont différents. Crieur 1 à 75.
Chaque chiffre est calé sur le rayon réel de son ovale (centre plus grand).
Chiffres NOIRS (Latin Modern). 10 tickets par feuille A4 portrait.
"""
import io
import os as _os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PAGE_W, PAGE_H = A4
CARTES_PAGE = 10
try:
    pdfmetrics.registerFont(TTFont("LMROMANSI", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    POLICE_NUM = "LMROMANSI"
except Exception:
    POLICE_NUM = "Times-Bold"
POLICE_PETIT = "Helvetica"
RAINBOW = ["#E53935","#FB8C00","#F9A825","#43A047","#00ACC1",
           "#1E88E5","#3949AB","#8E24AA","#D81B60","#6D4C41"]
NOIR = colors.Color(0,0,0)
GRIS = colors.Color(0.45,0.45,0.45)

PLAGES = [(1,15),(16,30),(31,45),(46,60),(61,75)]
T_SER = 9.0

# chaque ticket = ([ (x,y,taille) × 5 ovales g->d ], (serie_x, serie_y))
CARTES = [
    ([(60.9, 729.5, 22.5), (109.5, 745.3, 25.1), (160.2, 762.3, 28.4), (207.6, 746.5, 25.7), (256.2, 729.5, 23.8)], (275.4, 808.6)),
    ([(349.3, 729.5, 25.7), (392.2, 746.5, 31.7), (448.6, 761.1, 28.4), (501.6, 746.5, 32.4), (542.2, 729.5, 25.1)], (561.4, 808.6)),
    ([(59.8, 566.3, 23.8), (106.1, 585.5, 29.7), (159.1, 600.2, 27.7), (208.8, 583.3, 25.7), (252.8, 567.5, 21.9)], (275.4, 646.5)),
    ([(347.0, 566.3, 23.8), (395.5, 583.3, 27.1), (446.3, 598.0, 29.1), (500.5, 585.5, 32.4), (542.2, 567.5, 25.1)], (561.4, 646.5)),
    ([(60.9, 406.5, 22.5), (107.2, 421.2, 25.1), (160.2, 439.3, 28.4), (209.9, 422.4, 26.5), (251.7, 407.7, 23.1)], (275.4, 483.3)),
    ([(349.3, 407.7, 26.5), (395.5, 421.2, 26.5), (444.1, 439.3, 28.4), (496.0, 421.2, 25.7), (542.2, 407.7, 24.5)], (561.4, 483.3)),
    ([(60.9, 245.6, 25.7), (103.8, 262.6, 31.7), (156.9, 277.2, 28.4), (208.8, 263.7, 27.1), (252.8, 244.5, 21.9)], (275.4, 323.5)),
    ([(349.3, 245.6, 25.7), (392.2, 262.6, 31.7), (446.3, 275.0, 28.4), (496.0, 260.3, 25.7), (542.2, 245.6, 22.5)], (561.4, 323.5)),
    ([(62.1, 82.4, 23.8), (111.7, 101.6, 31.0), (158.0, 115.2, 29.7), (209.9, 99.4, 26.5), (253.9, 83.6, 25.1)], (275.4, 160.4)),
    ([(348.1, 82.4, 25.7), (396.7, 98.2, 25.7), (447.4, 114.1, 28.4), (496.0, 101.6, 27.7), (541.1, 83.6, 22.5)], (561.4, 160.4)),
]

def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("sicile_fond.png","sicile_couronne_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "sicile_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"sicile_fond.png")
_IMG_FOND=_fond()


def _gen_carte(rng):
    return [rng.randint(lo,hi) for (lo,hi) in PLAGES]


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                style="", motif="", **_ignore):
    n_=nb_tickets if nb_tickets is not None else nb_cartes
    n_=max(1,int(n_ if n_ else CARTES_PAGE))
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+7)
    serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,0,0,PAGE_W,PAGE_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for ovales, ser in CARTES:
            if faites>=n_: break
            nums=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col)
            for (cx,cy,sz),val in zip(ovales, nums):
                c.setFont(POLICE_NUM,sz)
                c.drawCentredString(cx, cy-sz*0.33, str(val))
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,T_SER)
            c.drawRightString(ser[0], ser[1], "%05d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, 6, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
