"""
MANAPRINT — Générateur DIAMANT (format A4)

💍 REFAIT LE 10/08 (sceau Maeva) : DIX BAGUES, deux par lettre du mot
BINGO. Chaque bague porte SON NUMÉRO au cœur de sa pierre — « une boule
dans chaque bague » — et chaque rangée porte sa lettre.

RÈGLE (sceau Maeva 10/08) : 10 numéros, DEUX PAR LETTRE —
  B : 1-15 · I : 16-30 · N : 31-45 · G : 46-60 · O : 61-75
Le sac du crieur ne change pas : c'est toujours 1 à 75.

⚡ ÉCONOMIE D'ENCRE : la bague est réduite à SON CONTOUR (les facettes
fines des petits diamants ont été retirées à la découpe : 22 % d'encre
en moins), et le dessin est pâli une fois pour toutes.
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgd
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


# Couleurs DIAMANT : alternance jaune / orange (fidèle à la maquette)
DIAMANT_COULEURS = ["#F2C60A", "#F57C00"]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)
GRIS_CROIX = colors.Color(0.72, 0.72, 0.72)
GRIS_GRILLE = colors.Color(0.55, 0.55, 0.55)

# ══ DEUX GAMMES COMMERCIALES (vision Maeva) ══════════════════════════
# ÉCO      : écriture fine DejaVu ExtraLight, gris 0,50 — économie de toner
# PREMIUM  : écriture grasse Helvetica-Bold, gris 0,55 — style P15
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TF
try:
    # 💎 10/08 (sceau Maeva) : la GRASSE CONDENSÉE, celle de QUINES 90.
    # Elle est plus étroite qu'une grasse ordinaire, donc on peut la
    # monter plus haut à place égale — et elle se lit de loin.
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

# 💍 LA BAGUE DE MAEVA, et l'intérieur de sa pierre (mesuré au pixel).
_RATIO_BAGUE = 0.973
PIERRE = (0.233, 0.767, 0.208, 0.781)   # x0, x1, y0, y1 — l'intérieur du diamant
# ⚠️ 10/08 : ces fractions ont été RECALCULÉES sur l'image finale (le plus
# grand rectangle vide au cœur de la pierre). Les premières venaient du
# cadrage d'avant et disaient la pierre plus large que haute — l'inverse
# de la vérité — ce qui bridait les chiffres à 18 pt au lieu de 25.
import os as _os2


def _choisir_image(motif, ratio_attendu):
    """🛟 Retrouve le dessin, quel que soit son nom de fichier.

    Au téléversement, le nom peut garder un préfixe de livraison ou
    recevoir un « (1) ». On prend donc, parmi les fichiers dont le nom
    contient `motif`, celui dont les PROPORTIONS collent au dessin
    attendu — la seule marque qui ne mente pas.
    """
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


_IMAGE_BAGUE = _choisir_image("diamant_bague", _RATIO_BAGUE)

# 💍 12 cartes / A4 (sceau Maeva 10/08) : le carton d'avant laissait
# un large blanc a droite des bagues. En le serrant sur elles, on en
# tient QUATRE par rangee au lieu de deux — deux fois plus de cartons
# par feuille, et les chiffres gardent leurs 18 pt.
# ═══ 💎 LES DIX DIAMANTS (sceau Maeva 14/08) ═══
# « VOTRE JEU DIAMANT » : dix diamants taillés, chacun portant SA LETTRE
# sur un ruban et son corps hexagonal pour le numéro.
# ⚠️ L'ORDRE suit les rubans du dessin : rangée du haut B·B·I·I·N,
# rangée du bas G·G·N·O·O.
_RATIO_DIAM = 1.4991
DIAMANTS = [[0.2418, 0.8185], [0.399, 0.7436], [0.5617, 0.6849], [0.7154, 0.8189], [0.8658, 0.6874], [0.224, 0.2444], [0.3884, 0.2213], [0.5554, 0.2325], [0.7265, 0.2304], [0.8955, 0.2302]]
LARG_DIAM = 0.106
HAUT_DIAM = 0.1732
# ⚠️ chaque case dit (lettre, rang) : le rang 0 est le premier numéro de
# la paire, le rang 1 le second.
ORDRE_RUBANS = [("B", 0), ("B", 1), ("I", 0), ("I", 1), ("N", 0),
                ("G", 0), ("G", 1), ("N", 1), ("O", 0), ("O", 1)]
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


_IMAGE_DIAM = _choisir_image("diamant_dix", _RATIO_DIAM)


# ⚠️ 14/08 : le dessin est en PAYSAGE (ratio 1,50) — on passe de 12 cartes
# à 8 cartes-plaques (2 colonnes × 4 rangées).
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
FOOT_H = 3 * mm
BANDEAU_H = 2.8 * mm
GRID_N = 5  # 5x5

# Le motif DIAMANT : cases pleines (ligne, colonne), lignes numérotées du HAUT
POSITIONS = {
    (0, 0), (0, 2), (0, 4),
    (1, 1), (1, 2), (1, 3),
    (3, 1), (3, 2), (3, 3),
    (4, 0), (4, 2), (4, 4),
}
# Nombre de numéros nécessaires par colonne
_NB_PAR_COL = [2, 2, 4, 2, 2]


LETTRES_BINGO = "BINGO"


def _gen_carte():
    """🎰 DIX numéros : DEUX par lettre du mot BINGO, triés.

    B : 1-15 · I : 16-30 · N : 31-45 · G : 46-60 · O : 61-75
    (sceau Maeva 10/08 — avant, la grille en portait 12.)
    """
    return [sorted(random.sample(range(lo, hi + 1), 2)) for (lo, hi) in RANGES]

def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 💎 LA PLAQUE AUX DIX DIAMANTS ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les dix corps suivent, chacun à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_DIAM):
        try:
            c.drawImage(_IMAGE_DIAM, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS le corps du diamant, jamais en dur.
    # ⚠️ MESURER AVEC LA VRAIE POLICE (`police_ch`), pas Helvetica.
    # ⚠️ le corps est un HEXAGONE qui se resserre vers le bas : le chiffre
    #    se pose dans sa partie large, en haut.
    _lg_c = _pw * LARG_DIAM
    _ht_c = _ph * HAUT_DIAM
    _t_num = 25.0
    # ⚠️⚠️ 14/08 : le chiffre doit tenir DANS LE CŒUR VIDÉ (0,92 du corps),
    # pas déborder sur les arêtes de la pierre. On borne donc à 0,80 en
    # largeur — c'est ce qui garde le diamant entièrement visible.
    # ⚠️⚠️ 14/08 (nouvelle image, plus grands diamants) : Maeva veut 25 pt.
    # Le cœur est ouvert à 1,12 du corps dans l'image, et le chiffre est
    # borné à 1,10 — il tient DEDANS sans mordre les arêtes de la pierre.
    while _t_num > 6 and (_lg_d("88", police_ch, _t_num) > _lg_c * 1.10
                          or _t_num * 0.72 > _ht_c * 0.62):
        _t_num -= 0.5

    # ═══ les DIX numéros, au cœur de leur diamant ═══
    # ⚠️ `carte` est une LISTE de cinq paires triées (B, I, N, G, O).
    _par_lettre = {"B": carte[0], "I": carte[1], "N": carte[2],
                   "G": carte[3], "O": carte[4]}
    for _k, (_lettre, _rang) in enumerate(ORDRE_RUBANS):
        _vals = _par_lettre.get(_lettre) or []
        if _rang >= len(_vals):
            continue
        _n = _vals[_rang]
        _dx, _dy = DIAMANTS[_k]
        _nx = _px + _dx * _pw
        _ny = _py + _dy * _ph - _t_num * 0.34
        # ⭐⭐ 14/08 (sceau Maeva : « je n'aime pas quand les chiffres
        # cachent nos diamants — trouve une solution où on voit bien le
        # diamant ») : PLUS DE VOILE BLANC PLAQUÉ SUR LA PIERRE.
        # ⚠️ LA SOLUTION EST DANS L'IMAGE : le CŒUR de chaque pierre a été
        # vidé de ses facettes (un losange inscrit à 0,78 de sa taille).
        # La couronne, les arêtes extérieures et la pointe restent — la
        # pierre se voit entièrement, et le chiffre a sa place nette.
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LE BANDEAU, écrit dans sa pastille creuse ═══
    c.setFillColor(gris_ch)
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "   \u2022   " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_d(_bl, "Helvetica-Bold", _tb) > _pw * 0.30:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.535, _py + _ph * 0.030, _bl)


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
        titre_aff = titre_jeu if titre_jeu else "DIAMANT"
        # ⚠️ 14/08 : PLUS DE TITRE EN HAUT DE PAGE — le dessin porte déjà
        # « DIAMANT » en grand. Seul le numéro de page reste, discret.
        c.setFillColor(GRIS40); c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 5 * mm, "Page %d" % no_page)

        idx = 0
        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte()
                if couleur and couleur_perso:
                    coul = couleur_perso
                elif couleur:
                    coul = DIAMANT_COULEURS[idx % len(DIAMANT_COULEURS)]  # jaune / orange
                else:
                    coul = "#999999"
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1
                idx += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True, titre_jeu="")
    with open("test_diamant.pdf", "wb") as f:
        f.write(pdf.read())
    print("DIAMANT g\u00e9n\u00e9r\u00e9")
