# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur FUNDAY (format A4)
20 cartes par feuille A4 (2 colonnes × 10 rangées).
Chaque carte : en-tête F · U · N · D · A · Y puis UNE rangée de 6 numéros,
un par colonne :  F = 1-15, U = 16-30, N = 31-45, D = 46-60, A = 61-75, Y = 76-90.
Cercles POINTILLÉS sur les numéros U, D et Y (2e, 4e, 6e — fidèle au modèle).
Pied de carte : « N° SERIE | 050001 ».
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
LETTRES = "FUNDAY"
# (min, max) par lettre — F U N D A Y
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 90)]
CERCLES = (1, 3, 5)      # positions des cercles pointillés : U, D, Y

COLS_PAGE = 2
ROWS_PAGE = 10
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 2.4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
ZONE_QR = 16 * mm        # bande de droite réservée au QR de vérification


def _gen_carte(rng):
    """6 numéros : un par colonne F-U-N-D-A-Y, chacun dans sa plage."""
    return [rng.randint(pmin, pmax) for pmin, pmax in PLAGES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # Géométrie : zone de jeu à gauche, bande QR à droite, pied en bas
    zx = x0 + 2.5 * mm
    zw = CARD_W - 2.5 * mm - ZONE_QR
    cell_w = zw / 6
    PIED_H = 4.6 * mm

    # En-tête : les lettres F U N D A Y (fidèle au modèle)
    let_y = y0 + CARD_H - 3.4 * mm
    c.setFillColor(col); c.setFont(POLICE, 5.5)
    for i, lettre in enumerate(LETTRES):
        c.drawCentredString(zx + (i + 0.5) * cell_w, let_y, lettre)

    # Rangée des 6 numéros — cercles pointillés sur U, D, Y
    num_base = y0 + PIED_H + (CARD_H - PIED_H - 6 * mm) * 0.34
    taille = 24  # gros chiffres au maximum
    rayon = 5.4 * mm  # cercles agrandis avec les chiffres
    for i, val in enumerate(nums):
        cx = zx + (i + 0.5) * cell_w
        if i in CERCLES:
            c.setStrokeColor(col); c.setLineWidth(0.7)
            c.setDash(1.5, 1.5)
            c.circle(cx, num_base + taille * 0.36, rayon, stroke=1, fill=0)
            c.setDash()
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, val, cx, num_base, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(cx, num_base, str(val))

    # Pied de carte : « N° SERIE | 050001 » — le titre client vit avec la série
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(zx, y0 + PIED_H, zx + zw, y0 + PIED_H)
    c.line(zx + zw * 0.42, y0 + 0.8 * mm, zx + zw * 0.42, y0 + PIED_H - 0.6 * mm)
    pied_g = "N\u00b0 SERIE"
    if titre_jeu and titre_jeu.strip().upper() != "FUNDAY":
        pied_g = titre_jeu.strip()[:22]
    c.setFillColor(GRIS_CLAIR if pied_g == "N\u00b0 SERIE" else col)
    c.setFont(POLICE, 4.2)
    c.drawCentredString(zx + zw * 0.21, y0 + 1.6 * mm, pied_g)
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawCentredString(zx + zw * 0.71, y0 + 1.5 * mm, "%06d" % serie)

    # Signature du jeu — le nom FUNDAY apparaît TOUJOURS (bande QR, verticalement)
    c.saveState()
    c.translate(x0 + CARD_W - 1.6 * mm, y0 + 2.5 * mm)
    c.rotate(90)
    c.setFillColor(col); c.setFont(POLICE, 4.2)
    signature = "FUNDAY by TUKEA" + ("  " + telephone if telephone else "")
    c.drawString(0, 0, signature[:40])
    c.restoreState()

    # QR de vérification par carte (anti-duplication) — bande de droite
    if _sec and evenement_id:
        try:
            _q = 12.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - ZONE_QR + 1.0 * mm,
                           y0 + (CARD_H - _q) / 2 - 1.0 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=20, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(960000 + int(serie_start))
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
    pdf = generer_pdf(nb_cartes=20, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89.22.23.05")
    with open("test_funday.pdf", "wb") as f:
        f.write(pdf.read())
    print("FUNDAY généré")
