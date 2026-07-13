# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur IGO (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées). Le jeu « pour 5 boules ».
Chaque carte, 3 étages séparés par des traits (fidèle au modèle) :
  étage 1 : la rangée  I(16-30)  G(46-60)  O(61-75)
  étage 2 : un solitaire G (46-60), centré
  étage 3 : un solitaire G (46-60), centré
5 numéros par carte — la colonne G en fournit 3 (tous distincts).
En-tête à 2 lignes : « Le jeu IGO pour 5 boules by TUKEA … » + « Carte N° 030001 ».
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
# Les plages du jeu IGO
PLAGE_I = (16, 30)
PLAGE_G = (46, 60)
PLAGE_O = (61, 75)

COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 8.5 * mm         # en-tête à 2 lignes
ZONE_QR_H = 15 * mm      # bande basse réservée au QR de vérification


def _gen_carte(rng):
    """5 numéros : (i, g1, o) pour la rangée haute + (g2, g3) solitaires.
    Les 3 numéros G sont distincts."""
    i = rng.randint(*PLAGE_I)
    o = rng.randint(*PLAGE_O)
    g1, g2, g3 = rng.sample(range(PLAGE_G[0], PLAGE_G[1] + 1), 3)
    return (i, g1, o, g2, g3)


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    i_num, g1, o_num, g2, g3 = nums

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête à 2 lignes — le nom du jeu apparaît TOUJOURS (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    l1 = "Le jeu IGO pour 5 boules by TUKEA" + ((" " + telephone) if telephone else "")
    if titre_jeu and "IGO" not in titre_jeu.strip().upper():
        l1 = "Le jeu IGO \u00b7 " + titre_jeu.strip() + " by TUKEA" + ((" " + telephone) if telephone else "")
    c.setFillColor(col); c.setFont(POLICE, 4.4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 3.2 * mm, l1[:64])
    c.setFont(POLICE, 5.5)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 7.2 * mm, "Carte N\u00b0 %06d" % serie)

    # Les 3 étages (QR dans la bande basse)
    z_top = hdr_bas
    z_bot = y0 + ZONE_QR_H
    row_h = (z_top - z_bot) / 3
    # traits horizontaux entre les étages (fidèle au modèle)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, z_top - row_h, x0 + CARD_W, z_top - row_h)
    c.line(x0, z_top - 2 * row_h, x0 + CARD_W, z_top - 2 * row_h)
    c.line(x0, z_bot, x0 + CARD_W, z_bot)

    taille = 26
    def chiffre(val, cx, cyc):
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # étage 1 : I G O côte à côte
    y1 = z_top - row_h / 2
    chiffre(i_num, x0 + CARD_W * 0.20, y1)
    chiffre(g1,    x0 + CARD_W * 0.50, y1)
    chiffre(o_num, x0 + CARD_W * 0.80, y1)
    # étages 2 et 3 : les solitaires G, centrés
    chiffre(g2, x0 + CARD_W / 2, z_top - 1.5 * row_h)
    chiffre(g3, x0 + CARD_W / 2, z_top - 2.5 * row_h)

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

    rng = random.Random(930500 + int(serie_start))
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
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_igo.pdf", "wb") as f:
        f.write(pdf.read())
    print("IGO généré")
