# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TOPDAY (format A4)
12 cartes par feuille A4 (2 colonnes × 6 rangées).
Chaque carte épelle T·O·P·D·A·Y : en-tête à 3 paires de lettres avec leurs
plages, puis 3 BOÎTES ARRONDIES de 2 numéros chacune (fidèle au modèle) :
  boîte T·O : un 1-15 (en HAUT) + un 16-30 (en BAS)
  boîte P·D : un 31-45 (en HAUT) + un 46-60 (en BAS)
  boîte A·Y : DEUX numéros 61-75 distincts, un en haut, un en bas
Les 2 numéros de chaque boîte sont EMPILÉS (décision Maeva) — plus lisibles !
6 numéros par carte. Pied : « N° SERIE | 054001 » + signature + QR.
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
# Les 3 boîtes de TOPDAY : (lettres, plages des 2 numéros)
BOITES = [
    (("T", "O"), ((1, 15), (16, 30))),
    (("P", "D"), ((31, 45), (46, 60))),
    (("A", "Y"), ((61, 75), (61, 75))),   # deux 61-75 distincts, ordre libre !
]

COLS_PAGE = 2
ROWS_PAGE = 6
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 2.8 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 7 * mm           # les lettres + leurs plages
PIED_H = 4.4 * mm        # N° SÉRIE + signature
ZONE_QR = 12 * mm        # bout droit de la zone des boîtes, réservé au QR


def _gen_carte(rng):
    """6 numéros : (T,O), (P,D), (A,Y) — la 3e boîte : 2 distincts 61-75 mélangés."""
    to = (rng.randint(1, 15), rng.randint(16, 30))
    pd = (rng.randint(31, 45), rng.randint(46, 60))
    ay = rng.sample(range(61, 76), 2)
    rng.shuffle(ay)
    return [to, pd, tuple(ay)]


def _dessiner_carte(c, x0, y0, paires, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.rect(x0, y0, CARD_W, CARD_H, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.8 * mm)

    # Pied : « N° SERIE | 054001 » + signature (le nom TOUJOURS visible)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + PIED_H, x0 + CARD_W, y0 + PIED_H)
    c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.2)
    c.drawString(x0 + 2 * mm, y0 + 1.4 * mm, "N\u00b0 SERIE")
    signature = "TOPDAY by TUKEA"
    if titre_jeu and "TOPDAY" not in titre_jeu.strip().upper():
        signature += " \u00b7 " + titre_jeu.strip()
    if telephone:
        signature += " \u00b7 " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.2)
    c.drawCentredString(x0 + CARD_W * 0.5, y0 + 1.4 * mm, signature[:52])
    c.setFont(POLICE, 6)
    c.drawRightString(x0 + CARD_W - 2 * mm, y0 + 1.3 * mm, "%06d" % serie)

    # Les 3 boîtes arrondies + leurs lettres en tête (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    zw = CARD_W - ZONE_QR
    boite_w = (zw - 4 * mm) / 3
    boite_h = hdr_bas - (y0 + PIED_H) - 2.4 * mm
    taille = 32  # bien gros, grâce à l'empilement (Maeva)
    for bi, ((lettres, _), vals) in enumerate(zip(BOITES, paires)):
        bx = x0 + 1.5 * mm + bi * (boite_w + 1.25 * mm)
        by = y0 + PIED_H + 1.2 * mm
        # les lettres + leurs plages
        c.setFillColor(col)
        for li, (lettre, (pmin, pmax)) in enumerate(zip(lettres, BOITES[bi][1])):
            lx = bx + boite_w * (0.28 if li == 0 else 0.72)
            c.setFont(POLICE, 6)
            c.drawCentredString(lx, hdr_bas + 3.2 * mm, lettre)
            c.setFont(POLICE, 3.4)
            c.drawCentredString(lx, hdr_bas + 0.8 * mm, "%d-%d" % (pmin, pmax))
        # la boîte arrondie
        c.setStrokeColor(col); c.setLineWidth(0.9)
        c.roundRect(bx, by, boite_w, boite_h, 2.2 * mm, stroke=1, fill=0)
        # les 2 numéros EMPILÉS : un en haut, un en bas (décision Maeva)
        for li, val in enumerate(vals):
            cx = bx + boite_w * 0.5
            cy = by + boite_h * (0.72 if li == 0 else 0.28)
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cy - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cy - taille * 0.36, str(val))

    # QR de vérification par carte (anti-duplication) — bout droit
    if _sec and evenement_id:
        try:
            _q = min(CARD_H - PIED_H - 4 * mm, 11.5 * mm)
            _sec.carton_qr(c, x0 + CARD_W - ZONE_QR + (ZONE_QR - _q) / 2,
                           y0 + PIED_H + (CARD_H - PIED_H - _q) / 2 - 1.0 * mm, _q, evenement_id, serie)
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

    rng = random.Random(935200 + int(serie_start))
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
                paires = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, paires, coul, serie, titre_jeu, telephone,
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
    with open("test_topday.pdf", "wb") as f:
        f.write(pdf.read())
    print("TOPDAY généré")
