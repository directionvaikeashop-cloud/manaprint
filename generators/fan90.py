"""
MANAPRINT — Générateur FAN 90 (format A4)
8 cartes par feuille (2 colonnes × 4 rangées).
Chaque carte : 7 numéros en disposition libre « éventail » :
  • 1 numéro 1-10   dans un SOLEIL (haut gauche)
  • 1 numéro 20-30
  • 2 numéros 31-45
  • 1 numéro 46-59
  • 1 numéro 76-90  dans un CERCLE POINTILLÉ (au centre)
  • 1 numéro 60-75  dans un SOLEIL (bas droit)
Règle du jeu : toutes les boules de 1 à 90 SAUF le 11 à 19.
Cartes jaune soleil (ou couleur_perso / N&B). Gammes ÉCO / PREMIUM.
Microtexte + QR de sécurité.
"""
import io
import math
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les cartons sortent normalement, simplement sans microtexte.
try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None


JAUNE_FAN = "#F2DE00"
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)

# ══ DEUX GAMMES COMMERCIALES (vision Maeva) ══════════════════════════
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
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4

COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

FOOT_H = 3 * mm

# Les 7 places de l'éventail : (plage, position x, position y, décor)
#   positions en fractions de la carte ; décor : "soleil", "cercle" ou ""
PLACES = [
    ((1, 10),  0.16, 0.78, "soleil"),
    ((31, 45), 0.52, 0.80, ""),
    ((20, 30), 0.30, 0.58, ""),
    ((76, 90), 0.52, 0.58, "cercle"),
    ((46, 59), 0.76, 0.58, ""),
    ((31, 45), 0.52, 0.36, ""),
    ((60, 75), 0.80, 0.22, "soleil"),
]


def _gen_carte():
    """Tire les 7 numéros (les deux 31-45 sont distincts)."""
    deux_3145 = random.sample(range(31, 46), 2)
    i31 = 0
    nums = []
    for (lo, hi), _, _, _ in PLACES:
        if (lo, hi) == (31, 45):
            nums.append(deux_3145[i31]); i31 += 1
        else:
            nums.append(random.randint(lo, hi))
    return nums


def _soleil(c, cx, cy, r, col):
    """Dessine un soleil (étoile à 12 branches) autour du point (cx, cy)."""
    p = c.beginPath()
    n = 12
    for i in range(2 * n):
        ang = math.pi / n * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.62
        x = cx + rr * math.cos(ang)
        y = cy + rr * math.sin(ang)
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    p.close()
    c.setStrokeColor(col); c.setLineWidth(1.0)
    c.drawPath(p, stroke=1, fill=0)


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure jaune
    c.setStrokeColor(col)
    c.setLineWidth(1.2)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.8 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # Les 7 numéros de l'éventail
    taille = 24
    for (plage, fx, fy, deco), n in zip(PLACES, nums):
        cx = x0 + fx * CARD_W
        cy = y0 + FOOT_H + fy * (CARD_H - FOOT_H - 2 * mm)
        if deco == "soleil":
            _soleil(c, cx, cy + taille * 0.16, 8.2 * mm, col)
        elif deco == "cercle":
            c.setStrokeColor(col); c.setLineWidth(0.9)
            c.setDash(2.2, 2.0)
            c.circle(cx, cy + taille * 0.16, 6.4 * mm, stroke=1, fill=0)
            c.setDash()
        if _sec:
            _sec.chiffre_micro(c, n, cx, cy, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(cx, cy, str(n))

    # Bandeau règle du jeu (en bas à gauche, comme la maquette)
    bandeau = "Le jeu FAN 90 boules sans le 11 \u00e0 19"
    if titre_jeu:
        bandeau += "  \u2014  " + titre_jeu
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawString(x0 + 2 * mm, y0 + FOOT_H + 1.0 * mm, bandeau[:64])

    # Pied : N° série + responsable
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, f"N\u00b0 {serie:06d}")
    if telephone:
        c.drawRightString(x0 + CARD_W - 1.5 * mm, y0 + 1.3 * mm, f"Resp. {telephone}")

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            _q = 7.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 1.5 * mm, y0 + 1.5 * mm, _q, evenement_id, serie)
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
        titre_aff = titre_jeu if titre_jeu else "FAN 90"
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
                        else JAUNE_FAN if couleur else "#999999")
                _dessiner_carte(c, x0, y0, nums, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=8, couleur=True, titre_jeu="")
    with open("test_fan90.pdf", "wb") as f:
        f.write(pdf.read())
    print("FAN 90 g\u00e9n\u00e9r\u00e9")
