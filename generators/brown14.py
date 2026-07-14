# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur BROWN 14 BOULES (format A4)
8 cartes par feuille A4 (2 colonnes × 4 rangées).
Chaque carte : en-tête B | R | O | W | N puis grille 5×3 — 14 numéros triés
par colonne (fidèle au modèle) :
  B = 1-15 (×3), R = 16-30 (×3), O = 31-45 (×2), W = 46-60 (×3), N = 61-75 (×3)
La case O de la 1re rangée accueille le NUMÉRO DE SÉRIE en filigrane
(la signature du modèle !). QR de vérification dans la bande basse.
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
LETTRES = "BROWN"
# (min, max, nombre) par lettre — la colonne O n'a que 2 numéros
# (sa case du haut accueille le numéro de série en filigrane)
COLONNES = [(1, 15, 3), (16, 30, 3), (31, 45, 2), (46, 60, 3), (61, 75, 3)]

COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 6 * mm
ZONE_QR_H = 15 * mm      # bande basse : signature + QR de vérification


def _gen_carte(rng):
    """14 numéros : 3 par lettre (2 pour O), triés vers le bas."""
    return [sorted(rng.sample(range(pmin, pmax + 1), n)) for pmin, pmax, n in COLONNES]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 5

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête B | R | O | W | N (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.45)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    c.setFillColor(col); c.setFont(POLICE, 7)
    for i, lettre in enumerate(LETTRES):
        c.drawCentredString(x0 + (i + 0.5) * cell_w, hdr_bas + 1.7 * mm, lettre)

    # Grille 5×3 (traits complets, fidèle au modèle)
    z_top = hdr_bas
    z_bot = y0 + ZONE_QR_H
    row_h = (z_top - z_bot) / 3
    c.setStrokeColor(col); c.setLineWidth(0.35)
    for i in range(1, 5):
        c.line(x0 + i * cell_w, z_bot, x0 + i * cell_w, y0 + CARD_H)
    for i in range(1, 3):
        c.line(x0, z_top - i * row_h, x0 + CARD_W, z_top - i * row_h)
    c.line(x0, z_bot, x0 + CARD_W, z_bot)

    # Le NUMÉRO DE SÉRIE en filigrane — case O, 1re rangée (la signature du modèle)
    c.setFillColor(colors.Color(0.86, 0.83, 0.78))
    c.setFont(POLICE, 7)
    c.drawCentredString(x0 + 2.5 * cell_w, z_top - 0.5 * row_h - 2.4, "%06d" % serie)

    # Les 14 numéros triés (la colonne O commence à la 2e rangée)
    taille = 36  # LE MAX physique : 2 chiffres = 45.7pt dans des cases de 53.6pt
    for ci, ((pmin, pmax, n), nums) in enumerate(zip(COLONNES, cols_nums)):
        cx = x0 + (ci + 0.5) * cell_w
        premiere = 3 - n  # O (n=2) commence rangée 1 ; les autres rangée 0
        for ri, val in enumerate(nums):
            cyc = z_top - (premiere + ri + 0.5) * row_h
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # Bande basse : signature (le nom du jeu apparaît TOUJOURS) + QR
    signature = "BROWN 14 boules by TUKEA"
    if titre_jeu and "BROWN" not in titre_jeu.strip().upper():
        signature += " · " + titre_jeu.strip()
    if telephone:
        signature += " · " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.2)
    c.drawString(x0 + 3 * mm, y0 + 2.0 * mm, signature[:64])

    # QR de vérification par carte (anti-duplication) — bande basse, à droite
    if _sec and evenement_id:
        try:
            _q = 12.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.5 * mm,
                           y0 + (ZONE_QR_H - _q) / 2, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(931400 + int(serie_start))
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
    pdf = generer_pdf(nb_cartes=8, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_brown14.pdf", "wb") as f:
        f.write(pdf.read())
    print("BROWN 14 boules généré")
