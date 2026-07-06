# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur OHANA 75 · 8 BOULES (format A4)
9 cartes (bandes allongées) par feuille A4, empilées.
Chaque carte : 8 numéros en ligne, alternant GROS chiffre (sans rond) et
petit chiffre dans un ROND POINTILLÉ. N° de série en boîte à gauche.
4 plages (2 numéros chacune) : 1-15, 16-30, 46-60, 61-75.
Dans chaque plage : le plus petit = gros chiffre, le plus grand = petit chiffre rond.
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
RANGES = [(1, 15), (16, 30), (46, 60), (61, 75)]

CARTES_PAGE = 9
MARGIN_X = 6 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 6 * mm
GUTTER_Y = 2 * mm

CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (CARTES_PAGE - 1) * GUTTER_Y) / CARTES_PAGE


def _gen_carte(rng):
    """8 entrées (valeur, rond_pointille) : par plage, petit=gros chiffre, grand=rond."""
    out = []
    for (a, b) in RANGES:
        pair = sorted(rng.sample(range(a, b + 1), 2))
        out.append((pair[0], False))   # gros chiffre
        out.append((pair[1], True))    # petit chiffre, rond pointillé
    return out


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # ---- En-tête ----
    htxt_y = y0 + CARD_H - 4.3 * mm
    # boîte série (gauche)
    sb_w, sb_h = 16 * mm, 4.4 * mm
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.roundRect(x0 + 2 * mm, htxt_y - 1.7 * mm, sb_w, sb_h, 0.8 * mm, stroke=1, fill=0)
    c.setFillColor(col); c.setFont(POLICE, 7)
    c.drawCentredString(x0 + 2 * mm + sb_w / 2, htxt_y, "%05d" % serie)
    # titre centré
    titre = (titre_jeu or "Le jeu OHANA 75 pour 8 boules")
    if telephone:
        titre += "  " + telephone
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawCentredString(x0 + CARD_W / 2 + 9 * mm, htxt_y, titre[:54])

    # ---- Ligne des 8 numéros ----
    zone_top = htxt_y - 3 * mm
    zone_bot = y0 + 2 * mm
    cy = (zone_top + zone_bot) / 2

    gauche = x0 + 12 * mm
    droite = x0 + CARD_W - 8 * mm
    pas = (droite - gauche) / 7.0
    xs = [gauche + i * pas for i in range(8)]

    for i, (val, rond) in enumerate(nums):
        x = xs[i]
        if rond:
            # petit chiffre dans rond pointillé
            c.setStrokeColor(col); c.setLineWidth(0.7)
            c.setDash([1.4, 1.4])
            c.circle(x, cy, 6.6 * mm, stroke=1, fill=0)
            c.setDash([])
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, x, cy - 10, 28, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, 28)
                c.drawCentredString(x, cy - 10, str(val))
        else:
            # gros chiffre
            if _sec:
                _sec.chiffre_micro(c, val, x, cy - 13.5, 40, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, 40)
                c.drawCentredString(x, cy - 13.5, str(val))

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            _q = 8.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 1.5 * mm, y0 + 1.5 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=9, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + CARTES_PAGE - 1) // CARTES_PAGE

    rng = random.Random(758000 + int(serie_start))
    serie = int(serie_start)
    faites = 0
    no_page = 1

    for _ in range(nb_pages):
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 4.5 * mm, "%d" % no_page)
        for row in range(CARTES_PAGE):
            if faites >= nb_cartes:
                break
            y0 = MARGIN_BOT + (CARTES_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
            x0 = MARGIN_X
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
    pdf = generer_pdf(nb_cartes=9, couleur=True,
                      titre_jeu="Le jeu OHANA 75 pour 8 boules", telephone="89 22 23 05")
    with open("test_ohana8.pdf", "wb") as f:
        f.write(pdf.read())
    print("OHANA 75 8 boules généré")
