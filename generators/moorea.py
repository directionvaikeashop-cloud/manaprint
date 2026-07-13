# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur MOOREA (format A4)
8 cartes par feuille A4 (2 colonnes × 4 rangées).
Chaque carte : 13 numéros disposés EN LOSANGE (1-3-5-3-1) :
  col 1 = 1 numéro  (1-15)     — la pointe gauche
  col 2 = 3 numéros (16-30)
  col 3 = 5 numéros (31-45)    — le cœur du losange
  col 4 = 3 numéros (46-60)
  col 5 = 1 numéro  (61-75)    — la pointe droite
Numéro de série en haut à droite, « MOOREA by TUKEA » en pied de carte.
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
# (min, max) par colonne — MOOREA, le losange 1-3-5-3-1
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
COMPTES = [1, 3, 5, 3, 1]  # nombre de numéros par colonne

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
    """13 numéros en losange : 1 + 3 + 5 + 3 + 1, chaque colonne dans sa plage, triés."""
    return [sorted(rng.sample(range(pmin, pmax + 1), n))
            for (pmin, pmax), n in zip(PLAGES, COMPTES)]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête — le nom du jeu apparaît TOUJOURS + série en haut à droite (fidèle au modèle)
    hdr_y = y0 + CARD_H - 4.0 * mm
    titre = "MOOREA"
    if titre_jeu and titre_jeu.strip().upper() != titre.upper():
        titre += "  —  " + titre_jeu.strip()
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawString(x0 + 3 * mm, hdr_y, titre[:48])
    c.setFont(POLICE, 6.5)
    c.drawRightString(x0 + CARD_W - 3 * mm, hdr_y, "N\u00b0 %06d" % serie)

    # Zone du losange (le QR vit dans la bande dédiée du bas)
    zone_top = hdr_y - 3.0 * mm
    zone_bot = y0 + 8 * mm   # le losange descend : le QR vit à gauche, le cœur au centre
    zone_h = zone_top - zone_bot
    # 5 colonnes : pointes étroites, cœur large
    lx = x0 + 4 * mm
    lw = CARD_W - 8 * mm
    frac = [0.15, 0.21, 0.28, 0.21, 0.15]           # losange bien espacé sur toute la largeur
    xs, cursor = [], lx + (lw - lw * sum(frac)) / 2  # centré
    for f in frac:
        xs.append(cursor + (lw * f) / 2)
        cursor += lw * f

    # tailles : gros chiffres au cœur, moyens sur les ailes
    taille = 33  # gros chiffres bien visibles, losange aéré
    pas5 = zone_h / 5                       # pas vertical du cœur (5 rangées)
    for ci, nums in enumerate(cols_nums):
        n = len(nums)
        # rangées occupées, centrées verticalement sur les 5 rangées du cœur
        premiere = (5 - n) / 2.0
        for ri, val in enumerate(nums):
            cyc = zone_top - (premiere + ri + 0.5) * pas5
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, xs[ci], cyc - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(xs[ci], cyc - taille * 0.36, str(val))

    # Pied de carte : signature du jeu (fidèle au modèle « MOOREA by TUKEA »)
    pied = "MOOREA by TUKEA"
    if telephone:
        pied += "  " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.5)
    c.drawRightString(x0 + CARD_W - 3 * mm, y0 + 2.2 * mm, pied[:52])

    # QR de vérification par carte (anti-duplication) — bande dédiée bas-gauche
    if _sec and evenement_id:
        try:
            _q = 13.0 * mm
            _sec.carton_qr(c, x0 + 2.0 * mm, y0 + 2.5 * mm, _q, evenement_id, serie)
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

    rng = random.Random(930000 + int(serie_start))
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
    pdf = generer_pdf(nb_cartes=8, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89.22.23.05")
    with open("test_moorea.pdf", "wb") as f:
        f.write(pdf.read())
    print("MOOREA généré")
