# -*- coding: utf-8 -*-
"""MANAPRINT — TRIPLE I NI'A (maquette de Maeva du 22/11/2026).

10 tickets par feuille A4 PORTRAIT (5 x 2). La maquette (N° ____, étoiles,
logo TRIPLE I NI'A, batteries, circuits) est reprise TELLE QUELLE comme fond,
en gris uni ; les n° de série imprimés sur la maquette sont gommés et réécrits.
RÈGLE (plages de TRIPLE ACTION 75, lues sur la feuille remplie de Maeva) —
chaque batterie = 3 numéros d'une même plage, triés : les 2 plus petits dans
les cases, le plus grand dans l'ovale dessous.
   place 1 et 6 : 1 batterie  -> I 16-30
   place 2 et 7 : 2 batteries -> I 16-30 · N 31-45
   place 3 et 8 : 2 batteries -> B 1-15 · G 46-60
   place 4 et 9 : 3 batteries -> I 16-30 · G 46-60 · O 61-75
   place 5 et 10: 1 batterie  -> N 31-45
Sur une rangée de 5 tickets, chaque numéro d'une plage ne sort qu'une fois.
Crieur : 1 à 75. Chiffres NOIRS, gras, grossis au maximum.
"""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PAGE_W, PAGE_H = A4
CARTES_PAGE = 10
PLAGES = {"B": (1, 15), "I": (16, 30), "N": (31, 45), "G": (46, 60), "O": (61, 75)}
# plages des batteries, de haut en bas, pour chaque place d'une rangée
REGLE = [["I"], ["I", "N"], ["B", "G"], ["I", "G", "O"], ["N"]]

_ICI = _os.path.dirname(_os.path.abspath(__file__))
POLICE, CAP = "Times-Bold", 0.66
try:
    pdfmetrics.registerFont(TTFont("TINIAB", _os.path.join(_ICI, "LiberationSerif-Bold.ttf")))
    POLICE, CAP = "TINIAB", 0.66
except Exception:
    pass
NOIR = colors.Color(0.05, 0.05, 0.05)
GRIS = colors.Color(0.30, 0.30, 0.30)
RAINBOW = ["#E53935", "#FB8C00", "#43A047", "#00ACC1", "#1E88E5", "#8E24AA", "#D81B60", "#6D4C41"]

_FOND = _os.path.join(_ICI, "triple_inia_fond.png")
_IMG_W, _IMG_H = 1061.0, 1483.0
MARGE = 6 * 72 / 25.4
ECH = min((PAGE_W - 2 * MARGE) / _IMG_W, (PAGE_H - 2 * MARGE - 12) / _IMG_H)
OX = (PAGE_W - _IMG_W * ECH) / 2.0
OY = MARGE

# batteries relevées sur la maquette (px) : case 1 (x, y), case 2 (x, y), ovale (x, y), l/h case, l/h ovale
BATTERIES = {3: [(730.5, 313.0, 786.0, 313.0, 741.5, 367.0, 51, 60, 91, 40), (724.0, 454.0, 783.5, 454.0, 741.0, 506.0, 56, 58, 92, 40), (731.5, 595.0, 787.0, 595.5, 742.5, 650.0, 51, 60, 93, 42)], 2: [(517.0, 325.0, 575.5, 325.0, 533.0, 379.5, 55, 60, 92, 41), (525.0, 528.5, 580.5, 528.5, 533.5, 584.0, 52, 61, 93, 42)], 1: [(317.0, 349.0, 374.0, 349.5, 327.5, 405.5, 54, 62, 95, 43), (309.5, 529.0, 369.5, 529.0, 326.5, 584.0, 57, 60, 93, 42)], 0: [(105.5, 370.0, 164.0, 370.5, 117.0, 429.0, 55, 66, 100, 46)], 4: [(940.5, 372.0, 999.0, 372.5, 953.0, 431.5, 55, 66, 100, 45)], 8: [(731.0, 1028.5, 786.0, 1028.5, 742.5, 1082.0, 50, 59, 93, 40), (725.5, 1163.0, 784.5, 1163.0, 742.0, 1213.0, 55, 56, 92, 38), (731.0, 1290.5, 787.0, 1290.0, 743.0, 1342.5, 52, 57, 92, 39)], 7: [(519.0, 1044.0, 578.5, 1044.0, 534.0, 1097.0, 56, 58, 92, 40), (526.0, 1210.0, 580.5, 1210.0, 533.5, 1263.5, 52, 60, 93, 41)], 6: [(319.0, 1060.0, 375.5, 1060.5, 331.0, 1115.0, 53, 60, 96, 42), (314.5, 1206.0, 373.0, 1206.0, 329.0, 1260.0, 55, 60, 94, 42)], 5: [(106.5, 1095.5, 166.0, 1095.5, 118.0, 1154.5, 56, 65, 102, 47)], 9: [(941.0, 1100.0, 1000.0, 1100.0, 953.5, 1159.5, 56, 66, 101, 47)]}
SERIE = {0: (113.0, 36.5), 1: (324.0, 36.5), 2: (531.0, 36.5), 3: (740.0, 36.5), 4: (949.5, 36.5), 5: (114.0, 772.5), 6: (324.5, 772.5), 7: (531.5, 772.5), 8: (739.5, 772.5), 9: (949.5, 772.5)}


def _px(x):
    return OX + x * ECH


def _py(y):
    return OY + (_IMG_H - y) * ECH


# ⭐ 22/11 (Maeva : « peut-on grossir encore les chiffres ») : la HAUTEUR
#    commande, et l'écriture est SERRÉE juste ce qu'il faut pour tenir en
#    largeur (comme L'AS DES AS) — les chiffres montent bien plus haut.
def _ajuste(larg_px, haut_px, serre_min=82.0):
    t = haut_px * ECH / CAP
    while t > 6:
        serre = min(100.0, 100.0 * larg_px * ECH / pdfmetrics.stringWidth("88", POLICE, t))
        if serre >= serre_min:
            return t, serre
        t -= 0.25
    return t, 100.0


T_CASE, S_CASE = _ajuste(43.0, 41.0)
T_OVALE, S_OVALE = _ajuste(64.0, 28.0)


def _rangee(rng, deja):
    besoin = {}
    for place in REGLE:
        for k in place:
            besoin[k] = besoin.get(k, 0) + 1
    r = None
    for _ in range(200):
        pioche = {}
        for k, n in besoin.items():
            a, b = PLAGES[k]
            t = list(range(a, b + 1))
            rng.shuffle(t)
            pioche[k] = [sorted(t[3 * i:3 * i + 3]) for i in range(n)]
        r = [[pioche[k].pop() for k in place] for place in REGLE]
        cles = [tuple(tuple(x) for x in tk) for tk in r]
        if not any(cl in deja for cl in cles):
            deja.update(cles)
            return r
    return r


def _num(c, s, xc, yc, t, serre=100.0):
    o = c.beginText()
    o.setTextRenderMode(2)
    c.setLineWidth(0.02 * t)
    o.setFont(POLICE, t)
    o.setHorizScale(serre)
    o.setTextOrigin(xc - c.stringWidth(s, POLICE, t) * serre / 200.0, yc - t * CAP / 2.0)
    o.textOut(s)
    c.drawText(o)


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="",
                _deja=None, **_ig):
    n_ = nb_tickets if nb_tickets is not None else nb_cartes
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("TRIPLE I NI'A")
    rng = random.Random(int(serie_start) * 100003 + 4242)
    deja = _deja if _deja is not None else set()
    col_imposee = None
    if couleur and couleur_perso:
        try:
            col_imposee = colors.HexColor(couleur_perso)
        except Exception:
            col_imposee = None
    try:
        no_page = max(1, int(page_start))
    except Exception:
        no_page = 1
    serie = int(serie_start)
    faits = 0
    while faits < n_:
        c.drawImage(_FOND, OX, OY, _IMG_W * ECH, _IMG_H * ECH, preserveAspectRatio=False, mask="auto")
        for rg in range(2):
            rangee = _rangee(rng, deja)
            for col in range(5):
                if faits >= n_:
                    break
                idx = rg * 5 + col
                coul = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else NOIR
                c.saveState()
                c.setFillColor(coul)
                c.setStrokeColor(coul)
                c.setLineJoin(1)
                for (x1, y1, x2, y2, xo, yo, _wc, _hc, _wo, _ho), (v1, v2, v3) in zip(BATTERIES[idx], rangee[col]):
                    _num(c, str(v1), _px(x1), _py(y1), T_CASE, S_CASE)
                    _num(c, str(v2), _px(x2), _py(y2), T_CASE, S_CASE)
                    _num(c, str(v3), _px(xo), _py(yo), T_OVALE, S_OVALE)
                c.restoreState()
                sx, sy = SERIE[idx]
                c.setFillColor(GRIS)
                c.setFont("Helvetica-Bold", 7.5)
                c.drawCentredString(_px(sx), _py(sy) - 7.5 * 0.36, "%06d" % serie)
                serie += 1
                faits += 1
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 7)
        c.drawRightString(PAGE_W - MARGE - 4, PAGE_H - MARGE - 7, "%d" % no_page)
        if (nom_evenement or "").strip():
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - MARGE - 7, nom_evenement.strip()[:90])
        no_page += 1
        c.showPage()
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_triple_inia.pdf", "wb").write(generer_pdf(nb_tickets=10, couleur=False).read())
    print("TRIPLE I NI'A genere")
