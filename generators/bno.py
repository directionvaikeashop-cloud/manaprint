# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur BNO 8 BOULES (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : grille 3 colonnes (B-N-O) × 3 rangées.
La case CENTRALE (colonne du milieu, rangée du milieu) est toujours VIDE
et accueille le QR de vérification. => 8 numéros par carton.
Colonnes : B=1-15, N=31-45, O=61-75 (colonnes B, N, O du bingo).
Numéro de série EN HAUT ("Carte N° 00001").
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris (2 gammes ÉCO/PREMIUM).
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgv
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne
try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None


try:
    pdfmetrics.registerFont(TTFont("DJL", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    POLICE = "DJL"
except Exception:
    POLICE = "Helvetica"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)


# ══ DEUX GAMMES COMMERCIALES ══════════════════════════
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TF
try:
    _pm.registerFont(_TF("DJLECO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    _POLICE_ECO = "DJLECO"
except Exception:
    _POLICE_ECO = "Helvetica"
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)
_POLICE_P15 = "Helvetica-Bold"
_GRIS_P15 = colors.Color(0.55, 0.55, 0.55)

def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4
# (min, max) par colonne — BNO 8 boules (colonnes B, N, O du bingo)
PLAGES = [(1, 15), (31, 45), (61, 75)]

COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """8 numéros : col1 = 3 nums, col3 = 3 nums, col2 (milieu) = 2 nums.
    La case centrale (col2, rangée 1) est vide -> accueille le QR."""
    col1 = sorted(rng.sample(range(PLAGES[0][0], PLAGES[0][1] + 1), 3))
    col3 = sorted(rng.sample(range(PLAGES[2][0], PLAGES[2][1] + 1), 3))
    col2n = sorted(rng.sample(range(PLAGES[1][0], PLAGES[1][1] + 1), 2))
    col2 = [col2n[0], None, col2n[1]]  # centre vide
    grille = [
        [col1[0], col2[0], col3[0]],
        [col1[1], None,    col3[1]],   # centre vide
        [col1[2], col2[2], col3[2]],
    ]
    return grille


# 🎰 LE JETON DE CASINO (sceau Maeva 01/08) : rondelle à créneaux alternés,
# anneau intérieur, le numéro au centre — dessiné au trait, jamais de pavé plein.
_CRENEAUX = 6          # créneaux du pourtour (6 = allure du jeton, encre légère)


def _jeton(c, cx, cy, r, valeur, col, gris_ch, police_ch):
    """Un pion de casino : le numéro trône au centre de la rondelle."""
    from reportlab.lib import colors as _c
    # rondelle
    c.setStrokeColor(col); c.setLineWidth(0.7)
    c.circle(cx, cy, r, stroke=1, fill=0)
    # créneaux : un arc épais un sur deux (l'alternance du jeton de casino)
    c.setLineWidth(r * 0.15)
    pas = 360.0 / _CRENEAUX
    for k in range(0, _CRENEAUX, 2):
        c.arc(cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86,
              k * pas + pas * 0.18, pas * 0.64)
    # anneau intérieur (la plage claire où s'inscrit la valeur)
    c.setLineWidth(0.5)
    c.circle(cx, cy, r * 0.66, stroke=1, fill=0)
    # le numéro, au calibre de la rondelle
    t = r * 1.02
    if _sec:
        _sec.chiffre_micro(c, valeur, cx, cy - t * 0.34, t, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch); c.setFont(police_ch, t)
        c.drawCentredString(cx, cy - t * 0.34, str(valeur))


# 💰 PIONS DE VALEUR (sceau Maeva 01/08) : 2 cases condamnées par carton
_PIONS_VALEURS = [5, 10, 15, 20, 50, 100]     # nos références, en francs
_PIONS_PAR_CARTE = 2


def _pions_de_la_carte(serie):
    """Deux cases condamnées + leur valeur — mêmes pour une même série."""
    import random as _r
    rng = _r.Random(800000 * 7 + serie * 131)
    postes = rng.sample(range(8), _PIONS_PAR_CARTE)      # toute carte a >= 8 cases
    return {p: rng.choice(_PIONS_VALEURS) for p in postes}


def _jeton_valeur(c, cx, cy, r, francs, col, gris_ch, police_ch):
    """Le pion de valeur : la rondelle, et la somme au centre."""
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.setLineWidth(r * 0.15)
    pas = 360.0 / _CRENEAUX
    for k in range(0, _CRENEAUX, 2):
        c.arc(cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86,
              k * pas + pas * 0.18, pas * 0.64)
    c.setLineWidth(0.6)
    c.circle(cx, cy, r * 0.70, stroke=1, fill=0)
    t = r * 0.66 if francs < 100 else r * 0.54
    c.setFillColor(col); c.setFont(police_ch, t)
    c.drawCentredString(cx, cy - t * 0.22, str(francs))
    c.setFont("Helvetica-Bold", r * 0.32)
    c.drawCentredString(cx, cy - r * 0.52, "FRANCS")


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id="", jetons=False):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 3

    # Bordure carte
    _cond = _pions_de_la_carte(serie) if jetons else {}
    _rang = [0]
    if jetons:
        # ✍️ signature à la manière de MOOREA revisité (sceau Maeva 01/08)
        # ✂️ 05/08 (demande Maeva) : la mention qui suivait le nom est RETIRÉE
        # (elle faisait sortir la ligne de la grille). On ne garde que le NOM
        # du jeu, et la taille se règle seule pour ne JAMAIS déborder.
        _t = "BNO CASINO"
        if titre_jeu and "CASINO" not in titre_jeu.strip().upper():
            _t += "  \u2014  " + titre_jeu.strip()[:26]
        if telephone:
            _t += "  " + str(telephone)[:16]
        _ts = 6.4
        while _ts > 4.4 and _lgv(_t, "Helvetica-Bold", _ts) > CARD_W - 6 * mm:
            _ts -= 0.2
        while _lgv(_t, "Helvetica-Bold", _ts) > CARD_W - 6 * mm and len(_t) > 12:
            _t = _t[:-1]
        c.setFillColor(col); c.setFont("Helvetica-Bold", _ts)
        c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 5.0 * mm, _t)
        c.setFont("Helvetica", 5.4)
        c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 8.4 * mm, "Carte N\u00b0 %05d" % serie)
    if not jetons:            # 🎰 CASINO : pas de contour, les pions flottent
        c.setStrokeColor(col); c.setLineWidth(0.8)
        c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête (titre + N° carte)
    hdr_y = y0 + CARD_H - 3.5 * mm
    titre = "BNO 8 boules"
    if titre_jeu and "BNO" not in titre_jeu.strip().upper():
        titre = "BNO 8 boules \u00b7 " + titre_jeu.strip()   # le nom du jeu TOUJOURS affiché (décision Maeva)
    elif titre_jeu:
        titre = titre_jeu.strip()
    if telephone:
        titre += " " + telephone
    c.setFillColor(col); c.setFont(POLICE, 5)
    if not jetons: c.drawCentredString(x0 + CARD_W / 2, hdr_y, titre[:64])
    c.setFillColor(col); c.setFont(POLICE, 6.5)
    if not jetons: c.drawCentredString(x0 + CARD_W / 2, hdr_y - 4 * mm, "Carte N° %05d" % serie)

    # Zone grille 3×3
    grid_top = hdr_y - 6.5 * mm
    grid_bot = y0 + 2.5 * mm
    cell_w = CARD_W / ncols
    grid_h = grid_top - grid_bot
    row_h = grid_h / 3

    # séparateurs de grille
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
    for i in range(1, ncols):
        if not jetons: c.line(x0 + i * cell_w, grid_bot, x0 + i * cell_w, grid_top)
    for r in range(1, 3):
        yy = grid_top - r * row_h
        if not jetons: c.line(x0 + 1.5 * mm, yy, x0 + CARD_W - 1.5 * mm, yy)

    # contenu
    for r in range(3):
        for cc in range(3):
            cx = x0 + (cc + 0.5) * cell_w
            cyc = grid_top - (r + 0.5) * row_h
            val = grille[r][cc]
            if val is None:
                # case centrale vide (r==1, cc==1) -> QR ; les autres None restent vides
                if r == 1 and cc == 1 and _sec and evenement_id:
                    try:
                        _q = min(cell_w, row_h) - 2.5 * mm
                        _q = max(5.0 * mm, _q)
                        _sec.carton_qr(c, cx - _q / 2, cyc - _q / 2, _q, evenement_id, serie)
                    except Exception:
                        pass
                continue
            if jetons:
                _k = _rang[0]; _rang[0] += 1
                _r_jeton = min(cell_w, row_h) * 0.40
                if _k in _cond:
                    _jeton_valeur(c, cx, cyc, _r_jeton, _cond[_k], col, gris_ch, police_ch)
                else:
                    _jeton(c, cx, cyc, _r_jeton, val, col, gris_ch, police_ch)
                continue
            if _sec:
                _sec.chiffre_micro(c, val, cx, cyc - 11, 32, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, 32)
                c.drawCentredString(cx, cyc - 11, str(val))


def _generer_old(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", jetons=False, page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(800000 + int(serie_start))
    serie = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 9)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 7.2 * mm, "%03d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                grille = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, grille, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id, jetons=jetons)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf



def generer_pdf_casino(**kw):
    """🎰 Le jumeau CASINO : chaque numéro vit dans un pion de casino."""
    kw["jetons"] = True
    return _generer_old(**kw)


# ══════════════════════════════════════════════════════════════════════
# ⭐ NOUVELLE MAQUETTE BNO (04/10) — releve au trait sur la maquette de
#    Maeva : double cadre arrondi, en-tete « B N O » et tableau de SIX
#    cases (2 rangees x 3 colonnes). SIX numeros, DEUX par colonne :
#    B 1-15 · N 31-45 · O 61-75.  16 cartons par feuille A4 PAYSAGE.
#    NE PAS « ameliorer » le decor. La planche est posee une fois puis
#    recopiee seize fois, chaque fois dans la couleur de son carton
#    (gris #555555 en N&B). SEULE generer_pdf change ; le jumeau CASINO
#    (generer_pdf_casino -> _generer_old) garde son ancienne planche.
# ══════════════════════════════════════════════════════════════════════
import os as _bn_os
from reportlab.lib.pagesizes import landscape as _bn_landscape

_BN_PAGE_W, _BN_PAGE_H = _bn_landscape(A4)
_BN_ASPECT = 359.0 / 237.0
_BN_COLS = 4
_BN_ROWS = 4
_BN_PAR_PAGE = _BN_COLS * _BN_ROWS
_BN_MARGE_X = 6 * mm
_BN_GUTTER_X = 3 * mm
_BN_GUTTER_Y = 3 * mm
_BN_CARD_W = (_BN_PAGE_W - 2 * _BN_MARGE_X - (_BN_COLS - 1) * _BN_GUTTER_X) / _BN_COLS
_BN_CARD_H = _BN_CARD_W / _BN_ASPECT
_BN_BLOC_H = _BN_ROWS * _BN_CARD_H + (_BN_ROWS - 1) * _BN_GUTTER_Y
_BN_MARGE_TOP = 7 * mm
_BN_MARGE_BOT = _BN_PAGE_H - _BN_MARGE_TOP - _BN_BLOC_H

try:
    pdfmetrics.registerFont(TTFont("LMROMANBNO", _bn_os.path.join(
        _bn_os.path.dirname(_bn_os.path.abspath(__file__)), "LatinModern.ttf")))
    _BN_POLICE_ECO = "LMROMANBNO"
except Exception:
    _BN_POLICE_ECO = _POLICE_ECO
_BN_GRIS_ECO = colors.Color(0.40, 0.40, 0.40)
_BN_GRAS_TRAIT = 0.012
_BN_GRIS_P15 = colors.Color(0.14, 0.14, 0.14)
_BN_TRAIT_NB = "#555555"

# les six cases (fx depuis la gauche, fy depuis le HAUT) : haut B,N,O puis bas B,N,O
_BN_CELLULES = [
    (0.175, 0.407), (0.496, 0.407), (0.820, 0.407),
    (0.175, 0.783), (0.496, 0.783), (0.820, 0.783),
]
_BN_PLAGES = [(1, 15), (31, 45), (61, 75)]   # B, N, O
_BN_TAILLE = 40.0
_BN_TSERIE = 5.0


def _bn_style(style):
    if str(style).lower() in ("p15", "premium"):
        return _BN_POLICE_ECO, _BN_GRIS_P15
    return _BN_POLICE_ECO, _BN_GRIS_ECO


def _bn_graver_planche(c):
    nom = "BNO6_DECOR"
    if not getattr(c, "_bno6_forme_faite", False):
        c.beginForm(nom, lowerx=0, lowery=0, upperx=_BN_CARD_W, uppery=_BN_CARD_H)
        p = c.beginPath()
        for contour in _BN_DECOR.split("|"):
            i = 0
            n = len(contour)
            while i < n:
                cmd = contour[i]
                j = i + 1
                while j < n and contour[j] not in "mlc":
                    j += 1
                v = [float(x) for x in contour[i + 1:j].split(",")]
                if cmd == "m":
                    p.moveTo(v[0] / 1000.0 * _BN_CARD_W, _BN_CARD_H - v[1] / 1000.0 * _BN_CARD_H)
                elif cmd == "l":
                    p.lineTo(v[0] / 1000.0 * _BN_CARD_W, _BN_CARD_H - v[1] / 1000.0 * _BN_CARD_H)
                else:
                    p.curveTo(v[0] / 1000.0 * _BN_CARD_W, _BN_CARD_H - v[1] / 1000.0 * _BN_CARD_H,
                              v[2] / 1000.0 * _BN_CARD_W, _BN_CARD_H - v[3] / 1000.0 * _BN_CARD_H,
                              v[4] / 1000.0 * _BN_CARD_W, _BN_CARD_H - v[5] / 1000.0 * _BN_CARD_H)
                i = j
            p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.endForm()
        c._bno6_forme_faite = True
    return nom


def _bn_poser(c, x0, y0, couleur):
    nom = _bn_graver_planche(c)
    c.saveState()
    c.setFillColor(couleur)
    c.translate(x0, y0)
    c.doForm(nom)
    c.restoreState()


def _bn_gen_grille(rng):
    duos = [sorted(rng.sample(range(lo, hi + 1), 2)) for lo, hi in _BN_PLAGES]
    return [duos[0][0], duos[1][0], duos[2][0],
            duos[0][1], duos[1][1], duos[2][1]]


def _bn_tirer(rng, deja):
    for _ in range(400):
        g = _bn_gen_grille(rng)
        cle = tuple(g)
        if cle not in deja:
            deja.add(cle)
            return g
    return g


def _bn_dessiner(c, x0, y0, grille, serie, couleur, style="eco"):
    police_ch, gris_ch = _bn_style(style)
    _bn_poser(c, x0, y0, couleur)
    taille = _BN_TAILLE
    for k, (fx, fy) in enumerate(_BN_CELLULES):
        cx = x0 + _BN_CARD_W * fx
        cy = y0 + _BN_CARD_H * (1.0 - fy) - taille * 0.36
        val = grille[k]
        if _sec:
            _sec.chiffre_micro(c, val, cx, cy, taille, gris_ch, police_ch, epaisseur=_BN_GRAS_TRAIT)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(cx, cy, str(val))
    c.setFillColor(GRIS); c.setFont(POLICE, _BN_TSERIE)
    c.drawRightString(x0 + _BN_CARD_W - 2.0 * mm, y0 + 1.4 * mm, "N° %06d" % serie)
    if _sec:
        try:
            _sec.cadre_micro(c, x0, y0, _BN_CARD_W, _BN_CARD_H, serie, retrait=0.9 * mm)
        except Exception:
            pass


def generer_pdf(nb_cartes=16, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", style="eco", evenement_id="", motif="",
                page_start=1, **_):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=_bn_landscape(A4), pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + _BN_PAR_PAGE - 1) // _BN_PAR_PAGE
    rng = random.Random(610000 + int(serie_start))
    serie = int(serie_start)
    no_page = max(1, int(page_start))
    faits = 0
    _deja = set()
    for _p in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 8)
            c.drawCentredString(_BN_PAGE_W / 2, _BN_PAGE_H - 4.4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 5.5)
        c.drawRightString(_BN_PAGE_W - _BN_MARGE_X, _BN_PAGE_H - 4.4 * mm, "%03d" % no_page)
        for row in range(_BN_ROWS):
            for col_i in range(_BN_COLS):
                if faits >= nb_cartes:
                    break
                x0 = _BN_MARGE_X + col_i * (_BN_CARD_W + _BN_GUTTER_X)
                y0 = _BN_MARGE_BOT + (_BN_ROWS - 1 - row) * (_BN_CARD_H + _BN_GUTTER_Y)
                grille = _bn_tirer(rng, _deja)
                coul = colors.HexColor(
                    couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else _BN_TRAIT_NB)
                _bn_dessiner(c, x0, y0, grille, serie, coul, style=style)
                serie += 1
                faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    with open("test_bno.pdf", "wb") as f:
        f.write(generer_pdf(nb_cartes=16, couleur=True).read())
    print("BNO (nouvelle maquette) genere")


# == LE DESSIN DE SA PLANCHE, RELEVE AU TRAIT (un carton, millièmes) ==
_BN_DECOR = (
    "m29.2,994c24.7,990.9,17.1,982.3,12.5,974.9l4.2,961.5l3.4,505.6l2.7,49.7l8.6,35.3c11.8,27.3,19.3,17.1,25.2,12.5c35.8,4.4,43.9,4.2,501.4,4.2c958.8,4.2,967,4.4,977.5,12.5c983.5,17.1,990.9,27.3,994.2,35.3"
    "l1000.1,49.7l999.3,505.6l998.6,961.5l990.3,974.9c973.6,1001.7,1007.5,1000,500.8,999.8c120,999.7,36.1,998.7,29.2,994|m971.4,980.3c976.7,976.4,983.5,967.4,986.4,960.3c991.4,947.8,991.6,930.1,991.6,499.5"
    "c991.6,51.8,991.6,51.8,985.8,40.6c972.7,15.2,1006.4,16.9,501.4,16.9c-3.6,16.9,30.1,15.2,17,40.6c11.1,51.8,11.1,51.8,11.2,499.5c11.2,929.2,11.4,947.8,16.4,960.2c28.1,989.2,-9.6,987.1,501,987.2c925.5,98"
    "7.3,962.3,986.8,971.4,980.3|m48.1,966.6c38.3,964.8,31.3,960.7,27.2,954.4l20.9,944.9l20.9,779.2c20.9,627.7,21.3,612.6,25.8,602.1c28.5,595.9,29.5,590.7,28,590.7c20.7,590.7,19.2,555.4,20,402l20.9,244.9l2"
    "8.6,233.2l36.3,221.5l180,220.4c301.4,219.4,324.9,220.1,331.8,225.3c338.9,230.7,340.9,230.7,347.5,225.5c358.8,216.5,638.4,216.5,649.7,225.5c656.3,230.7,658.4,230.7,665.4,225.3c672.3,220.1,696.2,219.4,8"
    "19.8,220.4l966.1,221.5l973.3,231.7l980.5,242l980.5,410.7c980.5,560.2,980,580.4,976,587c971.9,594,971.9,595.1,976,601.4c980,607.4,980.5,627.2,980.5,776.1l980.5,944l973.3,954.9c968.8,961.8,961.8,966.7,9"
    "54.5,968.2c948.1,969.4,881.4,970,806.3,969.4c685.4,968.5,668.9,967.6,662.7,961.5c656.3,955,655.4,955.1,649.6,962.2c643.7,969.3,634.4,969.8,497.9,969.1c388.4,968.5,350.9,967,346.4,963.1c341.5,958.9,338"
    ".4,959.1,330.4,964.2c322.1,969.5,300,970.4,191.6,969.9c120.7,969.5,56.1,968.1,48.1,966.6|m332.7,948.4c336.5,940.3,337,916.8,337,776.8c337,631.8,336.6,613.8,332.4,606.9c328.1,599.6,319.7,599.2,182.2,59"
    "9.2c53.6,599.2,36.1,599.9,32.2,605.8c28.4,611.6,27.9,632.9,27.9,776.4l27.9,940.3l35.2,949.1c42.4,957.6,45.1,957.8,185.5,957.8l328.4,957.8l332.7,948.4|m646.4,953.4c651.6,949.2,651.8,942.8,651.8,779.2c6"
    "51.8,652.7,651,608,648.5,604.2c646,600.4,608.9,599.2,499,599.2c366.9,599.2,352.3,599.8,347.7,606.1c342.9,612.7,342.6,623.6,342.6,777.7c342.6,925,343.1,943.2,347.2,950.1c351.6,957.4,359.9,957.8,496.4,9"
    "57.8c590.8,957.8,642.9,956.3,646.4,953.4|m968.1,947.4l974.9,937.1l974.9,775.8c974.9,631.7,974.4,613.8,970.3,606.9c966,599.6,957.6,599.2,818,599.2c684.5,599.2,669.9,599.8,665.3,606.1c660.5,612.7,660.2,"
    "623.6,660.2,777.7c660.2,925,660.7,943.2,664.8,950.1c669.1,957.4,677.5,957.8,815.3,957.8l961.3,957.8l968.1,947.4|m343.9,595.2c346,590.2,340.7,585.2,337,588.7c333.9,591.6,335.9,599.2,339.8,599.2c341.2,5"
    "99.2,343,597.4,343.9,595.2|m660.2,595.6c660.2,590.1,656.9,586.5,654.2,589c651.3,591.7,653.8,599.2,657.5,599.2c659,599.2,660.2,597.6,660.2,595.6|m334.2,578.3c336,573.1,337,511.6,337,407.8c337,265.7,336"
    ".5,244.5,332.7,238.7c328.8,232.8,311.3,232.1,182.4,232.1l36.5,232.1l32.2,241.4c28.4,249.5,27.9,273.1,27.9,413.6c27.9,534.6,28.7,577.7,31.2,581.4c33.7,585.2,71.2,586.5,182.9,586.5c326.7,586.5,331.4,586"
    ".2,334.2,578.3|m651.1,414c651.7,291.7,651,242,648.7,237.8c646.1,233.1,619.5,232.1,499.2,232.1c366.9,232.1,352.3,232.7,347.7,239.1c342.9,245.6,342.6,256.5,342.6,408.1c342.6,512.2,343.7,573.1,345.5,578."
    "4c348.3,586.4,352.4,586.5,499.4,585.5l650.4,584.4l651.1,414|m972,578.3c973.9,573.1,974.9,512.2,974.9,409.6c974.9,254.6,974.7,248.6,969.4,240.5c963.9,232.3,960.1,232.1,817.1,232.1c684.5,232.1,669.9,232"
    ".7,665.3,239.1c660.5,245.6,660.2,256.5,660.2,411.2c660.2,534,661,577.7,663.5,581.4c666,585.2,704.2,586.5,818,586.5c964.6,586.5,969.3,586.3,972,578.3|m744.6,185.2c739.7,183.1,731.9,175.6,727.3,168.5c70"
    "6.4,136.8,712.3,85.7,739.1,67.2c761.8,51.6,791.1,62,802.2,89.4c809.7,108.1,809.7,140.8,802.2,159.5c792.3,184.1,767.4,195.2,744.6,185.2|m206.1,124.5l206.1,63.3l234,63.3c258.1,63.3,262.6,64.4,267.4,71.7"
    "c274,81.8,274.9,106.3,268.8,113.9c265.2,118.4,265.6,120.7,271.6,131.6c280.4,147.4,280.4,162.1,271.7,175.3c265.3,185,263,185.7,235.5,185.7l206.1,185.7l206.1,124.5|m468,124.5c468,74.6,468.7,63.3,471.9,6"
    "3.3c474.1,63.3,482.4,75.2,490.4,89.7c498.4,104.2,511,126.2,518.5,138.5l532,161l532,112.2c532,71.5,532.7,63.3,536.2,63.3c539.7,63.3,540.4,72.9,540.4,124.8c540.4,174,539.6,186,536.7,184.9c534.6,184.2,52"
    "0.5,161.8,505.3,135.3l477.7,87.1l476.9,136.4c476.3,176.4,475.4,185.7,472.1,185.7c468.6,185.7,468,175.5,468,124.5|m264.4,167c271.8,156.9,271.8,146.9,264.3,136.7c259.7,130.3,254.2,128.7,237.2,128.7l215."
    "9,128.7l215,147.1c213.6,177.2,214.5,178.3,237.9,176.6c253.2,175.4,260.1,172.9,264.4,167|m788.4,162.3c812.4,127.4,797,71.7,763.3,71.7c739.7,71.7,724.2,92.8,724.2,125.2c724.2,157.1,741.7,178.7,765.4,176"
    "c776.9,174.8,781.9,171.8,788.4,162.3|m258.4,111.6c266.7,102.8,266.4,86.4,257.9,77.9c253.2,73.2,246.1,71.7,233.6,72.6l215.9,73.8l215,90.1c214.5,99.1,214.8,109,215.6,112.3c217.8,120.8,250.3,120.3,258.4,"
    "111.6"
)
