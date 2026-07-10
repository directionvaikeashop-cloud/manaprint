"""
MANAPRINT — Générateur HAVAI (format A4)
6 cartes par feuille (2 colonnes × 3 rangées).
Chaque carte : en-tête H·A·V·A·I, grille 5×5, 8 numéros TRIÉS en motif :
  H (1-15)  : rangées 1 et 5        A (16-30) : rangée 3
  V (31-45) : rangées 2 et 4        A (46-60) : rangée 3
  I (61-75) : rangées 1 et 5
Cases vides propres. QR de sécurité dans la colonne I (milieu, cases vides).
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
GRIS_GRILLE = colors.Color(0.62, 0.62, 0.62)

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

FOOT_H = 3 * mm
BANDEAU_H = 2.6 * mm
HDR_H = 4.2 * mm
GRID_N = 5

LETTRES = ["H", "A", "V", "A", "I"]
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
# Motif HAVAI : cases pleines (ligne, colonne), lignes numérotées du HAUT
POSITIONS = {
    (0, 0), (0, 4),
    (1, 2),
    (2, 1), (2, 3),
    (3, 2),
    (4, 0), (4, 4),
}
_NB_PAR_COL = [2, 1, 2, 1, 2]


def _gen_carte():
    """8 numéros TRIÉS par colonne selon le motif HAVAI."""
    carte = {}
    for ci, (lo, hi) in enumerate(RANGES):
        nums = sorted(random.sample(range(lo, hi + 1), _NB_PAR_COL[ci]))
        lignes = sorted(r for (r, c) in POSITIONS if c == ci)
        for k, ri in enumerate(lignes):
            carte[(ri, ci)] = nums[k]
    return carte


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / GRID_N

    # Bordure
    c.setStrokeColor(col)
    c.setLineWidth(1.0)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # Mini-bandeau
    bandeau = "LE JEU \u00ab HAVAI \u00bb"
    if titre_jeu:
        bandeau += "  \u2014  " + titre_jeu
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 2.2 * mm, bandeau[:60])

    # En-tête H A V A I
    hdr_y = y0 + CARD_H - BANDEAU_H - HDR_H - 1.0 * mm
    c.setFillColor(col); c.setFont("Helvetica-Bold", 9)
    for i, lettre in enumerate(LETTRES):
        cx = x0 + (i + 0.5) * cell_w
        c.drawCentredString(cx, hdr_y + 1.2 * mm, lettre)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_y, x0 + CARD_W, hdr_y)

    # Grille 5×5
    grid_top = hdr_y
    zone_h = grid_top - (y0 + FOOT_H)
    cell_h = zone_h / GRID_N

    c.setStrokeColor(GRIS_GRILLE); c.setLineWidth(0.35)
    for i in range(1, GRID_N):
        yy = y0 + FOOT_H + i * cell_h
        c.line(x0, yy, x0 + CARD_W, yy)
    for i in range(1, GRID_N):
        xx = x0 + i * cell_w
        c.line(xx, y0 + FOOT_H, xx, grid_top)

    # Numéros (les cases vides restent propres, sans croix)
    taille = 26
    for (ri, ci), n in carte.items():
        cx = x0 + (ci + 0.5) * cell_w
        bas = grid_top - (ri + 1) * cell_h
        cy = bas + cell_h * 0.30
        if _sec:
            _sec.chiffre_micro(c, n, cx, cy, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(cx, cy, str(n))

    # 🎯 QR intégré : colonne I, au milieu (3 cases vides superposées)
    if _sec and evenement_id:
        try:
            _q = 13.0 * mm
            _xq = x0 + 4 * cell_w + (cell_w - _q) / 2
            _yq = grid_top - 3 * cell_h + 4.4 * mm
            _sec.carton_qr(c, _xq, _yq, _q, evenement_id, serie)
        except Exception:
            pass

    # Pied : série centrée (façon maquette) + Resp.
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY); c.setFont("Helvetica", 5)
    c.drawCentredString(x0 + CARD_W / 2, y0 + 1.2 * mm, f"{serie:06d}")
    if telephone:
        c.setFont("Helvetica", 4.5)
        c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, f"Resp. {telephone}")


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
        titre_aff = titre_jeu if titre_jeu else "HAVAI"
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
                carte = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur
                        else "#999999")
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True)
    with open("test_havai.pdf", "wb") as f:
        f.write(pdf.read())
    print("HAVAI g\u00e9n\u00e9r\u00e9")
