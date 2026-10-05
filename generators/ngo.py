# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur NGO 8 BOULES (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : grille 3 colonnes (B-N-O) × 3 rangées.
La case CENTRALE (colonne du milieu, rangée du milieu) est toujours VIDE
et accueille le QR de vérification. => 8 numéros par carton.
Colonnes : N=31-45, G=46-60, O=61-75 (colonnes N, G, O du bingo).
Numéro de série EN PIED ("N° SÉRIE ... 000001").
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
import os as _os

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
# (min, max) par colonne — NGO 8 boules (colonnes B, N, O du bingo)
PLAGES = [(31, 45), (46, 60), (61, 75)]

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
    rng = _r.Random(700000 * 7 + serie * 131)
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
        _t = "NGO CASINO"
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

    # En-tête (titre)
    hdr_y = y0 + CARD_H - 3.5 * mm
    titre = "NGO 8 boules"
    if titre_jeu and "NGO" not in titre_jeu.strip().upper():
        titre = "NGO 8 boules \u00b7 " + titre_jeu.strip()   # le nom du jeu TOUJOURS affiché (décision Maeva)
    elif titre_jeu:
        titre = titre_jeu.strip()
    if telephone:
        titre += " " + telephone
    c.setFillColor(col); c.setFont(POLICE, 5)
    if not jetons: c.drawCentredString(x0 + CARD_W / 2, hdr_y, titre[:64])

    # En-tête colonnes N - G - O
    cell_w = CARD_W / ncols
    lettres_y = hdr_y - 4 * mm
    for i, lettre in enumerate(["N", "G", "O"]):
        c.setFillColor(col); c.setFont(POLICE, 6.5)
        c.drawCentredString(x0 + (i + 0.5) * cell_w, lettres_y, lettre)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    if not jetons: c.line(x0, lettres_y - 1.5 * mm, x0 + CARD_W, lettres_y - 1.5 * mm)

    # Zone grille 3×3
    grid_top = lettres_y - 1.5 * mm
    grid_bot = y0 + 5 * mm
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

    # Pied : N° SÉRIE (comme la référence NGO)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    if not jetons: c.line(x0, y0 + 4.5 * mm, x0 + CARD_W, y0 + 4.5 * mm)
    c.setFillColor(GRIS_CLAIR); c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 2 * mm, y0 + 1.5 * mm, "N° SÉRIE")
    c.setFillColor(col); c.setFont("Helvetica", 6)
    c.drawRightString(x0 + CARD_W - 2 * mm, y0 + 1.5 * mm, "%06d" % serie)


def _generer_old(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", jetons=False, page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(700000 + int(serie_start))
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
# ⭐ NOUVELLE MAQUETTE NGO (04/10) — releve au trait sur la maquette de
#    Maeva : double cadre arrondi, en-tete « N G O » et tableau de SIX
#    cases (2 rangees x 3 colonnes). SIX numeros, DEUX par colonne :
#    N 31-45 · G 46-60 · O 61-75.  16 cartons par feuille A4 PAYSAGE.
#    NE PAS « ameliorer » le decor. La planche est posee une fois puis
#    recopiee seize fois, chaque fois dans la couleur de son carton
#    (gris #555555 en N&B). SEULE generer_pdf change ; le jumeau CASINO
#    (generer_pdf_casino -> _generer_old) garde son ancienne planche.
# ══════════════════════════════════════════════════════════════════════
from reportlab.lib.pagesizes import landscape as _landscape

_NG_PAGE_W, _NG_PAGE_H = _landscape(A4)
_NG_ASPECT = 363.0 / 238.0
_NG_COLS = 4
_NG_ROWS = 4
_NG_PAR_PAGE = _NG_COLS * _NG_ROWS
_NG_MARGE_X = 6 * mm
_NG_GUTTER_X = 3 * mm
_NG_GUTTER_Y = 3 * mm
_NG_CARD_W = (_NG_PAGE_W - 2 * _NG_MARGE_X - (_NG_COLS - 1) * _NG_GUTTER_X) / _NG_COLS
_NG_CARD_H = _NG_CARD_W / _NG_ASPECT
_NG_BLOC_H = _NG_ROWS * _NG_CARD_H + (_NG_ROWS - 1) * _NG_GUTTER_Y
_NG_MARGE_TOP = 7 * mm
_NG_MARGE_BOT = _NG_PAGE_H - _NG_MARGE_TOP - _NG_BLOC_H

try:
    pdfmetrics.registerFont(TTFont("LMROMANNGO", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    _NG_POLICE_ECO = "LMROMANNGO"
except Exception:
    _NG_POLICE_ECO = _POLICE_ECO
_NG_GRIS_ECO = colors.Color(0.40, 0.40, 0.40)
_NG_GRAS_TRAIT = 0.012
_NG_GRIS_P15 = colors.Color(0.14, 0.14, 0.14)
_NG_TRAIT_NB = "#555555"

_NG_CELLULES = [
    (0.178, 0.410), (0.498, 0.410), (0.818, 0.410),
    (0.178, 0.788), (0.498, 0.788), (0.818, 0.788),
]
_NG_TAILLE = 40.0
_NG_TSERIE = 5.0


def _ng_style(style):
    if str(style).lower() in ("p15", "premium"):
        return _NG_POLICE_ECO, _NG_GRIS_P15
    return _NG_POLICE_ECO, _NG_GRIS_ECO


def _ng_graver_planche(c):
    nom = "NGO6_DECOR"
    if not getattr(c, "_ngo6_forme_faite", False):
        c.beginForm(nom, lowerx=0, lowery=0, upperx=_NG_CARD_W, uppery=_NG_CARD_H)
        p = c.beginPath()
        for contour in _NG_DECOR.split("|"):
            i = 0
            n = len(contour)
            while i < n:
                cmd = contour[i]
                j = i + 1
                while j < n and contour[j] not in "mlc":
                    j += 1
                v = [float(x) for x in contour[i + 1:j].split(",")]
                if cmd == "m":
                    p.moveTo(v[0] / 1000.0 * _NG_CARD_W, _NG_CARD_H - v[1] / 1000.0 * _NG_CARD_H)
                elif cmd == "l":
                    p.lineTo(v[0] / 1000.0 * _NG_CARD_W, _NG_CARD_H - v[1] / 1000.0 * _NG_CARD_H)
                else:
                    p.curveTo(v[0] / 1000.0 * _NG_CARD_W, _NG_CARD_H - v[1] / 1000.0 * _NG_CARD_H,
                              v[2] / 1000.0 * _NG_CARD_W, _NG_CARD_H - v[3] / 1000.0 * _NG_CARD_H,
                              v[4] / 1000.0 * _NG_CARD_W, _NG_CARD_H - v[5] / 1000.0 * _NG_CARD_H)
                i = j
            p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.endForm()
        c._ngo6_forme_faite = True
    return nom


def _ng_poser(c, x0, y0, couleur):
    nom = _ng_graver_planche(c)
    c.saveState()
    c.setFillColor(couleur)
    c.translate(x0, y0)
    c.doForm(nom)
    c.restoreState()


def _ng_gen_grille(rng):
    duos = [sorted(rng.sample(range(lo, hi + 1), 2)) for lo, hi in PLAGES]
    return [duos[0][0], duos[1][0], duos[2][0],
            duos[0][1], duos[1][1], duos[2][1]]


def _ng_tirer(rng, deja):
    for _ in range(400):
        g = _ng_gen_grille(rng)
        cle = tuple(g)
        if cle not in deja:
            deja.add(cle)
            return g
    return g


def _ng_dessiner(c, x0, y0, grille, serie, couleur, style="eco"):
    police_ch, gris_ch = _ng_style(style)
    _ng_poser(c, x0, y0, couleur)
    taille = _NG_TAILLE
    for k, (fx, fy) in enumerate(_NG_CELLULES):
        cx = x0 + _NG_CARD_W * fx
        cy = y0 + _NG_CARD_H * (1.0 - fy) - taille * 0.36
        val = grille[k]
        if _sec:
            _sec.chiffre_micro(c, val, cx, cy, taille, gris_ch, police_ch, epaisseur=_NG_GRAS_TRAIT)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(cx, cy, str(val))
    c.setFillColor(GRIS); c.setFont(POLICE, _NG_TSERIE)
    c.drawRightString(x0 + _NG_CARD_W - 2.0 * mm, y0 + 1.4 * mm, "N° %06d" % serie)
    if _sec:
        try:
            _sec.cadre_micro(c, x0, y0, _NG_CARD_W, _NG_CARD_H, serie, retrait=0.9 * mm)
        except Exception:
            pass


def generer_pdf(nb_cartes=16, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", style="eco", evenement_id="", motif="",
                page_start=1, **_):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=_landscape(A4), pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + _NG_PAR_PAGE - 1) // _NG_PAR_PAGE
    rng = random.Random(640000 + int(serie_start))
    serie = int(serie_start)
    no_page = max(1, int(page_start))
    faits = 0
    _deja = set()
    for _p in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 8)
            c.drawCentredString(_NG_PAGE_W / 2, _NG_PAGE_H - 4.4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 5.5)
        c.drawRightString(_NG_PAGE_W - _NG_MARGE_X, _NG_PAGE_H - 4.4 * mm, "%03d" % no_page)
        for row in range(_NG_ROWS):
            for col_i in range(_NG_COLS):
                if faits >= nb_cartes:
                    break
                x0 = _NG_MARGE_X + col_i * (_NG_CARD_W + _NG_GUTTER_X)
                y0 = _NG_MARGE_BOT + (_NG_ROWS - 1 - row) * (_NG_CARD_H + _NG_GUTTER_Y)
                grille = _ng_tirer(rng, _deja)
                coul = colors.HexColor(
                    couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else _NG_TRAIT_NB)
                _ng_dessiner(c, x0, y0, grille, serie, coul, style=style)
                serie += 1
                faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    with open("test_ngo.pdf", "wb") as f:
        f.write(generer_pdf(nb_cartes=16, couleur=True).read())
    print("NGO (nouvelle maquette) genere")


# == LE DESSIN DE SA PLANCHE, RELEVE AU TRAIT (un carton, millièmes) ==
_NG_DECOR = (
    "m22.8,993.8c17.9,990.5,11.4,981.6,8.3,974c2.9,960.3,2.8,953.9,2.8,502.9c2.8,-1.8,1.6,29.6,20.1,12.4c28.8,4.4,37.6,4.2,500,4.2c962.1,4.2,971.2,4.4,979.9,12.4c984.7,16.9,990.9,25.8,993.7,32.2c998.4,43.1"
    ",998.7,68.3,999.4,495.6c1000.3,1007,1001.5,976.9,979.7,991.9c968.7,999.5,952,999.8,500,999.7c104,999.7,30.3,998.8,22.8,993.8|m975.3,981c979.7,977.6,984.6,971.1,986.1,966.6c990.7,953.6,992,60.6,987.4,4"
    "3.3c979.9,14.7,1017.2,16.6,497.1,17.8l27.1,18.9l19.1,32.6l11,46.4l11,501.6l11,956.8l16.9,968.3c20.1,974.6,25.4,981.3,28.6,983.3c31.8,985.2,244.3,987,500.8,987.1c911.7,987.4,968.2,986.6,975.3,981|m178."
    "7,966.4c43.7,964.4,36.1,963.9,30.6,956.3c24.9,948.4,24.8,945.7,24.8,781.8c24.8,636,25.3,614.1,29.2,605.7c33.2,596.9,33.2,595.5,29.2,588.7c25.3,582.1,24.8,561.3,24.9,411.4c25,228.5,24.7,231.5,39.7,222."
    "9c44.5,220,96.8,218.5,186.8,218.5c302.7,218.5,327.7,219.6,334,224.6c340.6,229.8,342.6,229.8,349.2,224.6c360.6,215.5,634.1,215.6,645.5,224.7c652.4,230.2,654.3,230.2,661.2,224.7c667.9,219.4,691.1,218.5,"
    "812.1,218.5c959.5,218.5,969.7,219.5,975.3,235.5c976.9,240.1,978,309.4,978,410.6c978,555.3,977.4,579.2,973.7,587.3c969.8,595.8,969.8,597.5,973.7,606c977.4,614,978,637.7,978,779.8c978,939.8,977.8,944.5,"
    "972.3,955.3l966.5,966.4l814.8,966.4c677.4,966.4,662.5,965.7,657.9,959.4c653.2,953,652.5,953,647.9,959.4c643.3,965.7,628.8,966.4,496.7,966.4c369.6,966.4,350.1,965.6,347.1,960c344.6,955.5,342.6,954.9,34"
    "0.1,958.1c332.6,967.6,316.4,968.4,178.7,966.4|m333.3,949.6c338.7,941.5,338.8,935.6,338.8,780.2c338.8,649.7,338.1,617.7,335,611.3c331.4,603.6,325.7,603.4,184.2,604.2c50,605,36.9,605.7,33.7,612.2c31.1,6"
    "17.5,30.3,658,30.3,780.2c30.3,935.6,30.5,941.5,35.8,949.6c41.2,957.8,45,958,184.6,958c324.2,958,328,957.8,333.3,949.6|m644.6,949.6c649.9,941.5,650.1,935.6,650.1,780.2c650.1,652.3,649.4,617.7,646.4,611"
    ".5c642.9,604.2,635.5,603.9,498.6,604.5c397.7,605,353.4,606.6,350.8,609.8c347.8,613.6,347.1,647.3,347.1,781.8c347.1,936.8,347.5,949.5,351.9,953.4c355,956.2,407.2,957.8,497.9,957.9c635.5,958,639.3,957.8"
    ",644.6,949.6|m963.6,951.4l969.7,944.9l969.7,780c969.7,657.4,968.9,613.8,966.4,610.1c961.6,602.8,666.5,602.8,661.7,610.1c659.2,613.8,658.4,657.8,658.4,782.1c658.4,936.8,658.8,949.5,663.2,953.4c666.3,95"
    "6.2,719.6,957.8,812.7,957.9c939.3,958,958.2,957.2,963.6,951.4|m345.1,602.5c346,601.1,346,597.3,345.2,594c344.1,589.4,342.8,589.2,339.9,592.8c337.8,595.4,336.8,599.3,337.7,601.3c339.4,605.6,342.7,606.2"
    ",345.1,602.5|m656.4,602.5c657.3,601.1,657.3,597.3,656.5,594c655.4,589.4,654.1,589.2,651.2,592.8c649.1,595.4,648.1,599.3,649,601.3c650.7,605.6,654,606.2,656.4,602.5|m334.5,585.8c338.3,580.1,338.8,558.5"
    ",338.8,413.3c338.8,306.9,337.8,244.4,336,239.2c333.2,231.3,328.7,231.1,186,231.1l38.9,231.1l34.6,240.4c28.1,254.5,28.1,569.1,34.6,583.1l38.9,592.4l184.5,592.4c313.3,592.4,330.7,591.7,334.5,585.8|m645."
    "1,585.5c649.8,579,650.1,568,650.1,412.9c650.1,306.8,649.1,244.4,647.3,239.2c644.5,231.3,640,231.1,499.1,231.1c389.7,231.1,352.9,232.3,350.4,236.1c345.7,243.4,345.7,580.1,350.4,587.4c352.9,591.2,389.2,"
    "592.4,496.9,592.4c626.2,592.4,640.5,591.8,645.1,585.5|m964.4,588.1c969.5,583.9,969.7,577.5,969.7,412.5c969.7,284.8,968.9,239.9,966.4,236.1c961.6,228.9,666.5,228.9,661.7,236.1c657,243.4,657,580.1,661.7"
    ",587.4c666.1,594,956.3,594.7,964.4,588.1|m209.4,124.3c209.4,46,210.4,45.6,244,110.2l268.6,157.3l269.4,110.2c270,72.1,270.9,63,274.2,63c277.6,63,278.2,73.2,278.2,123.9c278.2,175,277.6,184.9,274.2,184.9"
    "c271.9,184.9,259.3,164.1,246.1,138.7c232.9,113.2,221.4,92.4,220.5,92.4c219.7,92.4,219,112.7,219,137.5c219,177.1,218.4,182.8,214.2,184.1c209.8,185.4,209.4,180.3,209.4,124.3|m485.6,178.9c471.3,169,465.1"
    ",149.8,466.2,118.8c467,96.7,468.4,90.6,475.2,79.8c491,54.7,520.2,53.3,535.6,76.8c543.2,88.4,543.5,89.8,538.8,92.3c535.4,94.1,531.5,91.8,527.3,85.3c522.7,78.4,517.7,75.6,509.6,75.6c488,75.6,476.6,92.8,"
    "476.6,125.3c476.6,143.7,482.1,157.3,493.1,166c503.3,174,509.6,173.9,523.4,165.5c532.7,159.8,534.4,156.9,534.4,146.6c534.4,135,533.9,134.5,522,134.5c512.9,134.5,509.6,132.8,509.6,128.2c509.6,123.2,513."
    "5,121.8,527.7,121.8l545.7,121.8l544.9,143.5c544.2,161.4,542.8,166.6,536.5,173.7c526.7,184.9,498.4,187.7,485.6,178.9|m741.8,178c715.8,158.4,714.8,93.8,740,68.6c750.2,58.4,775.9,58.4,786.1,68.6c803.8,86"
    ".3,809.5,123.9,799,155.1c789.8,182.6,762.5,193.5,741.8,178|m779,163.8c804.6,140,794.6,76,765.3,75.7c744.6,75.5,732.8,93.1,732.8,124c732.8,143.6,736.6,154,747.4,164.1c758.6,174.5,767.6,174.4,779,163.8"
)
