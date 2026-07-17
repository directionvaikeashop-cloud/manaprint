# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur P12 MARATHON (format A4 PAYSAGE)
12 grilles BINGO par feuille (4 colonnes × 3 rangées) — fidèle au modèle
de Maeva : en-tête B·I·N·G·O avec le N° de série encadré sous le N,
grille 5×5 du bingo américain, B 1-15 · I 16-30 · N 31-45 · G 46-60 ·
O 61-75 (ordre LIBRE), la case CENTRALE « MARATHON » — élargie en
SANCTUAIRE (croix centrale 16 mm) pour loger ENTIÈREMENT le QR de
vérification sans toucher aux chiffres (le mot MARATHON s'affiche
quand il n'y a pas d'événement).
Arc-en-ciel de 12 couleurs (ou couleur_perso) / gris (N&B). 2 gammes ÉCO/PREMIUM.
Caller : entrée « P6 / P12 / P15 MARATHON » (1-75) — boutons PAIRS/IMPAIRS inclus.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
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

GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)

# L'arc-en-ciel du modèle : 12 cartes, 12 couleurs
RAINBOW = ["#E53935", "#FB8C00", "#FDD835", "#43A047",
           "#00ACC1", "#5E35B1", "#8E24AA", "#D81B60",
           "#00897B", "#7CB342", "#F4511E", "#1E88E5"]


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

PAGE_W, PAGE_H = landscape(A4)
LETTRES = "BINGO"
COLONNES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

COLS_PAGE = 4
ROWS_PAGE = 3
MARGIN_X = 7 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 6 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 7 * mm             # l'en-tête B·I·N·G·O + série encadrée sous le N
PIED_H = 1.6 * mm          # respiration : la dernière rangée ne touche pas le bord

SANCTUAIRE = 16.0 * mm     # la case royale MARATHON/QR : jamais un chiffre touché


def _gen_carte(rng):
    """Grille BINGO : 5 numéros distincts par colonne (4 au centre N),
    ordre LIBRE dans les colonnes — fidèle au modèle."""
    cols = []
    for ci, (pmin, pmax) in enumerate(COLONNES):
        n = 4 if ci == 2 else 5
        cols.append(rng.sample(range(pmin, pmax + 1), n))
    return cols


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    # Colonnes en croix : la colonne N (centre) élargie pour le sanctuaire
    _cw = (CARD_W - SANCTUAIRE) / 4
    LARGEURS = [_cw, _cw, SANCTUAIRE, _cw, _cw]
    X_COL = [x0 + sum(LARGEURS[:i]) for i in range(6)]

    # Bordure carte arrondie et colorée (fidèle au modèle)
    c.setStrokeColor(col); c.setLineWidth(1.6)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête : les lettres B I N G O dans la couleur de la carte,
    # et le N° de série ENCADRÉ sous le N (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    for i, lettre in enumerate(LETTRES):
        cx = (X_COL[i] + X_COL[i + 1]) / 2
        c.setFillColor(col)
        if i == 2:
            c.setFont("Helvetica-Bold", 5.5)
            c.drawCentredString(cx, y0 + CARD_H - 2.6 * mm, lettre)
            bw, bh = 11 * mm, 3.0 * mm
            c.setStrokeColor(col); c.setLineWidth(0.5)
            c.roundRect(cx - bw / 2, y0 + CARD_H - 6.4 * mm, bw, bh, 0.6 * mm, stroke=1, fill=0)
            c.setFillColor(GRIS); c.setFont("Helvetica", 4.4)
            c.drawCentredString(cx, y0 + CARD_H - 5.6 * mm, "%06d" % serie)
        else:
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(cx, y0 + CARD_H - 4.6 * mm, lettre)

    # La grille 5×5 en croix : rangée centrale rehaussée pour le sanctuaire
    z_top = hdr_bas
    z_bot = y0 + PIED_H
    _rh = (z_top - z_bot - SANCTUAIRE) / 4
    HAUTEURS = [_rh, _rh, SANCTUAIRE, _rh, _rh]
    Y_ROW = [z_top - sum(HAUTEURS[:i]) for i in range(6)]   # plafonds des rangées
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
    for i in range(1, 5):
        c.line(X_COL[i], z_bot, X_COL[i], z_top)
        c.line(x0, Y_ROW[i], x0 + CARD_W, Y_ROW[i])

    # Les 24 numéros — ordre libre (fidèle au modèle)
    taille = 24
    for ci, nums in enumerate(cols_nums):
        cx = (X_COL[ci] + X_COL[ci + 1]) / 2
        rangees = (0, 1, 3, 4) if ci == 2 else (0, 1, 2, 3, 4)
        for val, ri in zip(nums, rangees):
            cyc = (Y_ROW[ri] + Y_ROW[ri + 1]) / 2
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # Le SANCTUAIRE central : le QR y loge ENTIER (sans code texte : le scan
    # dit tout) — ou le mot MARATHON du modèle quand il n'y a pas d'événement
    cx_c = (X_COL[2] + X_COL[3]) / 2
    cy_c = (Y_ROW[2] + Y_ROW[3]) / 2
    qr_ok = False
    if _sec and evenement_id:
        try:
            _q = 12.0 * mm
            qr_ok = _sec.carton_qr(c, cx_c - _q / 2, cy_c - _q / 2, _q, evenement_id, serie,
                                   avec_code=False)
        except Exception:
            qr_ok = False
    if not qr_ok:
        c.setFillColor(GRIS); c.setFont(POLICE, 7.5)
        c.drawCentredString(cx_c, cy_c + 0.8 * mm, "MARA")
        c.drawCentredString(cx_c, cy_c - 3.4 * mm, "THON")

    # Signature discrète sous la carte (marque + titre client + téléphone)
    signature = "P12 by TUKEA"
    if titre_jeu and "P12" not in titre_jeu.strip().upper():
        signature += " \u00b7 " + titre_jeu.strip()
    if telephone:
        signature += " \u00b7 " + telephone
    c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.0)
    c.drawCentredString(x0 + CARD_W / 2, y0 - 2.6 * mm, signature[:64])


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(120300 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 8)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 4.2 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 6.4 * mm, "%03d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                cols_nums = _gen_carte(rng)
                idx = (serie - 1) % len(RAINBOW)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[idx] if couleur else "#9A9A9A")
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
    with open("test_p12.pdf", "wb") as f:
        f.write(pdf.read())
    print("P12 Marathon généré")
