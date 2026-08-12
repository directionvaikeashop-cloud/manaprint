# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur POW 9 BOULES (format A4)

🧺 NÉ LE 11/08 (demande des clientes de Maeva) : le jumeau de POW 8
BOULES, mais avec NEUF numéros — trois par colonne, la grille est
pleine. Les boules sont rangées DANS LE PANIER TRESSÉ de Maeva.

RÈGLE : 9 numéros, trois par colonne —
  colonne 1 : 1-9 · colonne 2 : 10-18 · colonne 3 : 19-27
(POW 8 en avait 8, avec une case vide en bas au milieu pour le QR.)

12 cartes par feuille A4 (3 colonnes × 4 rangées).
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgp
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les cartons sortent normalement, simplement sans microtexte.
try:
    from generators import motifs as _motifs
except Exception:
    try:
        import motifs as _motifs
    except Exception:
        _motifs = None

try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None


try:
    pdfmetrics.registerFont(TTFont("DJL", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    POLICE = "DJL"
except Exception:
    POLICE = "Helvetica"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)


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
# (min, max) par colonne — POW 9 boules
PLAGES = [(1, 9), (10, 18), (19, 27)]

# 🧺 LE PANIER DE MAEVA — les boules s'y rangent.
_RATIO_PANIER = 0.9677
# 🧺 LES TROIS COMPARTIMENTS DU PANIER (sceau Maeva 11/08) : les deux
# anses descendent dans le corps et le partagent en trois — une
# colonne de numéros par compartiment. ⚠️ Les anses ont été DÉPLACÉES
# au tiers à la découpe : sur le dessin d'origine elles tombaient à
# 28 % et 72 %, ce qui donnait un compartiment central quatre fois
# plus large que les deux autres.
ZONES = [[0.048, 0.301], [0.384, 0.616], [0.699, 0.952]]
HAUT = (0.1, 0.58)     # le ventre, du bas vers le haut
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


_IMAGE_PANIER = _choisir_image("pow_panier", _RATIO_PANIER)

COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """9 numéros : col1 = 3 nums (1-9), col2 = 3 nums (10-18), col3 = 3 nums (19-27).
    Grille 3×3 entièrement remplie."""
    col1 = sorted(rng.sample(range(PLAGES[0][0], PLAGES[0][1] + 1), 3))
    col2 = sorted(rng.sample(range(PLAGES[1][0], PLAGES[1][1] + 1), 3))
    col3 = sorted(rng.sample(range(PLAGES[2][0], PLAGES[2][1] + 1), 3))
    grille = [
        [col1[0], col2[0], col3[0]],
        [col1[1], col2[1], col3[1]],
        [col1[2], col2[2], col3[2]],   # ⚡ POW 9 : la grille est PLEINE
    ]
    return grille


# 🎲 LES PETITS NUMÉROS EN VRAIS DÉS (sceau Maeva 30/07) : 1-6 = un dé à
# points ; 7, 8, 9 = DEUX dés dont les points s'additionnent (7=4+3, 8=4+4,
# 9=5+4) ; à partir de 10, le chiffre reste roi (un dé ne sait pas dire 47).
_DECOMP_DES = {7: (4, 3), 8: (4, 4), 9: (5, 4)}


def _un_de(c, cx, cy, t, valeur, col, gris_ch):
    """Un vrai dé : carré arrondi blanc bordé couleur, points gris disposés
    comme sur les dés du commerce."""
    r = t / 2.0
    c.setStrokeColor(col); c.setLineWidth(1.1)
    c.setFillColor(colors.white)
    c.roundRect(cx - r, cy - r, t, t, t * 0.18, stroke=1, fill=1)
    q = t * 0.26
    pos = {1: [(0, 0)], 2: [(-q, q), (q, -q)], 3: [(-q, q), (0, 0), (q, -q)],
           4: [(-q, q), (q, q), (-q, -q), (q, -q)],
           5: [(-q, q), (q, q), (0, 0), (-q, -q), (q, -q)],
           6: [(-q, q), (q, q), (-q, 0), (q, 0), (-q, -q), (q, -q)]}[valeur]
    c.setFillColor(gris_ch)
    for dx, dy in pos:
        c.circle(cx + dx, cy + dy, t * 0.085, stroke=0, fill=1)


def _dessine_des(c, valeur, cx, cy, col, gris_ch):
    if valeur <= 6:
        _un_de(c, cx, cy, 11.5 * mm, valeur, col, gris_ch)
    else:
        a, b = _DECOMP_DES[valeur]
        _un_de(c, cx - 4.4 * mm, cy, 7.8 * mm, a, col, gris_ch)
        _un_de(c, cx + 4.4 * mm, cy, 7.8 * mm, b, col, gris_ch)


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id="", motif="", des=False):
    # 🖼️ filigrane décoratif (option client) — dessiné EN PREMIER, tout passe dessus
    if _motifs and motif:
        _motifs.dessiner_filigrane(c, x0, y0, CARD_W, CARD_H, motif, graine=serie, nb=2, echelle=0.9)
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 3

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête (2 lignes : titre + N° carte) — le nom du jeu apparaît TOUJOURS
    hdr_y = y0 + CARD_H - 3.5 * mm
    titre = "POW 9 boules"
    if titre_jeu and titre_jeu.strip().upper() != titre.upper():
        titre += "  —  " + titre_jeu.strip()
    if telephone:
        titre += " " + telephone
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y, titre[:60])
    c.setFillColor(col); c.setFont(POLICE, 6.5)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y - 4 * mm, "Carte N° %05d" % serie)

    # Zone grille 3×3
    grid_top = hdr_y - 6.5 * mm
    grid_bot = y0 + 2.5 * mm
    cell_w = CARD_W / ncols
    grid_h = grid_top - grid_bot
    row_h = grid_h / 3

    # ═══ 🧺 LE PANIER DE MAEVA, ET LES NEUF BOULES DEDANS ═══
    # Le panier occupe le carton ; les numéros se rangent dans son
    # ventre, trois par colonne. Plus de traits séparateurs : le
    # tressage sépare déjà les colonnes à l'œil.
    # ⚡ 11/08 (sceau Maeva) : LE PANIER PREND TOUTE LA PLACE. Avant, une
    # bande de 11 mm lui était retirée pour le QR — le panier ne faisait
    # plus que 38 mm de large sur les 59 disponibles, et les chiffres
    # tombaient à 21 pt. Le QR se pose désormais PAR-DESSUS le coin bas,
    # sur le tressage du fond, où aucun numéro ne vit.
    pw = CARD_W - 2.0 * mm
    ph = pw / _RATIO_PANIER
    if ph > grid_top - grid_bot:
        ph = grid_top - grid_bot
        pw = ph * _RATIO_PANIER
    px = x0 + (CARD_W - pw) / 2
    py = grid_bot + (grid_top - grid_bot - ph) / 2
    if _os2.path.exists(_IMAGE_PANIER):
        try:
            c.drawImage(_IMAGE_PANIER, px, py, pw, ph, mask="auto",
                        preserveAspectRatio=True)
        except Exception:
            pass

    # le ventre du panier : c'est là que les boules se rangent
    vy = py + HAUT[0] * ph
    vh = (HAUT[1] - HAUT[0]) * ph
    rh2 = vh / 3.0
    # chaque colonne va dans SON compartiment, entre les anses
    larg_mini = min((z[1] - z[0]) for z in ZONES) * pw
    taille = 32.0
    while taille > 10 and (_lgp("88", "Helvetica-Bold", taille) > larg_mini * 0.86
                           or taille * 0.72 > rh2 * 0.80):
        taille -= 0.5
    for r in range(3):
        for cc in range(3):
            val = grille[r][cc]
            if val is None:
                continue
            cx = px + (ZONES[cc][0] + ZONES[cc][1]) / 2 * pw
            cyc = vy + vh - (r + 0.5) * rh2
            if des and val <= 9:   # 🎲 jumeau CASINO : le petit numéro vit en dés
                _dessine_des(c, val, cx, cyc, col, gris_ch)
            elif _sec:
                _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            # ⚠️ POW 9 : la grille est PLEINE, il n'y a plus de case vide
            # au milieu. Le QR se pose SOUS le panier, au coin bas-droit.
            # ⚠️ le QR se pose SOUS L'ANSE, en haut à gauche : c'est le
            # seul coin du panier où aucun numéro ne vit. En bas à droite,
            # il mangeait le dernier chiffre de la 3e colonne.
            _q = 8.5 * mm
            _sec.carton_qr(c, px + pw * 0.045, py + ph * 0.70,
                           _q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif="", des=False, page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(900000 + int(serie_start))
    serie = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 9)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 7.2 * mm, "%03d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                grille = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, grille, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id, motif=motif, des=des)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


def generer_pdf_casino(**kw):
    """🎲 POW CASINO — le jumeau où les numéros 1-9 vivent en vrais dés."""
    kw["des"] = True
    return generer_pdf(**kw)


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="POW 9 boules",
                      telephone="89.22.23.05")
    with open("test_pow.pdf", "wb") as f:
        f.write(pdf.read())
    print("POW 9 boules généré")
