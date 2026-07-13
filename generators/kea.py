# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur KEA (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : en-tête à 2 lignes (« KEA … » + « Carte N° 030001 ») puis
grille complète de TROIS rangées × 3 colonnes — 9 numéros par carte,
3 distincts par colonne, non triés (fidèle au modèle) :
  colonne 1 = 35-45,  colonne 2 = 46-56,  colonne 3 = 57-67
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
# (min, max) par colonne — KEA (mêmes plages que TEA)
PLAGES = [(35, 45), (46, 56), (57, 67)]

COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 8 * mm           # en-tête à 2 lignes
ZONE_QR_H = 15 * mm      # bande basse réservée au QR de vérification


def _gen_carte(rng):
    """9 numéros : 3 distincts par colonne, chacun dans sa plage, NON triés
    (fidèle au modèle : l'ordre vertical est libre)."""
    return [rng.sample(range(pmin, pmax + 1), 3) for pmin, pmax in PLAGES]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 3

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête à 2 lignes — le nom du jeu apparaît TOUJOURS (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    l1 = "KEA by TUKEA" + ((" " + telephone) if telephone else "")
    if titre_jeu and "KEA" not in titre_jeu.strip().upper():
        l1 = "KEA · " + titre_jeu.strip() + ((" " + telephone) if telephone else "")
    c.setFillColor(col); c.setFont(POLICE, 4.4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 3.0 * mm, l1[:64])
    c.setFont(POLICE, 5.5)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 6.8 * mm, "Carte N° %06d" % serie)

    # Zone des numéros : grille complète 3 rangées × 3 colonnes
    z_top = hdr_bas
    z_bot = y0 + ZONE_QR_H
    row_h = (z_top - z_bot) / 3
    # traits de la grille (fidèle au modèle : cases complètes)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    for i in (1, 2):
        c.line(x0 + i * cell_w, z_bot, x0 + i * cell_w, hdr_bas)
    for i in range(4):
        c.line(x0 + 1.5 * mm, z_top - i * row_h, x0 + CARD_W - 1.5 * mm, z_top - i * row_h)
    taille = 26
    for ci, nums in enumerate(cols_nums):
        cx = x0 + (ci + 0.5) * cell_w
        for ri, val in enumerate(nums):
            cyc = z_top - (ri + 0.5) * row_h
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # QR de vérification par carte (anti-duplication) — bande basse, centré
    if _sec and evenement_id:
        try:
            _q = 12.5 * mm
            _sec.carton_qr(c, x0 + (CARD_W - _q) / 2, y0 + 1.2 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(930700 + int(serie_start))
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
                      telephone="89.22.23.05")
    with open("test_kea.pdf", "wb") as f:
        f.write(pdf.read())
    print("KEA généré")
