"""
MANAPRINT — Générateur TRIPLE ACTION 75 (format A4)
Modèle d'origine Ticket Bingo : 10 tickets par feuille A4 (5 colonnes × 2 rangées).
Chaque ticket : 5 groupes empilés T/R/I/P/L, cercle + grand + petit numéro.
Chiffres gros et noirs. Couleurs arc-en-ciel alternant carte par carte.
Ligne de découpe entre les deux rangées, numéro de page en haut.
"""
import io
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


RAINBOW = [
    "#E53935", "#FF7043", "#FB8C00", "#F9A825",
    "#43A047", "#00ACC1", "#1E88E5", "#3949AB",
    "#8E24AA", "#D81B60", "#6D4C41", "#546E7A",
]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
  # gris 40% (mode noir & blanc)
GREY = colors.Color(0.42, 0.42, 0.42)


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

COLS = 5
ROWS = 2
MARGIN_X = 6 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 6 * mm
GUTTER_X = 2 * mm
CUT_GAP = 6 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS - 1) * GUTTER_X) / COLS
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - CUT_GAP) / ROWS

HDR_H = 7 * mm
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
LETTERS = ["T", "R", "I", "P", "L"]


def _gen_grille():
    return [sorted(random.sample(range(lo, hi + 1), 3)) for (lo, hi) in RANGES]


def _dessiner_ticket(c, x0, y0, grille, couleur_hex, serie, couleur=True, titre_jeu="", telephone="", style="eco"):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    encre = NOIR if couleur else GRIS40  # chiffres noirs en couleur, gris 40% en N&B

    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    hdr_y = y0 + CARD_H - HDR_H
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", 11)
    lettres = "TRIPL"
    n = len(lettres)
    for i, lettre in enumerate(lettres):
        lx = x0 + CARD_W * (i + 0.5) / (n + 1)
        c.drawCentredString(lx, hdr_y + 3.5 * mm, lettre)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x0 + CARD_W * (n + 0.5) / (n + 1), hdr_y + 3.5 * mm, "75")

    c.setFillColor(GREY)
    c.setFont("Helvetica", 5)
    serie_txt = f"N° {serie:06d}"
    if titre_jeu:
        serie_txt += "  ·  " + titre_jeu[:22]
    c.drawCentredString(x0 + CARD_W / 2, hdr_y + 2.4 * mm, serie_txt)
    if telephone:
        c.setFont("Helvetica", 4.5)
        c.drawCentredString(x0 + CARD_W / 2, hdr_y + 0.7 * mm, f"Resp. {telephone}")

    c.setStrokeColor(col)
    c.setLineWidth(0.5)
    c.line(x0 + 2 * mm, hdr_y - 0.6 * mm, x0 + CARD_W - 2 * mm, hdr_y - 0.6 * mm)

    body_h = CARD_H - HDR_H
    group_h = body_h / 5
    for gi, nums in enumerate(grille):
        gy = y0 + body_h - (gi + 1) * group_h
        cx = x0 + CARD_W / 2
        num_cercle, num_grand, num_petit = nums

        cercle_x = x0 + CARD_W * 0.28
        cercle_y = gy + group_h * 0.60
        rayon = 6.4 * mm
        c.setStrokeColor(col)
        c.setLineWidth(0.9)
        c.circle(cercle_x, cercle_y, rayon, stroke=1, fill=0)
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, num_cercle, cercle_x, cercle_y - 9, 26, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, 26)
            c.drawCentredString(cercle_x, cercle_y - 9, str(num_cercle))

        grand_x = x0 + CARD_W * 0.70
        if _sec:
            _sec.chiffre_micro(c, num_grand, grand_x, cercle_y - 9, 26, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, 26)
            c.drawCentredString(grand_x, cercle_y - 9, str(num_grand))

        if _sec:
            _sec.chiffre_micro(c, num_petit, cx, gy + group_h * 0.04, 26, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, 26)
            c.drawCentredString(cx, gy + group_h * 0.04, str(num_petit))

        if gi < 4:
            c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))
            c.setLineWidth(0.3)
            c.line(x0 + 3 * mm, gy, x0 + CARD_W - 3 * mm, gy)


def generer_pdf(nb_tickets=10, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco"):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_tickets = max(1, min(int(nb_tickets), 1000))
    par_page = COLS * ROWS
    nb_pages = (nb_tickets + par_page - 1) // par_page

    serie = serie_start
    no_page = 1
    for _ in range(nb_pages):
        # En-tête de page : nom événement (gros) + titre jeu + date/lieu + n° page
        if nom_evenement:
            c.setFillColor(NOIR)
            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        titre_aff = titre_jeu if titre_jeu else "TRIPLE ACTION 75"
        ligne2 = titre_aff
        if date_lieu:
            ligne2 += "  ·  " + date_lieu
        ligne2 += f"  ·  Page {no_page}"
        c.setFillColor(GREY)
        c.setFont("Helvetica", 7)
        y_ligne2 = (PAGE_H - 8.5 * mm) if nom_evenement else (PAGE_H - 6 * mm)
        c.drawCentredString(PAGE_W / 2, y_ligne2, ligne2)

        for row in range(ROWS):
            for col_i in range(COLS):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                if row == 0:
                    y0 = MARGIN_BOT + CARD_H + CUT_GAP
                else:
                    y0 = MARGIN_BOT
                grille = _gen_grille()
                if not couleur:
                    coul = "#999999"
                elif couleur_perso:
                    coul = couleur_perso
                else:
                    coul = RAINBOW[(serie - 1) % len(RAINBOW)]
                _dessiner_ticket(c, x0, y0, grille, coul, serie, couleur, titre_jeu, telephone, style=style)
                serie += 1

        cut_y = MARGIN_BOT + CARD_H + CUT_GAP / 2
        c.setStrokeColor(GREY)
        c.setLineWidth(0.4)
        c.setDash(2, 2)
        c.line(MARGIN_X, cut_y, PAGE_W - MARGIN_X, cut_y)
        c.setDash()
        c.setFillColor(GREY)
        c.setFont("Helvetica", 8)
        c.drawString(MARGIN_X, cut_y + 1, "\u2702")

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_tickets=10, serie_start=1)
    with open("test_ta75_a4.pdf", "wb") as f:
        f.write(pdf.read())
    print("PDF A4 généré : test_ta75_a4.pdf")
