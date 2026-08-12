"""
MANAPRINT — Générateur CHAMPAGNE (format A4)

🥂 REFAIT LE 08/08 (sceau Maeva) : la FLÛTE de Maeva trône au centre du
carton, et les DOUZE NUMÉROS s'éparpillent tout autour, chacun dans SA
BULLE — comme les bulles qui montent dans le verre.

RÈGLE INCHANGÉE : 12 numéros, cinq colonnes de quinzaines —
  1-15 (un) · 16-30 (trois) · 31-45 (quatre) · 46-60 (trois) · 61-75 (un)
Le sac du crieur ne change donc pas d'un chiffre.

Les places des bulles ont été CALCULÉES (60 000 essais) pour qu'aucune
ne tombe sur la flûte ni ne touche sa voisine : 14,5 mm d'écart minimal
pour des bulles de 13,2 mm.
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


# Couleurs CHAMPAGNE : alternance jaune / orange (fidèle à la maquette)
CHAMPAGNE_COULEURS = ["#F2C60A", "#F57C00"]
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

# 🥂 LA FLÛTE DE MAEVA et les places de ses bulles.
_RATIO_FLUTE = 800.0 / 1291.0
import os as _os2


def _choisir_image(motif, ratio_attendu):
    """🛟 Retrouve le dessin, quel que soit son nom de fichier."""
    dossier = _os2.path.dirname(_os2.path.abspath(__file__))
    exact = _os2.path.join(dossier, motif + ".png")
    candidats = []
    try:
        for f in _os2.listdir(dossier):
            if motif in f and f.lower().endswith(".png"):
                candidats.append(_os2.path.join(dossier, f))
    except Exception:
        return exact
    if not candidats:
        return exact
    meilleur, ecart = candidats[0], 9e9
    for chemin in candidats:
        try:
            from PIL import Image as _Im
            with _Im.open(chemin) as im:
                e = abs(im.width / float(im.height) - ratio_attendu)
        except Exception:
            continue
        if e < ecart:
            meilleur, ecart = chemin, e
    return meilleur


_IMAGE_FLUTE = _choisir_image("champagne_flute", _RATIO_FLUTE)

# Les DOUZE bulles, en millimètres depuis le coin bas-gauche de la zone
# de jeu (90 × 78 mm). Calculées pour ne jamais toucher la flûte ni se
# chevaucher — 14,5 mm d'écart minimal.
ZONE_L, ZONE_H = 90.0, 78.0
FLUTE_L = 44
R_BULLE = 6.6
BULLES = [
    (8.43, 34.73),
    (8.2, 66.44),
    (69.02, 66.28),
    (73.03, 30.59),
    (8.57, 18.17),
    (70.0, 15.84),
    (15.84, 47.22),
    (81.15, 57.49),
    (82.09, 7.79),
    (72.88, 45.24),
    (20.76, 9.23),
    (20.95, 26.02),
]
BANDEAU_H = 2.8 * mm
GRID_N = 5  # 5x5

# Le motif CHAMPAGNE (coupe) : cases pleines (ligne, colonne), du HAUT
POSITIONS = {
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
    (1, 1), (1, 2), (1, 3),
    (3, 2),
    (4, 1), (4, 2), (4, 3),
}
# Nombre de numéros nécessaires par colonne
_NB_PAR_COL = [1, 3, 4, 3, 1]


def _gen_carte():
    """Tire les numéros du motif DIAMANT : dict {(ligne, col): numéro}."""
    carte = {}
    for ci, (lo, hi) in enumerate(RANGES):
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

    # Mini-bandeau : nom du jeu + nom du tournoi (sécurité)
    bandeau = "LE JEU \u00ab CHAMPAGNE \u00bb"
    if titre_jeu:
        bandeau += "  \u2014  " + titre_jeu
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 2.3 * mm, bandeau[:60])

    # ═══ LA FLÛTE AU CENTRE, LES NUMÉROS DANS LES BULLES ═══
    grid_top = y0 + CARD_H - BANDEAU_H - 2.0 * mm
    z_bot = y0 + FOOT_H
    z_h = grid_top - z_bot
    z_w = CARD_W

    # l'échelle : la zone du carton par rapport à celle des calculs
    ex = z_w / (ZONE_L * mm)
    ey = z_h / (ZONE_H * mm)

    # ── la flûte, au centre ──────────────────────────────────────────────
    fl_l = FLUTE_L * mm * ex
    fl_h = fl_l / _RATIO_FLUTE
    if fl_h > z_h - 2 * mm:
        fl_h = z_h - 2 * mm
        fl_l = fl_h * _RATIO_FLUTE
    flx = x0 + (z_w - fl_l) / 2
    fly = z_bot + (z_h - fl_h) / 2
    if _os2.path.exists(_IMAGE_FLUTE):
        try:
            c.drawImage(_IMAGE_FLUTE, flx, fly, fl_l, fl_h, mask="auto",
                        preserveAspectRatio=True)
        except Exception:
            pass

    # ── les douze bulles, éparpillées autour ─────────────────────────────
    # L'ordre suit le motif d'origine (colonnes de quinzaines) : la règle
    # du jeu n'a pas bougé, seul l'habillage a changé.
    valeurs = [carte[k] for k in sorted(carte.keys(), key=lambda k: (k[1], k[0]))]
    r = R_BULLE * mm * min(ex, ey)
    # ⚠️ le chiffre doit tenir DANS sa bulle : on cale sa taille sur la
    # largeur réelle d'un nombre à deux chiffres, pas à l'estime.
    from reportlab.pdfbase.pdfmetrics import stringWidth as _lgb
    taille = 30.0
    while taille > 12.0 and _lgb("88", "Helvetica-Bold", taille) > r * 1.52:
        taille -= 0.5
    for (bx_mm, by_mm), val in zip(BULLES, valeurs):
        bx = x0 + bx_mm * mm * ex
        by = z_bot + by_mm * mm * ey
        # la bulle : un cercle au trait, avec son petit reflet
        c.setFillColor(colors.white)
        c.setStrokeColor(col)
        c.setLineWidth(0.9)
        c.circle(bx, by, r, stroke=1, fill=1)
        c.setLineWidth(0.5)
        p = c.beginPath()
        p.arc(bx - r * 0.66, by + r * 0.16, bx - r * 0.16, by + r * 0.66, 200, 70)
        c.drawPath(p, stroke=1, fill=0)
        ny = by - taille * 0.34
        if _sec:
            _sec.chiffre_micro(c, val, bx, ny, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, taille)
            c.drawCentredString(bx, ny, str(val))

    # Pied : N° série + responsable sur chaque grille
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, f"N\u00b0 {serie:06d}")
    if telephone:
        c.drawRightString(x0 + CARD_W - 1.5 * mm, y0 + 1.3 * mm, f"Resp. {telephone}")

    # 🎯 QR intégré : dans la RANGÉE CENTRALE vide de la grille (aucun chiffre dérangé)
    if _sec and evenement_id:
        try:
            # ⚠️ l'ancienne grille a disparu : le QR se pose desormais dans
            # la seule place libre trouvee entre les bulles et la flute
            # (calculee : 11.0 mm de cote, a 2,4 mm de sa voisine).
            _q = 11.0 * mm * min(ex, ey)
            _sec.carton_qr(c, x0 + 78.5 * mm * ex, z_bot + 66.5 * mm * ey,
                           _q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    serie = serie_start
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    encre = NOIR if couleur else GRIS40

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        titre_aff = titre_jeu if titre_jeu else "CHAMPAGNE"
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
                    coul = CHAMPAGNE_COULEURS[idx % len(CHAMPAGNE_COULEURS)]  # jaune / orange (champagne !)
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
    with open("test_champagne.pdf", "wb") as f:
        f.write(pdf.read())
    print("CHAMPAGNE g\u00e9n\u00e9r\u00e9")
