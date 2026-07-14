# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TAHAA (format A4 PAYSAGE)
18 cartes-bandeaux par feuille A4 paysage (3 colonnes × 6 rangées).
Chaque carte : 5 numéros dans des CERCLES (fidèle au modèle) :
  rangée haute : 1-15 (gauche) · 31-45 (centre) · 61-75 (droite)
  rangée basse :      16-30 (centre-gauche) · 46-60 (centre-droit)
Ligne signature au centre : « TAHAA pour 5 boules by TUKEA … » (fidèle au modèle).
QR de vérification dans le coin bas-droit. Série discrète en bas à gauche.
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris (2 gammes ÉCO/PREMIUM).
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
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

PAGE_W, PAGE_H = landscape(A4)
# Les 5 boules de TAHAA : (plage, position) — haut: coins + centre, bas: centre-gauche/droit
BOULES = [
    ((1, 15),  0.11, 0.72),   # haut-gauche
    ((31, 45), 0.50, 0.72),   # haut-centre
    ((61, 75), 0.89, 0.72),   # haut-droit
    ((16, 30), 0.31, 0.26),   # bas centre-gauche
    ((46, 60), 0.69, 0.26),   # bas centre-droit
]

COLS_PAGE = 3
ROWS_PAGE = 6
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 7 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """5 numéros : un par plage TAHAA."""
    return [rng.randint(pmin, pmax) for (pmin, pmax), _, _ in BOULES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.8 * mm)

    # Les 5 boules cerclées (fidèle au modèle)
    rayon = 5.4 * mm  # cercles élargis avec les chiffres
    taille = 24  # AU MAX dans les cercles (Maeva)
    for val, fx, fy in [(v, fx, fy) for v, ((a, b), fx, fy) in zip(nums, BOULES)]:
        cx = x0 + CARD_W * fx
        cy = y0 + CARD_H * fy
        c.setStrokeColor(col); c.setLineWidth(0.8)
        c.circle(cx, cy, rayon, stroke=1, fill=0)
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, val, cx, cy - taille * 0.36, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(cx, cy - taille * 0.36, str(val))

    # Ligne signature au CENTRE — le nom du jeu apparaît TOUJOURS (fidèle au modèle)
    signature = "TAHAA pour 5 boules by TUKEA"
    if titre_jeu and "TAHAA" not in titre_jeu.strip().upper():
        signature = "TAHAA \u00b7 " + titre_jeu.strip() + " by TUKEA"
    if telephone:
        signature += " " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.2)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H * 0.48, signature[:66])

    # Série discrète en bas à gauche
    c.setFillColor(col); c.setFont(POLICE, 4.6)
    c.drawString(x0 + 2.2 * mm, y0 + 1.6 * mm, "N\u00b0 %06d" % serie)

    # QR de vérification par carte (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            _q = min(CARD_H * 0.40, 11.5 * mm)
            _sec.carton_qr(c, x0 + CARD_W - _q - 1.8 * mm,
                           y0 + 1.5 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=18, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(931800 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 8)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 6.4 * mm, "%03d" % no_page)

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
    pdf = generer_pdf(nb_cartes=18, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="87 04 32 21")
    with open("test_tahaa.pdf", "wb") as f:
        f.write(pdf.read())
    print("TAHAA généré")
