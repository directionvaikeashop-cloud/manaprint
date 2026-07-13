# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur MOON (format A4)
6 cartes par feuille A4 (2 colonnes × 3 rangées).
Chaque carte : en-tête M | O | O | N puis grille 4×4 en DAMIER (escalier) :
  rangées 1 et 3 -> colonnes M et O(2)   ·   rangées 2 et 4 -> colonnes O(1) et N
8 numéros par carte, 2 par colonne (triés vers le bas) :
  M = 1-15,  O = 16-30,  O = 46-60,  N = 61-75   (le 31-45 n'existe pas !)
Un CROISSANT DE LUNE en filigrane dans la case vide d'honneur (fidèle au modèle),
et le QR de vérification logé dans une case vide du bas. Pied : « 015001 ».
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris (2 gammes ÉCO/PREMIUM).
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

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GRIS = colors.Color(0.42, 0.42, 0.42)
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
LETTRES = ["M", "O", "O", "N"]
# (min, max) par colonne — MOON saute le 31-45 !
PLAGES = [(1, 15), (16, 30), (46, 60), (61, 75)]
# rangées occupées par colonne (le damier) : M et O(2) -> rangées 0 et 2 ;
# O(1) et N -> rangées 1 et 3
RANGEES = [(0, 2), (1, 3), (0, 2), (1, 3)]

COLS_PAGE = 2
ROWS_PAGE = 3
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 7 * mm
PIED_H = 5 * mm


def _gen_carte(rng):
    """8 numéros : 2 distincts par colonne, triés vers le bas."""
    return [sorted(rng.sample(range(pmin, pmax + 1), 2)) for pmin, pmax in PLAGES]


def _croissant(c, cx, cy, r, teinte):
    """Le croissant de lune en filigrane (fidèle au modèle)."""
    c.saveState()
    c.setFillColor(teinte)
    c.circle(cx, cy, r, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.circle(cx + r * 0.42, cy + r * 0.18, r * 0.88, stroke=0, fill=1)
    c.restoreState()


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 4

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête M | O | O | N (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.45)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    c.setFillColor(col); c.setFont(POLICE, 8)
    for i, lettre in enumerate(LETTRES):
        c.drawCentredString(x0 + (i + 0.5) * cell_w, hdr_bas + 2.0 * mm, lettre)

    # Grille 4×4 (traits complets, fidèle au modèle)
    z_top = hdr_bas
    z_bot = y0 + PIED_H
    row_h = (z_top - z_bot) / 4
    c.setStrokeColor(col); c.setLineWidth(0.35)
    for i in range(1, 4):
        c.line(x0 + i * cell_w, z_bot, x0 + i * cell_w, y0 + CARD_H)
        c.line(x0, z_top - i * row_h, x0 + CARD_W, z_top - i * row_h)
    c.line(x0, z_bot, x0 + CARD_W, z_bot)

    # Le croissant de lune en filigrane — case d'honneur (rangée 1, 2e colonne)
    _croissant(c, x0 + 1.5 * cell_w, z_top - 0.5 * row_h,
               min(cell_w, row_h) * 0.34, colors.Color(0.90, 0.90, 0.93))

    # Les 8 numéros en damier
    taille = 40  # gros chiffres au maximum
    for ci, (nums, rangs) in enumerate(zip(cols_nums, RANGEES)):
        cx = x0 + (ci + 0.5) * cell_w
        for val, ri in zip(nums, rangs):
            cyc = z_top - (ri + 0.5) * row_h
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # Pied de carte : signature + série (le nom du jeu apparaît TOUJOURS)
    signature = "MOON by TUKEA"
    if titre_jeu and titre_jeu.strip().upper() != "MOON":
        signature += " · " + titre_jeu.strip()
    if telephone:
        signature += " · " + telephone
    c.setFillColor(col); c.setFont(POLICE, 3.9)
    c.drawString(x0 + 2.5 * mm, y0 + 1.7 * mm, signature[:56])
    c.setFont(POLICE, 6.5)
    c.drawCentredString(x0 + CARD_W / 2, y0 + 1.5 * mm, "%06d" % serie)

    # QR de vérification par carte — logé dans la case vide du bas (rangée 4, 1re colonne)
    if _sec and evenement_id:
        try:
            _q = min(row_h - 2.5 * mm, cell_w - 3 * mm, 13.5 * mm)
            _sec.carton_qr(c, x0 + (cell_w - _q) / 2,
                           z_bot + (row_h - _q) / 2, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(915000 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page
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
                cols_nums = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, cols_nums, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_moon.pdf", "wb") as f:
        f.write(pdf.read())
    print("MOON généré")
