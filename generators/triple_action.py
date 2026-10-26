# -*- coding: utf-8 -*-
"""MANAPRINT — TRIPLE ACTION 75 — maquette RETRAVAILLÉE par Maeva (12/10).

RÈGLE ABSOLUE : la nouvelle maquette (cadre, « N° » + trait, titre « TRIPLE
ACTION 75 », palmier, étoiles, oiseaux) est reprise TELLE QUELLE, posée comme
UNE SEULE image de fond — impression rapide, pas de gris. RIEN n'a été
redessiné ni ajouté au décor.

LA RÈGLE DU JEU NE CHANGE PAS :
   5 rangées par ticket, une par plage : 1-15 · 16-30 · 31-45 · 46-60 · 61-75
   Chaque rangée porte TROIS numéros : un dans la bulle (à gauche), un grand
   (à droite), un petit (au centre, en bas). 10 tickets par feuille A4 portrait
   (5 colonnes × 2 rangées).
Chiffres NOIRS (Latin Modern), au plus grand qui tient. N° de série sur le trait.
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
CARTES_PAGE = 10
MAQ_W, MAQ_H = 1055.0, 1491.0   # la maquette remplit l'A4 (ratio 0,7076 ≈ 0,7071)

try:
    pdfmetrics.registerFont(TTFont("LMROMANTA", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    POLICE_NUM = "LMROMANTA"
except Exception:
    POLICE_NUM = "Times-Bold"
POLICE_PETIT = "Helvetica"
try:
    pdfmetrics.registerFont(TTFont("DJCONDB", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "DejaVuSansCondensed-Bold.ttf")))
    POLICE_PETIT3 = "DJCONDB"       # 3e chiffre : condensée grasse (étroite, plus grosse)
except Exception:
    POLICE_PETIT3 = "Helvetica-Bold"
RAINBOW = ["#E53935","#FF7043","#FB8C00","#F9A825","#43A047","#00ACC1",
           "#1E88E5","#3949AB","#8E24AA","#D81B60","#6D4C41","#546E7A"]
NOIR = colors.Color(0,0,0)            # 2 chiffres du haut : noir franc
GRIS = colors.Color(0.45,0.45,0.45)
GRIS_TROIS = colors.Color(0.50,0.50,0.50)   # 3e chiffre : gris économie de toner

RANGES = [(1,15),(16,30),(31,45),(46,60),(61,75)]
_T_SERIE = 7.0

# Géométrie en PIXELS de la maquette (origine en HAUT-gauche) :
#   tx0,tx1 = bords intérieurs du ticket ; bty,bby = haut/bas du CORPS ;
#   sx,sy   = position du N° de série (sur le trait après « N° »)
_STRIPS_PX = [
    # haut (corps 146 -> 712 : marge au bas pour que le 3e chiffre ne déborde pas)
    (14, 211, 146, 712, 66, 42),
    (230, 420, 146, 712, 282, 42),
    (438, 619, 146, 712, 490, 42),
    (638, 827, 146, 712, 690, 42),
    (845,1039, 146, 712, 897, 42),
    # bas (corps 894 -> 1456)
    (14, 211, 894, 1456, 66, 790),
    (230, 420, 894, 1456, 282, 790),
    (438, 619, 894, 1456, 490, 790),
    (638, 827, 894, 1456, 690, 790),
    (845,1039, 894, 1456, 897, 790),
]

# Marge blanche autour (zone non imprimable de l'imprimante) : on réduit
# l'ensemble pour que les bordures des tickets ne débordent pas à l'impression.
from reportlab.lib.units import mm as _mm
MARGE = 5 * _mm
FOND_X = MARGE
FOND_Y = MARGE
FOND_W = PAGE_W - 2 * MARGE
FOND_H = PAGE_H - 2 * MARGE
def _MX(px): return FOND_X + px / MAQ_W * FOND_W
def _MY(px): return FOND_Y + (MAQ_H - px) / MAQ_H * FOND_H

# Pré-calcul des cartons en points PDF
CARTES = []
for (tx0,tx1,bty,bby,sx,sy) in _STRIPS_PX:
    CARTES.append(dict(
        x0=_MX(tx0), x1=_MX(tx1),
        bt=_MY(bty), bb=_MY(bby),
        ser=(_MX(sx), _MY(sy)),
    ))


def _fond():
    d=_os.path.dirname(_os.path.abspath(__file__))
    for nom in ("triple_action_fond.png","triple_action75_fond.png"):
        p=_os.path.join(d,nom)
        if _os.path.exists(p): return p
    try:
        for f in _os.listdir(d):
            if "triple_action_fond" in f.lower() and f.lower().endswith(".png"): return _os.path.join(d,f)
    except Exception: pass
    return _os.path.join(d,"triple_action_fond.png")
_IMG_FOND=_fond()


def _gen_grille(rng):
    return [sorted(rng.sample(range(lo,hi+1),3)) for (lo,hi) in RANGES]

def _marathon(rng, n_tickets):
    """Systeme MARATHON : par GROUPES DE 5 tickets, les 15 numeros de chaque
    plage sont repartis 3 par ticket -> sur 5 tickets chaque numero 1-75 sort
    UNE seule fois (aucun doublon entre les tickets du groupe)."""
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
    rng=random.Random(int(serie_start)*100003+75)
    serie=int(serie_start); faites=0
    _grilles=_marathon(rng, n_)
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,FOND_X,FOND_Y,FOND_W,FOND_H,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for carte in CARTES:
            if faites>=n_: break
            grille=_grilles[faites]
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else NOIR
            col_cercle = col if couleur else GRIS
            x0=carte["x0"]; x1=carte["x1"]; CW=x1-x0
            bt=carte["bt"]; bb=carte["bb"]; body_h=bt-bb
            group_h=body_h/5.0
            rayon=min(group_h*0.31, CW*0.27)
            tnum=min(36.0, CW*0.44)              # grand : Latin Modern
            tbulle=min(36.0, CW*0.44)            # chiffre de la bulle (même taille)
            for ri,nums in enumerate(grille):
                gy=bt-(ri+1)*group_h
                n_cercle,n_grand,n_petit=nums
                cercle_x=x0+CW*0.28; cercle_y=gy+group_h*0.66
                grand_x=x0+CW*0.73
                c.setStrokeColor(col_cercle); c.setLineWidth(0.8)
                c.circle(cercle_x, cercle_y, rayon, stroke=1, fill=0)
                # ⭐ 25/10 (Maeva : chiffres TRIPLE ACTION trop fins) : on épaissit
                #   les 2 chiffres principaux par un CONTOUR centré (remplir+contourer),
                #   sans changer l'écriture Latin Modern.
                c.setFillColor(col); c.setStrokeColor(col)
                for _xx, _tt, _val in ((cercle_x, tbulle, n_cercle), (grand_x, tnum, n_grand)):
                    _t = c.beginText(_xx - _sw(str(_val), POLICE_NUM, _tt)/2.0, cercle_y - _tt*0.34)
                    _t.setFont(POLICE_NUM, _tt); _t.setTextRenderMode(2)
                    c.setLineWidth(max(0.3, _tt*0.035))
                    _t.textOut(str(_val)); c.drawText(_t)
                c._code.append('0 Tr')
                # 3e chiffre : condensée grasse, logé dans la place libre sous la bulle,
                #   taille maxi qui tient sans toucher la bulle ni le trait.
                slot_bas = gy + 2.0                      # juste au-dessus du trait
                slot_haut = (cercle_y - rayon) - 2.0     # juste sous la bulle
                tpetit = min(32.0, (slot_haut - slot_bas) / 0.73)
                petit_x = x0 + CW*0.50
                petit_cy = (slot_bas + slot_haut) / 2.0
                c.setFillColor(col if couleur else GRIS_TROIS)   # 3e chiffre en gris (éco toner)
                c.setFont(POLICE_PETIT3, tpetit)
                c.drawCentredString(petit_x, petit_cy - tpetit*0.36, str(n_petit))
                c.setFillColor(col)
                # trait séparateur entre chaque groupe de 3 chiffres (épaissi)
                if ri < 4:
                    c.setStrokeColor(GRIS); c.setLineWidth(1.3)
                    c.line(x0+CW*0.06, gy, x1-CW*0.06, gy)
            # N° de série
            t=_T_SERIE
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,t)
            c.drawString(carte["ser"][0], carte["ser"][1], "%06d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(GRIS); c.setFont(POLICE_PETIT,6.0)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6, PAGE_H-10, "%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
