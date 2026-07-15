# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur LETTRE U (format A4)
6 cartes par feuille A4 (2 colonnes × 3 rangées).
Chaque carte : 13 numéros disposés en GRAND U (fidèle au modèle) :
  · bras GAUCHE : 5 numéros 1-15, triés vers le bas (4 cases + le coin)
  · PLANCHER : 3 numéros — un en 16-30, un en 31-45, un en 46-60
  · bras DROIT : 5 numéros 61-75, triés vers le bas (4 cases + le coin)
Au centre : le PERSONNAGE U aux grands yeux rigolos (dessiné main),
le QR de vérification et la série. Chaque numéro dans sa case.
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
PLAGE_GAUCHE = (1, 15)     # 5 numéros (bras gauche + coin)
PLANCHER = [(16, 30), (31, 45), (46, 60)]   # 1 numéro chacun
PLAGE_DROITE = (61, 75)    # 5 numéros (coin + bras droit)

COLS_PAGE = 2
ROWS_PAGE = 3
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
BAS_H = 15 * mm            # la rangée du plancher du U


def _gen_carte(rng):
    """13 numéros : 5 à gauche (1-15), 3 au plancher, 5 à droite (61-75), triés."""
    gauche = sorted(rng.sample(range(PLAGE_GAUCHE[0], PLAGE_GAUCHE[1] + 1), 5))
    plancher = [rng.randint(pmin, pmax) for pmin, pmax in PLANCHER]
    droite = sorted(rng.sample(range(PLAGE_DROITE[0], PLAGE_DROITE[1] + 1), 5))
    return gauche, plancher, droite


def _personnage_u(c, cx, cy, h, col):
    """Le personnage U aux grands yeux rigolos (fidèle au modèle)."""
    w = h * 0.72
    ep = h * 0.16          # l'épaisseur du corps du U
    c.saveState()
    c.setStrokeColor(col); c.setLineWidth(1.1)
    # le corps : contour extérieur puis intérieur (un U dodu)
    p = c.beginPath()
    p.moveTo(cx - w / 2, cy + h / 2)
    p.lineTo(cx - w / 2, cy - h / 2 + w / 2)
    p.arcTo(cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + w, startAng=180, extent=180)
    p.lineTo(cx + w / 2, cy + h / 2)
    p.lineTo(cx + w / 2 - ep, cy + h / 2)
    p.lineTo(cx + w / 2 - ep, cy - h / 2 + w / 2)
    p.arcTo(cx - w / 2 + ep, cy - h / 2 + ep, cx + w / 2 - ep, cy - h / 2 + w - ep,
            startAng=0, extent=-180)
    p.lineTo(cx - w / 2 + ep, cy + h / 2)
    p.close()
    c.drawPath(p, stroke=1, fill=0)
    # les grands yeux rigolos au sommet des bras
    for dx in (-w / 2 + ep / 2, w / 2 - ep / 2):
        ex, ey = cx + dx, cy + h / 2 + h * 0.05
        c.setFillColor(colors.white); c.setStrokeColor(col); c.setLineWidth(0.9)
        c.circle(ex, ey, h * 0.13, stroke=1, fill=1)
        c.setFillColor(col)
        c.circle(ex + h * 0.03, ey + h * 0.03, h * 0.05, stroke=0, fill=1)
    c.restoreState()


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    gauche, plancher, droite = nums

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    cell_w = CARD_W / 5
    bras_h = (CARD_H - BAS_H) / 4
    taille = 30

    def case(cx_case, cy_case, cw, ch, val):
        c.setStrokeColor(col); c.setLineWidth(0.4)
        c.rect(cx_case, cy_case, cw, ch, stroke=1, fill=0)
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, val, cx_case + cw / 2, cy_case + ch / 2 - taille * 0.36,
                               taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(cx_case + cw / 2, cy_case + ch / 2 - taille * 0.36, str(val))

    # Bras gauche (4 cases) — triés vers le bas
    for ri in range(4):
        case(x0, y0 + CARD_H - (ri + 1) * bras_h, cell_w, bras_h, gauche[ri])
    # Bras droit (4 cases) — triés vers le bas
    for ri in range(4):
        case(x0 + 4 * cell_w, y0 + CARD_H - (ri + 1) * bras_h, cell_w, bras_h, droite[ri])
    # Le plancher : coin gauche + 3 du milieu + coin droit
    bas = [gauche[4]] + plancher + [droite[4]]
    for i, val in enumerate(bas):
        case(x0 + i * cell_w, y0, cell_w, BAS_H, val)

    # L'étage central, de haut en bas : le personnage U 😃, la signature,
    # la série, puis le QR — chacun chez soi, sans se marcher dessus
    centre_x = x0 + CARD_W / 2
    _personnage_u(c, centre_x, y0 + BAS_H + 44 * mm, 24 * mm, col)

    signature = "LETTRE U by TUKEA"
    if titre_jeu and titre_jeu.strip().upper() not in ("LETTRE U", "U"):
        signature += " \u00b7 " + titre_jeu.strip()
    if telephone:
        signature += " \u00b7 " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.4)
    c.drawCentredString(centre_x, y0 + BAS_H + 26.5 * mm, signature[:52])
    c.setFont(POLICE, 5)
    c.drawCentredString(centre_x, y0 + BAS_H + 22.5 * mm, "N\u00b0 %06d" % serie)

    # QR de vérification par carte — en bas de l'étage central
    if _sec and evenement_id:
        try:
            _q = 12.0 * mm
            _sec.carton_qr(c, centre_x - _q / 2, y0 + BAS_H + 5.5 * mm,
                           _q, evenement_id, serie)
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

    rng = random.Random(934600 + int(serie_start))
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
    pdf = generer_pdf(nb_cartes=6, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_lettre_u.pdf", "wb") as f:
        f.write(pdf.read())
    print("LETTRE U généré")
