"""
MANAPRINT — Générateur DUAL DAB 75 (format A4)
6 cartes par feuille (2 colonnes × 3 rangées).
Chaque carte : 4 PAIRES + 1 numéro cerclé (pointillés) = 9 numéros :
  haut :  paire 1-15   ·  paire 16-30
  centre : numéro 61-75 dans un cercle pointillé
  bas :   paire 31-45  ·  paire 46-60
Chaque paire est triée et reliée par « / » ou « ↔ » (au hasard).
QR de sécurité au milieu-droit. Couleur arc-en-ciel / N&B. ÉCO / PREMIUM.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

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
HDR_H = 6 * mm

# (plage, position x en fraction, rangée "haut"/"bas")
PAIRES = [
    ((1, 15),  0.26, "haut"),
    ((16, 30), 0.73, "haut"),
    ((31, 45), 0.26, "bas"),
    ((46, 60), 0.73, "bas"),
]
PLAGE_CENTRE = (61, 75)


def _gen_carte():
    """4 paires triées + 1 numéro central ; séparateurs / ou ↔ au hasard."""
    paires = []
    for (lo, hi), fx, rang in PAIRES:
        a, b = sorted(random.sample(range(lo, hi + 1), 2))
        sep = random.choice(["slash", "fleche"])
        paires.append((a, b, sep, fx, rang))
    centre = random.randint(*PLAGE_CENTRE)
    return paires, centre


def _fleche(c, x1, x2, y, col):
    """Dessine une double-flèche ↔ entre x1 et x2 à la hauteur y."""
    c.setStrokeColor(col)
    c.setLineWidth(0.8)
    c.line(x1, y, x2, y)
    a = 1.3 * mm
    c.line(x1, y, x1 + a, y + a * 0.8)
    c.line(x1, y, x1 + a, y - a * 0.8)
    c.line(x2, y, x2 - a, y + a * 0.8)
    c.line(x2, y, x2 - a, y - a * 0.8)


def _dessiner_carte(c, x0, y0, donnees, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    paires, centre = donnees
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure
    c.setStrokeColor(col)
    c.setLineWidth(1.0)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête double : titre à gauche, "by TUKEA" à droite
    hdr_y = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_y, x0 + CARD_W, hdr_y)
    c.line(x0 + CARD_W * 0.44, hdr_y, x0 + CARD_W * 0.44, y0 + CARD_H)
    c.setFillColor(col); c.setFont("Helvetica-Bold", 7)
    titre = titre_jeu[:18] if titre_jeu else "DUAL DAB 75"
    c.drawString(x0 + 3 * mm, hdr_y + 1.8 * mm, titre)
    c.setFillColor(GREY); c.setFont("Helvetica-Oblique", 5)
    droite = f"by TUKEA {telephone}" if telephone else "by TUKEA"
    c.drawRightString(x0 + CARD_W - 3 * mm, hdr_y + 2.0 * mm, droite)

    taille = 30  # GROS chiffres — les cartes sont spacieuses, on en profite !

    def num(n, xx, yy):
        if _sec:
            _sec.chiffre_micro(c, n, xx, yy, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(xx, yy, str(n))

    # Les 4 paires
    for a, b, sep, fx, rang in paires:
        cx = x0 + CARD_W * fx
        yy = y0 + CARD_H * (0.66 if rang == "haut" else 0.14)
        wa = stringWidth(str(a), police_ch, taille)
        wb = stringWidth(str(b), police_ch, taille)
        wsep = 6.2 * mm
        total = wa + wsep + wb
        xa = cx - total / 2 + wa / 2
        xb = cx + total / 2 - wb / 2
        num(a, xa, yy)
        num(b, xb, yy)
        milieu_g = xa + wa / 2 + 1.0 * mm
        milieu_d = xb - wb / 2 - 1.0 * mm
        if sep == "fleche":
            _fleche(c, milieu_g, milieu_d, yy + taille * 0.30, gris_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString((milieu_g + milieu_d) / 2, yy, "/")

    # Le numéro central dans son cercle pointillé
    ccx = x0 + CARD_W / 2
    ccy = y0 + CARD_H * 0.42
    c.setStrokeColor(col); c.setLineWidth(0.7)
    c.setDash(1.6, 1.8)
    c.circle(ccx, ccy + taille * 0.16, 10.0 * mm, stroke=1, fill=0)
    c.setDash()
    num(centre, ccx, ccy)

    # 🎯 QR au milieu-droit (entre les deux rangées de paires)
    if _sec and evenement_id:
        try:
            _q = 13.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.5 * mm,
                           y0 + CARD_H * 0.42 - 5.5 * mm, _q, evenement_id, serie)
        except Exception:
            pass

    # Pied : N° SERIE + numéro
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, "N\u00b0 SERIE")
    c.drawRightString(x0 + CARD_W - 1.5 * mm, y0 + 1.3 * mm, f"{serie:06d}")


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
        titre_aff = titre_jeu if titre_jeu else "DUAL DAB 75"
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
    with open("test_dual_dab.pdf", "wb") as f:
        f.write(pdf.read())
    print("DUAL DAB 75 g\u00e9n\u00e9r\u00e9")
