# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur RUBIS 75 (format A4)
12 cartes par feuille A4 (2 colonnes × 6 rangées).
Chaque carte : grille 5 colonnes (R-U-B-I-S) × 3 rangées.
La case CENTRALE (colonne B, rangée du milieu) est toujours VIDE (centre libre).
=> 14 numéros par carton.
Colonnes : R=1-15, U=16-30, B=31-45, I=46-60, S=61-75.
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

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne
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
GREY = colors.Color(0.60, 0.60, 0.60)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)


# ══ DEUX GAMMES COMMERCIALES ══════════════════════════
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
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4
LETTERS = ["R", "U", "B", "I", "S"]
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

# ═══ 💎 LE COFFRET AUX QUATORZE PIERRES (sceau Maeva 14/08) ═══
# « RUBIS 75 » : un écrin ouvert, ses quatorze gemmes taillées en
# rectangle, une serrure au pied et des diamants aux coins.
# ⚠️ Les pierres sont rangées 4 · 3 · 4 · 3, du HAUT vers le BAS.
# ⚠️ On les remplit dans l'ordre de lecture — le dessin ne porte pas les
# lettres R·U·B·I·S, les numéros y coulent naturellement.
_RATIO_COFFRET = 1.4964
PIERRES = [(0.315, 0.6672), (0.4656, 0.6683), (0.615, 0.6683), (0.7637, 0.6684), (0.3771, 0.5331), (0.5399, 0.533), (0.7005, 0.5317), (0.2949, 0.403), (0.4571, 0.403), (0.6176, 0.4078), (0.7839, 0.4091), (0.3688, 0.2725), (0.5383, 0.2725), (0.7048, 0.2724)]
LARG_PIERRE = 0.1160
HAUT_PIERRE = 0.1030
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_ru


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


_IMAGE_COFFRET = _choisir_image("rubis_coffret", _RATIO_COFFRET)


# ⚠️ 14/08 : le dessin est en PAYSAGE (ratio 1,50) — on passe de 10 cartes
# à 8 cartes-plaques (2 colonnes × 4 rangées).
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

HDR_H = 4 * mm
FOOT_H = 3.5 * mm


def _gen_carte(rng):
    """5 colonnes × 3 rangées. 3 numéros triés par colonne, SAUF la colonne B
    (milieu) qui n'a que 2 numéros : la case centrale (B, rangée 1) est vide.
    Retourne une matrice grille[rangée][colonne] (None = case vide)."""
    cols = []
    for ci, (lo, hi) in enumerate(RANGES):
        if ci == 2:  # colonne B : centre libre -> 2 numéros (rangées 0 et 2)
            nums = sorted(rng.sample(range(lo, hi + 1), 2))
            cols.append([nums[0], None, nums[1]])
        else:
            nums = sorted(rng.sample(range(lo, hi + 1), 3))
            cols.append([nums[0], nums[1], nums[2]])
    # transposer en grille[rangée][colonne]
    grille = [[cols[c][r] for c in range(5)] for r in range(3)]
    return grille


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 💎 LA PLAQUE AU COFFRET ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les quatorze pierres suivent, chacune à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_COFFRET):
        try:
            c.drawImage(_IMAGE_COFFRET, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⭐⭐ LA POLICE DES CHIFFRES : « Helvetica-Bold » (sceau Maeva 14/08).
    # Le secret n'est pas la taille, c'est LE GRAS — 58 % de chair contre
    # 24 % pour DJLECO : les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_p = _pw * LARG_PIERRE
    _ht_p = _ph * HAUT_PIERRE
    _t_num = 34.0
    while _t_num > 6 and (_lg_ru("88", _POLICE_NUM, _t_num) > _lg_p * 0.80
                          or _t_num * 0.72 > _ht_p * 0.74):
        _t_num -= 0.5

    # ═══ les QUATORZE numéros, dans les pierres du coffret ═══
    # ⚠️ `grille` est 3×5 ; la case centrale (colonne B, rangée 1) est None.
    # On aplatit en sautant le vide, puis on remplit les pierres dans
    # l'ordre de lecture du dessin (4 · 3 · 4 · 3).
    _plat = [v for rangee in grille for v in rangee if v is not None]
    for _k, _n in enumerate(_plat[:14]):
        _bx, _by = PIERRES[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, _POLICE_NUM)
        else:
            c.setFillColor(gris_ch)
            c.setFont(_POLICE_NUM, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LE BANDEAU, écrit dans sa pastille (déjà creuse au dessin) ═══
    c.setFillColor(gris_ch)
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "        \u2605        " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_ru(_bl, "Helvetica-Bold", _tb) > _pw * 0.44:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.555, _py + _ph * 0.042, _bl)


def generer_pdf(nb_cartes=10, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(975000 + int(serie_start))
    serie = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 9)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        # ⚠️ 14/08 : le numéro de page passe à DROITE et en tout petit —
        # le dessin porte déjà « RUBIS 75 » en grand au centre.
        c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 5 * mm, "Page %d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                grille = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, grille, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=10, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="RUBIS 75",
                      telephone="89.22.23.05")
    with open("test_rubis.pdf", "wb") as f:
        f.write(pdf.read())
    print("RUBIS 75 généré")
