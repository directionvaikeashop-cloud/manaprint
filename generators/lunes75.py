# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur LUNES 75 (format A4)
12 cartes hautes par feuille A4 (4 colonnes × 3 rangées).
Chaque carte : bandeau « LUNES 75 · 8 BOULES », puis DEUX colonnes triées :
  gauche = 1-30 (×4)   ·   droite = 46-75 (×4)
Le 31-45 n'existe pas (la cousine de MOON — caller informé) !
8 boules au lieu des 10 du modèle historique (décision Maeva) : le CREUX
libéré en bas accueille le QR de vérification — la modernisation TUKEA.
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
# Les 2 colonnes de LUNES 75 — le 31-45 n'existe pas !
PLAGES = [(1, 30), (46, 75)]
NB_PAR_COL = 4   # 8 boules (décision Maeva) — le creux libéré porte le QR

COLS_PAGE = 4
ROWS_PAGE = 3
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 6 * mm
CREUX_H = 15 * mm        # le creux : la 5e case de la grille — QR + série


def _gen_carte(rng):
    """8 numéros : 4 distincts par colonne, triés vers le bas."""
    return [sorted(rng.sample(range(pmin, pmax + 1), NB_PAR_COL)) for pmin, pmax in PLAGES]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.8 * mm)

    # Bandeau — le nom du jeu apparaît TOUJOURS (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    bandeau = "LUNES 75 \u00b7 8 BOULES"
    if titre_jeu and "LUNES" not in titre_jeu.strip().upper():
        bandeau += " \u00b7 " + titre_jeu.strip().upper()[:14]
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawCentredString(x0 + CARD_W / 2, hdr_bas + 2.0 * mm, bandeau[:38])

    # Les 2 colonnes de 4 numéros + LE CREUX intégré DANS la grille (5e rangée)
    z_top = hdr_bas
    grid_bot = y0 + 2.2 * mm
    creux_top = grid_bot + CREUX_H
    row_h = (z_top - creux_top) / NB_PAR_COL
    cell_w = CARD_W / 2
    c.setStrokeColor(col); c.setLineWidth(0.35)
    c.line(x0 + cell_w, creux_top, x0 + cell_w, z_top)   # séparateur central (s'arrête au creux)
    for i in range(1, NB_PAR_COL):
        c.line(x0 + 1.5 * mm, z_top - i * row_h, x0 + CARD_W - 1.5 * mm, z_top - i * row_h)
    c.line(x0 + 1.5 * mm, creux_top, x0 + CARD_W - 1.5 * mm, creux_top)  # plafond du creux
    c.line(x0 + 1.5 * mm, grid_bot, x0 + CARD_W - 1.5 * mm, grid_bot)    # plancher de la grille

    taille = 32
    for ci, nums in enumerate(cols_nums):
        cx = x0 + (ci + 0.5) * cell_w
        for ri, val in enumerate(nums):
            cyc = z_top - (ri + 0.5) * row_h
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # LE CREUX : QR de vérification au centre + signature + série (décision Maeva)
    if _sec and evenement_id:
        try:
            _q = min(CREUX_H - 3.2 * mm, 12.5 * mm)
            _sec.carton_qr(c, x0 + (CARD_W - _q) / 2, y0 + 1.4 * mm, _q, evenement_id, serie)
        except Exception:
            pass
    signature = "by TUKEA"
    if telephone:
        signature += " " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.0)
    c.drawString(x0 + 1.8 * mm, y0 + 1.6 * mm, signature[:20])
    c.saveState()
    c.translate(x0 + CARD_W - 2.0 * mm, y0 + 2.0 * mm)
    c.rotate(90)
    c.setFont(POLICE, 4.6)
    c.drawString(0, 0, "N\u00b0 %06d" % serie)
    c.restoreState()


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(933100 + int(serie_start))
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
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_lunes75.pdf", "wb") as f:
        f.write(pdf.read())
    print("LUNES 75 généré")
