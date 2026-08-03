"""
🚀 SPACE X — LA FLOTTE DE FUSÉES (né le 02/08 — hommage de Maeva à Elon Musk)
Chaque carton porte 10 fusées ; chaque fusée emporte 4 numéros triés, UN PAR
TRANCHE : 1-19 · 20-39 · 40-69 · 70-90. 40 numéros par carton, jamais deux
fois le même. Les fusées sont dessinées au trait (économie de toner).
Les fusées sont dessinées AU TRAIT (économie de toner), le ciel de Maeva
passe en filigrane très pâle derrière.
"""
import io
import os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    from generators import securite as _sec
except ImportError:
    try:
        import securite as _sec
    except ImportError:
        _sec = None

_POLICE_ECO = "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("DJBOLDF", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    _POLICE_ECO = "DJBOLDF"
except Exception:
    pass
_GRIS_ECO = colors.Color(0.5, 0.5, 0.5)
_GRIS_P15 = colors.Color(0.25, 0.25, 0.25)


def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_ECO, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
COLS_PAGE, ROWS_PAGE = 1, 1            # UNE grande carte par A4 : les fusées sont hautes
MARGIN_X, MARGIN_TOP, MARGIN_BOT = 10 * mm, 10 * mm, 10 * mm
GUTTER_Y = 5 * mm
CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - GUTTER_Y) / ROWS_PAGE

T_NUM = 32                              # calibre des numéros dans les hublots
GRAINE = 987000                         # graine propre (986000 grillée par les essais)

RAINBOW = ["#E63946", "#2A9D8F", "#457B9D", "#8E7DBE", "#D62828",
           "#6A994E", "#BC6C25", "#7209B7", "#F72585", "#E9C46A"]
# les 3 fusées d'un même carton : trois teintes qui se distinguent d'un coup d'œil
NB_FUSEES = 10                          # 2 rangées de 5 (choix Maeva 02/08)
COLS_FUSEES = 5                         # 5 fusées par rangée
# six teintes qui se distinguent d'un coup d'œil dans la salle
TRIO = [("#2A9D8F", "verte"), ("#457B9D", "bleue"), ("#E63946", "rouge"),
        ("#E9C46A", "or"), ("#7209B7", "violette"), ("#F4A261", "orange")]

_DOSSIER = os.path.dirname(os.path.abspath(__file__))
_CIEL = os.path.join(_DOSSIER, "spacex_ciel.png")

# 🎯 LES QUATRE TRANCHES (choix Maeva 02/08) : 1-19 · 20-39 · 40-69 · 70-90
# Les 9 hublots d'une fusée s'y répartissent au prorata de leur taille.
TRANCHES = [(1, 19), (20, 39), (40, 69), (70, 90)]
PAR_TRANCHE = [1, 1, 1, 1]              # 4 hublots : un par tranche
DIZAINES = [t for t, k in zip(TRANCHES, PAR_TRANCHE) for _ in range(k)]


def _gen_carte(rng):
    """6 fusées × 9 numéros pris dans les 4 tranches (2+2+3+2), triés, sans doublon."""
    pris = set()
    fusees = []
    for _ in range(NB_FUSEES):
        nums = []
        for (a, b), k in zip(TRANCHES, PAR_TRANCHE):
            libres = [n for n in range(a, b + 1) if n not in pris]
            tirage = rng.sample(libres, k)
            pris.update(tirage)
            nums.extend(tirage)
        fusees.append(sorted(nums))
    return fusees


def _fusee(c, cx, bas, larg, haut, nums, col, gris_ch, police_ch,
           evenement_id="", serie=0):
    """Une fusée au trait : pointe (avec le QR au nez), corps à hublots, ailerons."""
    r = larg / 2.0
    corps_h = haut * 0.74
    c.setStrokeColor(col)
    c.setLineWidth(1.1)

    # ── la pointe ──
    p = c.beginPath()
    p.moveTo(cx - r, bas + corps_h)
    p.curveTo(cx - r * 0.75, bas + corps_h + haut * 0.16,
              cx - r * 0.28, bas + corps_h + haut * 0.24, cx, bas + haut)
    p.curveTo(cx + r * 0.28, bas + corps_h + haut * 0.24,
              cx + r * 0.75, bas + corps_h + haut * 0.16, cx + r, bas + corps_h)
    c.drawPath(p, stroke=1, fill=0)

    # ── le corps ──
    c.roundRect(cx - r, bas, larg, corps_h, r * 0.30, stroke=1, fill=0)

    # ── les ailerons ──
    for s in (-1, 1):
        a = c.beginPath()
        a.moveTo(cx + s * r, bas + haut * 0.14)
        a.lineTo(cx + s * (r + larg * 0.42), bas - haut * 0.02)
        a.lineTo(cx + s * r, bas + haut * 0.02)
        a.close()
        c.drawPath(a, stroke=1, fill=0)

    # 🚫 pas de flamme sous la fusée (choix Maeva 02/08) : la grille reste propre

    # ── 🎯 LE QR AU NEZ DE LA FUSÉE (sceau Maeva 02/08) ──
    q = 12 * mm
    place_qr = 0.0
    if _sec and evenement_id:
        try:
            _sec.carton_qr(c, cx - q / 2, bas + corps_h - q - 2.5 * mm, q,
                           evenement_id, serie, avec_code=False)
            place_qr = q + 5.5 * mm
        except Exception:
            place_qr = 0.0

    # ── les hublots numérotés, du haut vers le bas ──
    # 🛟 le rayon suit le PAS : deux hublots ne peuvent jamais se toucher
    marge = larg * 0.14
    haut_h = bas + corps_h - marge - place_qr
    bas_h = bas + marge * 1.6
    pas = (haut_h - bas_h) / (len(nums) - 1)
    rh = min(larg * 0.40, pas * 0.44)
    haut_h -= rh * 0.4
    bas_h += rh * 0.4
    pas = (haut_h - bas_h) / (len(nums) - 1)
    rh = min(larg * 0.40, pas * 0.44)
    for i, n in enumerate(nums):
        cy = haut_h - i * pas
        c.setFillColor(colors.white)
        c.setStrokeColor(col)
        c.setLineWidth(0.7)
        c.circle(cx, cy, rh, stroke=1, fill=1)
        if _sec:
            t = min(T_NUM, rh * 1.35)
            _sec.chiffre_micro(c, n, cx, cy - t * 0.34, t, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            t = min(T_NUM, rh * 1.35)
            c.setFont(police_ch, t)
            c.drawCentredString(cx, cy - t * 0.34, str(n))


def _dessiner_carte(c, x0, y0, fusees, couleur_hex, serie, titre_jeu="", telephone="",
                    style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # 🚫 pas d'image de fond (choix Maeva 02/08) : rien ne gêne les fusées

    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.2 * mm)

    # ── en-tête ──
    tete = "SPACE X \u00b7 la flotte de fus\u00e9es"
    if titre_jeu and titre_jeu.strip().upper() not in ("SPACE X", "SPACEX"):
        tete += "  \u2014  " + titre_jeu.strip()[:26]
    if telephone:
        tete += "  " + str(telephone)[:16]
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 8 * mm, tete[:72])
    c.setFont("Helvetica", 7.4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 12.5 * mm, "Carte N\u00b0 %05d" % serie)

    # ── les 3 fusées ──
    n = len(fusees)
    cols = COLS_FUSEES
    rangs = (n + cols - 1) // cols
    zone_h = (CARD_H - 26 * mm) / rangs - 4 * mm
    pas_x = (CARD_W - 8 * mm) / cols
    larg = pas_x / 1.85                  # les ailerons débordent de 0,42 × larg de chaque côté
    for i, nums in enumerate(fusees):
        r, cc = divmod(i, cols)
        cx = x0 + 4 * mm + pas_x * (cc + 0.5)
        bas = y0 + 10 * mm + (rangs - 1 - r) * (zone_h + 4 * mm)
        teinte = colors.HexColor(TRIO[i % len(TRIO)][0]) if couleur_hex != "#9A9A9A" else col
        _fusee(c, cx, bas, larg, zone_h, nums, teinte, gris_ch, police_ch,
               evenement_id=evenement_id, serie=serie)

    # 🚫 plus de QR au pied : chaque fusée porte le sien au nez


def generer_pdf(nb_cartes=1, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", telephone="", date_lieu="",
                couleur_perso=None, style="eco", evenement_id="", motif=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    rng = random.Random(GRAINE + serie_start)
    serie, faites, no_page = serie_start, 0, 1

    while faites < nb_cartes:
        for row in range(ROWS_PAGE):
            if faites >= nb_cartes:
                break
            x0 = MARGIN_X
            y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
            fusees = _gen_carte(rng)
            coul = (couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
            _dessiner_carte(c, x0, y0, fusees, coul, serie, titre_jeu, telephone,
                            style=style, evenement_id=evenement_id)
            serie += 1
            faites += 1
        c.setFillColor(colors.Color(0.72, 0.72, 0.72))
        c.setFont("Helvetica", 5.4)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 5.5 * mm, "%03d" % no_page)
        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=2, couleur=True, titre_jeu="SPACE X", telephone="89 22 23 05")
    with open("test_spacex.pdf", "wb") as f:
        f.write(pdf.read())
    print("SPACE X généré")
