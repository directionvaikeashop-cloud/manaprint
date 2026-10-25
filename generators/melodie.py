# -*- coding: utf-8 -*-
"""MANAPRINT — MÉLODIE (RANIHEI SISTERS & SHOP), maquette portée musicale.
8 cartons/feuille. 10 ovales (2 rangées × 5 colonnes) sur une portée.
Règle : 75 boules classique, 2 par colonne -> 10 numéros :
  col0 B 1-15, col1 I 16-30, col2 N 31-45, col3 G 46-60, col4 O 61-75.
Se joue en « OHANA ti'a » (paires) ou en keno (1 par 1) — même carton.
Maquette reprise telle quelle ; on ajoute les chiffres et la série."""
import io, os as _os, json as _json, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4[1], A4[0]        # paysage
CARTES_PAGE = 8
POLICE = "Helvetica-Bold"
GRIS = colors.Color(0.38, 0.38, 0.38)
RAINBOW = ["#E53935","#FB8C00","#F9A825","#43A047","#00ACC1",
           "#1E88E5","#3949AB","#8E24AA","#D81B60","#6D4C41"]
PLAGES = [(1,15),(16,30),(31,45),(46,60),(61,75)]   # B I N G O (par colonne)

_d = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "melodie_pos.json")))
_IMG_W, _IMG_H = _d["W"], _d["H"]
_CELLS = _d["cells"]      # 8 cartons x 10 (x,y) ordonnés col0h,col0b,col1h,col1b,...
_SER = _d["ser"]
_RW, _RH = _d["rw"], _d["rh"]
MARGE = 4.5 * mm
_AVW = PAGE_W - 2*MARGE
_AVH = PAGE_H - 2*MARGE
def _x(px): return MARGE + px/_IMG_W*_AVW
def _y(py): return (PAGE_H-MARGE) - py/_IMG_H*_AVH

def _fond():
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "melodie_fond.png")
_IMG_FOND = _fond()

_RWPT = _RW/_IMG_W*_AVW
_RHPT = _RH/_IMG_H*_AVH
def _taille():
    t = 34.0
    while t > 8 and (stringWidth("88", POLICE, t) > 2*_RWPT*0.80 or t*0.70 > 2*_RHPT*0.82):
        t -= 0.5
    return t
_T = _taille()

def _gen_carton(rng):
    vals = [None]*10
    for col in range(5):
        a, b = PLAGES[col]
        n1, n2 = rng.sample(range(a, b+1), 2)
        vals[col*2] = n1       # rangée haut
        vals[col*2+1] = n2     # rangée bas
    return vals

def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start)*100003 + 421)
    serie = int(serie_start); faites = 0
    try: page_dep = max(1, int(page_start))
    except Exception: page_dep = 1
    while faites < n_:
        try: c.drawImage(_IMG_FOND, MARGE, MARGE, _AVW, _AVH, preserveAspectRatio=False, mask="auto")
        except Exception: pass
        for k in range(CARTES_PAGE):
            if faites >= n_: break
            vals = _gen_carton(rng)
            col = colors.HexColor(RAINBOW[serie % len(RAINBOW)]) if couleur else GRIS
            c.setFillColor(col); c.setFont(POLICE, _T)
            for pos, (px, py) in enumerate(_CELLS[k]):
                v = vals[pos]
                if v is None: continue
                c.drawCentredString(_x(px), _y(py) - _T*0.36, str(v))
            # série : recouvre le "001" du modèle
            sx, sy = _SER[k]
            c.setFillColor(colors.white)
            c.rect(_x(sx)-26, _y(sy)-9, 52, 18, fill=1, stroke=0)
            c.setFillColor(colors.Color(0.15,0.15,0.15)); c.setFont("Helvetica-BoldOblique", 13)
            c.drawCentredString(_x(sx), _y(sy)-13*0.34, "%03d" % serie)
            serie += 1; faites += 1
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(colors.Color(0.55,0.55,0.55)); c.setFont("Helvetica", 6)
            nfe = page_dep + (faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6*mm, PAGE_H-7*mm, "%03d" % nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
