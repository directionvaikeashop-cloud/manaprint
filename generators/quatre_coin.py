# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur 4 COIN (jeu des 4 coins, format A4 portrait)
6 cartes par feuille (2 colonnes × 3 rangées).
Chaque carte : grille 5×5, en-tête "4 C O I N".
Les chiffres sont placés dans les 4 COINS (blocs 2×2) ; la croix centrale
(colonne du milieu + rangée du milieu) est vide ; une boule-logo au centre.
Colonnes (BINGO 75) : col0=1-15, col1=16-30, col2=31-45 (VIDE), col3=46-60, col4=61-75.
16 chiffres par carte (4 par colonne active), tirés sans doublon, ordre aléatoire.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les cartons sortent normalement, simplement sans microtexte.
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
try:
    pdfmetrics.registerFont(TTFont("DJB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    POLICE_NUM = "DJB"
except Exception:
    POLICE_NUM = "Helvetica-Bold"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GRIS = colors.Color(0.60, 0.60, 0.60)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)



# ══ DEUX GAMMES COMMERCIALES (vision Maeva) ══════════════════════════
# ÉCO      : écriture fine DejaVu ExtraLight, gris 0,50 — économie de toner
# PREMIUM  : écriture grasse Helvetica-Bold, gris 0,55 — style P15
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
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4

LETTRES = ["4", "C", "O", "I", "N"]
# plages BINGO 75 par colonne (col2 = vide)
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
# colonnes actives (avec chiffres) = toutes sauf celle du milieu
COLS_ACTIVES = [0, 1, 3, 4]
# rangées remplies (toutes sauf celle du milieu)
ROWS_ACTIVES = [0, 1, 3, 4]

COLS_PAGE = 2
ROWS_PAGE = 3
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 6 * mm
GUTTER_Y = 6 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """Grille 5×5 : 4 chiffres par colonne active (rangées 0,1,3,4), sans doublon."""
    carte = [[None] * 5 for _ in range(5)]
    for c in COLS_ACTIVES:
        a, b = PLAGES[c]
        nums = rng.sample(range(a, b + 1), 4)   # 4 distincts, ordre aléatoire
        for k, r in enumerate(ROWS_ACTIVES):
            carte[r][c] = nums[k]
    return carte


def _boule(c, cx, cy, r, telephone):
    """Boule-logo BLANCHE (économie de toner) : contour léger + TK création + téléphone."""
    # cercle blanc, simple contour fin
    c.setFillColor(colors.white)
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.6)
    c.circle(cx, cy, r, stroke=1, fill=1)
    # textes en gris 40% (écriture fine DJL)
    c.setFillColor(GRIS40)
    c.setFont(POLICE, 5.4)
    c.drawCentredString(cx, cy + r * 0.30, "TK création")
    c.setFont(POLICE, 5.8)
    tel = (telephone or "89 22 23 05").replace(" ", "")
    c.drawCentredString(cx, cy - r * 0.50, tel)


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # bordure carte
    c.setStrokeColor(col); c.setLineWidth(1.0)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # en-tête 4 C O I N
    head_h = 9 * mm
    grid_top = y0 + CARD_H - head_h
    grid_bot = y0 + 3 * mm
    gx0 = x0 + 2.5 * mm
    grid_w = CARD_W - 5 * mm
    cell_w = grid_w / 5
    grid_h = grid_top - grid_bot
    cell_h = grid_h / 5

    # lettres d'en-tête (écriture fine DJL)
    for i, L in enumerate(LETTRES):
        cx = gx0 + (i + 0.5) * cell_w
        c.setFillColor(col); c.setFont(POLICE, 19)
        c.drawCentredString(cx, grid_top + 2.2 * mm, L)

    # grille 5×5
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.5)
    for i in range(6):
        c.line(gx0 + i * cell_w, grid_bot, gx0 + i * cell_w, grid_top)
    for j in range(6):
        yy = grid_bot + j * cell_h
        c.line(gx0, yy, gx0 + 5 * cell_w, yy)

    # numéros (écriture fine DJL, comme BROWN 8, gris 40%)
    c.setFont(POLICE, 32)
    for r in range(5):
        for cc in range(5):
            v = carte[r][cc]
            if v is not None:
                cx = gx0 + (cc + 0.5) * cell_w
                cyc = grid_top - (r + 0.5) * cell_h
                if _sec:  # chiffres "billet de banque" remplis de microtexte
                    _sec.chiffre_micro(c, v, cx, cyc - 11, 32, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch)
                    c.setFont(police_ch, 32)
                    c.drawCentredString(cx, cyc - 11, str(v))

    # boule-logo au centre
    cx_c = gx0 + 2.5 * cell_w
    cy_c = grid_top - 2.5 * cell_h
    rayon = min(cell_w, cell_h) * 0.46
    _boule(c, cx_c, cy_c, rayon, telephone)

    # série en bas
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawRightString(x0 + CARD_W - 2.5 * mm, y0 + 0.8 * mm, "%06d" % serie)

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            _q = 8.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 1.5 * mm, y0 + 1.5 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 20000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random()   # graine fraîche : cartes uniques à chaque génération
    serie = int(serie_start)
    no_page = 1
    faites = 0

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 9)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, carte, coul, serie, telephone, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True, nom_evenement="ASSOCIATION TE MANU",
                      titre_jeu="4 COIN", telephone="89 22 23 05")
    with open("test_4coin.pdf", "wb") as f:
        f.write(pdf.read())
    print("4 COIN généré")
