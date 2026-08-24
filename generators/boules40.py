# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur 40 BOULES (format A4)
12 cartes par feuille A4 (2 colonnes × 6 rangées). Le jeu « 8 boules » sur 40.
Chaque carte : 8 numéros en quinconce 2-1-2-1-2 dans 5 colonnes de huit :
  col 1 = 2 numéros empilés (1-8)
  col 2 = 1 GRAND numéro   (9-16)
  col 3 = 2 numéros empilés (17-24)
  col 4 = 1 GRAND numéro   (25-32)
  col 5 = 2 numéros empilés (33-40)
Grille à traits : séparateurs verticaux entre colonnes, trait horizontal
au milieu des colonnes empilées (fidèle au modèle).
En-tête : « Le jeu 40 boules · 8 boules » — pied : « N° SÉRIE | 030001 ».
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris (2 gammes ÉCO/PREMIUM).
"""
import io
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
# Les 5 colonnes du 40 BOULES : (min, max, nombre de numéros)
COLONNES = [(1, 8, 2), (9, 16, 1), (17, 24, 2), (25, 32, 1), (33, 40, 2)]

# ═══ 🐙 LA PIEUVRE ET SES HUIT BULLES (sceau Maeva 14/08) ═══
# « J'AI 40 BOULES — 8 BOULES » : une pieuvre souriante, ses huit
# tentacules qui portent chacun une bulle pour un numéro.
# ⚠️ L'ORDRE de lecture : de haut en bas, gauche puis droite.
_RATIO_PIEUVRE = 1.5018
BULLES = [[0.3741, 0.7193], [0.7476, 0.7179], [0.269, 0.5682], [0.8442, 0.5677], [0.2962, 0.3527], [0.804, 0.3447], [0.4631, 0.1985], [0.648, 0.1997]]
DIAM_BULLE = 0.108
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_p


def _choisir_image(motif_img, ratio_attendu):
    """🛟 Retrouve le dessin, quel que soit son nom de fichier."""
    dossier = _os2.path.dirname(_os2.path.abspath(__file__))
    exact = _os2.path.join(dossier, motif_img + ".png")
    candidats = []
    try:
        for f in _os2.listdir(dossier):
            if motif_img in f and f.lower().endswith(".png"):
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


_IMAGE_PIEUVRE = _choisir_image("b40_pieuvre", _RATIO_PIEUVRE)


# ⚠️ 14/08 : le dessin est en PAYSAGE (ratio 1,50) — on passe de 12 cartes
# à 8 cartes-plaques (2 colonnes × 4 rangées).
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 2.8 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
ZONE_QR = 13.7 * mm      # bande QR resserrée (place aux chiffres 32 pts)


def _gen_carte(rng):
    """8 numéros : [2, 1, 2, 1, 2] par colonne, chacun dans sa plage, empilés triés."""
    return [sorted(rng.sample(range(pmin, pmax + 1), n)) for pmin, pmax, n in COLONNES]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id="", motif=""):
    # 🖼️ filigrane décoratif (option client) — dessiné EN PREMIER, tout passe dessus
    if _motifs and motif:
        _motifs.dessiner_filigrane(c, x0, y0, CARD_W, CARD_H, motif, graine=serie, nb=2, echelle=0.9)
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 🐙 LA PLAQUE À LA PIEUVRE ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les huit bulles suivent, chacune à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_PIEUVRE):
        try:
            c.drawImage(_IMAGE_PIEUVRE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS la bulle, jamais en dur.
    # ⚠️ MESURER AVEC LA VRAIE POLICE (`police_ch`), pas Helvetica.
    _dia = _pw * DIAM_BULLE
    _t_num = 25.0
    while _t_num > 6 and (_lg_p("88", police_ch, _t_num) > _dia * 1.00
                          or _t_num * 0.72 > _dia * 0.82):
        _t_num -= 0.5

    # ═══ les HUIT numéros, dans les bulles de la pieuvre ═══
    # ⚠️ cols_nums donne CINQ colonnes de tailles 2-1-2-1-2. On les aplatit
    # dans l'ordre de lecture des bulles.
    _plat = [v for col in cols_nums for v in col]
    for _k, _n in enumerate(_plat[:8]):
        _bx, _by = BULLES[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LES DEUX BANDEAUX, écrits dans leurs pastilles creuses ═══
    c.setFillColor(gris_ch)
    _t8 = 7.0
    while _t8 > 3.2 and _lg_p("8 BOULES", "Helvetica-Bold", _t8) > _pw * 0.14:
        _t8 -= 0.25
    c.setFont("Helvetica-Bold", _t8)
    c.drawCentredString(_px + _pw * 0.560, _py + _ph * 0.795, "8 BOULES")

    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "   \u2022   " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_p(_bl, "Helvetica-Bold", _tb) > _pw * 0.29:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.530, _py + _ph * 0.028, _bl)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(985000 + int(serie_start))
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
                cols_nums = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, cols_nums, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id, motif=motif)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89.22.23.05")
    with open("test_boules40.pdf", "wb") as f:
        f.write(pdf.read())
    print("40 BOULES généré")
