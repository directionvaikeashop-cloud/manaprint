"""
MANAPRINT — Générateur DUAL DAB 75 (format A4)
6 cartes par feuille (2 colonnes × 3 rangées).
Chaque carte : 4 PAIRES + 1 numéro cerclé (pointillés) = 9 numéros :
  haut :  paire 1-15   ·  paire 16-30
  centre : numéro 61-75 dans un cercle pointillé
  bas :   paire 31-45  ·  paire 46-60
Chaque paire est triée et reliée par « / » ou « ↔ » (au hasard).
QR de sécurité au milieu-droit. Couleur arc-en-ciel / N&B. ÉCO / PREMIUM.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

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
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
# ═══ 🍾 LES CAPSULES (sceau Maeva 14/08) ═══
# « DUAL DAB » : quatre paires de capsules de bouteille et une GRANDE
# capsule au centre, entourée d'éclairs.
# ⚠️ DEUX SORTES DE PAIRES dans le dessin :
#   · paires 1 et 4 → DEUX capsules rondes reliées par une flèche ↔
#   · paires 2 et 3 → UNE barrette allongée, ses deux numéros de part et
#     d'autre du « / »
# L'ORDRE des neuf places suit celui du jeu :
#   1-15 a·b · 16-30 a·b · 61-75 (le centre) · 31-45 a·b · 46-60 a·b
_RATIO_DAB = 1.5018
PLACES = [[0.2244, 0.6377], [0.3991, 0.6381], [0.7164, 0.6359], [0.8702, 0.6359], [0.5456, 0.4432], [0.2481, 0.2071], [0.3869, 0.2071], [0.7019, 0.2126], [0.8781, 0.2126]]
LARG_CAPS = 0.0964
HAUT_CAPS = 0.1455
LARG_CENTRE = 0.1628
HAUT_CENTRE = 0.2432
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_d


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


_IMAGE_DAB = _choisir_image("dab_capsules", _RATIO_DAB)


COLS_PAGE = 2
ROWS_PAGE = 4          # 8 grilles par feuille A4 (décision Maeva, 28/07)
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

FOOT_H = 3.5 * mm
HDR_H = 6 * mm

# (plage, position x en fraction, rangée "haut"/"bas")
PAIRES = [
    ((1, 15),  0.26, "haut"),
    ((16, 30), 0.73, "haut"),
    ((31, 45), 0.26, "bas"),
    ((46, 60), 0.73, "bas"),
]
PLAGE_CENTRE = (61, 75)


def _gen_carte():
    """4 paires triées + 1 numéro central ; séparateurs / ou ↔ au hasard."""
    paires = []
    for (lo, hi), fx, rang in PAIRES:
        a, b = sorted(random.sample(range(lo, hi + 1), 2))
        sep = random.choice(["slash", "fleche"])
        paires.append((a, b, sep, fx, rang))
    centre = random.randint(*PLAGE_CENTRE)
    return paires, centre


def _fleche(c, x1, x2, y, col):
    """Dessine une double-flèche ↔ entre x1 et x2 à la hauteur y."""
    c.setStrokeColor(col)
    c.setLineWidth(0.8)
    c.line(x1, y, x2, y)
    a = 1.3 * mm
    c.line(x1, y, x1 + a, y + a * 0.8)
    c.line(x1, y, x1 + a, y - a * 0.8)
    c.line(x2, y, x2 - a, y + a * 0.8)
    c.line(x2, y, x2 - a, y - a * 0.8)


def _dessiner_carte(c, x0, y0, donnees, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    paires, centre = donnees
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 🍾 LA PLAQUE AUX CAPSULES ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les neuf places suivent, chacune à son endroit.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_DAB):
        try:
            c.drawImage(_IMAGE_DAB, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ deux tailles : les huit capsules de paire, et LA GRANDE du centre.
    # ⚠️ MESURER AVEC LA VRAIE POLICE (`police_ch`), pas Helvetica.
    _lg_p = _pw * LARG_CAPS
    _ht_p = _ph * HAUT_CAPS
    _t_num = 25.0
    # ⚠️⚠️ 14/08 (Maeva veut 22 à 25 pt dans les paires) : la capsule fait
    # 9,29 mm et « 88 » à 25 pt en prend 11,22 — il DÉBORDE un peu, mais
    # les capsules d'une paire sont espacées de 0,175 pour une largeur de
    # 0,096 : il reste 0,078 de vide entre elles, le chiffre ne touche
    # jamais sa voisine. On desserre donc à 1,22.
    # ⚠️ mesuré avec la VRAIE police (DJLECO), pas Helvetica.
    while _t_num > 6 and (_lg_d("88", police_ch, _t_num) > _lg_p * 1.22
                          or _t_num * 0.72 > _ht_p * 0.68):
        _t_num -= 0.5

    _lg_g = _pw * LARG_CENTRE
    _ht_g = _ph * HAUT_CENTRE
    _t_gros = 34.0
    while _t_gros > 8 and (_lg_d("88", police_ch, _t_gros) > _lg_g * 0.86
                           or _t_gros * 0.72 > _ht_g * 0.52):
        _t_gros -= 0.5

    # ═══ les NEUF numéros, dans leurs capsules ═══
    # ⚠️ `paires` donne quatre (a, b, sep, fx, rang) ; on aplatit dans
    # l'ordre du dessin, en glissant le centre à la cinquième place.
    _plat = []
    for _k, (_a, _b, _sep, _fx, _rang) in enumerate(paires):
        _plat += [_a, _b]
        if _k == 1:
            _plat.append(centre)
    for _k, _n in enumerate(_plat[:9]):
        _dx, _dy = PLACES[_k]
        _t = _t_gros if _k == 4 else _t_num
        _nx = _px + _dx * _pw
        _ny = _py + _dy * _ph - _t * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LE BANDEAU, écrit dans sa pastille creuse ═══
    c.setFillColor(gris_ch)
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "   \u2605   " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_d(_bl, "Helvetica-Bold", _tb) > _pw * 0.31:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.520, _py + _ph * 0.030, _bl)


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
        titre_aff = titre_jeu if titre_jeu else "DUAL DAB 75"
        # ⚠️ 14/08 : PLUS DE TITRE EN HAUT DE PAGE — le dessin porte déjà
        # « DUAL DAB » en grand. Seul le numéro de page reste, discret.
        c.setFillColor(colors.Color(0.62, 0.62, 0.62)); c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 5 * mm, "Page %d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                donnees = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur
                        else "#999999")
                _dessiner_carte(c, x0, y0, donnees, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True, telephone="89 22 23 05")
    with open("test_dual_dab.pdf", "wb") as f:
        f.write(pdf.read())
    print("DUAL DAB 75 g\u00e9n\u00e9r\u00e9")
