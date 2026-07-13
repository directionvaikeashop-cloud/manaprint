"""
MANAPRINT — Générateur TUREIA (format A4)
6 cartes par feuille (2 colonnes × 3 rangées).
Chaque carte : grille 5×5 SANS lettres, 12 numéros en motif TUREIA symétrique :
  rang 1 :        col 2, 4
  rang 2 : col 1,        5
  rang 3 : col 1, 2, 4, 5
  rang 4 : col 1,        5   (bandeau du jeu au centre)
  rang 5 :        col 2, 4
La colonne CENTRALE ne porte aucun numéro (décor en croisillons).
Plages : 1-15 / 16-30 / — / 46-60 / 61-75 (3 numéros par colonne jouée).
Bordures épaisses rouge/jaune en alternance (ou couleur_perso).
Gammes ÉCO / PREMIUM. Microtexte + QR de sécurité.
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


# Couleurs TUREIA : alternance rouge / jaune (fidèle à la maquette)
TUREIA_COULEURS = ["#C62828", "#F2D410"]
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

COLS_PAGE = 2
ROWS_PAGE = 3
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
FOOT_H = 3 * mm
BANDEAU_H = 2.8 * mm
GRID_N = 5  # 5x5

# Le motif TUREIA : cases pleines (ligne, colonne), lignes numérotées du HAUT
POSITIONS = {
    (0, 1), (0, 3),
    (1, 0), (1, 4),
    (2, 0), (2, 1), (2, 3), (2, 4),
    (3, 0), (3, 4),
    (4, 1), (4, 3),
}
# Nombre de numéros nécessaires par colonne (la colonne centrale ne joue pas)
_NB_PAR_COL = [3, 3, 0, 3, 3]


def _gen_carte():
    """Tire les numéros du motif DIAMANT : dict {(ligne, col): numéro}."""
    carte = {}
    for ci, (lo, hi) in enumerate(RANGES):
        if _NB_PAR_COL[ci] == 0:
            continue
        nums = random.sample(range(lo, hi + 1), _NB_PAR_COL[ci])
        lignes = sorted(r for (r, c) in POSITIONS if c == ci)
        for k, ri in enumerate(lignes):
            carte[(ri, ci)] = nums[k]
    return carte


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / GRID_N

    # Bordure ÉPAISSE (signature DIAMANT)
    c.setStrokeColor(col)
    c.setLineWidth(2.4)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.8 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.4 * mm)

    # Grille 5×5 pleine hauteur (le bandeau du jeu sera posé AU CENTRE, rangée 4)
    grid_top = y0 + CARD_H - 2.0 * mm
    zone_h = grid_top - (y0 + FOOT_H)
    cell_h = zone_h / GRID_N

    # Traits de la grille (fins, gris)
    c.setStrokeColor(GRIS_GRILLE); c.setLineWidth(0.35)
    for i in range(GRID_N + 1):
        yy = y0 + FOOT_H + i * cell_h
        c.line(x0, yy, x0 + CARD_W, yy)
    for i in range(1, GRID_N):
        xx = x0 + i * cell_w
        c.line(xx, y0 + FOOT_H, xx, grid_top)

    # Bandeau du jeu AU CENTRE de la carte (rangée 4, colonnes 2-4)
    bandeau = "LE JEU \u00ab TUREIA \u00bb"
    if titre_jeu:
        bandeau += "  \u2014  " + titre_jeu
    cell_h_tmp = (grid_top - (y0 + FOOT_H)) / GRID_N
    y_bandeau = grid_top - 3 * cell_h_tmp - cell_h_tmp * 0.55
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawCentredString(x0 + CARD_W / 2, y_bandeau, bandeau[:52])
    CASES_BANDEAU = {(3, 1), (3, 2), (3, 3)}

    # Cases : numéro (motif TUREIA) ou croisillons
    taille = 33  # gros chiffres bien visibles
    for ri in range(GRID_N):
        for ci in range(GRID_N):
            cx = x0 + (ci + 0.5) * cell_w
            haut = grid_top - ri * cell_h          # bord haut de la case
            bas = haut - cell_h                    # bord bas de la case
            if (ri, ci) in POSITIONS:
                n = carte[(ri, ci)]
                cy = bas + cell_h * 0.30
                if _sec:  # chiffres "billet de banque" remplis de microtexte
                    _sec.chiffre_micro(c, n, cx, cy, taille, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                    c.drawCentredString(cx, cy, str(n))
            elif (ri, ci) in CASES_BANDEAU:
                pass  # zone du bandeau central : ni numéro, ni croix
            else:
                # case vide barrée d'une croix
                c.setStrokeColor(GRIS_CROIX); c.setLineWidth(0.4)
                r = 0.36
                c.line(cx - cell_w * r, bas + cell_h * (0.5 - r),
                       cx + cell_w * r, bas + cell_h * (0.5 + r))
                c.line(cx - cell_w * r, bas + cell_h * (0.5 + r),
                       cx + cell_w * r, bas + cell_h * (0.5 - r))

    # Pied : N° série + responsable sur chaque grille
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, f"N\u00b0 {serie:06d}")
    if telephone:
        c.drawRightString(x0 + CARD_W - 1.5 * mm, y0 + 1.3 * mm, f"Resp. {telephone}")

    # 🎯 QR intégré : dans la COLONNE CENTRALE morte (aucun chiffre dérangé)
    if _sec and evenement_id:
        try:
            _q = 14.0 * mm
            _xq = x0 + 2 * cell_w + (cell_w - _q) / 2
            _yq = grid_top - 2 * cell_h + 4.4 * mm
            _sec.carton_qr(c, _xq, _yq, _q, evenement_id, serie)
        except Exception:
            pass


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
        titre_aff = titre_jeu if titre_jeu else "TUREIA"
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
                carte = _gen_carte()
                if couleur and couleur_perso:
                    coul = couleur_perso
                elif couleur:
                    coul = TUREIA_COULEURS[idx % len(TUREIA_COULEURS)]  # rouge / jaune
                else:
                    coul = "#999999"
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1
                idx += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True, titre_jeu="")
    with open("test_tureia.pdf", "wb") as f:
        f.write(pdf.read())
    print("TUREIA g\u00e9n\u00e9r\u00e9")
