"""
🅱️ BNG — LA LETTRE ET SA BULLE (né le 05/08, sur l'idée de Maeva)

« Une lettre B avec une bulle qui accroche, et c'est dans cette bulle que
l'on met les chiffres — pareil pour le N et le G. »
Croquis choisi par Tatie : LA BULLE MORDUE — elle chevauche la lettre,
qui semble l'entourer.

RÈGLE : 5 numéros, aux plages du BINGO de la maison —
    B : DEUX numéros dans 1-15
    N : UN   numéro  dans 31-45
    G : DEUX numéros dans 46-60
Les numéros d'une même lettre sont triés.

ENCRE : bulles blanches au trait, aucun aplat. La teinte des chiffres est
imposée par la maison (app.py, gris 0,70 = 30 % d'encre).
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
    pdfmetrics.registerFont(TTFont("DJBOLDBNG", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    _POLICE_ECO = "DJBOLDBNG"
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
COLS_PAGE, ROWS_PAGE = 3, 4   # 12 cartes / A4 (sceau Maeva 10/08)               # 6 cartes / A4 (les bulles respirent)
MARGIN_X, MARGIN_TOP, MARGIN_BOT = 10 * mm, 7 * mm, 10 * mm
GUTTER_X, GUTTER_Y = 5 * mm, 5 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

GRAINE = 988000                            # 987000 = POE
# (lettre, plage, combien de bulles) — les plages du BINGO de la maison
LETTRES = [("B", (1, 15), 2), ("N", (31, 45), 1), ("G", (46, 60), 2)]
TAILLE_LETTRE = 44
TAILLE_CHIFFRE = 30

RAINBOW = ["#6A994E", "#2A9D8F", "#BC6C25", "#457B9D", "#E76F51", "#7209B7",
           "#E63946", "#F4A261", "#8E7DBE", "#264653", "#D62828", "#F72585"]


def _gen_carte(rng):
    """5 numéros : 2 pour le B, 1 pour le N, 2 pour le G — triés."""
    return [sorted(rng.sample(range(lo, hi + 1), combien))
            for _, (lo, hi), combien in LETTRES]


def _bulle(c, cx, cy, r, n, col, gris_ch, police_ch):
    """La bulle qui porte le chiffre : blanche, au trait, avec son reflet.
    Aucun aplat — rien que l'imprimante puisse transformer en pâté noir."""
    c.setFillColor(colors.white)
    c.setStrokeColor(col)
    c.setLineWidth(1.3)
    c.circle(cx, cy, r, stroke=1, fill=1)
    # ⚠️ 10/08 : le chiffre se cale sur SA BULLE, il n'a plus de taille
    # fixe. À 12 grilles la bulle a rétréci ; sans cela les chiffres
    # débordaient du cercle.
    _t = TAILLE_CHIFFRE
    while _t > 12 and _lg("88", "Helvetica-Bold", _t) > r * 2 * 0.76:
        _t -= 0.5
    if _sec:
        _sec.chiffre_micro(c, n, cx, cy - _t * 0.36, _t, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch)
        c.setFont(police_ch, _t)
        c.drawCentredString(cx, cy - _t * 0.36, str(n))
    c.setStrokeColor(colors.Color(0.82, 0.82, 0.82))
    c.setLineWidth(0.5)
    rl = r * 0.30
    gx, gy = cx - r * 0.44, cy + r * 0.44
    c.arc(gx - rl, gy - rl, gx + rl, gy + rl, 20, 150)


def _dessiner_carte(c, x0, y0, groupes, couleur_hex, serie,
                    titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── la ligne d'identité (le nom du jeu s'écrit TOUJOURS) ─────────────
    ligne = "BNG"
    if titre_jeu and titre_jeu.strip().upper() != "BNG":
        ligne += "  \u2014  " + titre_jeu.strip()[:26]
    if telephone:
        ligne += "  \u00b7  " + str(telephone)[:16]
    t = 7.4
    while t > 4.6 and _lg(ligne, "Helvetica-Bold", t) > CARD_W - 8 * mm:
        t -= 0.2
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", t)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 5.6 * mm, ligne)

    # ── les trois lettres, chacune avec ses bulles mordues ──────────────
    haut = y0 + CARD_H - 10.0 * mm
    bas = y0 + 13.0 * mm                  # le QR loge dessous
    zone_h = haut - bas
    # ⚡ 10/08 : la bulle se règle SUR LE CARTON, elle n'a plus de taille
    # fixe. À 12 grilles le carton a rétréci ; sans cela les bulles
    # débordaient et se chevauchaient.
    r_bulle = min(9.5 * mm, zone_h / 7.2, (CARD_W - 8 * mm) / 6.2)
    for i, ((lettre, _plage, _n), nums) in enumerate(zip(LETTRES, groupes)):
        cy = haut - zone_h * (i + 0.5) / len(LETTRES)
        # la lettre a la hauteur de sa bulle : elle reste bien lisible,
        # quelle que soit la taille du carton.
        t_lettre = min(TAILLE_LETTRE, (r_bulle * 2 * 0.80) / mm * 72 / 25.4)
        larg_l = _lg(lettre, "Helvetica-Bold", t_lettre)
        # les bulles : la première MORD la lettre (elle la chevauche d'un
        # cheveu, sans jamais la couvrir), les suivantes s'alignent.
        ecart = 2.6 * mm
        mordu = r_bulle * 0.18
        largeur = (larg_l - mordu) + len(nums) * r_bulle * 2 + (len(nums) - 1) * ecart
        lx = x0 + (CARD_W - largeur) / 2          # le groupe est centré
        # ⚡ 10/08 (sceau Maeva) : la lettre est CREUSE — un contour, et du
        # blanc dedans. Avant, chaque B, N et G était un aplat plein : à
        # trois lettres par carton et douze cartons par feuille, cela
        # faisait beaucoup d'encre pour rien. Le trait suffit à la lire.
        c.setFont("Helvetica-Bold", t_lettre)
        c.setStrokeColor(col)
        c.setFillColor(colors.white)
        c.setLineWidth(max(0.5, t_lettre * 0.022))
        _t = c.beginText(lx, cy - t_lettre * 0.35)
        _t.setTextRenderMode(2)          # 2 = remplir PUIS tracer le contour
        _t.setFont("Helvetica-Bold", t_lettre)
        _t.textOut(lettre)
        c.drawText(_t)
        depart = lx + larg_l - mordu
        for k, n in enumerate(nums):
            bx = depart + r_bulle + k * (r_bulle * 2 + ecart)
            _bulle(c, bx, cy, r_bulle, n, col, gris_ch, police_ch)

    # ── le pied : n° de carte + QR ───────────────────────────────────────
    c.setFillColor(col)
    c.setFont("Helvetica", 5.4)
    c.drawString(x0 + 4.5 * mm, y0 + 3.4 * mm, "Carte N\u00b0 %05d" % serie)
    if _sec and evenement_id:
        try:
            q = 10.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - q - 4.0 * mm, y0 + 2.0 * mm,
                           q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
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
    with open("test_bng.pdf", "wb") as f:
        f.write(generer_pdf(nb_cartes=8, couleur=True, telephone="89 22 23 05").read())
    print("BNG g\u00e9n\u00e9r\u00e9")
