# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur 40 BOULES (format A4)
12 cartes par feuille A4 (2 colonnes × 6 rangées). Le jeu « 8 boules » sur 40.
Chaque carte : 8 numéros en quinconce 2-1-2-1-2 dans 5 colonnes de huit :
  col 1 = 2 numéros empilés (1-8)
  col 2 = 1 GRAND numéro   (9-16)
  col 3 = 2 numéros empilés (17-24)
  col 4 = 1 GRAND numéro   (25-32)
  col 5 = 2 numéros empilés (33-40)
Grille à traits : séparateurs verticaux entre colonnes, trait horizontal
au milieu des colonnes empilées (fidèle au modèle).
En-tête : « Le jeu 40 boules · 8 boules by TUKEA » — pied : « N° SÉRIE | 030001 ».
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
# Les 5 colonnes du 40 BOULES : (min, max, nombre de numéros)
COLONNES = [(1, 8, 2), (9, 16, 1), (17, 24, 2), (25, 32, 1), (33, 40, 2)]

COLS_PAGE = 2
ROWS_PAGE = 6
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 2.8 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
ZONE_QR = 16 * mm        # bande de droite réservée au QR de vérification


def _gen_carte(rng):
    """8 numéros : [2, 1, 2, 1, 2] par colonne, chacun dans sa plage, empilés triés."""
    return [sorted(rng.sample(range(pmin, pmax + 1), n)) for pmin, pmax, n in COLONNES]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête — le nom du jeu apparaît TOUJOURS (fidèle au modèle)
    hdr_y = y0 + CARD_H - 3.4 * mm
    titre = "Le jeu 40 boules · 8 boules by TUKEA"
    if titre_jeu and "40 BOULES" not in titre_jeu.strip().upper():
        titre += " · " + titre_jeu.strip()
    if telephone:
        titre += " · " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.8)
    c.drawCentredString(x0 + (CARD_W - ZONE_QR) / 2, hdr_y, titre[:72])

    # Pied de carte : « N° SÉRIE | 030001 »
    PIED_H = 4.4 * mm
    zx = x0 + 1.5 * mm
    zw = CARD_W - 3 * mm - ZONE_QR
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(zx, y0 + PIED_H, zx + zw, y0 + PIED_H)
    c.line(zx + zw * 0.42, y0 + 0.8 * mm, zx + zw * 0.42, y0 + PIED_H - 0.6 * mm)
    c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.2)
    c.drawCentredString(zx + zw * 0.21, y0 + 1.5 * mm, "N\u00b0 S\u00c9RIE")
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawCentredString(zx + zw * 0.71, y0 + 1.4 * mm, "%06d" % serie)

    # Zone de jeu : 5 colonnes avec la grille à traits (fidèle au modèle)
    z_bot = y0 + PIED_H
    z_top = hdr_y - 2.4 * mm
    z_h = z_top - z_bot
    frac = [0.19, 0.21, 0.19, 0.21, 0.20]           # solitaires un peu plus larges
    xs, bords, cursor = [], [zx], zx
    for f in frac:
        xs.append(cursor + (zw * f) / 2)
        cursor += zw * f
        bords.append(cursor)

    # séparateurs verticaux entre les 5 colonnes
    c.setStrokeColor(col); c.setLineWidth(0.5)
    for b in bords[1:-1]:
        c.line(b, z_bot, b, z_top)

    for ci, ((pmin, pmax, n), nums) in enumerate(zip(COLONNES, cols_nums)):
        if n == 2:
            # trait horizontal au milieu de la colonne empilée
            c.setStrokeColor(col); c.setLineWidth(0.5)
            c.line(bords[ci], z_bot + z_h / 2, bords[ci + 1], z_bot + z_h / 2)
            for ri, val in enumerate(nums):
                cyc = z_top - (ri + 0.5) * (z_h / 2)
                if _sec:  # chiffres "billet de banque" remplis de microtexte
                    _sec.chiffre_micro(c, val, xs[ci], cyc - 22 * 0.36, 22, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch); c.setFont(police_ch, 22)
                    c.drawCentredString(xs[ci], cyc - 22 * 0.36, str(val))
        else:
            # le GRAND numéro solitaire, pleine hauteur
            cyc = z_bot + z_h / 2
            if _sec:
                _sec.chiffre_micro(c, nums[0], xs[ci], cyc - 30 * 0.36, 30, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, 30)
                c.drawCentredString(xs[ci], cyc - 30 * 0.36, str(nums[0]))

    # QR de vérification par carte (anti-duplication) — bande de droite
    if _sec and evenement_id:
        try:
            _q = 12.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - ZONE_QR + 1.2 * mm,
                           y0 + (CARD_H - _q) / 2 - 0.8 * mm, _q, evenement_id, serie)
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

    rng = random.Random(985000 + int(serie_start))
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
    with open("test_boules40.pdf", "wb") as f:
        f.write(pdf.read())
    print("40 BOULES généré")
