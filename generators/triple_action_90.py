# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TRIPLE ACTION 90 (format A4)
10 cartes-bandeaux par feuille A4 (1 colonne × 10 rangées, pleine largeur).
Chaque carte : 6 GROUPES côte à côte (1-15, 16-30, 31-45, 46-60, 61-75, 76-90).
Chaque groupe : 2 grands numéros en haut (le 1er dans un CERCLE POINTILLÉ)
                + 1 numéro plus petit centré dessous.  3 numéros × 6 = 18 numéros.
En-tête de carte : « TRIPLE ACTION 90 — 3 séries » à gauche, N° de série à droite.
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
# (min, max) des 6 groupes — TRIPLE ACTION 90
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 90)]

ROWS_PAGE = 10           # 10 bandeaux pleine largeur
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_Y = 2.4 * mm

CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
ZONE_QR = 19 * mm        # bande de droite réservée au QR de vérification


def _gen_carte(rng):
    """6 groupes de 3 numéros chacun, tirés dans leur plage (18 numéros)."""
    return [rng.sample(range(pmin, pmax + 1), 3) for pmin, pmax in PLAGES]


def _dessiner_carte(c, x0, y0, groupes, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure du bandeau
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête — le nom du jeu apparaît TOUJOURS (à gauche) + série (à droite)
    hdr_y = y0 + CARD_H - 3.2 * mm
    titre = "TRIPLE ACTION 90 — 3 séries"
    if titre_jeu and "TRIPLE ACTION 90" not in titre_jeu.strip().upper():
        titre += "  ·  " + titre_jeu.strip()
    if telephone:
        titre += "  ·  " + telephone
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawString(x0 + 3 * mm, hdr_y, titre[:70])
    c.setFont(POLICE, 6)
    c.drawRightString(x0 + CARD_W - ZONE_QR - 2 * mm, hdr_y, "N\u00b0 %06d" % serie)

    # Zone des 6 groupes (le QR vit dans la bande de droite)
    zx = x0 + 3 * mm
    zw = CARD_W - 3 * mm - ZONE_QR
    cell_w = zw / 6
    haut_y = y0 + CARD_H * 0.52      # ligne du haut (la paire)
    bas_y = y0 + 2.6 * mm            # ligne du bas (le petit numéro)
    rayon = 5.9 * mm  # cercles élargis avec les chiffres GROSSIS (décision Maeva)

    for gi, nums in enumerate(groupes):
        gx = zx + gi * cell_w
        n_cercle, n_grand, n_petit = nums
        # 1er numéro : dans son cercle POINTILLÉ (fidèle au modèle)
        cx1 = gx + cell_w * 0.28
        cy1 = haut_y + 1.2 * mm
        c.setStrokeColor(col); c.setLineWidth(0.7)
        c.setDash(1.6, 1.6)
        c.circle(cx1, cy1, rayon, stroke=1, fill=0)
        c.setDash()
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, n_cercle, cx1, haut_y - 5.4, 25, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, 25)
            c.drawCentredString(cx1, haut_y - 4.8, str(n_cercle))
        # 2e numéro : à droite du cercle
        cx2 = gx + cell_w * 0.72
        if _sec:
            _sec.chiffre_micro(c, n_grand, cx2, haut_y - 5.4, 25, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, 25)
            c.drawCentredString(cx2, haut_y - 4.8, str(n_grand))
        # 3e numéro : plus petit, centré dessous
        if _sec:
            _sec.chiffre_micro(c, n_petit, gx + cell_w / 2, bas_y, 22, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, 22)
            c.drawCentredString(gx + cell_w / 2, bas_y, str(n_petit))
        # fin séparation entre groupes (discrète, comme le modèle)
        if gi > 0:
            c.setStrokeColor(colors.Color(0.88, 0.88, 0.88)); c.setLineWidth(0.3)
            c.line(gx, y0 + 2 * mm, gx, y0 + CARD_H - 5 * mm)

    # QR de vérification par carte (anti-duplication) — bande de droite
    if _sec and evenement_id:
        try:
            _q = 13.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - ZONE_QR + (ZONE_QR - _q) / 2,
                           y0 + (CARD_H - _q) / 2 - 1.2 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=10, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + ROWS_PAGE - 1) // ROWS_PAGE

    rng = random.Random(945000 + int(serie_start))
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
            groupes = _gen_carte(rng)
            coul = (couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
            _dessiner_carte(c, x0, y0, groupes, coul, serie, titre_jeu, telephone,
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
                      telephone="89.22.23.05")
    with open("test_triple_action_90.pdf", "wb") as f:
        f.write(pdf.read())
    print("TRIPLE ACTION 90 généré")
