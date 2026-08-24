# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur 60 BOULES (format A4)
12 grilles par feuille A4 (2 colonnes × 6 rangées) — à la demande de Maeva
(le modèle historique en avait 18, on aère pour de plus grosses cartes).
Chaque carte : BANDEAU coloré « JEUX 60 · 8 BOULES · BY 2KEA » (texte blanc,
fidèle au modèle), puis grille 4×2 — 8 numéros triés par colonne :
  1-15 · 16-30 · 31-45 · 46-60   (2 par colonne, d'où les « 60 boules »)
Pied de carte : « N° SÉRIE | 027001 ». QR de vérification dans la bande droite.
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
_GRIS_ECO = colors.Color(0.58, 0.58, 0.58)  # allégé (économie d'encre, 27/07)
_POLICE_P15 = "Helvetica-Bold"
_GRIS_P15 = colors.Color(0.55, 0.55, 0.55)

def _style_chiffres(style):
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4
# Les 4 colonnes du 60 BOULES : 2 numéros chacune
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60)]

# ═══ 🦋 LES HUIT PAPILLONS (sceau Maeva 14/08) ═══
# « J'AI 60 BOULES — 8 BOULES » : huit papillons numérotés de 1 à 8, un
# cercle clair au cœur de chacun, reliés par des traits pointillés.
# ⚠️ L'ORDRE suit les PASTILLES NOIRES du dessin (1 à 8), pas la position :
#   1 haut-gauche · 2 haut-droite · 3 milieu-gauche · 4 centre
#   5 milieu-droite · 6 bas-gauche · 7 bas-centre · 8 bas-droite
_RATIO_PAP = 1.5018
PAPILLONS = [[0.2827, 0.673], [0.7434, 0.6571], [0.2761, 0.3911], [0.5131, 0.4999], [0.8429, 0.394], [0.4165, 0.1791], [0.6323, 0.2311], [0.8372, 0.1488]]
DIAM_PAP = 0.115
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_b


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


_IMAGE_PAP = _choisir_image("b60_papillons", _RATIO_PAP)


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
HDR_H = 6.2 * mm         # bandeau coloré JEUX 60
PIED_H = 4.4 * mm        # bande N° SÉRIE
ZONE_QR = 16 * mm        # bande de droite réservée au QR de vérification


def _gen_carte(rng):
    """8 numéros : 2 distincts par colonne, triés vers le bas."""
    return [sorted(rng.sample(range(pmin, pmax + 1), 2)) for pmin, pmax in PLAGES]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id="", motif=""):
    # 🖼️ filigrane décoratif (option client) — dessiné EN PREMIER, tout passe dessus
    if _motifs and motif:
        _motifs.dessiner_filigrane(c, x0, y0, CARD_W, CARD_H, motif, graine=serie, nb=2, echelle=0.9)
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 🦋 LA PLAQUE AUX PAPILLONS ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les huit cercles suivent, chacun à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_PAP):
        try:
            c.drawImage(_IMAGE_PAP, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS le cercle du papillon, jamais en dur.
    # ⚠️ MESURER AVEC LA VRAIE POLICE (`police_ch`), pas Helvetica.
    _dia = _pw * DIAM_PAP
    _t_num = 25.0
    while _t_num > 6 and (_lg_b("88", police_ch, _t_num) > _dia * 1.05
                          or _t_num * 0.72 > _dia * 0.86):
        _t_num -= 0.5

    # ═══ les HUIT numéros, au cœur de leur papillon ═══
    # ⚠️ cols_nums donne QUATRE COLONNES de deux numéros triés. On les
    # aplatit dans l'ordre des pastilles : 1,2 = 1-15 · 3,4 = 16-30 ·
    # 5,6 = 31-45 · 7,8 = 46-60.
    _plat = [v for col in cols_nums for v in col]
    for _k, _n in enumerate(_plat[:8]):
        _bx, _by = PAPILLONS[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LES DEUX BANDEAUX, écrits dans leurs pastilles creuses ═══
    # ⚠️ Ils étaient NOIRS PLEINS dans le dessin (plus de la moitié de
    # leur surface en encre) : ils sont désormais CREUX, texte en gris.
    c.setFillColor(gris_ch)
    _t8 = 6.5
    while _t8 > 3.2 and _lg_b("8 BOULES", "Helvetica-Bold", _t8) > _pw * 0.14:
        _t8 -= 0.25
    c.setFont("Helvetica-Bold", _t8)
    c.drawCentredString(_px + _pw * 0.530, _py + _ph * 0.800, "8 BOULES")

    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "   \u2022   " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_b(_bl, "Helvetica-Bold", _tb) > _pw * 0.28:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.532, _py + _ph * 0.020, _bl)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(932000 + int(serie_start))
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
                      telephone="89 22 23 05")
    with open("test_boules60.pdf", "wb") as f:
        f.write(pdf.read())
    print("60 BOULES généré")
