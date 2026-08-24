# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur BROWN 8 BOULES (format A4)
8 cartes par feuille A4 (2 colonnes × 4 rangées).
Chaque carte : grille 3×5 B·R·O·W·N, 8 numéros placés en quinconce, N° de série au centre.
Plages : B 1-15, R 16-30, O 31-45, W 46-60, N 61-75.
Disposition des numéros :
  rangée haute : B  ·  O  ·  N      (colonnes 0,2,4)
  rangée milieu:    R · (série) · W (colonnes 1,3 + centre = série)
  rangée basse : B  ·  O  ·  N      (colonnes 0,2,4)
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris 40%.
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
GRIS40 = colors.Color(0.60, 0.60, 0.60)        # chiffres
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)    # lignes de grille



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
LETTERS = ["B", "R", "O", "W", "N"]
# (lettre, min, max, nb de numéros)
# ⚠️⚠️ 14/08 (sceau Maeva : « les lettres sont les plages du jeu ») :
# LES LETTRES DEVIENNENT CELLES DU BINGO — B · I · N · G · O — au lieu de
# B · R · O · W · N. Les plages et les comptes ne changent PAS :
#   B ×2 : 1-15 · I ×1 : 16-30 · N ×2 : 31-45 · G ×1 : 46-60 · O ×2 : 61-75
PLAGES = [("B", 1, 15, 2), ("I", 16, 30, 1), ("N", 31, 45, 2),
          ("G", 46, 60, 1), ("O", 61, 75, 2)]

# ═══ 💐 LE BOUQUET DE HUIT FLEURS (sceau Maeva 14/08) ═══
# « VOTRE JEU BROWN — 8 BOULES » : huit fleurs liées d'un ruban, chacune
# portant SA LETTRE sur un fanion et son cœur rond pour le numéro.
# ⚠️ L'ORDRE suit les fanions du dessin : rangée du haut B·I·N·N,
# rangée du bas B·G·O·O.
_RATIO_BOUQUET = 1.4991
FLEURS = [[0.3108, 0.6544], [0.4644, 0.647], [0.6486, 0.6474], [0.821, 0.6541], [0.2939, 0.3968], [0.4603, 0.3981], [0.6519, 0.3979], [0.8277, 0.3953]]
DIAM_FLEUR = 0.112
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_w


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


_IMAGE_BOUQUET = _choisir_image("brown_bouquet", _RATIO_BOUQUET)

# ⚠️ l'ordre des numéros, fanion par fanion
ORDRE_FANIONS = [("B", 0), ("I", 0), ("N", 0), ("N", 1),
                 ("B", 1), ("G", 0), ("O", 0), ("O", 1)]

COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """Numéros distincts par colonne (2 pour B/O/N, 1 pour R/W)."""
    return {lettre: sorted(rng.sample(range(a, b + 1), n)) for lettre, a, b, n in PLAGES}


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 💐 LA PLAQUE AU BOUQUET ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les huit cœurs suivent, chacun à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_BOUQUET):
        try:
            c.drawImage(_IMAGE_BOUQUET, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS le cœur de la fleur, jamais en dur.
    # ⚠️ MESURER AVEC LA VRAIE POLICE (`police_ch`), pas Helvetica.
    _dia = _pw * DIAM_FLEUR
    _t_num = 25.0
    while _t_num > 6 and (_lg_w("88", police_ch, _t_num) > _dia * 1.05
                          or _t_num * 0.72 > _dia * 0.86):
        _t_num -= 0.5

    # ═══ les HUIT numéros, au cœur de leur fleur ═══
    for _k, (_lettre, _rang) in enumerate(ORDRE_FANIONS):
        _vals = carte.get(_lettre) or []
        if _rang >= len(_vals):
            continue
        _n = _vals[_rang]
        _fx, _fy = FLEURS[_k]
        _nx = _px + _fx * _pw
        _ny = _py + _fy * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LES DEUX BANDEAUX, écrits dans leurs pastilles creuses ═══
    # ⚠️ Ils étaient NOIRS PLEINS dans le dessin (70 % et 45 % de leur
    # surface en encre) : ils sont désormais CREUX, texte en gris.
    c.setFillColor(gris_ch)
    _t8 = 7.0
    while _t8 > 3.2 and _lg_w("8 BOULES", "Helvetica-Bold", _t8) > _pw * 0.14:
        _t8 -= 0.25
    c.setFont("Helvetica-Bold", _t8)
    c.drawCentredString(_px + _pw * 0.560, _py + _ph * 0.790, "8 BOULES")

    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "   \u2022   " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_w(_bl, "Helvetica-Bold", _tb) > _pw * 0.29:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.525, _py + _ph * 0.020, _bl)


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(680000 + int(serie_start))
    serie = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0

    for _ in range(nb_pages):
        # En-tête de page
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 10)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        # ⚠️ 14/08 : PLUS DE TITRE EN HAUT DE PAGE — le dessin de Maeva
        # porte déjà « BROWN » et « 8 BOULES » en grand. Seul le numéro de
        # page reste, discret, pour s'y retrouver dans une grosse commande.
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 5)
        c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 5 * mm, "Page %d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, carte, coul, serie, telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=8, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="GRAND LOTO",
                      date_lieu="20 déc 2026", telephone="87 12 34 56")
    with open("test_brown.pdf", "wb") as f:
        f.write(pdf.read())
    print("BROWN 8 boules généré")
