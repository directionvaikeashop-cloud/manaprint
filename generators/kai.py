# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur KAI 7 BOULES (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : grille 3×3. 7 numéros + 2 cases barrées d'un X (haut-droite, bas-gauche).
Colonnes : col1 = 1-10, col2 = 11-20, col3 = 21-30.
Disposition :
  col1 (rangées 0,1) · col2 (rangées 0,1,2) · col3 (rangées 1,2)
  case barrée : (rangée 0, col3) en haut-droite  et  (rangée 2, col1) en bas-gauche
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris 40%.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_k
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
# (min, max) par colonne
PLAGES = [(1, 10), (11, 20), (21, 30)]

# ═══ 🎲 LE PUZZLE AUX DÉS (sceau Maeva 13/08) ═══
# Neuf pièces, une paire de dés sur chacune. Il remplace les traits de
# grille : le dessin dit le jeu sans un mot.
# ⚠️ KAI n'a que SEPT numéros : deux cases restent barrées d'un X.
_RATIO_PUZZLE = 0.9981
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


_IMAGE_PUZZLE = _choisir_image("kai_puzzle", _RATIO_PUZZLE)

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
    """col1 : 2 nums (rangées 0,1) ; col2 : 3 nums (0,1,2) ; col3 : 2 nums (1,2)."""
    col1 = sorted(rng.sample(range(1, 11), 2))
    col2 = sorted(rng.sample(range(11, 21), 3))
    col3 = sorted(rng.sample(range(21, 31), 2))
    # grille[rangée][colonne] = numéro ou None (case barrée)
    grille = [
        [col1[0], col2[0], None],     # rangée 0 : col3 barrée (haut-droite)
        [col1[1], col2[1], col3[0]],  # rangée 1 : pleine
        [None,    col2[2], col3[1]],  # rangée 2 : col1 barrée (bas-gauche)
    ]
    return grille


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 3

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    # ⚠️⚠️ 13/08 (sceau Maeva : « retire la protection comme pour le WIN ») :
    # NI CADRE, NI MICROTEXTE, NI QR sur ce jeu. Maeva veut le carton net.
    # ⚠️ CE QUE CELA VEUT DIRE : KAI n'a plus aucune protection anti-copie.

    # ═══ 🎫 LE BANDEAU AUX BOUTS RONDS ═══
    # Le nom du jeu, le n° de série et le téléphone en une seule ligne,
    # dans une pastille en forme de gélule (rayon = moitié de la hauteur).
    hdr_y = y0 + CARD_H - 3.6 * mm
    titre = "KAI 7 boules"
    if titre_jeu and titre_jeu.strip().upper() != titre.upper():
        titre = titre_jeu.strip()
    _ligne = titre + "  \u00b7  N\u00b0 %05d" % serie
    if telephone:
        _ligne += "  \u00b7  " + telephone
    _t_l = 6.0
    while _t_l > 3.4 and _lg_k(_ligne, POLICE, _t_l) > CARD_W - 9.0 * mm:
        _t_l -= 0.25
    _bh = _t_l * 1.72
    _bw = min(_lg_k(_ligne, POLICE, _t_l) + _bh * 1.30, CARD_W - 2.0 * mm)
    _bx = x0 + (CARD_W - _bw) / 2
    _by = hdr_y - _bh * 0.34
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

    # ═══ 🎲 LE PUZZLE EST LA GRILLE ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'il épouse
    # la carte. Ses neuf pièces deviennent les neuf cases.
    grid_top = hdr_y - 2.2 * mm
    grid_bot = y0 + 1.0 * mm
    grid_h = grid_top - grid_bot
    _pw = CARD_W - 0.8 * mm
    _ph = grid_h
    _px = x0 + (CARD_W - _pw) / 2
    _py = grid_bot
    if _os2.path.exists(_IMAGE_PUZZLE):
        try:
            c.drawImage(_IMAGE_PUZZLE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass
    cell_w = _pw / 3.0
    row_h = _ph / 3.0
    # ⚠️ la taille se calcule DEPUIS la pièce, jamais en dur. La PAIRE DE
    # DÉS occupe le coin haut-gauche : le chiffre descend et va à droite.
    _t_num = 42.0
    while _t_num > 8 and (_lg_k("88", police_ch, _t_num) > cell_w * 0.78
                          or _t_num * 0.72 > row_h * 0.78):
        _t_num -= 0.5
    x0_g = _px

    # contenu des cellules
    for r in range(3):
        for cc in range(3):
            cx = x0_g + (cc + 0.54) * cell_w
            cyc = grid_top - (r + 0.62) * row_h
            val = grille[r][cc]
            if val is None:
                # ═══ 🧩 LA PIÈCE MANQUANTE (idée de Trésor, 13/08) ═══
                # Au lieu d'une croix posée par-dessus, la case devient un
                # TROU dans le puzzle : un creux hachuré, comme si la pièce
                # n'avait jamais été placée. C'est le geste naturel du
                # dessin — il dit « ici, rien à cocher » sans un mot.
                cell_x = x0_g + cc * cell_w
                cell_y = cyc - row_h / 2
                _m = min(cell_w, row_h) * 0.20
                _tx, _ty = cell_x + _m, cell_y + _m
                _tw, _th = cell_w - 2 * _m, row_h - 2 * _m
                # le creux, en trait fin et pointillé
                c.saveState()
                try:
                    c.setStrokeColor(GRIS_CLAIR)
                    c.setLineWidth(0.7)
                    c.setDash(2.2, 1.8)
                    c.roundRect(_tx, _ty, _tw, _th, min(_tw, _th) * 0.16,
                                stroke=1, fill=0)
                    c.setDash()
                    # ⚠️ 13/08 (sceau Maeva) : PAS DE HACHURES. Le creux
                    # pointillé suffit à dire le vide — les hachures
                    # alourdissaient la case et buvaient du toner.
                finally:
                    c.restoreState()
            elif _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cyc - _t_num * 0.34, _t_num, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, _t_num)
                c.drawCentredString(cx, cyc - 11, str(val))

    # ⚠️ 13/08 : PLUS DE PIED. Le n° de série est désormais dans le bandeau
    # du haut — l'écrire deux fois faisait doublon, et le pied débordait
    # sur le puzzle qui descend maintenant jusqu'au bas du carton.

    # ⚠️⚠️ 13/08 : PLUS DE QR — il vivait dans la case barrée du bas-gauche.
    # Cette case porte désormais la PIÈCE MANQUANTE (voir plus haut).

def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(770000 + int(serie_start))
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
                _dessiner_carte(c, x0, y0, grille, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Le jeu KAI pour 7 boules",
                      telephone="89 22 23 05")
    with open("test_kai.pdf", "wb") as f:
        f.write(pdf.read())
    print("KAI 7 boules généré")
