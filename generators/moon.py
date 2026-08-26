# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur MOON (format A4)
6 cartes par feuille A4 (2 colonnes × 3 rangées).
Chaque carte : en-tête M | O | O | N puis grille 4×4 en DAMIER (escalier) :
  rangées 1 et 3 -> colonnes M et O(2)   ·   rangées 2 et 4 -> colonnes O(1) et N
8 numéros par carte, 2 par colonne (triés vers le bas) :
  M = 1-15,  O = 16-30,  O = 46-60,  N = 61-75   (le 31-45 n'existe pas !)
Un CROISSANT DE LUNE en filigrane dans la case vide d'honneur (fidèle au modèle),
et le QR de vérification logé dans une case vide du bas. Pied : « 015001 ».
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
LETTRES = ["M", "O", "O", "N"]
# (min, max) par colonne — MOON saute le 31-45 !
PLAGES = [(1, 15), (16, 30), (46, 60), (61, 75)]
# CHIFFRES REMONTÉS (décision Maeva 24/07) : plus de damier à trous —
# chaque colonne empile ses 2 numéros sur 2 LIGNES pleines → carte courte, 8/A4
# ═══ 🌙 LES HUIT LUNES (sceau Maeva 14/08) ═══
# « VOTRE JEU MOON — 8 BOULES » : huit lunes cratérées, chacune coiffée
# de SA LETTRE — B · B · I · I en haut, G · G · O · O en bas.
# ⭐ Ces lettres tombent sur les quatre colonnes du jeu :
#   B = 1-15 · I = 16-30 · G = 46-60 · O = 61-75
# ⚠️ Le 31-45 n'existe pas dans MOON.
_RATIO_LUNES = 1.5018
LUNES = [[0.2551, 0.5474], [0.4539, 0.5473], [0.6604, 0.5474], [0.8645, 0.5474], [0.255, 0.238], [0.454, 0.2368], [0.6604, 0.2368], [0.8645, 0.2369]]
DIAM_LUNE = 0.1319
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_mo


def _choisir_image(motif_img, ratio_attendu):
    """Retrouve le dessin, quel que soit son nom de fichier."""
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


_IMAGE_LUNES = _choisir_image("moon_lunes", _RATIO_LUNES)


COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 7 * mm
PIED_H = 16 * mm   # le pied héberge désormais le QR


def _gen_carte(rng):
    """8 numéros : 2 distincts par colonne, triés vers le bas."""
    return [sorted(rng.sample(range(pmin, pmax + 1), 2)) for pmin, pmax in PLAGES]


def _croissant(c, cx, cy, r, teinte):
    """🌙 Le croissant de lune — MÊME SILHOUETTE qu'à l'origine, mais rempli
    d'un SEMIS DE POINTS au lieu d'un aplat gris (adouci le 04/08).

    Avant : un disque gris plein moins une morsure. À l'impression noir &
    blanc « au seuil », toute la surface basculait en NOIR PLEIN et la lune
    sortait comme un pâté. Maintenant : des points fins. À l'œil, le même
    croissant doux ; pour l'imprimante, plus aucun aplat à noircir.
    """
    mx, my, mr = cx + r * 0.42, cy + r * 0.18, r * 0.88   # la morsure
    c.saveState()
    p = c.beginPath()
    p.circle(cx, cy, r)
    c.clipPath(p, stroke=0, fill=0)          # on ne peint que dans la lune
    # ⚡ 10/08 : LE SEMIS EN LIGNES POINTILLÉES, plus en points isolés.
    # Avant, chaque point était un petit cercle — soit QUATRE courbes de
    # Bézier chacun, 529 points par lune, 8 752 cercles par feuille et
    # 2 155 Ko que l'imprimante devait avaler (téléchargement très lent).
    # Une ligne pointillée donne la MÊME trame à l'œil, mais ne coûte
    # qu'un trait : 21 lignes par lune au lieu de 529 cercles.
    pas = 2.1                                # même espacement qu'avant
    c.setStrokeColor(teinte)
    c.setLineWidth(0.72)                     # l'épaisseur d'un point d'avant
    c.setDash(0.72, pas - 0.72)              # un tiret court, puis du vide
    j = 0
    yy = cy - r
    while yy <= cy + r:
        demi = (r * r - (yy - cy) ** 2) ** 0.5 if abs(yy - cy) < r else 0
        if demi > 0.4:
            depart = cx - demi + (pas / 2 if j % 2 else 0)   # quinconce conservé
            c.line(depart, yy, cx + demi, yy)
        yy += pas
        j += 1
    c.setDash()                              # on referme le pointillé
    c.setStrokeColor(teinte); c.setLineWidth(0.5)
    c.circle(cx, cy, r, stroke=1, fill=0)    # le bord extérieur
    c.setFillColor(colors.white)             # la morsure : du BLANC, zéro encre
    c.circle(mx, my, mr, stroke=0, fill=1)
    c.setStrokeColor(teinte); c.setLineWidth(0.5)
    c.circle(mx, my, mr, stroke=1, fill=0)   # le bord intérieur du croissant
    c.restoreState()


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habilles. Maeva veut le carton net.

    # ═══ LA PLAQUE AUX HUIT LUNES ═══
    # PAS de preserveAspectRatio : on VEUT l'etirer pour qu'elle epouse
    # la carte. Les huit lunes suivent, chacune a sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_LUNES):
        try:
            c.drawImage(_IMAGE_LUNES, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » (sceau Maeva 14/08).
    # Le secret n'est pas la taille, c'est LE GRAS — 58 % de chair contre
    # 24 % pour DJLECO : les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _dia = _pw * DIAM_LUNE
    _t_num = 40.0
    while _t_num > 6 and (_lg_mo("88", _POLICE_NUM, _t_num) > _dia * 0.74
                          or _t_num * 0.72 > _dia * 0.64):
        _t_num -= 0.5

    # ═══ les HUIT numeros, dans les lunes ═══
    # `cols_nums` donne QUATRE colonnes de deux numeros tries.
    # L'ordre du dessin : B a · B b · I a · I b (haut) · G a · G b · O a · O b (bas)
    _B, _I, _G, _O = cols_nums
    _plat = [_B[0], _B[1], _I[0], _I[1], _G[0], _G[1], _O[0], _O[1]]
    for _k, _n in enumerate(_plat[:8]):
        _bx, _by = LUNES[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, _POLICE_NUM)
        else:
            c.setFillColor(gris_ch)
            c.setFont(_POLICE_NUM, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ LE BANDEAU, ecrit dans sa pastille (deja creuse au dessin) ═══
    c.setFillColor(gris_ch)
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "        \u2605        " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_mo(_bl, "Helvetica-Bold", _tb) > _pw * 0.42:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.535, _py + _ph * 0.036, _bl)


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(915000 + int(serie_start))
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
                                style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_moon.pdf", "wb") as f:
        f.write(pdf.read())
    print("MOON généré")
