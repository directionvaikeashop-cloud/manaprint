"""
MANAPRINT — Générateur LAGOON 5 BOULES (format A4)
12 cartes RONDES par feuille (3 colonnes × 4 rangées).
Chaque cercle : 5 numéros — 1-10 en haut, trio central 11-20 / 21-30 / 31-40,
41-50 en bas. Titre et N° de série à l'intérieur du cercle.
Bande basse réservée au QR de sécurité. Tirage : boules 1 à 50.
Couleur arc-en-ciel (ou couleur_perso) / N&B. Gammes ÉCO / PREMIUM.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

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
# ═══ 🏝️ LES CINQ ÎLOTS (sceau Maeva 14/08) ═══
# « VOTRE JEU LAGOON — 5 BOULES » : cinq îlots au lagon, leurs palmiers,
# et un cercle clair au cœur de chacun pour le numéro.
_RATIO_ILES = 1.4991
ILES = [[0.3067, 0.5353], [0.5567, 0.5373], [0.8074, 0.5347], [0.4128, 0.2088], [0.7256, 0.203]]
DIAM_ILE = 0.118
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_l


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


_IMAGE_ILES = _choisir_image("lagoon_iles", _RATIO_ILES)


# ⚠️ 14/08 : le dessin de Maeva est en PAYSAGE (ratio 1,50) — on passe de
# 12 cartes rondes à 8 cartes-plaques (2 colonnes × 4 rangées).
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

FOOT_H = 3 * mm
RAYON = 29 * mm  # grand cercle : le QR vit À L'INTÉRIEUR

RANGES = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50)]


def _gen_carte():
    """5 numéros : un par plage."""
    return [random.randint(lo, hi) for (lo, hi) in RANGES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cx = x0 + CARD_W / 2
    cy = y0 + FOOT_H + 1 * mm + RAYON

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 🏝️ LA PLAQUE AU LAGON ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les cinq îlots suivent, chacun à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_ILES):
        try:
            c.drawImage(_IMAGE_ILES, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS le cercle de l'îlot, jamais en dur.
    # ⚠️ MESURER AVEC LA VRAIE POLICE (`police_ch`), pas Helvetica : elle
    # est plus large et le chiffre déborderait.
    _dia = _pw * DIAM_ILE
    _t_num = 25.0
    while _t_num > 6 and (_lg_l("88", police_ch, _t_num) > _dia * 1.05
                          or _t_num * 0.72 > _dia * 0.86):
        _t_num -= 0.5

    # ═══ les CINQ numéros, au cœur de leur îlot ═══
    for _k, _n in enumerate(nums[:5]):
        _ix, _iy = ILES[_k]
        _nx = _px + _ix * _pw
        _ny = _py + _iy * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LES DEUX BANDEAUX, écrits dans leurs pastilles creuses ═══
    # ⚠️ Ils étaient NOIRS PLEINS dans le dessin (50 % de leur surface en
    # encre) : ils sont désormais CREUX, et le PDF y écrit en gris.
    c.setFillColor(gris_ch)
    _t5 = 6.5
    while _t5 > 3.2 and _lg_l("5 BOULES", "Helvetica-Bold", _t5) > _pw * 0.13:
        _t5 -= 0.25
    c.setFont("Helvetica-Bold", _t5)
    c.drawCentredString(_px + _pw * 0.537, _py + _ph * 0.795, "5 BOULES")

    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "   \u2605   " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_l(_bl, "Helvetica-Bold", _tb) > _pw * 0.34:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.525, _py + _ph * 0.036, _bl)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
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
        # ⚠️ 14/08 : PLUS DE TITRE EN HAUT DE PAGE — le dessin de Maeva
        # porte déjà « LAGOON » et « 5 BOULES » en grand. Seul le numéro
        # de page reste, discret, pour s'y retrouver dans une commande.
        c.setFillColor(GREY); c.setFont("Helvetica", 5)
        y2 = (PAGE_H - 8.5 * mm) if nom_evenement else (PAGE_H - 5 * mm)
        c.drawRightString(PAGE_W - 6 * mm, y2, f"Page {no_page}")

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                nums = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur
                        else "#999999")
                _dessiner_carte(c, x0, y0, nums, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True)
    with open("test_lagoon.pdf", "wb") as f:
        f.write(pdf.read())
    print("LAGOON g\u00e9n\u00e9r\u00e9")
