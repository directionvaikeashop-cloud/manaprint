# -*- coding: utf-8 -*-
"""MANAPRINT — NOËL · 6 boules (création 2KEA) · maquette CANVA de Maeva (26/11/2026,
« noel_canva_8_A4 ») reprise TELLE QUELLE : 8 billets / feuille A4 PAYSAGE (4 colonnes x 2 rangées),
traits de coupe en pointillés. Chaque billet : pastille « N° », houx, bonnet, bandeau NOËL,
flocons, losange, sapin à étoile, cadeaux et les 5 boules B · I · N · G · O.
Le dessin est rejoué TRAIT POUR TRAIT depuis la maquette et enregistré une seule fois par
document (fichier léger, impression d'une traite).
RÈGLE (inchangée) — 6 numéros :
   B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75 · LOSANGE (en haut) 76-90 -> crieur 1 à 90.
Chiffres comme la maquette : écriture à empattements grasse (Times-Bold), 30 pt (le maximum).
Le tout est réduit pour garder 6 mm de marge d'impression (Konica / Sharp).
(L'ancien noel.py reste dans le dossier, il n'est plus appelé.)"""
import io, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors

PAGE_W, PAGE_H = landscape(A4)
COLS, RANGS = 4, 2
CARTES_PAGE = COLS * RANGS                # 8
CELL_W, CELL_H = 210.4724, 297.6378
NOIR = colors.black
GRIS = colors.Color(.3, .3, .3)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
POLICE_NUM, T_NUM = "Times-Bold", 30
# (centre x, ligne de base, plage) : losange, B, I, G, N, O
CASES = [(105.1654, 194.1945, (76, 90)), (39.68504, 155.1784, (1, 15)), (39.68504, 94.23354, (16, 30)),
         (39.68504, 33.28866, (46, 60)), (170.0787, 138.1706, (31, 45)), (170.0787, 74.39102, (61, 75))]

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0
_DEJA = set()


def _numeros(rng):
    for _ in range(400):
        t = tuple(rng.randint(lo, hi) for _x, _y, (lo, hi) in CASES)
        if t not in _DEJA:
            break
    _DEJA.add(t)
    return t


def _txt(c, s, x, y, police, taille, col, centre=False):
    w = c.stringWidth(s, police, taille)
    t = c.beginText(x - w / 2.0 if centre else x, y); t.setFont(police, taille)
    t.setFillColor(col); t.textOut(s)
    c.drawText(t)


def _modele(c):
    if getattr(c, "_noel_modele", False):
        return
    d = _DESSIN
    for k, v in (("{HB}", "Helvetica-Bold"), ("{TB}", "Times-Bold"), ("{H}", "Helvetica")):
        d = d.replace(k, c._doc.getInternalFontName(v))
    c.beginForm("NOEL_DESSIN", 0, 0, CELL_W, CELL_H)
    c._code.append("q\n" + d + "\nQ")
    c.endForm()
    c._noel_modele = True


def _billet(c, ox, oy, serie, nums, col):
    _modele(c)
    c.saveState()
    c.translate(ox, oy)
    c.doForm("NOEL_DESSIN")
    _txt(c, "%06d" % serie, 27.63636, 287.1496, "Helvetica", 4.8, GRIS)
    for (cx, y, _pl), v in zip(CASES, nums):
        _txt(c, str(v), cx, y, POLICE_NUM, T_NUM, col, centre=True)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 2512)
    _DEJA.clear()
    serie = int(serie_start)
    faits = 0
    try:
        no_page = max(1, int(page_start))
    except Exception:
        no_page = 1
    col_imposee = None
    if couleur and couleur_perso:
        try:
            col_imposee = colors.HexColor(couleur_perso)
        except Exception:
            col_imposee = None

    while faits < n_:
        entete = "  \u00b7  ".join(t for t in ((nom_evenement or "").strip(), (date_lieu or "").strip()) if t)
        if entete:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - DECAL_Y / 2.0 - 2.5, entete)
        c.setFillColor(colors.Color(0.5, 0.5, 0.5)); c.setFont("Helvetica", 6)
        c.drawRightString(PAGE_W - DECAL_X, DECAL_Y / 2.0 - 2, "page %d" % no_page)

        c.saveState()
        c.translate(DECAL_X, DECAL_Y); c.scale(ECHELLE, ECHELLE)
        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ox = (idx % COLS) * CELL_W
            oy = (RANGS - 1 - idx // COLS) * CELL_H
            col = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else NOIR
            _billet(c, ox, oy, serie, _numeros(rng), col)
            serie += 1
            faits += 1
        c.setStrokeColor(colors.Color(0.5, 0.5, 0.5)); c.setLineWidth(0.3); c.setDash(2, 2)
        for i in range(1, COLS):
            c.line(i * CELL_W, 0, i * CELL_W, RANGS * CELL_H)
        for j in range(1, RANGS):
            c.line(0, j * CELL_H, COLS * CELL_W, j * CELL_H)
        c.restoreState()
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


_DESSIN = '0 0 0 RG\n1 1 1 rg\n.8 w\nn 59.81102 235.8425 m 37.13386 239.2441 l 42.80315 250.8661 l 37.13386 261.9213 l 59.81102 255.685 l h\nB*\n.5 w\nn 59.81102 235.8425 m 56.40945 233.0079 l S\n.8 w\nn 150.5197 235.8425 m 173.1969 239.2441 l 167.5276 250.8661 l 173.1969 261.9213 l 150.5197 255.685 l h\nB*\n.5 w\nn 150.5197 235.8425 m 153.9213 233.0079 l S\n.8 w\nn 56.97638 235.2756 m 89.10236 232.7244 121.2283 232.7244 153.3543 235.2756 c 153.3543 260.7874 l 121.2283 263.3386 89.10236 263.3386 56.97638 260.7874 c h\nB*\nBT 1 0 0 1 0 0 Tm 1.8 Tc 1 0 0 1 75.23391 242.0787 Tm 0 0 0 rg {H} 20 Tf 24 TL (NO\\313L) Tj 0 Tc ET\n0 0 0 RG\n1 1 1 rg\n.6 w\nq\n.819152 .573576 -0.573576 .819152 25.51181 265.0394 cm\nn 0 0 m 3.401575 1.700787 l 6.23622 .283465 l 9.070866 2.551181 l 11.90551 .850394 l 14.74016 2.834646 l 17.00787 0 l 14.74016 -2.834646 l 11.90551 -1.133858 l 9.070866 -2.834646 l 6.23622 -0.566929 l 3.401575 -1.984252 l h\nB*\nn 0 0 m 15.30709 0 l S\nQ\nq\n-0.866025 .5 -0.5 -0.866025 25.51181 265.0394 cm\nn 0 0 m 3.401575 1.700787 l 6.23622 .283465 l 9.070866 2.551181 l 11.90551 .850394 l 14.74016 2.834646 l 17.00787 0 l 14.74016 -2.834646 l 11.90551 -1.133858 l 9.070866 -2.834646 l 6.23622 -0.566929 l 3.401575 -1.984252 l h\nB*\nn 0 0 m 15.30709 0 l S\nQ\nn\n27.77953 265.0394 m\n27.77953 266.2918 26.76424 267.3071 25.51181 267.3071 c\n24.25939 267.3071 23.24409 266.2918 23.24409 265.0394 c\n23.24409 263.7869 24.25939 262.7717 25.51181 262.7717 c\n26.76424 262.7717 27.77953 263.7869 27.77953 265.0394 c\nB*\nn\n31.1811 262.7717 m\n31.1811 264.0241 30.16581 265.0394 28.91339 265.0394 c\n27.66096 265.0394 26.64567 264.0241 26.64567 262.7717 c\n26.64567 261.5192 27.66096 260.5039 28.91339 260.5039 c\n30.16581 260.5039 31.1811 261.5192 31.1811 262.7717 c\nB*\nn\n27.2126 261.3543 m\n27.2126 262.6068 26.19731 263.622 24.94488 263.622 c\n23.69246 263.622 22.67717 262.6068 22.67717 261.3543 c\n22.67717 260.1019 23.69246 259.0866 24.94488 259.0866 c\n26.19731 259.0866 27.2126 260.1019 27.2126 261.3543 c\nB*\n0 0 0 RG\n1 1 1 rg\n.7 w\nn 153.0709 272.6929 m 155.9055 288.2835 172.9134 292.5354 191.3386 281.1969 c 194.4567 276.6614 l 188.2205 273.8268 l 184.252 272.6929 l h\nB*\nn\n153.6378 267.0236 m\n186.5197 267.0236 l\n188.4001 267.0236 189.9213 268.5448 189.9213 270.4252 c\n189.9213 270.9921 l\n189.9213 272.8725 188.4001 274.3937 186.5197 274.3937 c\n153.6378 274.3937 l\n151.7574 274.3937 150.2362 272.8725 150.2362 270.9921 c\n150.2362 270.4252 l\n150.2362 268.5448 151.7574 267.0236 153.6378 267.0236 c\nh\nB*\nn\n198.7087 277.2283 m\n198.7087 279.5766 196.805 281.4803 194.4567 281.4803 c\n192.1084 281.4803 190.2047 279.5766 190.2047 277.2283 c\n190.2047 274.88 192.1084 272.9764 194.4567 272.9764 c\n196.805 272.9764 198.7087 274.88 198.7087 277.2283 c\nB*\n1 1 1 rg\n0 0 0 RG\n.4 w\nn\n9.637795 284.0315 m\n43.65354 284.0315 l\n45.22054 284.0315 46.48819 285.2991 46.48819 286.8661 c\n46.48819 291.4016 l\n46.48819 292.9686 45.22054 294.2362 43.65354 294.2362 c\n9.637795 294.2362 l\n8.070803 294.2362 6.80315 292.9686 6.80315 291.4016 c\n6.80315 286.8661 l\n6.80315 285.2991 8.070803 284.0315 9.637795 284.0315 c\nh\nB*\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 9.070866 287.1496 Tm 0 0 0 rg {HB} 4.2 Tf 5.04 TL (N\\260) Tj 0 Tc ET\n1 1 1 rg\n0 0 0 RG\n1.1 w\nn 105.1654 231.0236 m 151.937 204.0945 l 105.1654 177.1654 l 58.3937 204.0945 l h\nB*\n0 0 0 rg\n1 1 1 rg\n0 0 0 RG\n.7 w\nn 105.1654 113.3858 m 153.3543 57.54331 l 150.1417 51.30709 124.4409 51.30709 121.2283 57.54331 c 118.0157 51.30709 92.31496 51.30709 89.10236 57.54331 c 85.88976 51.30709 60.18898 51.30709 56.97638 57.54331 c h\nB*\n1 1 1 rg\n0 0 0 RG\n.7 w\nn 105.1654 137.4803 m 144.8504 95.81102 l 142.2047 89.5748 121.0394 89.5748 118.3937 95.81102 c 115.748 89.5748 94.58268 89.5748 91.93701 95.81102 c 89.29134 89.5748 68.12598 89.5748 65.48031 95.81102 c h\nB*\n1 1 1 rg\n0 0 0 RG\n.7 w\nn 105.1654 158.7402 m 132.0945 126.9921 l 130.2992 120.7559 115.937 120.7559 114.1417 126.9921 c 112.3465 120.7559 97.98425 120.7559 96.18898 126.9921 c 94.3937 120.7559 80.0315 120.7559 78.23622 126.9921 c h\nB*\n1 1 1 rg\n0 0 0 RG\n.7 w\nn 105.1654 179.1496 m 102.1663 171.9389 l 94.38172 171.3148 l 100.3127 166.2343 l 98.5007 158.6379 l 105.1654 162.7087 l 111.83 158.6379 l 110.018 166.2343 l 115.949 171.3148 l 108.1644 171.9389 l h\nB*\n1 1 1 rg\n0 0 0 RG\n.6 w\nn 89.5748 15.59055 31.1811 22.67717 re B*\nn 88.72441 38.26772 32.88189 3.401575 re B*\nn 105.1654 15.59055 m 105.1654 41.66929 l S\nn 105.1654 41.66929 m 98.3622 48.47244 96.09449 39.9685 105.1654 41.66929 c\nS\nn 105.1654 41.66929 m 111.9685 48.47244 114.2362 39.9685 105.1654 41.66929 c\nS\n1 1 1 rg\n0 0 0 RG\n.6 w\nn 71.14961 15.59055 19.84252 15.59055 re B*\nn 70.29921 31.1811 21.54331 3.401575 re B*\nn 81.07087 15.59055 m 81.07087 34.58268 l S\nn 81.07087 34.58268 m 74.26772 41.38583 72 32.88189 81.07087 34.58268 c\nS\nn 81.07087 34.58268 m 87.87402 41.38583 90.14173 32.88189 81.07087 34.58268 c\nS\n1 1 1 rg\n0 0 0 RG\n.6 w\nn 119.3386 15.59055 19.84252 15.59055 re B*\nn 118.4882 31.1811 21.54331 3.401575 re B*\nn 129.2598 15.59055 m 129.2598 34.58268 l S\nn 129.2598 34.58268 m 122.4567 41.38583 120.189 32.88189 129.2598 34.58268 c\nS\nn 129.2598 34.58268 m 136.063 41.38583 138.3307 32.88189 129.2598 34.58268 c\nS\n0 0 0 RG\n1 1 1 rg\n1.2 w\nn\n67.46457 170.0787 m\n67.46457 185.4209 55.02725 197.8583 39.68504 197.8583 c\n24.34283 197.8583 11.90551 185.4209 11.90551 170.0787 c\n11.90551 154.7365 24.34283 142.2992 39.68504 142.2992 c\n55.02725 142.2992 67.46457 154.7365 67.46457 170.0787 c\nB*\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 36.01658 183.9685 Tm 0 0 0 rg {TB} 11 Tf 13.2 TL (B) Tj 0 Tc ET\n0 0 0 rg\n0 0 0 RG\n1 1 1 rg\n1.2 w\nn\n67.46457 109.1339 m\n67.46457 124.4761 55.02725 136.9134 39.68504 136.9134 c\n24.34283 136.9134 11.90551 124.4761 11.90551 109.1339 c\n11.90551 93.79165 24.34283 81.35433 39.68504 81.35433 c\n55.02725 81.35433 67.46457 93.79165 67.46457 109.1339 c\nB*\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 37.54466 123.0236 Tm 0 0 0 rg {TB} 11 Tf 13.2 TL (I) Tj 0 Tc ET\n0 0 0 rg\n0 0 0 RG\n1 1 1 rg\n1.2 w\nn\n67.46457 48.18898 m\n67.46457 63.53119 55.02725 75.9685 39.68504 75.9685 c\n24.34283 75.9685 11.90551 63.53119 11.90551 48.18898 c\n11.90551 32.84677 24.34283 20.40945 39.68504 20.40945 c\n55.02725 20.40945 67.46457 32.84677 67.46457 48.18898 c\nB*\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 35.40696 62.07874 Tm 0 0 0 rg {TB} 11 Tf 13.2 TL (G) Tj 0 Tc ET\n0 0 0 rg\n0 0 0 RG\n1 1 1 rg\n1.2 w\nn\n197.8583 153.0709 m\n197.8583 168.4131 185.4209 180.8504 170.0787 180.8504 c\n154.7365 180.8504 142.2992 168.4131 142.2992 153.0709 c\n142.2992 137.7287 154.7365 125.2913 170.0787 125.2913 c\n185.4209 125.2913 197.8583 137.7287 197.8583 153.0709 c\nB*\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 166.1068 166.9606 Tm 0 0 0 rg {TB} 11 Tf 13.2 TL (N) Tj 0 Tc ET\n0 0 0 rg\n0 0 0 RG\n1 1 1 rg\n1.2 w\nn\n197.8583 89.29134 m\n197.8583 104.6335 185.4209 117.0709 170.0787 117.0709 c\n154.7365 117.0709 142.2992 104.6335 142.2992 89.29134 c\n142.2992 73.94913 154.7365 61.51181 170.0787 61.51181 c\n185.4209 61.51181 197.8583 73.94913 197.8583 89.29134 c\nB*\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 165.8007 103.1811 Tm 0 0 0 rg {TB} 11 Tf 13.2 TL (O) Tj 0 Tc ET\n0 0 0 rg\n0 0 0 RG\n.4 w\nn 16.72441 209.7638 m 36 209.7638 l S\nn 20.09764 209.7638 m 17.72919 208.1054 l S\nn 20.09764 209.7638 m 17.72919 211.4222 l S\nn 32.62677 209.7638 m 34.99522 211.4222 l S\nn 32.62677 209.7638 m 34.99522 208.1054 l S\nn 21.54331 201.4172 m 31.1811 218.1104 l S\nn 23.22992 204.3385 m 23.48192 201.4582 l S\nn 23.22992 204.3385 m 20.60948 203.1166 l S\nn 29.49449 215.1891 m 29.24249 218.0694 l S\nn 29.49449 215.1891 m 32.11493 216.411 l S\nn 31.1811 201.4172 m 21.54331 218.1104 l S\nn 29.49449 204.3385 m 32.11493 203.1166 l S\nn 29.49449 204.3385 m 29.24249 201.4582 l S\nn 23.22992 215.1891 m 20.60948 216.411 l S\nn 23.22992 215.1891 m 23.48192 218.0694 l S\n0 0 0 RG\n.4 w\nn 170.3622 209.7638 m 189.6378 209.7638 l S\nn 173.7354 209.7638 m 171.367 208.1054 l S\nn 173.7354 209.7638 m 171.367 211.4222 l S\nn 186.2646 209.7638 m 188.633 211.4222 l S\nn 186.2646 209.7638 m 188.633 208.1054 l S\nn 175.1811 201.4172 m 184.8189 218.1104 l S\nn 176.8677 204.3385 m 177.1197 201.4582 l S\nn 176.8677 204.3385 m 174.2473 203.1166 l S\nn 183.1323 215.1891 m 182.8803 218.0694 l S\nn 183.1323 215.1891 m 185.7527 216.411 l S\nn 184.8189 201.4172 m 175.1811 218.1104 l S\nn 183.1323 204.3385 m 185.7527 203.1166 l S\nn 183.1323 204.3385 m 182.8803 201.4582 l S\nn 176.8677 215.1891 m 174.2473 216.411 l S\nn 176.8677 215.1891 m 177.1197 218.0694 l S\n0 0 0 RG\n.4 w\nn 171.7795 35.43307 m 191.0551 35.43307 l S\nn 175.1528 35.43307 m 172.7843 33.77467 l S\nn 175.1528 35.43307 m 172.7843 37.09147 l S\nn 187.6819 35.43307 m 190.0503 37.09147 l S\nn 187.6819 35.43307 m 190.0503 33.77467 l S\nn 176.5984 27.0865 m 186.2362 43.77965 l S\nn 178.285 30.0078 m 178.537 27.12746 l S\nn 178.285 30.0078 m 175.6646 28.78586 l S\nn 184.5496 40.85834 m 184.2976 43.73868 l S\nn 184.5496 40.85834 m 187.17 42.08028 l S\nn 186.2362 27.0865 m 176.5984 43.77965 l S\nn 184.5496 30.0078 m 187.17 28.78586 l S\nn 184.5496 30.0078 m 184.2976 27.12746 l S\nn 178.285 40.85834 m 175.6646 42.08028 l S\nn 178.285 40.85834 m 178.537 43.73868 l S'


if __name__ == "__main__":
    open("test_noel.pdf", "wb").write(generer_pdf(nb_cartes=8, couleur=False).read())
    print("NOEL genere")
