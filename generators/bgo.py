# -*- coding: utf-8 -*-
"""MANAPRINT — Générateur BGO (A4 PAYSAGE, 16 cartons/feuille).

REGLE ABSOLUE : le decor plus bas EST la planche de Maeva, relevee au trait
   sur sa maquette (le double cadre arrondi, l'en-tete « B G O » et le tableau
   de SIX cases, 2 rangees x 3 colonnes, avec ses points aux croisees).
   RIEN n'a ete redessine, rien ajoute, rien enleve : on se contente
   d'ECRIRE LES NUMEROS dans les six cases. NE PAS « ameliorer ».

LA REGLE DU JEU : SIX numeros, DEUX par colonne —
   B 1-15 · G 46-60 · O 61-75.  Le crieur sort 1-15, 46-60, 61-75
   (le 16-30 et le 31-45 n'existent pas sur ce jeu).

CE QUI CHANGE : avant, la grille 3x3 (9 numeros) a 12 cartons/feuille.
   Maintenant SIX numeros (2 par colonne) et 16 cartons par feuille A4
   PAYSAGE. Sans la reinscription dans app.py (16/feuille), 500 feuilles
   commandees n'en donneraient que 375.

L'ARC-EN-CIEL EST CARTON PAR CARTON : la planche n'est gravee qu'une fois
   (un seul carton), puis reposee seize fois, chaque fois dans la couleur de
   SON carton. En noir & blanc on la repose au gris #555555. Les chiffres
   gardent le gris de la maison impose par app.py.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None

try:
    pdfmetrics.registerFont(TTFont("DJLBGO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    POLICE = "DJLBGO"
except Exception:
    POLICE = "Helvetica"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)

import os as _os
try:
    pdfmetrics.registerFont(TTFont("LMROMANBGO", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    _POLICE_ECO = "LMROMANBGO"
except Exception:
    try:
        pdfmetrics.registerFont(TTFont("DJLECOBGO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
        _POLICE_ECO = "DJLECOBGO"
    except Exception:
        _POLICE_ECO = "Helvetica"
_GRIS_ECO = colors.Color(0.40, 0.40, 0.40)
_GRAS_TRAIT = 0.012
_POLICE_P15 = _POLICE_ECO
_GRIS_P15 = colors.Color(0.14, 0.14, 0.14)

TRAIT_NB = "#555555"


def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


# ── GEOMETRIE DE LA FEUILLE (A4 PAYSAGE, 4 colonnes x 4 rangees) ──
PAGE_W, PAGE_H = landscape(A4)
ASPECT = 366.0 / 240.0            # largeur/hauteur d'un carton (releve sur la maquette)
COLS_PAGE = 4
ROWS_PAGE = 4
CARTES_PAGE = COLS_PAGE * ROWS_PAGE
MARGE_X = 6 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 3 * mm
CARD_W = (PAGE_W - 2 * MARGE_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = CARD_W / ASPECT
_BLOC_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_TOP = 7 * mm
MARGE_BOT = PAGE_H - MARGE_TOP - _BLOC_H

# ── LES SIX CASES (fx depuis la gauche, fy depuis le HAUT) :
#    haut B,G,O puis bas B,G,O ──
CELLULES = [
    (0.179, 0.408), (0.497, 0.408), (0.816, 0.408),
    (0.179, 0.783), (0.497, 0.783), (0.816, 0.783),
]
PLAGES = [(1, 15), (46, 60), (61, 75)]   # B, G, O

TAILLE_CHIFFRE = 40.0
_T_SERIE = 5.0


def _graver_planche(c):
    nom = "BGO_DECOR"
    if not getattr(c, "_bgo_forme_faite", False):
        c.beginForm(nom, lowerx=0, lowery=0, upperx=CARD_W, uppery=CARD_H)
        p = c.beginPath()
        for contour in _DECOR.split("|"):
            i = 0
            n = len(contour)
            while i < n:
                cmd = contour[i]
                j = i + 1
                while j < n and contour[j] not in "mlc":
                    j += 1
                v = [float(x) for x in contour[i + 1:j].split(",")]
                if cmd == "m":
                    p.moveTo(v[0] / 1000.0 * CARD_W, CARD_H - v[1] / 1000.0 * CARD_H)
                elif cmd == "l":
                    p.lineTo(v[0] / 1000.0 * CARD_W, CARD_H - v[1] / 1000.0 * CARD_H)
                else:
                    p.curveTo(v[0] / 1000.0 * CARD_W, CARD_H - v[1] / 1000.0 * CARD_H,
                              v[2] / 1000.0 * CARD_W, CARD_H - v[3] / 1000.0 * CARD_H,
                              v[4] / 1000.0 * CARD_W, CARD_H - v[5] / 1000.0 * CARD_H)
                i = j
            p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.endForm()
        c._bgo_forme_faite = True
    return nom


def _poser_carton(c, x0, y0, couleur):
    nom = _graver_planche(c)
    c.saveState()
    c.setFillColor(couleur)
    c.translate(x0, y0)
    c.doForm(nom)
    c.restoreState()


def _gen_grille(rng):
    """SIX numeros : deux par colonne (B 1-15, G 46-60, O 61-75), tries
    croissants du haut vers le bas. Ordre rendu : haut B,G,O puis bas B,G,O."""
    duos = [sorted(rng.sample(range(lo, hi + 1), 2)) for lo, hi in PLAGES]
    return [duos[0][0], duos[1][0], duos[2][0],
            duos[0][1], duos[1][1], duos[2][1]]


def _tirer(rng, deja):
    for _ in range(400):
        grille = _gen_grille(rng)
        cle = tuple(grille)
        if cle not in deja:
            deja.add(cle)
            return grille
    return grille


def _dessiner_carton(c, x0, y0, grille, serie, couleur, style="eco"):
    police_ch, gris_ch = _style_chiffres(style)
    _poser_carton(c, x0, y0, couleur)
    taille = TAILLE_CHIFFRE
    for k, (fx, fy) in enumerate(CELLULES):
        cx = x0 + CARD_W * fx
        cy = y0 + CARD_H * (1.0 - fy) - taille * 0.36
        val = grille[k]
        if _sec:
            _sec.chiffre_micro(c, val, cx, cy, taille, gris_ch, police_ch,
                               epaisseur=_GRAS_TRAIT)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, taille)
            c.drawCentredString(cx, cy, str(val))
    c.setFillColor(GRIS)
    c.setFont(POLICE, _T_SERIE)
    c.drawRightString(x0 + CARD_W - 2.0 * mm, y0 + 1.4 * mm, "N° %06d" % serie)
    if _sec:
        try:
            _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)
        except Exception:
            pass


def generer_pdf(nb_cartes=16, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", style="eco", evenement_id="", motif="",
                page_start=1, **_):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + CARTES_PAGE - 1) // CARTES_PAGE
    rng = random.Random(590000 + int(serie_start))
    serie = int(serie_start)
    no_page = max(1, int(page_start))
    faits = 0
    _deja = set()
    for _p in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 8)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 4.4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 5.5)
        c.drawRightString(PAGE_W - MARGE_X, PAGE_H - 4.4 * mm, "%03d" % no_page)
        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faits >= nb_cartes:
                    break
                x0 = MARGE_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGE_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                grille = _tirer(rng, _deja)
                coul = colors.HexColor(
                    couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else TRAIT_NB)
                _dessiner_carton(c, x0, y0, grille, serie, coul, style=style)
                serie += 1
                faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    with open("test_bgo.pdf", "wb") as f:
        f.write(generer_pdf(nb_cartes=16, couleur=True).read())
    print("BGO genere")


# == LE DESSIN DE SA PLANCHE, RELEVE AU TRAIT (un carton, millièmes) ==
_DECOR = (
    "m25.2,991.7c16.3,985.5,12.2,979.4,8.2,965.8c3,948.4,2.9,934.6,2.8,500c2.7,0.2,1.4,34.2,21.6,13.6l30.9,4.2l499.7,4.2c959.6,4.2,968.7,4.4,977.3,12.3c995.7,29.4,994.4,-7.1,994.7,498.7c995,1006.7,996.1,97"
    "5,977.4,990.6c969.1,997.5,942.2,998,502.7,998.9c45.9,999.8,36.7,999.7,25.2,991.7|m619.7,983.4l970.4,983.3l978.4,971.2l986.3,959l986.3,502.1c986.3,196.8,985.4,42.6,983.5,37.3c975.9,15.6,1001.4,16.7,499"
    ".5,16.7c43.1,16.7,34,16.9,25.4,24.8c19.6,30.2,15.7,38.3,13.7,48.8c11.5,60,10.9,193.3,11.5,511.4l12.3,958.1l19.9,969.7c29.9,985,36.7,985.7,165.3,984.4c222.4,983.9,426.9,983.4,619.7,983.4|m38.8,962.3c25"
    ".6,954.2,24.6,941.4,24.6,776c24.6,634.8,25,621.4,29.7,607.4c34.3,593.5,34.4,591.7,30.3,585.6c26.5,579.6,26,559.5,26,409.9l26,240.9l33.6,230.9l41.3,220.8l186.7,220.8c306.9,220.8,333.1,221.8,337.6,226.7"
    "c342.3,231.7,343.8,231.7,348.3,226.7c352.6,221.8,378.5,220.8,498.3,220.8c627.1,220.8,643.5,221.6,647.8,227.5c652.3,233.6,653.2,233.6,658.9,227.5c664.4,221.6,681.9,220.8,813,220.8l960.8,220.8l967.4,231"
    ".6l974,242.3l974,410.3c974,563.7,973.6,579,969.3,586.3c964.8,593.8,964.8,594.6,969.3,601.4c973.6,608,974,623,974,777.1l974,945.6l967.8,955.1l961.6,964.6l815.2,965.7c691.4,966.7,667.6,965.9,660.9,960.8"
    "c654,955.5,651.9,955.5,645.4,960.7c634.1,969.7,360.1,969.5,348.8,960.4c341.9,955,340.3,955,335.2,960.5c330.2,965.8,308.9,966.6,187.2,966.4c107.4,966.3,42.3,964.5,38.8,962.3|m333.8,947.3c338.5,940.8,33"
    "8.8,930,338.8,776.7c338.8,633.5,338.3,612.3,334.5,606.5c330.7,600.8,313.4,600,185.8,600l41.3,600l37,609.3c33.4,617.3,32.8,640.4,32.8,778c32.8,931.9,33,937.8,38.3,945.8c43.6,954,47.4,954.2,186.3,954.2c"
    "315.1,954.2,329.3,953.5,333.8,947.3|m646,944.9c649.7,936.9,650.3,913.7,650.3,775.4c650.3,632.2,649.8,614.4,645.8,607.6c641.5,600.4,633.3,600,497.4,600c389.2,600,352.7,601.2,350.3,605c347.8,608.7,347,6"
    "52.8,347,777.7c347,933,347.3,945.7,351.8,949.7c354.9,952.4,407.4,954,499.2,954l641.8,954.2l646,944.9|m961.7,945.8c967,937.8,967.2,931.9,967.2,776.4c967.2,632.3,966.7,614.4,962.7,607.6c958.4,600.4,950."
    "1,600,811.6,600c701.2,600,664.2,601.2,661.7,605c657,612.2,657,942,661.7,949.2c664.2,952.9,701,954.2,810.7,954.2c952.6,954.2,956.4,954,961.7,945.8|m344.5,594.7c344.1,589.7,340.4,590.7,339.2,596c338.6,5"
    "98.8,339.6,600.3,341.4,599.4c343.2,598.5,344.6,596.3,344.5,594.7|m657,596.1c659,591.1,653.9,586.2,650.2,589.6c647.2,592.5,649.2,600,653,600c654.3,600,656.1,598.3,657,596.1|m336,579.4c339.8,568.4,339.8"
    ",252.4,336,241.4c333.2,233.6,328.7,233.3,187.2,233.3l41.3,233.3l37,242.6c30.6,256.5,30.6,564.3,37,578.2l41.3,587.5l187.2,587.5c328.7,587.5,333.2,587.3,336,579.4|m645.3,580.6c650,574.1,650.3,563.4,650."
    "3,411.6c650.3,307.8,649.3,246.6,647.4,241.4c644.7,233.6,640.2,233.3,499.1,233.3c389.5,233.3,352.7,234.6,350.3,238.3c345.6,245.5,345.6,575.3,350.3,582.5c352.7,586.3,389.1,587.5,496.9,587.5c626.5,587.5,"
    "640.8,586.8,645.3,580.6|m962.2,580.6c966.9,574.1,967.2,563.3,967.2,410.1c967.2,266.9,966.7,245.6,962.9,239.9c959.1,234.1,941.6,233.3,811.8,233.3c701.3,233.3,664.2,234.6,661.7,238.3c657,245.5,657,575.3"
    ",661.7,582.5c664.2,586.3,701.1,587.5,811.1,587.5c943.2,587.5,957.7,586.8,962.2,580.6|m210.4,127.9l210.4,67.5l226.1,64.8c241.9,62.2,256.8,66.3,263.9,75.3c268.5,81.1,269,108.9,264.7,115.5c262.5,118.9,26"
    "3.2,122.6,267.4,129.6c275.5,142.9,275,162.7,266.2,175.3c260,184.1,256.1,185.6,234.8,186.9l210.4,188.3l210.4,127.9|m487.2,179.3c474.2,167.3,469.1,149.3,470.5,120.2c471.7,94.2,477.7,80,492.4,68.4c508.3,"
    "55.7,535.1,63.8,543.3,83.9c548.2,95.8,540.2,98.7,531.4,88.2c515.8,69.6,493.4,75,485.2,99.5c473.7,133.4,485.1,169.9,508.3,173.6c522.8,175.8,538.3,163.7,538.3,150.1c538.3,142.9,536.5,141.7,526,141.7c515"
    ".5,141.7,513.7,140.4,513.7,133.3c513.7,125.9,515.5,125,529.7,125l545.7,125l547.4,144.4c548.6,157.3,548,165.8,545.8,170c535.8,188.2,502.5,193.6,487.2,179.3|m758,183.5c754.8,181.5,749.1,174.1,745.1,166."
    "9c731.6,142.4,732,106,746.2,81.4c761.1,55.5,786.8,51.8,805,73.1c827.6,99.4,822.8,161.9,796.8,180.7c786.8,187.9,767.4,189.3,758,183.5|m798.6,159.1c808.8,143.4,811.5,116.9,804.8,97.8c799.1,81.7,790.5,75"
    ",775.6,75c745.4,75,735.2,146.5,762.4,167.9c774.9,177.8,788.5,174.5,798.6,159.1|m259,165.8c264.2,157.9,262.8,142.7,256.2,135.7c252.6,131.8,244.4,129.2,235.7,129.2l221.3,129.2l221.3,150l221.3,170.8l238."
    "5,170.8c248.3,170.8,257.2,168.7,259,165.8|m256.1,105.5c258.9,99.8,258.8,96.8,255.8,89.8c252.9,83.2,248.7,81,236.7,80l221.3,78.8l221.3,94.9c221.3,103.8,222.2,112.6,223.4,114.3c227,119.9,252.5,113.1,256"
    ".1,105.5"
)
