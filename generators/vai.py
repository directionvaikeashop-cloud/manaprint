# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur VAI 9 BOULES (format A4)

💧 REFAIT LE 08/08 (sceau Maeva, sur son dessin de gouttes) : VAI, c'est
l'eau — alors les NEUF NUMÉROS tombent chacun DANS SA GOUTTE, en pluie
sur le carton : cinq gouttes en haut, quatre en dessous, en quinconce.

RÈGLE INCHANGÉE : 9 numéros, trois colonnes de dizaines —
  61-70 · 71-80 · 81-90
Le sac du crieur ne change donc pas d'un chiffre.

⚡ ÉCONOMIE D'ENCRE : les gouttes sont DESSINÉES AU TRAIT, pas posées en
image. Aucun aplat, rien à décompresser.
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgv
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
GRIS40 = colors.Color(0.60, 0.60, 0.60)
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
# (min, max) par colonne — VAI 9 boules
PLAGES = [(61, 70), (71, 80), (81, 90)]

COLS_PAGE = 2   # 8 cartes / A4 (choix Maeva 08/08 : garder le calibre 30 pt)
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """9 numéros : col1 = 3 nums (1-9), col2 = 3 nums (10-18), col3 = 3 nums (19-27).
    Grille 3×3 entièrement remplie."""
    col1 = sorted(rng.sample(range(PLAGES[0][0], PLAGES[0][1] + 1), 3))
    col2 = sorted(rng.sample(range(PLAGES[1][0], PLAGES[1][1] + 1), 3))
    col3 = sorted(rng.sample(range(PLAGES[2][0], PLAGES[2][1] + 1), 3))
    grille = [
        [col1[0], col2[0], col3[0]],
        [col1[1], col2[1], col3[1]],
        [col1[2], col2[2], col3[2]],
    ]
    return grille


def _goutte(c, cx, cy, larg, col):
    """💧 UNE goutte au trait : pointe en haut, ventre rond en bas, et le
    petit reflet en arc — le dessin de Maeva. Tout au trait, aucun aplat."""
    r = larg / 2.0
    haut = larg * 1.42
    bas = cy - haut * 0.44
    pointe = cy + haut * 0.56
    ventre = bas + r
    c.setFillColor(colors.white)
    c.setStrokeColor(col)
    c.setLineWidth(0.75)
    p = c.beginPath()
    p.moveTo(cx, pointe)
    p.curveTo(cx + r * 0.52, ventre + r * 1.15, cx + r, ventre + r * 0.62, cx + r, ventre)
    p.curveTo(cx + r, ventre - r * 0.56, cx + r * 0.56, bas, cx, bas)
    p.curveTo(cx - r * 0.56, bas, cx - r, ventre - r * 0.56, cx - r, ventre)
    p.curveTo(cx - r, ventre + r * 0.62, cx - r * 0.52, ventre + r * 1.15, cx, pointe)
    c.drawPath(p, stroke=1, fill=1)
    c.setLineWidth(0.45)
    a = c.beginPath()
    a.moveTo(cx - r * 0.72, ventre + r * 0.18)
    a.curveTo(cx - r * 0.84, ventre - r * 0.14,
              cx - r * 0.72, ventre - r * 0.44, cx - r * 0.48, ventre - r * 0.58)
    c.drawPath(a, stroke=1, fill=0)
    return ventre


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 3

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête (2 lignes : titre + N° carte)
    hdr_y = y0 + CARD_H - 3.5 * mm
    titre = "VAI 9 boules"
    if titre_jeu and titre_jeu.strip().upper() != titre.upper():
        titre += "  —  " + titre_jeu.strip()
    if telephone:
        titre += " " + telephone
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y, titre[:60])
    c.setFillColor(col); c.setFont(POLICE, 6.5)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y - 4 * mm, "Carte N° %05d" % serie)

    # Zone grille 3×3
    grid_top = hdr_y - 6.5 * mm
    # 📏 08/08 : la bande du bas passe de 21 a 9 mm. Elle etait taillee
    # pour l'ancien carton ; en la reduisant, les gouttes retrouvent la
    # hauteur qu'il leur faut et les chiffres gardent leur calibre de 30 pt.
    grid_bot = y0 + 9 * mm
    cell_w = CARD_W / ncols
    grid_h = grid_top - grid_bot
    row_h = grid_h / 3

    # ═══ 💧 LA PLUIE DE NEUF GOUTTES ═══
    # Cinq en haut, quatre en dessous — un vrai rideau de pluie. Les
    # places ont ete CALCULEES pour que le calibre de 30 pt tienne dans
    # le ventre de chaque goutte.
    ZW, ZH = 91.0, 47.0
    L_G = 16.5
    GOUTTES = [[9.1, 34.78], [27.3, 34.78], [45.5, 34.78], [63.7, 34.78], [81.9, 34.78], [11.38, 12.22], [34.12, 12.22], [56.88, 12.22], [79.62, 12.22]]
    ex = (CARD_W - 4 * mm) / (ZW * mm)
    ey = (grid_top - grid_bot) / (ZH * mm)
    ech = min(ex, ey)
    lg = L_G * mm * ech
    taille = 30.0
    while taille > 12 and _lgv("88", "Helvetica-Bold", taille) > lg * 0.74:
        taille -= 0.5
    plat = [grille[r][cc] for r in range(3) for cc in range(3)]
    for (gx_mm, gy_mm), val in zip(GOUTTES, plat):
        gx = x0 + 2 * mm + gx_mm * mm * ex
        gy = grid_bot + gy_mm * mm * ey
        ventre = _goutte(c, gx, gy, lg, col)
        ny = ventre - taille * 0.30 + lg * 0.04
        if _sec:
            _sec.chiffre_micro(c, val, gx, ny, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(gx, ny, str(val))

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            # 🎯 QR dans la bande dédiée (aucun chiffre dérangé)
            _q = 13.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.0 * mm, y0 + 1.4 * mm,
                           _q, evenement_id, serie, avec_code=False)
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

    rng = random.Random(920000 + int(serie_start))
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
                grille = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, grille, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="VAI 9 boules",
                      telephone="89.22.23.05")
    with open("test_pow.pdf", "wb") as f:
        f.write(pdf.read())
    print("VAI 9 boules généré")
