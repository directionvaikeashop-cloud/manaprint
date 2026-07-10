"""
MANAPRINT — Générateur CERF VOLANT (format A4)
6 cartes par feuille (2 colonnes × 3 rangées).
Disposition en QUEUE DE CERF-VOLANT :
  bloc 2×2 en haut-gauche : 2 numéros 1-15 et 2 numéros 16-30 (triés)
  puis, en diagonale descendante : 1 numéro 46-60, 1 numéro 61-75.
Aucun numéro 31-45 (plage morte). Un cerf-volant souriant décore la carte.
QR de sécurité au coin bas-gauche. Couleur arc-en-ciel / N&B. ÉCO / PREMIUM.
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
GRIS_GRILLE = colors.Color(0.60, 0.60, 0.60)

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
COLS_PAGE = 2
ROWS_PAGE = 3
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

FOOT_H = 3.5 * mm
CELL = 15 * mm


def _gen_carte():
    """(col1 triée 1-15, col2 triée 16-30, n_a 46-60, n_b 61-75)"""
    c1 = sorted(random.sample(range(1, 16), 2))
    c2 = sorted(random.sample(range(16, 31), 2))
    return c1, c2, random.randint(46, 60), random.randint(61, 75)


def _cerf_volant(c, cx, cy, col):
    """Dessine un petit cerf-volant souriant avec sa queue ondulée."""
    h, w = 11 * mm, 8 * mm
    p = c.beginPath()
    p.moveTo(cx, cy + h * 0.55)
    p.lineTo(cx + w * 0.5, cy)
    p.lineTo(cx, cy - h * 0.45)
    p.lineTo(cx - w * 0.5, cy)
    p.close()
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.drawPath(p, stroke=1, fill=0)
    c.setLineWidth(0.4)
    c.line(cx, cy + h * 0.55, cx, cy - h * 0.45)
    c.line(cx - w * 0.5, cy, cx + w * 0.5, cy)
    # visage
    c.setFillColor(col)
    c.circle(cx - 1.2 * mm, cy + 1.6 * mm, 0.45 * mm, stroke=0, fill=1)
    c.circle(cx + 1.2 * mm, cy + 1.6 * mm, 0.45 * mm, stroke=0, fill=1)
    c.setLineWidth(0.5)
    c.arc(cx - 1.5 * mm, cy - 1.8 * mm, cx + 1.5 * mm, cy + 0.4 * mm,
          startAng=200, extent=140)
    # queue ondulée
    c.setLineWidth(0.5)
    b = c.beginPath()
    b.moveTo(cx, cy - h * 0.45)
    b.curveTo(cx - 4 * mm, cy - h * 0.45 - 5 * mm,
              cx + 3 * mm, cy - h * 0.45 - 9 * mm,
              cx - 2 * mm, cy - h * 0.45 - 13 * mm)
    b.curveTo(cx - 6 * mm, cy - h * 0.45 - 16 * mm,
              cx + 1 * mm, cy - h * 0.45 - 19 * mm,
              cx - 3 * mm, cy - h * 0.45 - 22 * mm)
    c.drawPath(b, stroke=1, fill=0)


def _dessiner_carte(c, x0, y0, donnees, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    c1, c2, n_a, n_b = donnees
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure
    c.setStrokeColor(col)
    c.setLineWidth(1.0)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.8 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # Bandeau
    bandeau = "LE JEU \u00ab CERF VOLANT \u00bb"
    if titre_jeu:
        bandeau += "  \u2014  " + titre_jeu
    elif telephone:
        bandeau += f"  \u00b7  by TUKEA {telephone}"
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 2.4 * mm, bandeau[:64])

    taille = 26

    def num(n, xx, yy):
        if _sec:
            _sec.chiffre_micro(c, n, xx, yy, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(xx, yy, str(n))

    def case(bx, btop):
        c.setStrokeColor(GRIS_GRILLE); c.setLineWidth(0.5)
        c.rect(bx, btop - CELL, CELL, CELL, stroke=1, fill=0)

    # Bloc 2×2 haut-gauche
    gx = x0 + 7 * mm
    gtop = y0 + CARD_H - 8 * mm
    grille = [[c1[0], c2[0]], [c1[1], c2[1]]]
    for ri in range(2):
        for ci in range(2):
            bx = gx + ci * CELL
            btop = gtop - ri * CELL
            case(bx, btop)
            num(grille[ri][ci], bx + CELL / 2, btop - CELL + CELL * 0.28)

    # La queue : case 46-60 puis case 61-75 en diagonale
    a_x, a_top = gx + 2 * CELL + 3 * mm, gtop - 2 * CELL + 4 * mm
    case(a_x, a_top)
    num(n_a, a_x + CELL / 2, a_top - CELL + CELL * 0.28)
    b_x, b_top = a_x + CELL + 3 * mm, a_top - CELL - 1 * mm
    case(b_x, b_top)
    num(n_b, b_x + CELL / 2, b_top - CELL + CELL * 0.28)

    # 🎯 QR au coin bas-gauche libre
    if _sec and evenement_id:
        try:
            _q = 13.0 * mm
            _sec.carton_qr(c, x0 + 4 * mm, y0 + FOOT_H + 5.2 * mm,
                           _q, evenement_id, serie)
        except Exception:
            pass

    # Pied : série centrée
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY); c.setFont("Helvetica", 5)
    c.drawCentredString(x0 + CARD_W / 2, y0 + 1.2 * mm, f"{serie:06d}")


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
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
        titre_aff = titre_jeu if titre_jeu else "CERF VOLANT"
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
                donnees = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur
                        else "#999999")
                _dessiner_carte(c, x0, y0, donnees, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True, telephone="89 22 23 05")
    with open("test_cerf_volant.pdf", "wb") as f:
        f.write(pdf.read())
    print("CERF VOLANT g\u00e9n\u00e9r\u00e9")
