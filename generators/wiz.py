# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur WIZ 4 BOULES (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : 4 numéros en losange —
  haut   : 1 numéro (16-30), centré
  milieu : 2 numéros — gauche (1-15) | droite (31-45), séparés d'un trait vertical
  bas    : 1 numéro (16-30), centré  (jamais le même que celui du haut)
En-tête « Le jeux WIZ pour 4 boules … », série en pied (fidèle au modèle).
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
# Les 3 plages du WIZ 4 boules
PLAGE_HAUT_BAS = (16, 30)   # haut ET bas (2 numéros distincts)
PLAGE_GAUCHE = (1, 15)
PLAGE_DROITE = (31, 45)

# ═══ 🧊 LES QUATRE GLAÇONS (sceau Maeva 13/08) ═══
# « VOTRE JEU WIZ — AVEC 4 CHIFFRES » : quatre glaçons empilés 2×2, chacun
# avec sa fenêtre claire au centre. Ils remplacent le losange d'origine :
# les numéros se lisent désormais EN CARRÉ, comme le dessin le demande.
_RATIO_GLACONS = 0.9982
FENETRES = [[0.3222, 0.6217], [0.6499, 0.622], [0.3222, 0.3059], [0.6503, 0.3059]]
LARG_FEN = 0.2144
HAUT_FEN = 0.2179
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_z


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


_IMAGE_GLACONS = _choisir_image("wiz_glacons", _RATIO_GLACONS)


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
    """4 numéros : haut (16-30), gauche (1-15), droite (31-45), bas (16-30 ≠ haut)."""
    haut, bas = rng.sample(range(PLAGE_HAUT_BAS[0], PLAGE_HAUT_BAS[1] + 1), 2)
    gauche = rng.randint(*PLAGE_GAUCHE)
    droite = rng.randint(*PLAGE_DROITE)
    return haut, gauche, droite, bas


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    haut, gauche, droite, bas = nums
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 13/08 : ni cadre, ni microtexte, ni QR — comme WIN, KAI et SUN.
    # Maeva veut le carton net ; le dessin se suffit à lui-même.

    # ═══ 🧊 LA PLAQUE AUX GLAÇONS ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les quatre fenêtres suivent, chacune à sa place.
    BANDE_PIED = 5.0 * mm
    _pw = CARD_W - 0.8 * mm
    _ph = CARD_H - 1.0 * mm - BANDE_PIED
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + BANDE_PIED + 0.5 * mm
    if _os2.path.exists(_IMAGE_GLACONS):
        try:
            c.drawImage(_IMAGE_GLACONS, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS la fenêtre du glaçon, jamais en dur.
    _fw = _pw * LARG_FEN
    _fh = _ph * HAUT_FEN
    _t_num = 44.0
    while _t_num > 8 and (_lg_z("88", police_ch, _t_num) > _fw * 0.80
                          or _t_num * 0.72 > _fh * 0.66):
        _t_num -= 0.5

    # ═══ les QUATRE numéros, dans leurs glaçons ═══
    # ⚠️ l'ordre du tirage est (haut, gauche, droite, bas) — hérité du
    # losange. On le range en CARRÉ : haut-gauche, haut-droite,
    # bas-gauche, bas-droite.
    for _i, _val in enumerate((haut, gauche, bas, droite)):
        _fx, _fy = FENETRES[_i]
        _nx = _px + _fx * _pw
        _ny = _py + _fy * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _val, _nx, _ny, _t_num, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t_num)
            c.drawCentredString(_nx, _ny, str(_val))

    # ═══ 🎫 LE BANDEAU AUX BOUTS RONDS, en pied ═══
    _ligne = "N\u00b0 %05d" % serie
    if telephone:
        _ligne += "  \u00b7  " + telephone
    _t_l = 5.4
    while _t_l > 3.2 and _lg_z(_ligne, POLICE, _t_l) > CARD_W - 9.0 * mm:
        _t_l -= 0.25
    _bh = _t_l * 1.72
    _bw = min(_lg_z(_ligne, POLICE, _t_l) + _bh * 1.30, CARD_W - 2.0 * mm)
    _bx = x0 + (CARD_W - _bw) / 2
    _by = y0 + 0.8 * mm
    _plein = couleur_hex not in ("#9A9A9A", "#999999")
    c.setStrokeColor(col)
    c.setLineWidth(0.6)
    if _plein:
        c.setFillColor(col)
        c.roundRect(_bx, _by, _bw, _bh, _bh / 2.0, stroke=1, fill=1)
        c.setFillColor(colors.white)
    else:
        c.roundRect(_bx, _by, _bw, _bh, _bh / 2.0, stroke=1, fill=0)
        c.setFillColor(col)
    c.setFont(POLICE, _t_l)
    c.drawCentredString(x0 + CARD_W / 2, _by + _bh * 0.32, _ligne)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random()   # graine fraîche : cartes uniques à chaque génération
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
                nums = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, nums, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="",
                      telephone="89 22 23 05")
    with open("test_wiz.pdf", "wb") as f:
        f.write(pdf.read())
    print("WIZ 4 boules généré")
