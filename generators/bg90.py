# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur BG 90 (format A4)
12 grilles par feuille A4 (3 colonnes × 4 rangées) — à la demande de Maeva
(le modèle historique en avait 18, on aère pour de plus grosses cartes).
Chaque carte : en-tête B | G | 90 puis grille 2 rangées × 3 colonnes —
5 BOULES triées vers le bas (décision Maeva) :
  B = 1-15 (×2) · G = 46-60 (×1, en haut) · 90 = 76-90 (×2)
La case du BAS-MILIEU est libérée pour le QR de vérification.
Deux grands sauts dans le tirage : ni 16-45, ni 61-75 (caller informé) !
Pied : « N° SERIE » + signature + numéro.
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
LETTRES = ["B", "G", "90"]
COLONNES = [(1, 15), (46, 60), (76, 90)]   # deux grands sauts !

COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 6 * mm
PIED_H = 4.4 * mm        # le pied fin : N° SERIE + signature + numéro


def _gen_carte(rng):
    """5 boules : 2 + 1 + 2 par famille, triées vers le bas.
    Le G libère sa case du bas pour le QR (décision Maeva)."""
    return [sorted(rng.sample(range(pmin, pmax + 1), n))
            for (pmin, pmax), n in zip(COLONNES, (2, 1, 2))]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 3

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.rect(x0, y0, CARD_W, CARD_H, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.8 * mm)

    # En-tête B | G | 90 (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    for i in range(1, 3):
        c.line(x0 + i * cell_w, hdr_bas, x0 + i * cell_w, y0 + CARD_H)
    c.setFillColor(col); c.setFont(POLICE, 6.5)
    for i, lettre in enumerate(LETTRES):
        c.drawCentredString(x0 + (i + 0.5) * cell_w, hdr_bas + 1.8 * mm, lettre)

    # Pied fin : « N° SERIE » + signature + numéro
    pied_haut = y0 + PIED_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, pied_haut, x0 + CARD_W, pied_haut)
    c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.2)
    c.drawString(x0 + 2 * mm, y0 + 1.4 * mm, "N\u00b0 SERIE")
    signature = "BG 90 by TUKEA"
    if titre_jeu and "BG" not in titre_jeu.strip().upper():
        signature += " \u00b7 " + titre_jeu.strip()
    if telephone:
        signature += " \u00b7 " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.0)
    c.drawCentredString(x0 + CARD_W / 2, y0 + 1.4 * mm, signature[:46])
    c.setFont(POLICE, 6)
    c.drawRightString(x0 + CARD_W - 2 * mm, y0 + 1.3 * mm, "%06d" % serie)

    # La grille 2×3 (traits complets)
    z_top = hdr_bas
    z_bot = pied_haut
    row_h = (z_top - z_bot) / 2
    c.setStrokeColor(col); c.setLineWidth(0.35)
    for i in range(1, 3):
        c.line(x0 + i * cell_w, z_bot, x0 + i * cell_w, z_top)
    c.line(x0 + 1.5 * mm, z_top - row_h, x0 + CARD_W - 1.5 * mm, z_top - row_h)

    # Les 5 boules — le G garde son numéro en haut
    taille = 40  # les plus gros du catalogue !
    for ci, nums in enumerate(cols_nums):
        cx = x0 + (ci + 0.5) * cell_w
        for ri, val in enumerate(nums):
            cyc = z_top - (ri + 0.5) * row_h
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # QR de vérification — logé dans la case libérée du BAS-MILIEU (décision Maeva)
    if _sec and evenement_id:
        try:
            _q = min(row_h - 2.4 * mm, cell_w - 3 * mm, 14.0 * mm)
            _sec.carton_qr(c, x0 + 1.5 * cell_w - _q / 2,
                           z_top - 1.5 * row_h - _q / 2, _q, evenement_id, serie)
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

    rng = random.Random(937900 + int(serie_start))
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
                      telephone="89 22 23 05")
    with open("test_bg90.pdf", "wb") as f:
        f.write(pdf.read())
    print("BG 90 généré")
