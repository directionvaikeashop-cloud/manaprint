# -*- coding: utf-8 -*-
"""MANAPRINT — BNO 8 BOULES (nouvelle maquette grille, reprise TELLE QUELLE).
16 cartons/feuille (4x4), en-tete « B N O », chaque carton = grille 3x3.
Colonnes : B (1-15) / N (31-45) / O (61-75). Case centrale N = LIBRE (serie).
8 numeros par carton (B x3, N x2, O x3). Maquette posee comme UNE image de
fond ; on n'ajoute QUE les chiffres. Chiffres pleins gris -> Konica rapide."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4[1], A4[0]        # paysage
CARTES_PAGE = 16
POLICE = "Times-Bold"
GRIS = colors.Color(0.40, 0.40, 0.40)
RAINBOW = ["#E53935","#FB8C00","#F9A825","#43A047","#00ACC1",
           "#1E88E5","#3949AB","#8E24AA","#D81B60","#6D4C41"]
PLAGES = [(1, 15), (31, 45), (61, 75)]   # B / N / O

_IMG_W, _IMG_H = 1536, 1024
MARGE = 4.5 * mm
_AVW = PAGE_W - 2*MARGE
_AVH = PAGE_H - 2*MARGE
def _x(px): return MARGE + px/_IMG_W*_AVW
def _y(py): return (PAGE_H-MARGE) - py/_IMG_H*_AVH

CELLS=[
 [[97, 84], [211, 84], [325, 84], [97, 146], [211, 146], [325, 146], [97, 208], [211, 208], [325, 208]],
 [[469, 84], [581, 84], [695, 84], [468, 146], [581, 146], [695, 146], [469, 208], [581, 208], [695, 208]],
 [[840, 84], [953, 84], [1066, 84], [840, 146], [953, 146], [1066, 146], [840, 208], [953, 208], [1066, 208]],
 [[1210, 84], [1324, 84], [1438, 84], [1210, 146], [1324, 146], [1438, 146], [1210, 208], [1324, 208], [1438, 208]],
 [[97, 338], [211, 338], [325, 338], [97, 400], [211, 400], [325, 400], [97, 462], [211, 462], [325, 462]],
 [[469, 338], [581, 338], [695, 338], [468, 400], [581, 400], [695, 400], [469, 462], [581, 462], [695, 462]],
 [[840, 338], [953, 338], [1066, 338], [840, 400], [953, 400], [1066, 400], [840, 462], [953, 462], [1066, 462]],
 [[1210, 338], [1324, 338], [1438, 338], [1210, 400], [1324, 400], [1438, 400], [1210, 462], [1324, 462], [1438, 462]],
 [[97, 591], [211, 591], [325, 591], [97, 652], [211, 652], [325, 652], [97, 713], [211, 714], [325, 714]],
 [[469, 591], [581, 591], [695, 591], [468, 652], [581, 652], [695, 652], [468, 714], [581, 714], [695, 714]],
 [[840, 591], [953, 591], [1066, 591], [840, 652], [953, 652], [1066, 652], [840, 714], [953, 714], [1066, 714]],
 [[1210, 591], [1324, 591], [1438, 591], [1210, 652], [1324, 652], [1438, 652], [1210, 714], [1324, 714], [1438, 714]],
 [[97, 840], [211, 840], [325, 840], [97, 902], [211, 901], [325, 901], [97, 963], [211, 963], [325, 963]],
 [[469, 840], [581, 840], [695, 840], [469, 902], [581, 902], [695, 901], [469, 963], [581, 963], [695, 963]],
 [[840, 840], [953, 840], [1066, 840], [840, 901], [953, 901], [1066, 901], [840, 963], [953, 963], [1066, 963]],
 [[1210, 841], [1324, 840], [1438, 840], [1210, 901], [1324, 901], [1439, 902], [1210, 963], [1324, 963], [1438, 963]],
]


def _fond():
    dloc=_os.path.dirname(_os.path.abspath(__file__))
    p=_os.path.join(dloc,"bno8_fond.png")
    return p
_IMG_FOND=_fond()

_CW = 114*_AVW/_IMG_W
_CH = 60*_AVH/_IMG_H
def _taille():
    t=40.0
    while t>8 and (stringWidth("88",POLICE,t)>_CW*0.82 or t*0.72>_CH*0.82):
        t-=0.5
    return t
_T=_taille()

def _gen_carton(rng):
    b=sorted(rng.sample(range(PLAGES[0][0],PLAGES[0][1]+1),3))
    n=sorted(rng.sample(range(PLAGES[1][0],PLAGES[1][1]+1),2))
    o=sorted(rng.sample(range(PLAGES[2][0],PLAGES[2][1]+1),3))
    # 9 cases a plat : 0..8 (centre idx4 = libre)
    vals=[b[0], n[0], o[0],
          b[1], None, o[1],
          b[2], n[1], o[2]]
    return vals

def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_=nb_cartes if nb_cartes is not None else nb_tickets
    n_=max(1,int(n_ if n_ else CARTES_PAGE))
    buf=io.BytesIO()
    c=canvas.Canvas(buf,pagesize=(PAGE_W,PAGE_H),pageCompression=1)
    rng=random.Random(int(serie_start)*100003+717)
    serie=int(serie_start); faites=0
    try: page_dep=max(1,int(page_start))
    except Exception: page_dep=1
    while faites<n_:
        try: c.drawImage(_IMG_FOND,MARGE,MARGE,_AVW,_AVH,preserveAspectRatio=False,mask="auto")
        except Exception: pass
        for k in range(CARTES_PAGE):
            if faites>=n_: break
            vals=_gen_carton(rng)
            col=colors.HexColor(RAINBOW[serie%len(RAINBOW)]) if couleur else GRIS
            c.setFillColor(col); c.setFont(POLICE,_T)
            for idx,(px,py) in enumerate(CELLS[k]):
                v=vals[idx]
                if v is None: continue
                c.drawCentredString(_x(px),_y(py)-_T*0.34,str(v))
            # serie discrete dans la case centrale libre (idx 4)
            cpx,cpy=CELLS[k][4]
            c.setFillColor(colors.Color(0.5,0.5,0.5)); c.setFont("Helvetica",6.5)
            c.drawCentredString(_x(cpx),_y(cpy)-6.5*0.34,"N\u00b0 %05d"%serie)
            serie+=1; faites+=1
        if page_dep>1 or faites>CARTES_PAGE:
            c.setFillColor(colors.Color(0.55,0.55,0.55)); c.setFont("Helvetica",6)
            nfe=page_dep+(faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6*mm,PAGE_H-7*mm,"%03d"%nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
