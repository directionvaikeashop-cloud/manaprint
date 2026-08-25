"""
MANAPRINT — Générateur ALOHA 75 (format A4)
12 cartes par feuille (2 colonnes × 6 rangées).
Chaque carte : 5 colonnes A·L·O·H·A, 2 numéros par colonne.
Plages : A 1-15, L 16-30, O 31-45, H 46-60, A 61-75.
Couleur arc-en-ciel (chiffres noirs) ou gris 40%. Personnalisation + téléphone responsable.
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

# ═══ 🌺 LE COLLIER DE FLEURS (sceau Maeva 14/08) ═══
# « ALOHA » : dix fleurs tressées en collier, chacune portant SA LETTRE
# sur une pastille et son cœur rond pour le numéro.
# ⚠️ LES LETTRES SONT CELLES DU BINGO (comme sur le dessin de Maeva) :
#   B ×2 : 1-15 · I ×2 : 16-30 · N ×2 : 31-45 · G ×2 : 46-60 · O ×2 : 61-75
# Les plages ne changent PAS — seules les lettres affichées.
# L'ORDRE : rangée du haut B·B·I·I·N, rangée du bas N·G·G·O·O.
_RATIO_COLLIER = 1.4336
FLEURS = [[0.2677, 0.6379], [0.4173, 0.6396], [0.5669, 0.6395], [0.7181, 0.6393], [0.8716, 0.6384], [0.2336, 0.2746], [0.4079, 0.2424], [0.5686, 0.2426], [0.7285, 0.2423], [0.9007, 0.2746]]
DIAM_FLEUR = 0.0782
# ⚠️ le cœur est un OVALE : sa hauteur est bornée pour ne pas recouvrir
# la PASTILLE DE LA LETTRE, qui vit 0,05 en dessous.
HAUT_FLEUR = 0.0782
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_a


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


_IMAGE_COLLIER = _choisir_image("aloha_collier", _RATIO_COLLIER)


# ⚠️ 14/08 : le dessin est en PAYSAGE (ratio 1,50) — on passe de 12 cartes
# à 8 cartes-plaques (2 colonnes × 4 rangées).
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 6 * mm
MARGIN_TOP = 12 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

LETTERS = ["A", "L", "O", "H", "A"]
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
HDR_H = 4 * mm
FOOT_H = 3.5 * mm


def _gen_carte():
    """5 colonnes, 2 numéros distincts triés par colonne."""
    return [sorted(random.sample(range(lo, hi + 1), 2)) for (lo, hi) in RANGES]


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre, telephone="", titre_jeu="", nom_jeu="ALOHA 75", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 🌺 LA PLAQUE AU COLLIER ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les dix cœurs suivent, chacun à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_COLLIER):
        try:
            c.drawImage(_IMAGE_COLLIER, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS le cœur, jamais en dur.
    # ⚠️ MESURER AVEC LA VRAIE POLICE (`police_ch`), pas Helvetica.
    # ⚠️ les fleurs sont espacées de 0,1395 pour un cœur de 0,088 : le
    #    chiffre peut déborder un peu sans jamais toucher sa voisine.
    _dia = _pw * DIAM_FLEUR
    # ⚠️ 14/08 : Maeva veut 23 pt sur ce jeu (le collier est fin, les
    # chiffres y respirent mieux un peu plus petits).
    # ⭐⭐ 14/08 : LA POLICE DES CHIFFRES DEVIENT « Helvetica-Bold ».
    # Maeva voulait des chiffres qui RENTRENT dans le rond ET qui fassent
    # « waouh ». Le secret n'est pas la taille : c'est LE GRAS.
    #   DJLECO       16,0 pt · 4,38 mm de haut · 24 % de chair
    #   Helvetica-Bold 18,5 pt · 4,76 mm de haut · 58 % de chair  ⭐
    #   Times-Bold   21,0 pt · 5,14 mm · mais ses empattements font
    #                « journal », moins moderne sur un carton coloré.
    # ⚠️ le cœur fait 7,50 mm : « 88 » à 18,5 pt en prend 6,92 — il tient
    # DEDANS avec de l'air.
    _POLICE_NUM = "Helvetica-Bold"
    _t_num = 18.5
    while _t_num > 6 and (_lg_a("88", _POLICE_NUM, _t_num) > _dia * 0.99
                          or _t_num * 0.72 > _ph * HAUT_FLEUR * 0.95):
        _t_num -= 0.5

    # ═══ les DIX numéros, au cœur de leur fleur ═══
    # ⚠️ `carte` donne CINQ colonnes de deux numéros triés. On les aplatit
    # dans l'ordre des pastilles : B·B · I·I · N (haut) puis N · G·G · O·O.
    _plat = [v for colonne in carte for v in colonne]
    for _k, _n in enumerate(_plat[:10]):
        _fx, _fy = FLEURS[_k]
        _nx = _px + _fx * _pw
        _ny = _py + _fy * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, _POLICE_NUM)
        else:
            c.setFillColor(gris_ch)
            c.setFont(_POLICE_NUM, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LE BANDEAU, écrit dans sa pastille creuse ═══
    # ⚠️ Il était NOIR PLEIN dans le dessin (54 % de sa surface) : il est
    # désormais CREUX, et le PDF y écrit en gris.
    c.setFillColor(gris_ch)
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "   \u2605   " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_a(_bl, "Helvetica-Bold", _tb) > _pw * 0.30:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.520, _py + _ph * 0.030, _bl)


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
        # En-tête de page
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        # ⚠️ 14/08 : PLUS DE TITRE EN HAUT DE PAGE — le dessin porte déjà
        # « ALOHA » en grand. Seul le numéro de page reste, discret.
        c.setFillColor(colors.Color(0.62, 0.62, 0.62)); c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 5 * mm, "Page %d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#999999")
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre, telephone, titre_jeu, "ALOHA 75", style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="GRAND LOTO",
                      date_lieu="20 déc 2026", telephone="87 12 34 56")
    with open("test_aloha.pdf", "wb") as f:
        f.write(pdf.read())
    print("ALOHA 75 généré")
