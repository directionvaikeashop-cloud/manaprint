# -*- coding: utf-8 -*-
"""MANAPRINT — Générateur ZIN (A4 PAYSAGE, 16 cartons/feuille).

REGLE ABSOLUE : le decor plus bas EST la planche de Maeva, relevee au trait
   sur sa maquette (le double cadre arrondi, l'en-tete « Z I N » et le tableau
   de SIX cases, 2 rangees x 3 colonnes, avec ses points aux croisees).
   RIEN n'a ete redessine, rien ajoute, rien enleve : on se contente
   d'ECRIRE LES NUMEROS dans les six cases. NE PAS « ameliorer ».

LA REGLE DU JEU : SIX numeros, DEUX par colonne —
   Z 1-12 · I 13-24 · N 25-36.  Le crieur sort 1-36 (trois familles de douze : Z, I, N).

CE QUI CHANGE : avant, la grille 3x3 (6 numeros, cases vides en diagonale) a 12 cartons/feuille.
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
    pdfmetrics.registerFont(TTFont("DJLZIN", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    POLICE = "DJLZIN"
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
    pdfmetrics.registerFont(TTFont("LMROMANZIN", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    _POLICE_ECO = "LMROMANZIN"
except Exception:
    try:
        pdfmetrics.registerFont(TTFont("DJLECOZIN", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
        _POLICE_ECO = "DJLECOZIN"
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
ASPECT = 360.0 / 239.0            # largeur/hauteur d'un carton (releve sur la maquette)
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
#    haut Z,I,N puis bas Z,I,N ──
CELLULES = [
    (0.175, 0.410), (0.493, 0.410), (0.810, 0.410),
    (0.175, 0.787), (0.493, 0.787), (0.810, 0.787),
]
PLAGES = [(1, 12), (13, 24), (25, 36)]   # Z, I, N

TAILLE_CHIFFRE = 40.0
_T_SERIE = 5.0


def _graver_planche(c):
    nom = "ZIN_DECOR"
    if not getattr(c, "_zin_forme_faite", False):
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
        c._zin_forme_faite = True
    return nom


def _poser_carton(c, x0, y0, couleur):
    nom = _graver_planche(c)
    c.saveState()
    c.setFillColor(couleur)
    c.translate(x0, y0)
    c.doForm(nom)
    c.restoreState()


def _gen_grille(rng):
    """SIX numeros : deux par colonne (Z 1-12, I 13-24, N 25-36), tries
    croissants du haut vers le bas. Ordre rendu : haut Z,I,N puis bas Z,I,N."""
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
    rng = random.Random(560000 + int(serie_start))
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
    with open("test_zin.pdf", "wb") as f:
        f.write(generer_pdf(nb_cartes=16, couleur=True).read())
    print("ZIN genere")


# == LE DESSIN DE SA PLANCHE, RELEVE AU TRAIT (un carton, millièmes) ==
_DECOR = (
    "m19.2,990.5c14.1,985.2,8.2,976.3,6.3,970.6c3.6,962.5,2.9,860,2.8,501.2l2.8,42.1l11.4,27.4c16.4,18.7,24.3,10.9,30.5,8.4c37.6,5.5,194.8,4.4,506,5.2c949.1,6.2,971.3,6.6,980.1,13.9c985.8,18.6,991.3,28.1,9"
    "94.6,39c999.7,55.8,999.9,73.4,999.9,503.9c1000,940.8,999.9,951.7,994.5,968.3c984.1,1000.6,1029.8,997.8,502.5,999l28.7,1000.1l19.2,990.5|m977.9,978c983.1,972.8,988.1,963.8,989.2,958.1c990.2,952.4,991.2"
    ",747.5,991.4,502.7c991.6,115.3,991.1,56,987.5,44.5c978.8,16.8,1017.4,19,506.9,17.6c183.4,16.7,39.9,17.7,32.8,20.8c27.1,23.3,20,30.2,16.8,36.2c11.1,47.1,11.1,49.4,11.2,503.7c11.2,930,11.6,960.8,16,969."
    "1c18.7,974,23.3,980.1,26.4,982.6c30.4,985.9,165.1,987.2,500.3,987.3l968.6,987.4l977.9,978|m31.8,956.3l25,946l25,779.8c25,631,25.5,612.8,29.6,606c33.9,598.9,33.9,597.8,29.6,590.7c25.5,583.8,25,565.3,25"
    ",413c25,243.5,25,243,31.1,234.5c37,226.1,40.1,225.9,183.7,225.9c313.1,225.9,330.7,226.7,334.5,232.5c338.5,238.5,339.3,238.5,343.3,232.5c347.1,226.7,364.6,225.9,494,225.9c618.9,225.9,641.3,226.9,646.3,"
    "232.1c651.5,237.6,652.6,237.6,655.6,232.1c658.5,226.8,680,225.9,810.2,225.9l961.4,225.9l968.2,236.2l975,246.5l975,413.2c975,570.1,974.7,580.5,969.8,588.4c964.8,596.5,964.8,597,969.8,606.4c974.7,615.4,"
    "975,626.3,975,781l975,946l968.2,956.3l961.4,966.5l810.8,966.5c676.6,966.5,659.6,965.8,655.2,959.8c650.7,953.7,649.8,953.7,644,959.8c638.4,965.8,621.1,966.5,493.4,966.5c365,966.5,348.5,965.8,344.1,959."
    "8c339.6,953.7,338.7,953.7,332.9,959.8c327.3,965.8,310,966.5,182.6,966.5l38.6,966.5l31.8,956.3|m328,953.8c333.1,949.7,333.3,943.3,333.3,781c333.3,655.6,332.5,611.3,330,607.5c327.5,603.8,291.2,602.5,183"
    ".7,602.5c54.5,602.5,40.2,603.2,35.6,609.4c30.9,615.9,30.6,626.7,30.6,778.1c30.6,944.8,30.8,949.4,41.7,955.3c49.9,959.7,322.4,958.3,328,953.8|m641.7,949.8c647,941.7,647.2,935.8,647.2,781.3c647.2,643.1,"
    "646.6,619.8,642.9,611.8l638.6,602.5l495.2,602.5c365.7,602.5,351.3,603.2,346.7,609.4c342,615.9,341.7,626.7,341.7,778.9c341.7,935.8,341.9,941.7,347.2,949.8c352.6,957.9,356.5,958.2,494.4,958.2c632.4,958."
    "2,636.3,957.9,641.7,949.8|m961.4,950.3l967.9,942.4l967.3,777.7c966.8,628.2,966.3,612.5,962,607.7c955.1,600.1,663.1,600.1,658.9,607.8c656.9,611.3,655.7,670.8,655.2,779.9c654.6,938.9,654.8,946.9,659.7,9"
    "52.4c664,957.1,691.4,958.2,809.9,958.2c948,958.2,955.3,957.8,961.4,950.3|m653.6,593.7c648.9,586.6,643.3,593.3,647.5,601c649.8,605.2,651.8,605.7,653.8,602.7c655.8,599.7,655.7,596.9,653.6,593.7|m342.8,5"
    "98.9c343.6,596.9,343.6,594.2,342.7,592.9c340.5,589.7,333.3,594.2,333.3,598.8c333.3,603.6,340.9,603.7,342.8,598.9|m333.3,418.9c334.4,283.9,334,248.3,331.1,242.1c327.6,234.7,320.8,234.3,184.6,234.3c45.4"
    ",234.3,41.5,234.5,36.1,242.7c30.7,250.8,30.6,256.6,30.6,412.4c30.6,516.1,31.6,576.7,33.4,581.9c36.3,589.8,40.2,590,184.1,588.9l331.9,587.9l333.3,418.9|m643.9,584.9c646.4,581.2,647.2,537.6,647.2,414.8c"
    "647.2,267,646.7,248.8,642.6,242c638.3,234.7,630,234.3,494.9,234.3c365.7,234.3,351.3,235,346.7,241.2c342,247.7,341.7,258.6,341.7,411c341.7,515.2,342.7,576.7,344.5,581.9c347.3,589.7,351.9,590,494,590c60"
    "4.3,590,641.4,588.7,643.9,584.9|m963.7,584c966.1,579.7,967.1,532.5,967.3,411.9c967.7,253.9,967.5,245.5,962.5,240.1c954.7,231.5,667.4,231.6,659.6,240.1c654.6,245.7,654.4,253,654.9,414.1c655.2,506.5,656"
    ".2,583.9,657.1,586.1c658,588.4,719.1,590,809.5,590c936.4,590,961,589,963.7,584|m188.9,186.5c188.9,183.3,201.4,160.2,216.7,135.4c231.9,110.5,244.4,88.7,244.4,86.9c244.4,85.1,231.9,83.7,216.7,83.7c193.8"
    ",83.7,188.9,82.6,188.9,77.4c188.9,72.1,194.8,71.1,225,71.1c256.3,71.1,261.1,72,261.1,77.8c261.1,81.5,248.4,105.5,232.9,131.2l204.7,177.8l232.9,179c255.5,180,261.1,181.4,261.1,186.3c261.1,191.4,254.9,1"
    "92.5,225,192.5c195.7,192.5,188.9,191.4,188.9,186.5|m480.6,133.9c480.6,78.1,480.8,75.3,486.1,75.3c491.4,75.3,491.7,78.1,491.7,133.9c491.7,189.7,491.4,192.5,486.1,192.5c480.8,192.5,480.6,189.7,480.6,133"
    ".9|m716.7,133.9c716.7,80.9,717.1,75.3,721.5,75.3c724.2,75.3,739.8,96.5,756.3,122.4c772.7,148.3,786,166.6,785.8,163.2c785.6,159.7,785.6,138.5,785.8,116.1c786.1,82.9,786.9,75.3,790.3,75.3c793.8,75.3,794"
    ".4,84.6,794.4,133.9c794.4,186.9,794,192.5,789.6,192.4c786.9,192.4,772.2,172,756.9,147.1l729.2,101.9l728.4,147.2c727.7,189,727.2,192.5,722.1,192.5c717,192.5,716.7,189.4,716.7,133.9"
)
