# -*- coding: utf-8 -*-
"""MANAPRINT — TRIPLE ACTION 90 — maquette RETRAVAILLÉE par Maeva (12/10).

RÈGLE ABSOLUE : la nouvelle maquette (10 bandeaux, en-tête « TRIPLE ACTION 90
– 3 séries – 2KEA & Associé – Papeete – 89 22 23 05 », « N° », 6 cellules avec
cercle pointillé) est reprise TELLE QUELLE, posée comme UNE SEULE image de fond
— impression rapide. Le « N° 900001 » figé a été effacé : le vrai numéro de
série est imprimé dynamiquement.

LE JEU : 6 groupes par ticket (1-15 · 16-30 · 31-45 · 46-60 · 61-75 · 76-90).
Chaque groupe = un TRIO : 2 numéros en haut (le 1er dans le CERCLE POINTILLÉ,
le 2e à droite), 1 numéro plus petit centré dessous. 3 × 6 = 18 numéros.
10 tickets par feuille A4 portrait.

SYSTÈME MARATHON : par groupes de 5 tickets, les 15 numéros de chaque plage
sont répartis 3 par ticket -> sur 5 tickets chaque numéro 1-90 sort UNE seule
fois (aucun doublon entre les tickets du groupe).
Chiffres NOIRS (Latin Modern). N° de série en haut à droite.
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
MAQ_W, MAQ_H = 1055.0, 1491.0
CARTES_PAGE = 10
try:
    pdfmetrics.registerFont(TTFont("LMROMAN90", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    POLICE_NUM = "LMROMAN90"
except Exception:
    POLICE_NUM = "Times-Bold"
POLICE_PETIT = "Helvetica"
try:
    pdfmetrics.registerFont(TTFont("DJCONDB90", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "DejaVuSansCondensed-Bold.ttf")))
    POLICE_PETIT3 = "DJCONDB90"     # 3e chiffre : condensée grasse (plus gros, étroit)
except Exception:
    POLICE_PETIT3 = "Helvetica-Bold"
RAINBOW = ["#E53935","#FB8C00","#F9A825","#43A047","#00ACC1",
           "#1E88E5","#3949AB","#8E24AA","#D81B60","#6D4C41"]
NOIR = colors.Color(0,0,0)
GRIS = colors.Color(0.45,0.45,0.45)

RANGES = [(1,15),(16,30),(31,45),(46,60),(61,75),(76,90)]

def _MX(px): return px / MAQ_W * PAGE_W
def _MY(px): return (MAQ_H - px) / MAQ_H * PAGE_H

# --- géométrie relevée sur la maquette (pixels, origine HAUT-gauche) ---
_TOPS = [28,173,318,464,609,755,901,1047,1193,1337]   # bord haut de chaque ticket
_DIV = 32          # hauteur de l'en-tête (haut -> début des cellules)
_CELL_X = [31,195,360,527,694,858,1023]               # bords verticaux des 6 cellules
_CIRC_DX, _CIRC_DY = 46, 27    # 1re boule (sans cercle, équilibrée à gauche)
_CIRC_R = 28
_D2X, _D2Y = 118, 27           # 2e numéro (à droite)
_D3X, _D3Y = 82, 74            # 3e numéro (condensé, bien vers le bas)
_SER_X, _SER_Y = 1014, 22      # N° de série (droite de l'en-tête)
_CIRC_R_PT = _CIRC_R / MAQ_W * PAGE_W

# cartons pré-calculés en points PDF
CARTES = []
for t in _TOPS:
    div = t + _DIV
    cells = []
    for ci in range(6):
        cl = _CELL_X[ci]
        cells.append(dict(
            bulle = (_MX(cl+_CIRC_DX), _MY(div+_CIRC_DY)),
            grand = (_MX(cl+_D2X), _MY(div+_D2Y)),
            petit = (_MX(cl+_D3X), _MY(div+_D3Y)),
        ))
    CARTES.append(dict(cells=cells, ser=(_MX(_SER_X), _MY(t+_SER_Y))))


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("triple_action90_fond.png","triple_action_90_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "triple_action90_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"triple_action90_fond.png")
_IMG_FOND=_fond()

# tailles (ajustées au gabarit de la cellule)
T_BULLE = 34.0     # 1er = identique au 2e
T_GRAND = 34.0     # 2e, à droite
T_PETIT = 27.0     # 3e, condensé gras, bien vers le bas
T_SER   = 7.5


def _marathon(rng, n_tickets):
    grilles=[]; t=0
    while t<n_tickets:
        paquet=[]
        for (lo,hi) in RANGES:
            nums=list(range(lo,hi+1)); rng.shuffle(nums)
            paquet.append([sorted(nums[3*k:3*k+3]) for k in range(5)])
        for k in range(5):
            if t>=n_tickets: break
            grilles.append([paquet[p][k] for p in range(len(RANGES))]); t+=1
    return grilles


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="",
                date_lieu="", telephone="", page_start=1, evenement_id="",
                style="", motif="", **_ignore):
    n_=nb_tickets if nb_tickets is not None else nb_cartes
    n_=max(1,int(n_ if n_ else CARTES_PAGE))
    buf=io.BytesIO(); c=canvas.Canvas(buf, pagesize=(PAGE_W,PAGE_H))
    rng=random.Random(int(serie_start)*100003+90)
    serie=int(serie_start); faites=0
    _grilles=_marathon(rng, n_)
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,0,0,PAGE_W,PAGE_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for carte in CARTES:
            if faites>=n_: break
            grille=_grilles[faites]
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            for ci,cell in enumerate(carte["cells"]):
                n1,n2,n3=grille[ci]   # triés : 1er=bulle, 2e=grand, 3e=petit
                bx,by=cell["bulle"]; gx,gy=cell["grand"]; px,py=cell["petit"]
                c.setFillColor(col)
                c.setFont(POLICE_NUM,T_BULLE)
                c.drawCentredString(bx, by-T_BULLE*0.34, str(n1))
                c.setFont(POLICE_NUM,T_GRAND)
                c.drawCentredString(gx, gy-T_GRAND*0.34, str(n2))
                # 3e chiffre : condensé gras, bien vers le bas
                c.setFont(POLICE_PETIT3,T_PETIT)
                c.drawCentredString(px, py-T_PETIT*0.34, str(n3))
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,T_SER)
            c.drawRightString(carte["ser"][0], carte["ser"][1], "%06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, 6, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
