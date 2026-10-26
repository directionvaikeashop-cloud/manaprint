# -*- coding: utf-8 -*-
"""MANAPRINT — SICILE — maquette RETRAVAILLÉE par Maeva (12/10).

👑 La couronne à cinq pierres. La nouvelle maquette (10 tickets 2×5, en-tête
« SICILE · 5 BOULES », « N° », pastille « 5 BOULES », pied « 2KEA & Associé –
Papeete · 89 22 23 05 ») est reprise TELLE QUELLE, posée comme UNE SEULE image
de fond. Le « N° 00001 » figé a été effacé : le vrai numéro de série est
imprimé dynamiquement.

RÈGLE — cinq numéros, une plage par goutte, de gauche à droite :
  goutte 1 (gauche) : 1-15 · goutte 2 : 16-30 · goutte 3 (centre, la plus
  grande) : 31-45 · goutte 4 : 46-60 · goutte 5 (droite) : 61-75.
Tout le sac 1-75 sert, les cinq numéros sont différents. Crieur 1 à 75.

CHIFFRES — chaque chiffre est AU PLUS GROS que sa propre goutte permet :
le rayon réel du ventre (bulbe) de chaque goutte a été mesuré sur la maquette
(cercle inscrit) ; la taille du chiffre est calée dessus (pire cas 2 chiffres)
et parfaitement centrée dans le bulbe. La goutte centrale reçoit les plus gros
chiffres, les gouttes latérales le maximum que leur bulbe plus petit autorise —
aucun débordement. Chiffres NOIRS (Latin Modern). 10 tickets A4 portrait.
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

# ⭐ Taille du chiffre = part du diamètre du bulbe (cercle inscrit mesuré sur la
#   maquette). FACTOR 0.76 => « 88 » (pire cas) occupe 76 % du diamètre : le plus
#   gros possible tout en gardant une marge pour ne jamais toucher le contour.
_FACTOR = 0.76
_VCEN = 0.345   # abaissement de la ligne de base pour centrer verticalement

# chaque ticket = ([ (bulbe_x, bulbe_y, rayon) × 5 gouttes g->d ], (serie_x, serie_y))
# (bulbe_x,bulbe_y) = centre réel du ventre de la goutte ; rayon = cercle inscrit
# mesuré sur sicile_fond.png. Coordonnées plein cadre (transposées plus bas).
CARTES = [
    ([(60.9,728.4,17.6),(108.3,743.7,18.6),(158.6,760.6,20.0),(208.2,744.2,18.6),(253.9,728.4,17.2)], (275.4,808.6)),
    ([(349.8,729.0,17.5),(396.7,743.1,18.4),(446.9,760.0,20.0),(496.6,744.8,18.6),(541.7,727.8,17.2)], (561.4,808.6)),
    ([(60.9,566.9,17.6),(108.3,582.7,18.6),(158.6,599.7,19.9),(208.2,582.7,18.6),(253.9,566.9,17.2)], (275.4,646.5)),
    ([(349.3,566.9,17.6),(396.7,582.2,18.4),(446.9,599.1,20.0),(496.6,583.3,18.5),(541.7,566.9,17.2)], (561.4,646.5)),
    ([(60.9,405.4,17.6),(108.3,421.8,18.6),(158.6,438.7,19.9),(208.2,421.8,18.6),(253.9,405.4,17.3)], (275.4,483.3)),
    ([(349.8,406.0,17.7),(396.7,420.7,18.4),(446.9,437.6,20.1),(496.0,421.8,18.6),(541.7,405.4,17.2)], (561.4,483.3)),
    ([(61.5,244.5,17.6),(108.3,259.7,18.6),(158.6,276.1,20.1),(208.2,260.3,18.6),(253.9,243.9,17.2)], (275.4,323.5)),
    ([(349.8,244.5,17.8),(396.7,259.2,18.4),(446.9,276.1,20.1),(496.0,260.3,18.6),(541.7,243.9,17.2)], (561.4,323.5)),
    ([(60.9,81.9,17.5),(108.3,98.8,18.8),(158.6,115.2,20.0),(208.2,98.8,18.6),(253.9,81.9,17.2)], (275.4,160.4)),
    ([(349.8,81.9,17.6),(396.7,97.7,18.5),(446.9,115.2,20.0),(496.6,98.8,18.6),(541.7,81.9,17.2)], (561.4,160.4)),
]

# Marge blanche (zone non imprimable) : on réduit l'ensemble pour que les
# bordures des tickets ne débordent pas à l'impression. Les coordonnées de
# CARTES (calculées plein cadre) sont transposées dans le cadre réduit.
from reportlab.lib.units import mm as _mm
MARGE = 5 * _mm
FOND_X = MARGE; FOND_Y = MARGE
FOND_W = PAGE_W - 2 * MARGE; FOND_H = PAGE_H - 2 * MARGE
_SX = FOND_W / PAGE_W; _SY = FOND_H / PAGE_H
CARTES = [
    ([(MARGE + x*_SX, MARGE + y*_SY, r*_SX) for (x, y, r) in ov],
     (MARGE + ser[0]*_SX, MARGE + ser[1]*_SY))
    for ov, ser in CARTES
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
        try: c.drawImage(_IMG_FOND,FOND_X,FOND_Y,FOND_W,FOND_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for ovales, ser in CARTES:
            if faites>=n_: break
            nums=_gen_carte(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            c.setFillColor(col)
            # ⭐ Chaque chiffre AU PLUS GROS dans sa goutte : taille = 2·rayon·FACTOR
            #   (rayon du bulbe propre à chaque goutte), centré sur le ventre réel.
            for (cx,cy,r),val in zip(ovales, nums):
                f=2.0*r*_FACTOR
                # ⭐ 25/10 (Maeva : « le gras de SICILE comme ROYAL ») : on
                #   épaissit le chiffre par un CONTOUR centré sur la lettre
                #   (remplir+contourer), sans changer l'écriture Latin Modern.
                t=c.beginText(cx - pdfmetrics.stringWidth(str(val),POLICE_NUM,f)/2.0,
                              cy - f*_VCEN)
                t.setFont(POLICE_NUM, f)
                t.setTextRenderMode(2)            # remplir ET contourer
                c.setStrokeColor(col)
                c.setLineWidth(max(0.3, f*0.035))
                t.textOut(str(val))
                c.drawText(t)
                c._code.append('0 Tr')            # sinon le mode de rendu reste actif
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,T_SER)
            c.drawRightString(ser[0], ser[1], "%05d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, 6, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
