# -*- coding: utf-8 -*-
"""MANAPRINT — OHANA 90 · 4 SÉRIES — le VRAI modèle (Maeva 27/11/2026 : « c'est ça le OHANA 90 4 série »).
4 cartes par feuille A4 PAYSAGE. Chaque carte : titre « OHANA 90 » en contour, « N° 00001 » à gauche,
colonnes B · I · N · G · O · 90, 5 rangées ; dans chaque case un numéro dans un rond (serif) et un numéro
en gras en bas à droite. Pas de case FREE.
RÈGLE : chaque colonne a sa plage (B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75 · 90 76-90) ;
10 numéros différents par colonne, 2 par case : le plus petit dans le rond, le plus grand en gras.
Crieur 1 à 90. Chiffres noirs (26 pt dans le rond, 21 pt en gras). En couleur : grille, ronds et
titre prennent la couleur de la carte, les chiffres restent noirs. Numéro de page en haut à droite."""
import io, os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab

_GRAS = "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("VeraBd", os.path.join(os.path.dirname(reportlab.__file__), "fonts", "VeraBd.ttf")))
    _GRAS = "VeraBd"
except Exception:
    pass

PW, PH = landscape(A4)
S = PW / 2000.0
CARTES = [(40, 40), (1018, 40), (40, 727), (1018, 727)]
CW, CH = 940, 646
COLX = [0, 157, 314, 471, 628, 785, 940]
TITRE_B = 82
ROWS = [133 + i * 102.6 for i in range(6)]
LET = ["B", "I", "N", "G", "O", "90"]
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 90)]
GAMME = ["#E91E63", "#8E24AA", "#F57C00", "#2E7D32", "#1E63C8", "#D32F2F"]
NOIR = colors.black
_DEJA = set()


def _tirage(rng):
    k = None
    for _ in range(200):
        cols = []
        for a, b in PLAGES:
            t = rng.sample(range(a, b + 1), 10)
            cols.append([tuple(sorted(t[2 * i:2 * i + 2])) for i in range(5)])
        k = tuple(tuple(c) for c in cols)
        if k not in _DEJA:
            break
    _DEJA.add(k)
    return cols


def _carte(c, x0, y0, serie, cols, trait):
    X = lambda px: (x0 + px) * S
    Y = lambda py: PH - (y0 + py) * S
    c.setStrokeColor(trait); c.setLineWidth(1.1)
    c.roundRect(X(0), Y(CH), CW * S, CH * S, 6)
    c.setLineWidth(0.6)
    c.line(X(0), Y(TITRE_B), X(CW), Y(TITRE_B))
    for r in ROWS:
        c.line(X(0), Y(r), X(CW), Y(r))
    for cx in COLX[1:-1]:
        c.line(X(cx), Y(TITRE_B), X(cx), Y(CH))
    c.saveState()
    w = c.stringWidth("OHANA 90", _GRAS, 23) + 7.0
    t = c.beginText(); t.setTextRenderMode(1); t.setFont(_GRAS, 23); t.setCharSpace(1.0)
    t.setTextOrigin(X(470) - w / 2, Y(60)); c.setLineWidth(1.0); c.setStrokeColor(trait)
    t.textOut("OHANA 90"); c.drawText(t)
    c.restoreState()
    c.setFillColor(NOIR); c.setFont("Times-Roman", 8)
    c.drawString(X(15), Y(64), "N° %05d" % (serie % 100000))
    c.setFillColor(trait if trait is not NOIR else colors.Color(.4, .4, .4)); c.setFont(_GRAS, 9.5)
    for i, l in enumerate(LET):
        c.drawCentredString(X((COLX[i] + COLX[i + 1]) / 2), Y(118), l)
    c.setStrokeColor(trait); c.setLineWidth(0.6); c.setFillColor(NOIR)
    for ci in range(6):
        for ri in range(5):
            petit, grand = cols[ci][ri]
            cl, ct = COLX[ci], ROWS[ri]
            ccx, ccy = X(cl + 50), Y(ct + 51)
            c.circle(ccx, ccy, 41 * S)
            c.setFont("Times-Roman", 26); c.drawCentredString(ccx, ccy - 8.6, str(petit))
            c.setFont(_GRAS, 21); c.drawRightString(X(COLX[ci + 1] - 5), Y(ct + 97), str(grand))


def generer_pdf(nb_cartes=4, serie_start=1, couleur=False, theme="", nom_evenement="", titre_jeu="",
                couleur_perso="", date_lieu="", telephone="", page_start=1, **_ig):
    n_ = max(1, int(nb_cartes or 4))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PW, PH), pageCompression=1)
    c.setTitle("OHANA 90 · 4 séries")
    rng = random.Random(int(serie_start) * 7919 + 90)
    _DEJA.clear()
    serie = int(serie_start)
    try:
        no_page = max(1, int(page_start))
    except Exception:
        no_page = 1
    col_imp = None
    if couleur and couleur_perso:
        try:
            col_imp = colors.HexColor(couleur_perso)
        except Exception:
            col_imp = None
    fin = serie + n_
    while serie < fin:
        c.setFont("Helvetica", 7); c.setFillColor(colors.Color(.4, .4, .4))
        c.drawRightString(1958 * S, PH - 40 * S + 2.5, "page %d" % no_page)     # à ras de la grille (Maeva 27/11)
        entete = "  ·  ".join(t for t in ((nom_evenement or "").strip(), (date_lieu or "").strip()) if t)
        if entete:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(PW / 2, PH - 40 * S + 2.5, entete)
        for (x0, y0) in CARTES:
            if serie >= fin:
                break
            if couleur:
                trait = col_imp or colors.HexColor(GAMME[serie % len(GAMME)])
            else:
                trait = colors.Color(.2, .2, .2)
            _carte(c, x0, y0, serie, _tirage(rng), trait)
            serie += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_ohana90_4s.pdf", "wb").write(generer_pdf(8, couleur=True).read())
