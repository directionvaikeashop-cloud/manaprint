# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur OHANA 90 · 24 BOULES (format A4)
6 bandeaux pleine largeur par feuille A4 (1 colonne × 6 rangées).
Chaque bandeau : série centrée en tête, puis DEUX LIGNES de 12 numéros
(24 boules !) — 2 par famille de quinze et par ligne, ordre LIBRE dans
chaque paire (fidèle au modèle), le 2e de chaque paire CERCLÉ (trait plein) :
  1-15 · 16-30 · 31-45 · 46-60 · 61-75 · 76-90
Les 4 numéros d'une même famille sont tous distincts sur la carte.
Signature « Ohana 90 pour 24 boules by TUKEA … » au pied (nom TOUJOURS visible).
QR de vérification au bout droit du bandeau.
Couleur arc-en-ciel (par bandeau) ou gris (N&B). Chiffres en gris (2 gammes ÉCO/PREMIUM).
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
# Les 6 familles de quinze — 2 numéros chacune = 12 boules
FAMILLES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 90)]

ROWS_PAGE = 6
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_Y = 2.8 * mm

CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 5 * mm
PIED_H = 3.6 * mm
ZONE_QR = 13 * mm        # bout droit du bandeau réservé au QR


def _gen_carte(rng):
    """2 lignes × 12 numéros : 4 distincts par famille (2 par ligne),
    ordre libre dans chaque paire (fidèle au modèle)."""
    l1, l2 = [], []
    for pmin, pmax in FAMILLES:
        quatre = rng.sample(range(pmin, pmax + 1), 4)
        p1, p2 = quatre[:2], quatre[2:]
        rng.shuffle(p1); rng.shuffle(p2)
        l1.extend(p1); l2.extend(p2)
    return l1, l2


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure bandeau
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.rect(x0, y0, CARD_W, CARD_H, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.8 * mm)

    # En-tête : la série centrée (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    c.setFillColor(col); c.setFont(POLICE, 7)
    c.drawCentredString(x0 + CARD_W / 2, hdr_bas + 1.3 * mm, "%06d" % serie)

    # Pied : signature — le nom du jeu apparaît TOUJOURS (fidèle au modèle)
    signature = "Ohana 90 pour 24 boules by TUKEA"
    if titre_jeu and "OHANA" not in titre_jeu.strip().upper():
        signature = "Ohana 90 \u00b7 24 boules \u00b7 " + titre_jeu.strip() + " by TUKEA"
    if telephone:
        signature += " " + telephone
    c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + 1.2 * mm, signature[:80])

    # Les DEUX lignes de 12 numéros — le 2e de chaque paire cerclé (trait plein)
    l1, l2 = nums
    zw = CARD_W - ZONE_QR
    cell_w = zw / 12
    z_top = hdr_bas
    z_bot = y0 + PIED_H
    row_h = (z_top - z_bot) / 2
    taille = 30  # LE MAX de la ligne de 12 (Maeva)
    rayon = min(cell_w * 0.47, row_h * 0.44)
    for ri, ligne in enumerate((l1, l2)):
        cy = z_top - (ri + 0.5) * row_h
        for i, val in enumerate(ligne):
            cx = x0 + (i + 0.5) * cell_w
            if i % 2 == 1:  # le 2e de la paire : cercle plein (fidèle au modèle)
                c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.55)
                c.circle(cx, cy, rayon, stroke=1, fill=0)
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cy - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cy - taille * 0.36, str(val))

    # QR de vérification par bandeau (anti-duplication) — bout droit
    if _sec and evenement_id:
        try:
            _q = min(CARD_H - 3.2 * mm, 11.5 * mm)
            _sec.carton_qr(c, x0 + CARD_W - ZONE_QR + (ZONE_QR - _q) / 2,
                           y0 + PIED_H + (CARD_H - HDR_H - PIED_H - _q) / 2, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(934300 + int(serie_start))
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
            if faites >= nb_cartes:
                break
            x0 = MARGIN_X
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
    with open("test_ohana90_24b.pdf", "wb") as f:
        f.write(pdf.read())
    print("OHANA 90 24 boules généré")
