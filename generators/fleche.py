# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TAHITI (ex-FLÈCHE, format A4)

🌺 REFAIT LE 09/08 (sceau Maeva) : la BOUTEILLE de Maeva occupe tout le
carton, et les DIX NUMÉROS montent DANS LE VERRE — deux par lettre du
mot BINGO. Au pied, sa fleur d'hibiscus, et DANS LE CŒUR DE LA FLEUR,
NOS DÉS (ceux de motifs.py, la marque de la maison).

RÈGLE (sceau Maeva 09/08) : 10 numéros, DEUX PAR LETTRE —
  B : 1-15 · I : 16-30 · N : 31-45 · G : 46-60 · O : 61-75
Le sac du crieur ne change pas : c'est toujours 1 à 75.

⚡ ÉCONOMIE D'ENCRE : le dessin est pâli une fois pour toutes à la
découpe, et les dés sont tracés au trait.
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgt
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
    # 🌺 12/08 (sceau Maeva) : la GRASSE CONDENSÉE, celle de QUINES 90.
    # Plus étroite qu'une grasse ordinaire, donc plus haute à place égale —
    # et elle se lit de loin. Le corps du verre offre 11,4 mm par nombre :
    # de quoi porter 27 pt, au-delà des 25 demandés.
    _pm.registerFont(_TF("DJBOLDC", "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"))
    _POLICE_ECO = "DJBOLDC"
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
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
# La FLÈCHE : rangées occupées par colonne (0 = rangée du haut)
# c1 : haut + plancher · c2 : 2e + plancher · c3 : 4e + plancher
# c4 : 3e, 4e + plancher · c5 : toutes (le bord droit complet)
RANGEES = [(0, 4), (1, 4), (3, 4), (2, 3, 4), (0, 1, 2, 3, 4)]
CASE_QR = (0, 2)   # (rangée, colonne) de la case barrée qui accueille le QR

# 🍾 LA BOUTEILLE DE MAEVA, et le cœur de sa fleur (mesuré au pixel).
_RATIO_TAHITI = 380.0 / 730.0
FLEUR = (0.005, 0.697, 0.000, 0.418)     # x0, x1, y0, y1 du bloc fleur
# 🍾 LE CORPS DE LA BOUTEILLE, mesuré ligne par ligne : c'est là que
# vivent les numéros (repère PDF, depuis le bas).
# ⚠️ 12/08 : le corps s'élargit de 4 % de chaque côté (0,395 → 0,880).
# Mesuré sur le dessin : le verre a encore du ventre à cet endroit, les
# nombres ne débordent pas. C'est ce qui permet les 25 pt demandés.
CORPS = (0.385, 0.890, 0.150, 0.585)     # x0, x1, y0, y1 du verre
# ⚠️ Le bas du verre est laisse a la FLEUR : les numeros s'arretent au-dessus.
LETTRES_BINGO = "BINGO"
# 💰 LE BONUS DE LA FLEUR : le montant est TIRE avec la carte.
MONTANTS = [5, 10, 20, 50, 100]
# ⚠️ le bas du corps est laisse a la FLEUR : les numeros s arretent au-dessus.
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


_IMAGE_TAHITI = _choisir_image("tahiti_bouteille", _RATIO_TAHITI)


def _un_de(c, cx, cy, t, valeur, col, gris_ch):
    """🎲 LE DÉ DU CASINO — exactement le tracé de nos jeux SUN/POW/WIN
    CASINO : carré arrondi blanc bordé couleur, points bien francs
    disposés comme sur les dés du commerce.

    C'est le « principe casino » voulu par Maeva (09/08) : les mêmes
    proportions partout, pour que le joueur reconnaisse nos dés d'un
    seul coup d'œil.
    """
    r = t / 2.0
    c.setStrokeColor(col)
    c.setLineWidth(1.1)
    c.setFillColor(colors.white)
    c.roundRect(cx - r, cy - r, t, t, t * 0.18, stroke=1, fill=1)
    q = t * 0.26
    pos = {1: [(0, 0)], 2: [(-q, q), (q, -q)], 3: [(-q, q), (0, 0), (q, -q)],
           4: [(-q, q), (q, q), (-q, -q), (q, -q)],
           5: [(-q, q), (q, q), (0, 0), (-q, -q), (q, -q)],
           6: [(-q, q), (q, q), (-q, 0), (q, 0), (-q, -q), (q, -q)]}[valeur]
    c.setFillColor(gris_ch)
    for dx, dy in pos:
        c.circle(cx + dx, cy + dy, t * 0.085, stroke=0, fill=1)


# 🎲 la décomposition du casino : au-delà de 6, DEUX dés dont la somme
# donne le nombre — la règle de SUN CASINO, reprise telle quelle.
DECOMP_DES = {7: (4, 3), 8: (4, 4), 9: (5, 4), 10: (5, 5), 11: (6, 5), 12: (6, 6)}


def _des_casino(c, valeur, cx, cy, ech, col, gris_ch):
    """Pose la valeur EN DÉS, à la manière du casino : un seul dé
    jusqu'à 6, deux dés au-delà."""
    if valeur <= 6:
        _un_de(c, cx, cy, 11.5 * mm * ech, valeur, col, gris_ch)
    else:
        a, b = DECOMP_DES.get(valeur, (5, 4))
        _un_de(c, cx - 4.4 * mm * ech, cy, 7.8 * mm * ech, a, col, gris_ch)
        _un_de(c, cx + 4.4 * mm * ech, cy, 7.8 * mm * ech, b, col, gris_ch)



# 🍾 6 cartes / A4 (sceau Maeva 09/08) : le carton d'avant laissait
# 28 mm de blanc de chaque cote de la bouteille. En le serrant sur
# elle, on en tient TROIS par rangee au lieu de deux — +50 % de
# cartons par feuille, et les chiffres ne perdent que 2 pt.
# ═══ 🍾 LE BAC AUX DIX BOUTEILLES (sceau Maeva 14/08) ═══
# « VOTRE JEU TAHITI — 10 BOUTEILLES » : dix bouteilles au frais dans un
# bac à glaçons, chacune portant SA LETTRE sur le goulot et son étiquette
# ovale pour le numéro. Deux rangées de cinq : B · I · N · G · O.
_RATIO_BAC = 1.5018
BOUTEILLES = [[0.2933, 0.5884], [0.4178, 0.586], [0.5507, 0.586], [0.6787, 0.5858], [0.8055, 0.5862], [0.2499, 0.3643], [0.3903, 0.3495], [0.5458, 0.3505], [0.702, 0.3492], [0.8452, 0.3616]]
LARG_ETIQ = 0.0743
RAP_ETIQ = 1.5
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_t


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


_IMAGE_BAC = _choisir_image("tahiti_bac", _RATIO_BAC)


# ⚠️ 14/08 : le dessin est en PAYSAGE (ratio 1,50) — on passe de 6 cartes
# à 8 cartes-plaques (2 colonnes × 4 rangées).
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 7 * mm
GUTTER_X = 3.5 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 6 * mm


def _gen_carte(rng):
    """🎰 DIX numéros : DEUX par lettre du mot BINGO, triés.

    B : 1-15 · I : 16-30 · N : 31-45 · G : 46-60 · O : 61-75
    (sceau Maeva 09/08 — avant, la flèche en portait 14.)
    """
    return ([sorted(rng.sample(range(lo, hi + 1), 2)) for (lo, hi) in PLAGES],
            rng.choice(MONTANTS))


def _dessiner_carte(c, x0, y0, cols_nums, bonus_des, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 5

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 🍾 LA PLAQUE AU BAC ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les dix étiquettes suivent, chacune à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_BAC):
        try:
            c.drawImage(_IMAGE_BAC, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS l'étiquette, jamais en dur.
    # ⚠️ MESURER AVEC LA VRAIE POLICE (`police_ch`), pas Helvetica.
    # ⚠️ l'étiquette est un OVALE : plus haute que large (×1,50), donc
    #    c'est sa LARGEUR qui bride.
    _lg_e = _pw * LARG_ETIQ
    _ht_e = _lg_e * RAP_ETIQ
    _t_num = 25.0
    # ⚠️ 14/08 : le chiffre peut DÉBORDER un peu de l'étiquette — il
    # repose sur le corps de la bouteille, que le voile éclaircit. On
    # desserre donc à 1,45 en largeur pour retrouver de la lisibilité.
    while _t_num > 6 and (_lg_t("88", police_ch, _t_num) > _lg_e * 1.45
                          or _t_num * 0.72 > _ht_e * 0.78):
        _t_num -= 0.5

    # ═══ les DIX numéros, sur l'étiquette de leur bouteille ═══
    # ⭐ 14/08 (sceau Maeva : « les ronds cachent le visuel des bouteilles,
    # trouve-nous une autre solution ») : PLUS D'OVALE BLANC PLAQUÉ SUR
    # LE VERRE. Le dessin reste intact, et le numéro se pose SUR
    # l'étiquette d'origine — avec, sous lui, un simple VOILE CLAIR qui
    # éclaircit le fond juste assez pour qu'il se lise, sans effacer les
    # reflets ni le galbe de la bouteille.
    # ⚠️ cols_nums donne CINQ paires (B, I, N, G, O). On les range en
    # DEUX RANGÉES : la rangée du haut prend le premier de chaque paire,
    # celle du bas le second — comme le dessin le montre.
    _haut = [p[0] for p in cols_nums]
    _bas = [p[1] for p in cols_nums]
    for _k, _n in enumerate(_haut + _bas):
        if _k >= len(BOUTEILLES):
            break
        _bx, _by = BOUTEILLES[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        # 🕯️ LE VOILE : un ovale blanc à peine opaque, juste sous le
        # chiffre. Il éclaircit le verre sans le masquer.
        c.saveState()
        try:
            c.setFillColor(colors.Color(1, 1, 1, alpha=0.72))
            _vw = _lg_e * 1.62
            _vh = _vw * 0.78
            c.ellipse(_nx - _vw / 2, _ny - _vh * 0.30,
                      _nx + _vw / 2, _ny + _vh * 0.70, stroke=0, fill=1)
        finally:
            c.restoreState()
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LE BANDEAU, écrit dans sa pastille creuse ═══
    # ⚠️ Il était NOIR PLEIN dans le dessin (61 % de sa surface en encre) :
    # il est désormais CREUX, et le PDF y écrit en gris.
    c.setFillColor(gris_ch)
    _t10 = 7.0
    while _t10 > 3.2 and _lg_t("10 BOUTEILLES", "Helvetica-Bold", _t10) > _pw * 0.15:
        _t10 -= 0.25
    c.setFont("Helvetica-Bold", _t10)
    c.drawCentredString(_px + _pw * 0.547, _py + _ph * 0.777, "10 BOUTEILLES")

    # le numéro de série, discret au pied du bac
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "   \u2022   " + telephone
    _tb = 6.5
    while _tb > 3.4 and _lg_t(_bl, "Helvetica-Bold", _tb) > _pw * 0.30:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.560, _py + _ph * 0.025, _bl)


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(935500 + int(serie_start))
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
                cols_nums, bonus_des = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, cols_nums, bonus_des, coul, serie, titre_jeu, telephone,
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
                      telephone="689 89 22 23 05")
    with open("test_fleche.pdf", "wb") as f:
        f.write(pdf.read())
    print("FLÈCHE généré")
