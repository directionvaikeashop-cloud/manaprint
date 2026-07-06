"""
MANAPRINT — Générateur BINGO BALL (format A4)
Design en croix. 10 cartes par feuille (2 colonnes × 5 rangées).
Chaque carte :
  - ligne horizontale de 5 numéros : B(1-15) I(16-30) N(31-45) G(46-60) O(61-75)
  - colonne verticale centrale : 1 numéro en haut + le numéro central de la ligne + 1 en bas
    (les 3 numéros verticaux sont dans la plage N 31-45)
  - titre "BINGO BALL" + N° série au-dessus du numéro haut
Responsable sur chaque grille. Couleur arc-en-ciel ou gris 40%.
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

COLS_PAGE = 2
ROWS_PAGE = 5
MARGIN_X = 8 * mm
MARGIN_TOP = 12 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 8 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]


def _gen_carte():
    """Ligne de 5 numéros + 2 numéros verticaux (plage N) distincts du central."""
    ligne = [random.randint(lo, hi) for (lo, hi) in RANGES]
    central = ligne[2]  # numéro N de la ligne
    # 2 autres numéros dans 31-45, différents du central
    pool = [n for n in range(31, 46) if n != central]
    haut, bas = sorted(random.sample(pool, 2))
    return ligne, haut, bas


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre, telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ligne, haut, bas = carte

    # Cadre extérieur de toute la carte (visuel fini)
    c.setStrokeColor(col); c.setLineWidth(1.2)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # 5 cases de la ligne horizontale
    cell_w = CARD_W / 5
    cell_h = 12 * mm
    # ligne centrée verticalement
    ligne_y = y0 + (CARD_H - cell_h) / 2 - 3 * mm

    # case verticale (même largeur que cell_w) : haut au-dessus, bas en-dessous
    cx_centre = x0 + 2 * cell_w  # case du milieu (index 2)

    # --- numéro du haut (sans cadre interne) ---
    haut_y = ligne_y + cell_h
    c.setFillColor(col); c.setFont("Helvetica-Bold", 7)
    titre_aff = "BINGO BALL"
    if titre_jeu:
        titre_aff += "  —  " + titre_jeu[:30]
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 4 * mm, titre_aff)
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 6.5 * mm, f"N° {serie:06d}")
    if _sec:
        _sec.chiffre_micro(c, haut, cx_centre + cell_w / 2, haut_y + cell_h * 0.30, 30, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch); c.setFont(police_ch, 30)
        c.drawCentredString(cx_centre + cell_w / 2, haut_y + cell_h * 0.30, str(haut))

    # --- ligne horizontale de 5 numéros (sans cadres internes) ---
    for i, num in enumerate(ligne):
        cx = x0 + i * cell_w
        if _sec:
            _sec.chiffre_micro(c, num, cx + cell_w / 2, ligne_y + cell_h * 0.30, 30, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, 30)
            c.drawCentredString(cx + cell_w / 2, ligne_y + cell_h * 0.30, str(num))

    # --- numéro du bas (sans cadre interne) ---
    bas_y = ligne_y - cell_h
    if _sec:
        _sec.chiffre_micro(c, bas, cx_centre + cell_w / 2, bas_y + cell_h * 0.30, 30, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch); c.setFont(police_ch, 30)
        c.drawCentredString(cx_centre + cell_w / 2, bas_y + cell_h * 0.30, str(bas))

    # --- responsable en bas de la carte ---
    if telephone:
        c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
        c.drawCentredString(x0 + CARD_W / 2, y0 + 1 * mm, f"Resp. {telephone}")

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            _q = 8.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 1.5 * mm, y0 + 1.5 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=10, serie_start=1, theme="", couleur=True,
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
        titre_aff = titre_jeu if titre_jeu else "BINGO BALL"
        ligne2 = titre_aff
        if date_lieu: ligne2 += "  ·  " + date_lieu
        ligne2 += f"  ·  Page {no_page}"
        c.setFillColor(GREY); c.setFont("Helvetica", 7)
        y2 = (PAGE_H - 8.5 * mm) if nom_evenement else (PAGE_H - 6 * mm)
        c.drawCentredString(PAGE_W / 2, y2, ligne2)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#999999")
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre, telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=10, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="GRAND LOTO",
                      date_lieu="20 déc 2026", telephone="87 12 34 56")
    with open("test_bb.pdf", "wb") as f:
        f.write(pdf.read())
    print("BINGO BALL généré")
