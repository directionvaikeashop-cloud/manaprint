# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TCHIN (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées), GROS CADRE épais
(fidèle au modèle rose fuchsia — le cadre prend la couleur de la carte).
Chaque carte : 5 numéros « pour 5 boules » :
  en haut, le GRAND numéro 11-20 (×1)
  colonne gauche : 1-10 (×2)  ·  colonne droite : 21-30 (×2)
En-tête : « Le jeu TCHIN pour 5 boules by TUKEA … » (le nom TOUJOURS visible).
QR de vérification en bas au centre, série discrète en bas à gauche.
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
PLAGE_HAUT = (11, 20)     # le grand numéro du haut
PLAGE_GAUCHE = (1, 10)    # colonne gauche (×2)
PLAGE_DROITE = (21, 30)   # colonne droite (×2)

COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
CADRE = 2.6 * mm          # l'épaisseur du GROS cadre (fidèle au modèle)


def _gen_carte(rng):
    """5 numéros : 1 grand (11-20), 2 à gauche (1-10), 2 à droite (21-30)."""
    haut = rng.randint(*PLAGE_HAUT)
    g = rng.sample(range(PLAGE_GAUCHE[0], PLAGE_GAUCHE[1] + 1), 2)
    d = rng.sample(range(PLAGE_DROITE[0], PLAGE_DROITE[1] + 1), 2)
    return haut, g, d


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    haut, gauche, droite = nums

    # LE GROS CADRE (fidèle au modèle) : rectangle plein + fenêtre blanche
    c.setFillColor(col)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.2 * mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.rect(x0 + CADRE, y0 + CADRE, CARD_W - 2 * CADRE, CARD_H - 2 * CADRE, stroke=0, fill=1)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0 + CADRE, y0 + CADRE, CARD_W - 2 * CADRE, CARD_H - 2 * CADRE,
                         serie, retrait=0.8 * mm)

    ix0 = x0 + CADRE
    iw = CARD_W - 2 * CADRE
    ih = CARD_H - 2 * CADRE
    iy0 = y0 + CADRE

    # Le GRAND numéro du haut (11-20)
    t_grand = 40  # bien gros (Maeva)
    if _sec:
        _sec.chiffre_micro(c, haut, ix0 + iw / 2, iy0 + ih - t_grand * 0.92, t_grand, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch); c.setFont(police_ch, t_grand)
        c.drawCentredString(ix0 + iw / 2, iy0 + ih - t_grand * 0.92, str(haut))

    # En-tête 2 lignes — le nom du jeu apparaît TOUJOURS (fidèle au modèle)
    l1 = "Le jeu TCHIN pour 5 boules by TUKEA"
    if titre_jeu and "TCHIN" not in titre_jeu.strip().upper():
        l1 = "Le jeu TCHIN \u00b7 " + titre_jeu.strip() + " by TUKEA"
    l2 = telephone if telephone else "manaprint.app"
    c.setFillColor(col); c.setFont(POLICE, 4.2)
    c.drawCentredString(ix0 + iw / 2, iy0 + ih * 0.615, l1[:58])
    c.setFont(POLICE, 4.2)
    c.drawCentredString(ix0 + iw / 2, iy0 + ih * 0.565, l2[:40])

    # Colonnes gauche (1-10) et droite (21-30) : 2 numéros chacune
    taille = 38  # bien gros (Maeva)
    for vals, fx in ((gauche, 0.22), (droite, 0.78)):
        for val, fy in zip(vals, (0.42, 0.185)):
            cx = ix0 + iw * fx
            cy = iy0 + ih * fy
            if _sec:
                _sec.chiffre_micro(c, val, cx, cy - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cy - taille * 0.36, str(val))

    # Série discrète + QR de vérification en bas au centre
    c.setFillColor(col); c.setFont(POLICE, 4.4)
    c.drawString(ix0 + 1.6 * mm, iy0 + 1.4 * mm, "N\u00b0 %06d" % serie)
    if _sec and evenement_id:
        try:
            _q = 11.5 * mm
            _sec.carton_qr(c, ix0 + (iw - _q) / 2, iy0 + 1.2 * mm, _q, evenement_id, serie)
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

    rng = random.Random(932600 + int(serie_start))
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
    with open("test_tchin.pdf", "wb") as f:
        f.write(pdf.read())
    print("TCHIN généré")
