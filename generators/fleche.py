# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur FLÈCHE (format A4)
6 cartes par feuille A4 (2 colonnes × 3 rangées).
Chaque carte : grille 5×5 dont 14 cases portent des numéros — la FLÈCHE ↘ :
la diagonale du haut, la pointe en bas à droite, le bord droit et le
plancher complets. Les cases vides sont BARRÉES d'une croix (fidèle au modèle).
Colonnes classiques : 1-15 · 16-30 · 31-45 · 46-60 · 61-75, et tout est
trié en DESCENDANT vers le bas (75, 74, 73… — l'élégance du modèle).
En-tête : « Le jeu FLÈCHE by TUKEA … » + N° de série. Le QR de vérification
occupe une case barrée du haut. Couleur arc-en-ciel (par carte) ou gris (N&B).
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
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
# La FLÈCHE : rangées occupées par colonne (0 = rangée du haut)
# c1 : haut + plancher · c2 : 2e + plancher · c3 : 4e + plancher
# c4 : 3e, 4e + plancher · c5 : toutes (le bord droit complet)
RANGEES = [(0, 4), (1, 4), (3, 4), (2, 3, 4), (0, 1, 2, 3, 4)]
CASE_QR = (0, 2)   # (rangée, colonne) de la case barrée qui accueille le QR

COLS_PAGE = 2
ROWS_PAGE = 3
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 6 * mm


def _gen_carte(rng):
    """14 numéros : par colonne, autant que de rangées occupées,
    triés en DESCENDANT vers le bas (fidèle au modèle)."""
    return [sorted(rng.sample(range(pmin, pmax + 1), len(rangs)), reverse=True)
            for (pmin, pmax), rangs in zip(PLAGES, RANGEES)]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 5

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête : nom du jeu (TOUJOURS visible) + série (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    l1 = "Le jeu \u00ab FL\u00c8CHE \u00bb by TUKEA"
    if titre_jeu and "FLECHE" not in titre_jeu.strip().upper().replace("\u00c8", "E"):
        l1 = "FL\u00c8CHE \u00b7 " + titre_jeu.strip() + " by TUKEA"
    if telephone:
        l1 += " " + telephone
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawString(x0 + 2.5 * mm, hdr_bas + 1.8 * mm, l1[:54])
    c.setFont(POLICE, 6.5)
    c.drawRightString(x0 + CARD_W - 2.5 * mm, hdr_bas + 1.7 * mm, "%06d" % serie)

    # La grille 5×5 (traits complets)
    z_top = hdr_bas
    z_bot = y0 + 1.5 * mm
    row_h = (z_top - z_bot) / 5
    c.setStrokeColor(col); c.setLineWidth(0.35)
    for i in range(1, 5):
        c.line(x0 + i * cell_w, z_bot, x0 + i * cell_w, z_top)
        c.line(x0 + 1.5 * mm, z_top - i * row_h, x0 + CARD_W - 1.5 * mm, z_top - i * row_h)
    c.line(x0 + 1.5 * mm, z_bot, x0 + CARD_W - 1.5 * mm, z_bot)

    # Les cases occupées (la flèche) et les cases barrées (les croix)
    occupees = {(ri, ci) for ci, rangs in enumerate(RANGEES) for ri in rangs}
    taille = 34
    for ri in range(5):
        for ci in range(5):
            cx = x0 + (ci + 0.5) * cell_w
            haut = z_top - ri * row_h
            cyc = haut - row_h / 2
            if (ri, ci) in occupees:
                continue  # le numéro sera posé plus bas
            if (ri, ci) == CASE_QR and _sec and evenement_id:
                continue  # cette case barrée accueille le QR
            # la croix de la case vide (fidèle au modèle)
            c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.4)
            m = 1.6 * mm
            c.line(cx - cell_w / 2 + m, haut - m, cx + cell_w / 2 - m, haut - row_h + m)
            c.line(cx - cell_w / 2 + m, haut - row_h + m, cx + cell_w / 2 - m, haut - m)

    # Les 14 numéros de la flèche, descendants vers le bas
    for ci, (nums, rangs) in enumerate(zip(cols_nums, RANGEES)):
        cx = x0 + (ci + 0.5) * cell_w
        for val, ri in zip(nums, rangs):
            cyc = z_top - (ri + 0.5) * row_h
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # QR de vérification — dans sa case barrée du haut
    if _sec and evenement_id:
        try:
            _q = min(row_h - 2.0 * mm, cell_w - 3 * mm, 12.5 * mm)
            qri, qci = CASE_QR
            _sec.carton_qr(c, x0 + (qci + 0.5) * cell_w - _q / 2,
                           z_top - (qri + 0.5) * row_h - _q / 2, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(935500 + int(serie_start))
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
    pdf = generer_pdf(nb_cartes=6, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="689 89 22 23 05")
    with open("test_fleche.pdf", "wb") as f:
        f.write(pdf.read())
    print("FLÈCHE généré")
