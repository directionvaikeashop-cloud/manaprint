"""
MANAPRINT — Générateur FLASH QUINES DEBOUT (format A4)
8 cartes HAUTES par feuille (4 colonnes × 2 rangées).
Chaque carte : 9 numéros en ZIGZAG (gauche/droite alternés), un par dizaine
du 90 : 1-9 / 10-19 / 20-29 / 30-39 / 40-49 / 50-59 / 60-69 / 70-79 / 80-90.
Les lettres F·L·A·S·H descendent à côté des numéros de gauche.
Cases vides barrées. QR de sécurité dans la bande basse.
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
]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)
GRIS_GRILLE = colors.Color(0.62, 0.62, 0.62)
GRIS_CROIX = colors.Color(0.74, 0.74, 0.74)

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
COLS_PAGE = 4
ROWS_PAGE = 2
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

HDR_H = 5 * mm
BANDE_QR = 18 * mm  # la maison du QR, en bas
N_ROWS = 9

RANGES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 49),
          (50, 59), (60, 69), (70, 79), (80, 90)]
FLASH = ["F", "L", "A", "S", "H"]  # à côté des numéros de gauche (rangées impaires)


def _gen_carte():
    """9 numéros, un par dizaine."""
    return [random.randint(lo, hi) for (lo, hi) in RANGES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 2

    # Bordure
    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.4 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête : série à gauche, titre à droite
    hdr_y = y0 + CARD_H - HDR_H
    c.setFillColor(GREY); c.setFont("Helvetica", 5)
    c.drawString(x0 + 1.5 * mm, hdr_y + 1.4 * mm, f"{serie:06d}")
    c.setFillColor(col); c.setFont("Helvetica-Bold", 5.5)
    titre = "F QUINES 90" if not titre_jeu else titre_jeu[:16]
    c.drawRightString(x0 + CARD_W - 1.5 * mm, hdr_y + 1.4 * mm, titre)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_y, x0 + CARD_W, hdr_y)

    # Grille zigzag 2 colonnes × 9 rangées
    grid_top = hdr_y
    grid_bot = y0 + BANDE_QR
    row_h = (grid_top - grid_bot) / N_ROWS

    c.setStrokeColor(GRIS_GRILLE); c.setLineWidth(0.3)
    for i in range(1, N_ROWS):
        yy = grid_bot + i * row_h
        c.line(x0, yy, x0 + CARD_W, yy)
    c.line(x0 + cell_w, grid_bot, x0 + cell_w, grid_top)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, grid_bot, x0 + CARD_W, grid_bot)

    taille = 25  # bien gros (Maeva, juil. 2026)
    i_flash = 0
    for ri in range(N_ROWS):
        gauche = (ri % 2 == 0)         # zigzag : pair = numéro à gauche
        ci_num = 0 if gauche else 1
        haut = grid_top - ri * row_h
        bas = haut - row_h
        for ci in range(2):
            cx = x0 + (ci + 0.5) * cell_w
            if ci == ci_num:
                cy = bas + row_h * 0.26
                if _sec:
                    _sec.chiffre_micro(c, nums[ri], cx, cy, taille, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                    c.drawCentredString(cx, cy, str(nums[ri]))
                if gauche and i_flash < len(FLASH):
                    c.setFillColor(col); c.setFont("Helvetica", 4.5)
                    c.drawString(cx + 5.5 * mm, cy - 0.2 * mm, FLASH[i_flash])
                    i_flash += 1
            else:
                # case vide barrée
                c.setStrokeColor(GRIS_CROIX); c.setLineWidth(0.35)
                r = 0.34
                c.line(cx - cell_w * r, bas + row_h * (0.5 - r),
                       cx + cell_w * r, bas + row_h * (0.5 + r))
                c.line(cx - cell_w * r, bas + row_h * (0.5 + r),
                       cx + cell_w * r, bas + row_h * (0.5 - r))

    # Bande basse : Resp. à gauche, QR à droite
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    if telephone:
        c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, f"Resp. {telephone}")
    if _sec and evenement_id:
        try:
            _q = 12.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.2 * mm, y0 + 5.4 * mm,
                           _q, evenement_id, serie)
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

    serie = serie_start
    no_page = 1
    encre = NOIR if couleur else GRIS40

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        titre_aff = titre_jeu if titre_jeu else "FLASH QUINES DEBOUT"
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
    pdf = generer_pdf(nb_cartes=8, couleur=True)
    with open("test_flash_debout.pdf", "wb") as f:
        f.write(pdf.read())
    print("FLASH QUINES DEBOUT g\u00e9n\u00e9r\u00e9")
