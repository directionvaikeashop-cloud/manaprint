"""
🦪 POE — LE JEU DE LA PERLE (né le 05/08, d'après le cadre ovale de Maeva)

⚠️ POE et POE PARAU sont DEUX JEUX DIFFÉRENTS.

LE MODÈLE : chaque numéro vit dans SON médaillon — le cadre ovale du dessin
de Maeva, où le mot du milieu est remplacé par le CHIFFRE et la fleur de
vanille par une PERLE (dessinée au trait, comme celles de POE PARAU).
Six médaillons par carton.

RÈGLE : 6 numéros, DEUX par plage — 45-60 · 61-75 · 76-90 — triés.
ENCRE : tout est au trait, aucun aplat. La teinte des chiffres est imposée
par la maison (app.py, gris 0,70 = 30 % d'encre).
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg

try:
    from generators import securite as _sec
except ImportError:
    try:
        import securite as _sec
    except ImportError:
        _sec = None

_POLICE_ECO = "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("DJBOLDPOE", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    _POLICE_ECO = "DJBOLDPOE"
except Exception:
    pass
_POLICE_P15 = _POLICE_ECO
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)     # imposé au boot par app.py
_GRIS_P15 = colors.Color(0.25, 0.25, 0.25)


def _style_chiffres(style):
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
COLS_PAGE, ROWS_PAGE = 2, 3               # 6 cartes / A4
MARGIN_X, MARGIN_TOP, MARGIN_BOT = 9 * mm, 6 * mm, 9 * mm
GUTTER_X, GUTTER_Y = 4 * mm, 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

GRAINE = 987000                            # 986000 = VANILLE DE DONA
PLAGES = [(45, 60), (61, 75), (76, 90)]    # 2 numéros par plage
TAILLE_CHIFFRE = 30

# la grille des médaillons : 2 colonnes × 3 rangées, une rangée par plage
MED_COLS, MED_ROWS = 2, 3

RAINBOW = ["#6A994E", "#2A9D8F", "#BC6C25", "#457B9D", "#E76F51", "#7209B7",
           "#E63946", "#F4A261", "#8E7DBE", "#264653", "#D62828", "#F72585"]


def _gen_carte(rng):
    """6 numéros : deux par plage, triés."""
    return [sorted(rng.sample(range(lo, hi + 1), 2)) for lo, hi in PLAGES]


def _perle(c, cx, cy, r, col):
    """🦪 La perle AU TRAIT (recette de POE PARAU) : ventre blanc, un cercle
    fin, un arc de galbe et un reflet. Aucun aplat : rien que l'imprimante
    puisse transformer en pâté noir."""
    c.setFillColor(colors.white)
    c.setStrokeColor(col)
    c.setLineWidth(0.8)
    c.circle(cx, cy, r, stroke=1, fill=1)
    c.setStrokeColor(colors.Color(0.74, 0.74, 0.74))
    c.setLineWidth(0.45)
    rg = r * 0.84
    c.arc(cx - rg, cy - rg, cx + rg, cy + rg, -75, 150)
    c.setStrokeColor(colors.Color(0.84, 0.84, 0.84))
    c.setLineWidth(0.4)
    rl = r * 0.32
    gx, gy = cx - r * 0.38, cy + r * 0.38
    c.arc(gx - rl, gy - rl, gx + rl, gy + rl, 20, 150)


def _medaillon(c, cx, cy, demi_l, demi_h, n, col, gris_ch, police_ch):
    """UN numéro dans SON cadre ovale, avec sa perle — le dessin de Maeva,
    le chiffre à la place du mot et la perle à la place de la fleur."""
    # l'ovale
    c.setStrokeColor(col)
    c.setLineWidth(1.6)
    c.ellipse(cx - demi_l, cy - demi_h, cx + demi_l, cy + demi_h, stroke=1, fill=0)

    # le chiffre, au cœur (légèrement décalé pour laisser sa place à la perle)
    nx = cx + demi_l * 0.16
    ny = cy - TAILLE_CHIFFRE * 0.36
    if _sec:
        _sec.chiffre_micro(c, n, nx, ny, TAILLE_CHIFFRE, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch)
        c.setFont(police_ch, TAILLE_CHIFFRE)
        c.drawCentredString(nx, ny, str(n))

    # la perle, posée sur le bord bas-gauche, avec ses brins
    r_perle = demi_h * 0.52
    px = cx - demi_l * 0.80
    py = cy - demi_h * 0.62
    c.setStrokeColor(col)
    c.setLineWidth(0.6)
    for hauteur, portee, creux in ((0.85, 1.55, 0.55), (0.25, 1.25, 0.30)):
        x1 = px + r_perle * portee * 1.5
        y1 = py + r_perle * creux
        p = c.beginPath()
        p.moveTo(px + r_perle * 0.55, py + r_perle * hauteur * 0.5)
        p.curveTo(px + r_perle * portee * 0.6, py + r_perle * hauteur,
                  x1 - r_perle * 0.5, y1 + r_perle * 0.25, x1, y1)
        c.drawPath(p, stroke=1, fill=0)
    _perle(c, px, py, r_perle, col)


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie,
                    titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── la ligne d'identité (le nom du jeu s'écrit TOUJOURS) ─────────────
    ligne = "POE"
    if titre_jeu and titre_jeu.strip().upper() != "POE":
        ligne += "  \u2014  " + titre_jeu.strip()[:26]
    if telephone:
        ligne += "  \u00b7  " + str(telephone)[:16]
    t = 7.4
    while t > 4.6 and _lg(ligne, "Helvetica-Bold", t) > CARD_W - 8 * mm:
        t -= 0.2
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", t)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 6.0 * mm, ligne)

    # ── les 6 médaillons : une rangée par plage ─────────────────────────
    haut = y0 + CARD_H - 10.5 * mm
    bas = y0 + 14.5 * mm          # le QR loge dessous, sans mordre le médaillon
    zone_h = haut - bas
    case_w = (CARD_W - 6 * mm) / MED_COLS
    case_h = zone_h / MED_ROWS
    demi_l = case_w * 0.455
    demi_h = case_h * 0.40
    for r, duo in enumerate(cols_nums):          # une rangée par plage
        for k, n in enumerate(duo):
            cx = x0 + 3 * mm + case_w * (k + 0.5)
            cy = haut - case_h * (r + 0.5)
            _medaillon(c, cx, cy, demi_l, demi_h, n, col, gris_ch, police_ch)

    # ── le pied : n° de carte + QR ───────────────────────────────────────
    c.setFillColor(col)
    c.setFont("Helvetica", 5.4)
    c.drawString(x0 + 4.5 * mm, y0 + 3.6 * mm, "Carte N\u00b0 %05d" % serie)
    if _sec and evenement_id:
        try:
            q = 10.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - q - 4.0 * mm, y0 + 2.2 * mm,
                           q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", telephone="", date_lieu="",
                couleur_perso=None, style="eco", evenement_id="", motif=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    rng = random.Random(GRAINE + serie_start)
    serie, faites, no_page = serie_start, 0, 1

    while faites < nb_cartes:
        for row in range(ROWS_PAGE):
            for coln in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + coln * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, _gen_carte(rng), coul, serie,
                                titre_jeu, telephone, style=style,
                                evenement_id=evenement_id)
                serie += 1
                faites += 1
        c.setFillColor(colors.Color(0.72, 0.72, 0.72))
        c.setFont("Helvetica", 5.4)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, "%03d" % no_page)
        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    with open("test_poe.pdf", "wb") as f:
        f.write(generer_pdf(nb_cartes=6, couleur=True, telephone="89 22 23 05").read())
    print("POE g\u00e9n\u00e9r\u00e9")
