# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur P15 MARATHON (format A4)
15 grilles BINGO par feuille A4 (3 colonnes × 5 rangées) — le légendaire
P15 des boutiques, fidèle au modèle historique de Maeva :
  bandeau B·I·N·G·O turquoise, grille 5×5 du bingo américain,
  B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75 (ordre LIBRE),
  la case CENTRALE est libre — élargie en SANCTUAIRE (croix centrale
  15 mm) pour loger ENTIÈREMENT le QR de vérification sans toucher
  aux chiffres (le coco 🥥 traditionnel s'affiche sans événement).
Pied fin : signature + N° de série. Tirage 1-75 complet.
Couleur turquoise du modèle (ou couleur_perso) / gris (N&B). 2 gammes ÉCO/PREMIUM.
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

TURQUOISE = "#00C2CC"      # le bandeau du modèle historique
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)
BRUN_COCO = colors.Color(0.45, 0.30, 0.18)
BRUN_FONCE = colors.Color(0.25, 0.15, 0.08)


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
LETTRES = "BINGO"
COLONNES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

COLS_PAGE = 3
ROWS_PAGE = 5
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 7 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 2.6 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 4.2 * mm           # le bandeau B·I·N·G·O turquoise
PIED_H = 3.4 * mm          # signature + N° de série


def _gen_carte(rng):
    """Grille BINGO : 5 numéros distincts par colonne (4 au centre N),
    ordre LIBRE dans les colonnes — fidèle au modèle."""
    cols = []
    for ci, (pmin, pmax) in enumerate(COLONNES):
        n = 4 if ci == 2 else 5
        cols.append(rng.sample(range(pmin, pmax + 1), n))
    return cols


def _dessiner_coco(c, cx, cy, r):
    """Le coco 🥥 traditionnel du P15 : rond brun et ses trois yeux."""
    c.saveState()
    c.setFillColor(BRUN_COCO); c.setStrokeColor(BRUN_FONCE); c.setLineWidth(0.5)
    c.circle(cx, cy, r, stroke=1, fill=1)
    c.setFillColor(BRUN_FONCE)
    for dx, dy in ((-0.32, 0.28), (0.32, 0.28), (0, -0.18)):
        c.circle(cx + dx * r, cy + dy * r, r * 0.13, stroke=0, fill=1)
    c.restoreState()


SANCTUAIRE = 15.2 * mm    # la case royale du QR : jamais un chiffre touché

def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    # Colonnes en croix : la colonne N (centre) élargie pour le sanctuaire
    _cw = (CARD_W - SANCTUAIRE) / 4
    LARGEURS = [_cw, _cw, SANCTUAIRE, _cw, _cw]
    X_COL = [x0 + sum(LARGEURS[:i]) for i in range(6)]

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.7)
    c.rect(x0, y0, CARD_W, CARD_H, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.7 * mm)

    # Bandeau B·I·N·G·O plein turquoise (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setFillColor(col)
    c.rect(x0, hdr_bas, CARD_W, HDR_H, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 6.5)
    for i, lettre in enumerate(LETTRES):
        c.drawCentredString((X_COL[i] + X_COL[i + 1]) / 2, hdr_bas + 1.1 * mm, lettre)

    # Pied fin : signature + N° de série
    pied_haut = y0 + PIED_H
    c.setStrokeColor(col); c.setLineWidth(0.35)
    c.line(x0, pied_haut, x0 + CARD_W, pied_haut)
    signature = "P15 by TUKEA"
    if titre_jeu and "P15" not in titre_jeu.strip().upper():
        signature += " \u00b7 " + titre_jeu.strip()
    if telephone:
        signature += " \u00b7 " + telephone
    c.setFillColor(col); c.setFont(POLICE, 3.6)
    c.drawString(x0 + 1.4 * mm, y0 + 1.0 * mm, signature[:44])
    c.setFillColor(GRIS); c.setFont(POLICE, 4.6)
    c.drawRightString(x0 + CARD_W - 1.4 * mm, y0 + 0.9 * mm, "%06d" % serie)

    # La grille 5×5 en croix : rangée centrale rehaussée pour le sanctuaire
    z_top = hdr_bas
    z_bot = pied_haut
    _rh = (z_top - z_bot - SANCTUAIRE) / 4
    HAUTEURS = [_rh, _rh, SANCTUAIRE, _rh, _rh]
    Y_ROW = [z_top - sum(HAUTEURS[:i]) for i in range(6)]   # plafonds des rangées
    c.setStrokeColor(col); c.setLineWidth(0.3)
    for i in range(1, 5):
        c.line(X_COL[i], z_bot, X_COL[i], z_top)
        c.line(x0, Y_ROW[i], x0 + CARD_W, Y_ROW[i])

    # Les 24 numéros — ordre libre (fidèle au modèle)
    taille = 20
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
    # dit tout) — ou le coco 🥥 traditionnel quand il n'y a pas d'événement
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
        _dessiner_coco(c, cx_c, cy_c, SANCTUAIRE * 0.30)


def generer_pdf(nb_cartes=15, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(940300 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 8)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 4.4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 6.6 * mm, "%03d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                cols_nums = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else TURQUOISE if couleur else "#9A9A9A")
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
    pdf = generer_pdf(nb_cartes=15, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_p15.pdf", "wb") as f:
        f.write(pdf.read())
    print("P15 Marathon généré")
