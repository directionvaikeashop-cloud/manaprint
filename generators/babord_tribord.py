# -*- coding: utf-8 -*-
"""MANAPRINT — BÂBORD TRIBORD (RANIHEI SISTERS & SHOP), maquette gouvernail.
8 cartons/feuille. 8 bulles autour d'une barre à roue ; moyeu = série.
Règle (post RANIHEI) : 2B · 2I · 2G · 2O  -> 8 numéros :
  B 1-15, I 16-30, G 46-60, O 61-75 (pas de N).
Placement des lettres sur les bulles (ordre 0..7 = haut, HG, HD, MG, MD, BG, BD, bas) :
  B -> 0,2   O -> 1,3   I -> 4,6   G -> 5,7   (fidèle au modèle).
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
PLAGES = {"B": (1, 15), "I": (16, 30), "G": (46, 60), "O": (61, 75)}
# bulle index -> lettre
BULLE_LETTRE = {0:"B", 2:"B", 1:"O", 3:"O", 4:"I", 6:"I", 5:"G", 7:"G"}

_d = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "babord_tribord_pos.json")))
_IMG_W, _IMG_H = _d["W"], _d["H"]
_BULLES = _d["bulles"]      # 8 cartons x 8 (x,y)
_SER = _d["ser"]            # 8 (x,y)
_RB = _d["r"]
MARGE = 4.5 * mm
_AVW = PAGE_W - 2*MARGE
_AVH = PAGE_H - 2*MARGE
def _x(px): return MARGE + px/_IMG_W*_AVW
def _y(py): return (PAGE_H-MARGE) - py/_IMG_H*_AVH

def _fond():
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "babord_tribord_fond.png")
_IMG_FOND = _fond()

# taille chiffre : tient dans la bulle (diagonale <= rayon*0.9)
_RB_PT = _RB/_IMG_W*_AVW
def _taille():
    t = 40.0
    while t > 8:
        w = stringWidth("88", POLICE, t); h = t*0.70
        if ((w/2)**2 + (h/2)**2) ** 0.5 <= _RB_PT*0.86:
            break
        t -= 0.5
    return t
_T = _taille()

def _gen_carton(rng):
    vals = [None]*8
    for lettre, idxs in {"B":[0,2],"O":[1,3],"I":[4,6],"G":[5,7]}.items():
        a, b = PLAGES[lettre]
        nums = rng.sample(range(a, b+1), 2)
        for pos, n in zip(idxs, nums):
            vals[pos] = n
    return vals

def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start)*100003 + 613)
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
            for pos, (px, py) in enumerate(_BULLES[k]):
                v = vals[pos]
                if v is None: continue
                c.drawCentredString(_x(px), _y(py) - _T*0.36, str(v))
            # série dans le moyeu (on recouvre le "001" du modèle)
            sx, sy = _SER[k]
            bw_pt = _RB_PT*1.9
            c.setFillColor(colors.white)
            c.rect(_x(sx)-bw_pt/2, _y(sy)-7, bw_pt, 15, fill=1, stroke=0)
            c.setFillColor(colors.Color(0.15,0.15,0.15)); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(_x(sx), _y(sy)-11*0.34, "%03d" % serie)
            serie += 1; faites += 1
        if page_dep > 1 or faites > CARTES_PAGE:
            c.setFillColor(colors.Color(0.55,0.55,0.55)); c.setFont("Helvetica", 6)
            nfe = page_dep + (faites-1)//CARTES_PAGE
            c.drawRightString(PAGE_W-6*mm, PAGE_H-7*mm, "%03d" % nfe)
        c.showPage()
    c.save(); buf.seek(0); return buf
