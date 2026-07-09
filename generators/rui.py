"""
MANAPRINT — Générateur RUI (format A4)
12 cartes par feuille (3 colonnes × 4 rangées).
Chaque carte : en-tête R·u·i, grille 3×3 : 6 numéros + 3 cases barrées
(placées au hasard, au plus 2 par colonne pour garder chaque colonne jouable).
Plages par colonne : R 30-39, u 40-49, i 50-59.
Couleur arc-en-ciel (ou couleur_perso) / N&B. Gammes ÉCO / PREMIUM.
Microtexte + QR de sécurité.
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
GREY = colors.Color(0.42, 0.42, 0.42)
GRIS_CROIX = colors.Color(0.72, 0.72, 0.72)
GRIS_GRILLE = colors.Color(0.55, 0.55, 0.55)

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

COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

RANGES = [(30, 39), (40, 49), (50, 59)]
LETTRES = ["R", "u", "i"]
FOOT_H = 3 * mm
BANDEAU_H = 2.6 * mm
HDR_H = 3.4 * mm
GRID_N = 3  # 3x3


def _gen_carte():
    """3 cases barrées au hasard (max 2 par colonne), 6 numéros : dict {(ligne, col): n} + set barrées."""
    while True:
        barrees = set(random.sample([(r, c) for r in range(3) for c in range(3)], 3))
        if all(sum(1 for (r, c) in barrees if c == ci) <= 2 for ci in range(3)):
            break
    carte = {}
    for ci, (lo, hi) in enumerate(RANGES):
        lignes = [r for r in range(3) if (r, ci) not in barrees]
        nums = random.sample(range(lo, hi + 1), len(lignes))
        for k, ri in enumerate(lignes):
            carte[(ri, ci)] = nums[k]
    return carte, barrees


def _dessiner_carte(c, x0, y0, donnees, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    carte, barrees = donnees
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / GRID_N

    # Bordure
    c.setStrokeColor(col)
    c.setLineWidth(1.0)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # Mini-bandeau : nom du jeu + nom du tournoi (sécurité)
    bandeau = "LE JEU \u00ab RUI \u00bb"
    if titre_jeu:
        bandeau += "  \u2014  " + titre_jeu
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 2.2 * mm, bandeau[:52])

    # En-tête : lettres R u i centrées par colonne
    hdr_y = y0 + CARD_H - BANDEAU_H - HDR_H - 1.2 * mm
    c.setFillColor(col); c.setFont("Helvetica-Bold", 8)
    for i, lettre in enumerate(LETTRES):
        cx = x0 + (i + 0.5) * cell_w
        c.drawCentredString(cx, hdr_y + 1.0 * mm, lettre)
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_y, x0 + CARD_W, hdr_y)

    # Grille 3×3
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

    taille = 24
    for ri in range(GRID_N):
        for ci in range(GRID_N):
            cx = x0 + (ci + 0.5) * cell_w
            haut = grid_top - ri * cell_h
            bas = haut - cell_h
            if (ri, ci) in barrees:
                c.setStrokeColor(GRIS_CROIX); c.setLineWidth(0.4)
                r = 0.36
                c.line(cx - cell_w * r, bas + cell_h * (0.5 - r),
                       cx + cell_w * r, bas + cell_h * (0.5 + r))
                c.line(cx - cell_w * r, bas + cell_h * (0.5 + r),
                       cx + cell_w * r, bas + cell_h * (0.5 - r))
            else:
                n = carte[(ri, ci)]
                cy = bas + cell_h * 0.30
                if _sec:  # chiffres "billet de banque" remplis de microtexte
                    _sec.chiffre_micro(c, n, cx, cy, taille, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                    c.drawCentredString(cx, cy, str(n))

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
        titre_aff = titre_jeu if titre_jeu else "RUI"
        ligne2 = titre_aff
        if date_lieu: ligne2 += "  \u00b7  " + date_lieu
        ligne2 += f"  \u00b7  Page {no_page}"
        c.setFillColor(GREY); c.setFont("Helvetica", 7)
        y2 = (PAGE_H - 8.5 * mm) if nom_evenement else (PAGE_H - 6 * mm)
        c.drawCentredString(PAGE_W / 2, y2, ligne2)

        idx = 0
        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                donnees = _gen_carte()
                if couleur and couleur_perso:
                    coul = couleur_perso
                elif couleur:
                    coul = RAINBOW[(serie - 1) % len(RAINBOW)]
                else:
                    coul = "#999999"
                _dessiner_carte(c, x0, y0, donnees, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1
                idx += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True, titre_jeu="")
    with open("test_rui.pdf", "wb") as f:
        f.write(pdf.read())
    print("RUI g\u00e9n\u00e9r\u00e9")
