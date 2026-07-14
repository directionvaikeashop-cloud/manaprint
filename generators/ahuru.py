# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur AHURU (format A4)
10 grilles par feuille A4 (2 colonnes × 5 rangées) — à la demande de Maeva
(le modèle historique en avait 15, on aère pour de plus grosses cartes).
Chaque carte : grille 4 colonnes × 5 rangées — 17 numéros triés par colonne :
  col 1 = 1-15 (×5) · col 2 = 31-45 (×5) · col 3 = 46-60 (×2, rangées 1 et 5)
  col 4 = 61-75 (×5)          — le 16-30 n'existe pas (caller informé) !
Le CŒUR de la colonne 3 (3 cases fusionnées) porte la signature
« Le jeu AHURU by TUKEA + téléphone »… et le QR de vérification.
Pied de carte : « N° SÉRIE | 000001 ».
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
# (min, max, nombre) par colonne — AHURU saute le 16-30 !
COLONNES = [(1, 15, 5), (31, 45, 5), (46, 60, 2), (61, 75, 5)]

COLS_PAGE = 2
ROWS_PAGE = 5
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
PIED_H = 4.4 * mm


def _gen_carte(rng):
    """17 numéros : 5 par colonne (2 pour la col 46-60), triés vers le bas."""
    return [sorted(rng.sample(range(pmin, pmax + 1), n)) for pmin, pmax, n in COLONNES]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 4

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # Pied de carte : « N° SÉRIE | 000001 »
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0 + 1.5 * mm, y0 + PIED_H, x0 + CARD_W - 1.5 * mm, y0 + PIED_H)
    c.line(x0 + CARD_W * 0.42, y0 + 0.8 * mm, x0 + CARD_W * 0.42, y0 + PIED_H - 0.6 * mm)
    c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.2)
    c.drawCentredString(x0 + CARD_W * 0.21, y0 + 1.5 * mm, "N\u00b0 S\u00c9RIE")
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawCentredString(x0 + CARD_W * 0.71, y0 + 1.4 * mm, "%06d" % serie)

    # Grille 4×5 — traits complets SAUF le cœur de la colonne 3 (3 cases fusionnées)
    z_top = y0 + CARD_H - 1.5 * mm
    z_bot = y0 + PIED_H
    row_h = (z_top - z_bot) / 5
    c3g = x0 + 2 * cell_w      # bord gauche de la colonne 3
    c3d = x0 + 3 * cell_w      # bord droit
    c.setStrokeColor(col); c.setLineWidth(0.35)
    for i in range(1, 4):
        c.line(x0 + i * cell_w, z_bot, x0 + i * cell_w, z_top)
    for i in range(1, 5):
        yl = z_top - i * row_h
        if i in (2, 3):
            # ces deux traits s'interrompent sur le cœur fusionné de la col 3
            c.line(x0 + 1.5 * mm, yl, c3g, yl)
            c.line(c3d, yl, x0 + CARD_W - 1.5 * mm, yl)
        else:
            c.line(x0 + 1.5 * mm, yl, x0 + CARD_W - 1.5 * mm, yl)

    # Les 17 numéros triés (col 3 : rangées 1 et 5 seulement)
    taille = 26
    for ci, ((pmin, pmax, n), nums) in enumerate(zip(COLONNES, cols_nums)):
        cx = x0 + (ci + 0.5) * cell_w
        rangees = (0, 4) if n == 2 else range(5)
        for val, ri in zip(nums, rangees):
            cyc = z_top - (ri + 0.5) * row_h
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # Le CŒUR (3 cases fusionnées de la col 3) : signature + QR — le nom TOUJOURS visible
    coeur_cx = x0 + 2.5 * cell_w
    coeur_haut = z_top - 1 * row_h
    l1 = "Le jeu AHURU"
    if titre_jeu and "AHURU" not in titre_jeu.strip().upper():
        l1 = "AHURU \u00b7 " + titre_jeu.strip()[:16]
    c.setFillColor(col); c.setFont(POLICE, 4.6)
    c.drawCentredString(coeur_cx, coeur_haut - 2.6 * mm, l1[:26])
    c.setFont(POLICE, 4.2)
    c.drawCentredString(coeur_cx, coeur_haut - 6.0 * mm, ("by TUKEA " + telephone if telephone else "by TUKEA")[:26])
    if _sec and evenement_id:
        try:
            _q = min(cell_w - 4 * mm, 3 * row_h - 9.5 * mm, 12.5 * mm)
            _sec.carton_qr(c, coeur_cx - _q / 2,
                           z_top - 4 * row_h + (3 * row_h - 7.5 * mm - _q) / 2 + 1.0 * mm,
                           _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=10, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(932300 + int(serie_start))
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
    pdf = generer_pdf(nb_cartes=10, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_ahuru.pdf", "wb") as f:
        f.write(pdf.read())
    print("AHURU généré")
