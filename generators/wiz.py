# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur WIZ 4 BOULES (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : 4 numéros en losange —
  haut   : 1 numéro (16-30), centré
  milieu : 2 numéros — gauche (1-15) | droite (31-45), séparés d'un trait vertical
  bas    : 1 numéro (16-30), centré  (jamais le même que celui du haut)
En-tête « Le jeux WIZ pour 4 boules by TUKEA … », série en pied (fidèle au modèle).
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
# Les 3 plages du WIZ 4 boules
PLAGE_HAUT_BAS = (16, 30)   # haut ET bas (2 numéros distincts)
PLAGE_GAUCHE = (1, 15)
PLAGE_DROITE = (31, 45)

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
    """4 numéros : haut (16-30), gauche (1-15), droite (31-45), bas (16-30 ≠ haut)."""
    haut, bas = rng.sample(range(PLAGE_HAUT_BAS[0], PLAGE_HAUT_BAS[1] + 1), 2)
    gauche = rng.randint(*PLAGE_GAUCHE)
    droite = rng.randint(*PLAGE_DROITE)
    return haut, gauche, droite, bas


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    haut, gauche, droite, bas = nums
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête (fidèle au modèle) — le nom du jeu apparaît TOUJOURS
    hdr_y = y0 + CARD_H - 3.0 * mm
    if titre_jeu and titre_jeu.strip() and "WIZ" not in titre_jeu.strip().upper():
        titre = "WIZ 4 boules  —  " + titre_jeu.strip()
    elif titre_jeu and titre_jeu.strip():
        titre = titre_jeu.strip()
    else:
        titre = "Le jeux WIZ pour 4 boules"
    if telephone:
        titre += " by TUKEA " + telephone
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y, titre[:56])

    # Trois zones : haut / milieu / bas (traits fins, fidèles au modèle)
    zone_top = y0 + CARD_H - 5.5 * mm
    zone_bot = y0 + 5.5 * mm
    zone_h = zone_top - zone_bot
    row_h = zone_h / 3

    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
    for r in (1, 2):
        yy = zone_top - r * row_h
        c.line(x0 + 1.5 * mm, yy, x0 + CARD_W - 1.5 * mm, yy)
    # trait vertical entre les 2 numéros du milieu
    c.line(x0 + CARD_W / 2, zone_top - 1.7 * row_h, x0 + CARD_W / 2, zone_top - 1.3 * row_h)

    # Les 4 numéros — gros chiffres bien visibles
    taille = 40
    positions = [
        (haut,   x0 + CARD_W / 2,    zone_top - 0.5 * row_h),
        (gauche, x0 + CARD_W * 0.25, zone_top - 1.5 * row_h),
        (droite, x0 + CARD_W * 0.75, zone_top - 1.5 * row_h),
        (bas,    x0 + CARD_W / 2,    zone_top - 2.5 * row_h),
    ]
    for val, px, py in positions:
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, val, px, py - taille * 0.36, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(px, py - taille * 0.36, str(val))

    # QR de vérification par carte (anti-duplication) — coin bas-gauche libre
    if _sec and evenement_id:
        try:
            _q = 13.0 * mm
            _sec.carton_qr(c, x0 + 2.0 * mm, y0 + 6.0 * mm, _q, evenement_id, serie)
        except Exception:
            pass

    # Pied : série centrée (fidèle au modèle « 0001 »)
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawCentredString(x0 + CARD_W / 2, y0 + 1.6 * mm, "%04d" % serie if serie < 10000 else "%06d" % serie)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random()   # graine fraîche : cartes uniques à chaque génération
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
                _dessiner_carte(c, x0, y0, nums, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="",
                      telephone="89 22 23 05")
    with open("test_wiz.pdf", "wb") as f:
        f.write(pdf.read())
    print("WIZ 4 boules généré")
