# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur HUAHINE (format A4)
8 cartes par feuille A4 (2 colonnes × 4 rangées). Le jeu « pour 6 boules ».
Chaque carte : 6 numéros disposés en croix (fidèle au modèle) :
  coin HAUT-GAUCHE  (1-15)     coin HAUT-DROIT  (76-90)
        PAIRE CENTRALE côte à côte (46-60)
  coin BAS-GAUCHE   (1-15)     coin BAS-DROIT   (76-90)
En-tête : « Le jeu HUAHINE · pour 6 boules by TUKEA Tél : … »
Pied de carte : « N° SERIE | 036001 ».
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
# Les 3 familles de HUAHINE : gauche 1-15, centre 46-60, droite 76-90 (2 numéros chacune)
PLAGE_G = (1, 15)
PLAGE_C = (46, 60)
PLAGE_D = (76, 90)

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
    """6 numéros : 2 à gauche (1-15), 2 au centre (46-60), 2 à droite (76-90)."""
    g = rng.sample(range(PLAGE_G[0], PLAGE_G[1] + 1), 2)
    cmid = sorted(rng.sample(range(PLAGE_C[0], PLAGE_C[1] + 1), 2))
    d = rng.sample(range(PLAGE_D[0], PLAGE_D[1] + 1), 2)
    # (haut-gauche, haut-droit, centre-1, centre-2, bas-gauche, bas-droit)
    return (g[0], d[0], cmid[0], cmid[1], g[1], d[1])


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    hg, hd, c1, c2, bg, bd = nums

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête — le nom du jeu apparaît TOUJOURS (fidèle au modèle)
    hdr_y = y0 + CARD_H - 3.6 * mm
    titre = "Le jeu HUAHINE · pour 6 boules"
    if titre_jeu and "HUAHINE" not in titre_jeu.strip().upper():
        titre += " · " + titre_jeu.strip()
    titre += " by TUKEA" + ((" Tél : " + telephone) if telephone else "")
    c.setFillColor(col); c.setFont(POLICE, 4.8)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y, titre[:78])

    # Pied de carte : « N° SERIE | 036001 »
    PIED_H = 4.6 * mm
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0 + 1.5 * mm, y0 + PIED_H, x0 + CARD_W - 1.5 * mm, y0 + PIED_H)
    c.line(x0 + CARD_W * 0.42, y0 + 0.8 * mm, x0 + CARD_W * 0.42, y0 + PIED_H - 0.6 * mm)
    c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.2)
    c.drawString(x0 + 3 * mm, y0 + 1.6 * mm, "N\u00b0 SERIE")
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawRightString(x0 + CARD_W - 3 * mm, y0 + 1.5 * mm, "%06d" % serie)

    # Zone de jeu (entre l'en-tête et le pied)
    z_bot = y0 + PIED_H + 2 * mm
    z_top = hdr_y - 3 * mm
    z_h = z_top - z_bot
    taille = 36  # bien gros (Maeva, juil. 2026)
    positions = [
        (hg, x0 + CARD_W * 0.13, z_bot + z_h * 0.80),   # haut-gauche  (1-15)
        (hd, x0 + CARD_W * 0.87, z_bot + z_h * 0.80),   # haut-droit   (76-90)
        (c1, x0 + CARD_W * 0.38, z_bot + z_h * 0.47),   # centre-1     (46-60)
        (c2, x0 + CARD_W * 0.62, z_bot + z_h * 0.47),   # centre-2     (46-60)
        (bg, x0 + CARD_W * 0.13, z_bot + z_h * 0.14),   # bas-gauche   (1-15)
        (bd, x0 + CARD_W * 0.87, z_bot + z_h * 0.14),   # bas-droit    (76-90)
    ]
    for val, px, py in positions:
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, val, px, py - taille * 0.36, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(px, py - taille * 0.36, str(val))

    # QR de vérification par carte (anti-duplication) — centre bas, entre les coins
    if _sec and evenement_id:
        try:
            _q = 13.0 * mm
            _sec.carton_qr(c, x0 + (CARD_W - _q) / 2, y0 + PIED_H + 1.2 * mm, _q, evenement_id, serie)
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

    rng = random.Random(975000 + int(serie_start))
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
                      telephone="87 77 34 26")
    with open("test_huahine.pdf", "wb") as f:
        f.write(pdf.read())
    print("HUAHINE généré")
