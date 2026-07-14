# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur BIEN SÛR (format A4)
8 cartes par feuille A4 (2 colonnes × 4 rangées), design original du modèle :
  · BOÎTE HAUTE (coin haut-gauche) : 3 numéros 1-20 — le min et le max
    empilés en GRAND, la médiane en petit à côté (fidèle au modèle)
  · DEUX ÉTIQUETTES FLÉCHÉES (haut-droit et bas-gauche) : 2 numéros 21-59
  · BOÎTE BASSE (coin bas-droit) : 3 numéros 60-75 — le min en petit
    au-dessus, les deux autres empilés en GRAND
8 boules par carte, partition complète du 1 à 75 (20 + 39 + 16).
Centre : « Le jeu Bien Sûr 1 à 75 by TUKEA + tél + N° » (le nom TOUJOURS visible).
QR de vérification au centre-gauche. Couleur arc-en-ciel (par carte) ou gris (N&B).
Chiffres en gris (2 gammes ÉCO/PREMIUM).
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
PLAGE_BOITE_HAUTE = (1, 20)    # 3 numéros
PLAGE_FLECHES = (21, 59)       # 2 numéros
PLAGE_BOITE_BASSE = (60, 75)   # 3 numéros

COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """8 numéros : 3 en 1-20, 2 en 21-59, 3 en 60-75 (triés)."""
    haut = sorted(rng.sample(range(*PLAGE_BOITE_HAUTE), 3) if False else rng.sample(range(PLAGE_BOITE_HAUTE[0], PLAGE_BOITE_HAUTE[1] + 1), 3))
    fleches = rng.sample(range(PLAGE_FLECHES[0], PLAGE_FLECHES[1] + 1), 2)
    bas = sorted(rng.sample(range(PLAGE_BOITE_BASSE[0], PLAGE_BOITE_BASSE[1] + 1), 3))
    return haut, fleches, bas


def _etiquette(c, x, y, w, h, col):
    """L'étiquette fléchée du modèle (pentagone pointe à droite)."""
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x + w - h * 0.55, y)
    p.lineTo(x + w, y + h / 2)
    p.lineTo(x + w - h * 0.55, y + h)
    p.lineTo(x, y + h)
    p.close()
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.drawPath(p, stroke=1, fill=0)


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    haut, fleches, bas = nums

    # Bordure carte bien arrondie (fidèle au modèle)
    c.setStrokeColor(col); c.setLineWidth(1.1)
    c.roundRect(x0, y0, CARD_W, CARD_H, 3.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.1 * mm)

    t_grand, t_petit, t_fleche = 32, 20, 28  # bien gros (Maeva)

    def chiffre(val, cx, cy, t):
        if _sec:
            _sec.chiffre_micro(c, val, cx, cy - t * 0.36, t, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, t)
            c.drawCentredString(cx, cy - t * 0.36, str(val))

    # ── BOÎTE HAUTE (haut-gauche) : min et max empilés, médiane en petit ──
    bw, bh = CARD_W * 0.36, CARD_H * 0.34  # boîtes élargies avec les chiffres
    bx, by = x0 + 2.2 * mm, y0 + CARD_H - bh - 2.2 * mm
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(bx, by, bw, bh, 1.8 * mm, stroke=1, fill=0)
    chiffre(haut[0], bx + bw * 0.32, by + bh * 0.75, t_grand)      # le min, en grand
    chiffre(haut[2], bx + bw * 0.44, by + bh * 0.24, t_grand)      # le max, en grand
    chiffre(haut[1], bx + bw * 0.78, by + bh * 0.76, t_petit)      # la médiane, en petit

    # ── ÉTIQUETTE FLÉCHÉE haut-droit ──
    ew, eh = CARD_W * 0.26, CARD_H * 0.17  # étiquettes élargies avec les chiffres
    ex, ey = x0 + CARD_W - ew - 2.4 * mm, y0 + CARD_H - eh - 3.0 * mm
    _etiquette(c, ex, ey, ew, eh, col)
    chiffre(fleches[0], ex + ew * 0.42, ey + eh * 0.50, t_fleche)

    # ── ÉTIQUETTE FLÉCHÉE bas-gauche ──
    ex2, ey2 = x0 + 2.4 * mm, y0 + 3.0 * mm + CARD_H * 0.04
    _etiquette(c, ex2, ey2, ew, eh, col)
    chiffre(fleches[1], ex2 + ew * 0.42, ey2 + eh * 0.50, t_fleche)

    # ── BOÎTE BASSE (bas-droit) : le min en petit au-dessus, les 2 autres en grand ──
    bx2, by2 = x0 + CARD_W - bw - 2.2 * mm, y0 + 2.2 * mm
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(bx2, by2, bw, bh, 1.8 * mm, stroke=1, fill=0)
    chiffre(bas[0], bx2 + bw * 0.44, by2 + bh * 0.78, t_petit)     # le min, en petit
    chiffre(bas[1], bx2 + bw * 0.27, by2 + bh * 0.28, t_grand)     # côte à côte en grand
    chiffre(bas[2], bx2 + bw * 0.74, by2 + bh * 0.26, t_grand)

    # ── Centre : le nom du jeu TOUJOURS visible (fidèle au modèle) ──
    l1 = "Le jeu Bien S\u00fbr 1 \u00e0 75 by TUKEA"
    if titre_jeu and "BIEN" not in titre_jeu.strip().upper():
        l1 = "Bien S\u00fbr \u00b7 " + titre_jeu.strip() + " by TUKEA"
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawCentredString(x0 + CARD_W * 0.52, y0 + CARD_H * 0.575, l1[:52])
    if telephone:
        c.setFont(POLICE, 4.6)
        c.drawCentredString(x0 + CARD_W * 0.52, y0 + CARD_H * 0.515, telephone[:24])
    c.setFont(POLICE, 4.6)
    c.drawCentredString(x0 + CARD_W * 0.52, y0 + CARD_H * 0.455, "N\u00b0 %06d" % serie)

    # QR de vérification par carte (anti-duplication) — centre-gauche
    if _sec and evenement_id:
        try:
            _q = 11.5 * mm
            _sec.carton_qr(c, x0 + 3.0 * mm, y0 + (CARD_H - _q) / 2 - 1.0 * mm, _q, evenement_id, serie)
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

    rng = random.Random(933700 + int(serie_start))
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
    pdf = generer_pdf(nb_cartes=8, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_bien_sur.pdf", "wb") as f:
        f.write(pdf.read())
    print("BIEN SÛR généré")
