"""
MANAPRINT — Générateur LAGOON 5 BOULES (format A4)
12 cartes RONDES par feuille (3 colonnes × 4 rangées).
Chaque cercle : 5 numéros — 1-10 en haut, trio central 11-20 / 21-30 / 31-40,
41-50 en bas. Titre et N° de série à l'intérieur du cercle.
Bande basse réservée au QR de sécurité. Tirage : boules 1 à 50.
Couleur arc-en-ciel (ou couleur_perso) / N&B. Gammes ÉCO / PREMIUM.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None


RAINBOW = [
    "#E53935", "#FF7043", "#FB8C00", "#F9A825",
    "#43A047", "#00ACC1", "#1E88E5", "#3949AB",
    "#8E24AA", "#D81B60", "#6D4C41", "#546E7A",
]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)

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
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

FOOT_H = 3 * mm
RAYON = 29 * mm  # grand cercle : le QR vit À L'INTÉRIEUR

RANGES = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50)]


def _gen_carte():
    """5 numéros : un par plage."""
    return [random.randint(lo, hi) for (lo, hi) in RANGES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cx = x0 + CARD_W / 2
    cy = y0 + FOOT_H + 1 * mm + RAYON

    # Le grand cercle LAGOON
    c.setStrokeColor(col)
    c.setLineWidth(1.1)
    c.circle(cx, cy, RAYON, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, cx - RAYON, cy - RAYON, 2 * RAYON, 2 * RAYON, serie,
                         retrait=-1.2 * mm)

    n_haut, n1, n2, n3, n_bas = nums
    taille = 26

    def chiffre(n, xx, yy):
        if _sec:
            _sec.chiffre_micro(c, n, xx, yy, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(xx, yy, str(n))

    # 1-10 en haut
    chiffre(n_haut, cx, cy + RAYON * 0.52)
    # Titre + série à l'intérieur
    bandeau = "LE JEU \u00ab LAGOON 5 BOULES \u00bb"
    if titre_jeu:
        bandeau = titre_jeu[:34]
    c.setFillColor(GREY); c.setFont("Helvetica", 3.6)
    c.drawCentredString(cx, cy + RAYON * 0.33, bandeau)
    c.setFont("Helvetica", 4.2)
    c.drawCentredString(cx, cy + RAYON * 0.22, f"N\u00b0 {serie:06d}")
    # Trio central 11-20 / 21-30 / 31-40
    yy = cy - RAYON * 0.02
    chiffre(n1, cx - RAYON * 0.58, yy)
    chiffre(n2, cx, yy)
    chiffre(n3, cx + RAYON * 0.58, yy)
    # Bas du cercle : le 41-50 à gauche, le QR à droite — TOUT est dans la grille
    chiffre(n_bas, cx - RAYON * 0.34, cy - RAYON * 0.67)
    if _sec and evenement_id:
        try:
            _q = 12.0 * mm
            _sec.carton_qr(c, cx + 2.5 * mm, cy - 19.5 * mm, _q, evenement_id, serie)
        except Exception:
            pass
    # Pied : Resp. à gauche
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    if telephone:
        c.drawString(x0 + 2 * mm, y0 + 1.3 * mm, f"Resp. {telephone}")


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    serie = serie_start
    no_page = 1
    encre = NOIR if couleur else GRIS40

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        titre_aff = titre_jeu if titre_jeu else "LAGOON 5 BOULES"
        ligne2 = titre_aff
        if date_lieu: ligne2 += "  \u00b7  " + date_lieu
        ligne2 += f"  \u00b7  Page {no_page}"
        c.setFillColor(GREY); c.setFont("Helvetica", 7)
        y2 = (PAGE_H - 8.5 * mm) if nom_evenement else (PAGE_H - 6 * mm)
        c.drawCentredString(PAGE_W / 2, y2, ligne2)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                nums = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur
                        else "#999999")
                _dessiner_carte(c, x0, y0, nums, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True)
    with open("test_lagoon.pdf", "wb") as f:
        f.write(pdf.read())
    print("LAGOON g\u00e9n\u00e9r\u00e9")
