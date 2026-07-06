# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur FLASH QUINES ALLONGÉ (format A4)
9 cartes (bandes allongées) par feuille A4, empilées.
Chaque carte : 9 numéros (un par dizaine 1-9, 10-19, …, 80-90), disposés en ZIGZAG
(haut/bas alternés) dans des ronds, reliés par des croix X. N° de série à droite.
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris 40%.
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
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GRIS_CLAIR = colors.Color(0.78, 0.78, 0.78)



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
DECADES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 49),
           (50, 59), (60, 69), (70, 79), (80, 90)]

CARTES_PAGE = 9
MARGIN_X = 6 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 6 * mm
GUTTER_Y = 2 * mm

CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (CARTES_PAGE - 1) * GUTTER_Y) / CARTES_PAGE


def _gen_carte(rng):
    """Un numéro par dizaine (9 numéros triés croissants)."""
    return [rng.randint(a, b) for (a, b) in DECADES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, libelle_gauche="", titre_jeu="", telephone="", style="eco"):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # ---- En-tête (titre centré seulement) ----
    htxt_y = y0 + CARD_H - 4.3 * mm
    centre = (titre_jeu or "FLASH QUINES ALLONGÉ")
    if telephone:
        centre += "   " + telephone
    c.setFillColor(col); c.setFont(POLICE, 6.5)
    c.drawCentredString(x0 + CARD_W / 2, htxt_y, centre[:48])

    # ---- Zone des numéros ----
    zone_top = htxt_y - 3 * mm
    zone_bot = y0 + 2 * mm
    cymid = (zone_top + zone_bot) / 2
    y_haut = cymid + 2.3 * mm
    y_bas = cymid - 2.3 * mm

    gauche = x0 + 9 * mm
    droite = x0 + CARD_W - 11 * mm
    pas = (droite - gauche) / 8.0
    xs = [gauche + i * pas for i in range(9)]
    ys = [y_haut if i % 2 == 0 else y_bas for i in range(9)]
    r = 7.4 * mm

    # Ronds + gros numéros
    for i in range(9):
        c.setStrokeColor(col); c.setLineWidth(0.9)
        c.circle(xs[i], ys[i], r, stroke=1, fill=0)
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, nums[i], xs[i], ys[i] - 11, 32, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, 32)
            c.drawCentredString(xs[i], ys[i] - 11, str(nums[i]))

    # Boîte série (bas droite)
    bw2, bh2 = 14 * mm, 4.6 * mm
    bx = x0 + CARD_W - bw2 - 1.5 * mm
    by = y0 + 1.2 * mm
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.roundRect(bx, by, bw2, bh2, 0.8 * mm, stroke=1, fill=0)
    c.setFillColor(GRIS); c.setFont(POLICE, 6.5)
    c.drawCentredString(bx + bw2 / 2, by + 1.4 * mm, "%06d" % serie)


def generer_pdf(nb_cartes=9, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco"):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + CARTES_PAGE - 1) // CARTES_PAGE

    rng = random.Random(900000 + int(serie_start))
    serie = int(serie_start)
    faites = 0
    no_page = 1
    libelle_gauche = nom_evenement or date_lieu

    for _ in range(nb_pages):
        # petit numéro de page en haut
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 4.5 * mm, "%03d" % no_page)
        for row in range(CARTES_PAGE):
            if faites >= nb_cartes:
                break
            y0 = MARGIN_BOT + (CARTES_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
            x0 = MARGIN_X
            nums = _gen_carte(rng)
            coul = (couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
            _dessiner_carte(c, x0, y0, nums, coul, serie, libelle_gauche, titre_jeu, telephone, style=style)
            serie += 1
            faites += 1
        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=9, couleur=True,
                      nom_evenement="PAPEETE", titre_jeu="FLASH QUINES ALLONGÉ",
                      date_lieu="", telephone="89 22 23 05")
    with open("test_flash_quines.pdf", "wb") as f:
        f.write(pdf.read())
    print("FLASH QUINES ALLONGÉ généré")
