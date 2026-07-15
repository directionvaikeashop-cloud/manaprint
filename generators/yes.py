# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur YES (format A4)
15 cartes par feuille A4 (3 colonnes × 5 rangées), bordure FINE
(économie d'encre, décision Maeva — comme les autres jeux du catalogue).
Chaque carte : 6 boules en DEUX LIGNES de 3 numéros :
  position 1 = 1-30  ·  position 2 = 31-60  ·  position 3 = 61-90
(un numéro de chaque famille par ligne, distincts sur la carte — tirage 1-90 !)
En-tête ÉPURÉ, décision Maeva : UNIQUEMENT « Le jeu YES by TUKEA 89 22 23 05 »
(le nom TOUJOURS visible). N° de série discret + QR de vérification au centre.
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
FAMILLES = [(1, 30), (31, 60), (61, 90)]   # une par position, ×2 lignes

COLS_PAGE = 3
ROWS_PAGE = 5
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """6 numéros : par famille, 2 distincts (un par ligne), ordre libre."""
    haut, bas = [], []
    for pmin, pmax in FAMILLES:
        a, b = rng.sample(range(pmin, pmax + 1), 2)
        haut.append(a); bas.append(b)
    return haut, bas


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    haut, bas = nums

    # Bordure FINE (économie d'encre, décision Maeva)
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    ix0 = x0 + 1.5 * mm
    iw = CARD_W - 3 * mm
    ih = CARD_H - 3 * mm
    iy0 = y0 + 1.5 * mm

    # Les deux lignes de 3 numéros
    taille = 34
    for vals, fy in ((haut, 0.78), (bas, 0.22)):
        for val, fx in zip(vals, (0.18, 0.50, 0.82)):
            cx = ix0 + iw * fx
            cy = iy0 + ih * fy
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cy - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cy - taille * 0.36, str(val))

    # L'étage du milieu ÉPURÉ (décision Maeva) : le nom seul + série + QR à droite
    l1 = "Le jeu YES by TUKEA"
    if titre_jeu and "YES" not in titre_jeu.strip().upper():
        l1 = "Le jeu YES \u00b7 " + titre_jeu.strip() + " by TUKEA"
    if telephone:
        l1 += " " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.6)
    c.drawCentredString(ix0 + iw * 0.42, iy0 + ih * 0.545, l1[:46])
    c.setFont(POLICE, 4.4)
    c.drawCentredString(ix0 + iw * 0.42, iy0 + ih * 0.435, "N\u00b0 %06d" % serie)

    # QR de vérification par carte (anti-duplication) — au milieu, à droite
    if _sec and evenement_id:
        try:
            _q = 9.5 * mm
            _sec.carton_qr(c, ix0 + iw * 0.83 - _q / 2, iy0 + ih * 0.5 - _q / 2, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=15, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(935800 + int(serie_start))
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
                nums = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, nums, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=15, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_yes.pdf", "wb") as f:
        f.write(pdf.read())
    print("YES généré")
