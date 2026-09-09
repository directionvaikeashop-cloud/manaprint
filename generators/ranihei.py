# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur RANIHEI (planche A4 paysage)

🌺 NÉ LE 03/09 (sceau Maeva) — LA PLANCHE DE RANIHEI SISTERS & SHOP.
Une feuille entière, encadrée d'hibiscus, qui porte SIX CARTES de bingo.
Chaque carte a son ruban « Carte N° … » et TROIS COLONNES DE TROIS RONDS,
coiffées de B-I, N-G et O-★.

RÈGLE — neuf numéros par carte, tous différents, trois par colonne :
  colonne B-I : 1-30
  colonne N-G : 31-60
  colonne O-★ : 61-90
⚠️ Les trois plages se suivent sans trou : tout le sac de 1 à 90 sert.
⚠️ Le sac du crieur va de 1 à 90.

⚠️⚠️ CE JEU EST À PART DANS LE CATALOGUE : le dessin n'est PAS un carton
   qu'on répète, c'est UNE FEUILLE ENTIÈRE. Une page du PDF = une planche
   = SIX cartes. D'où `cartes_par_feuille = 6` et une seule image par page.
⚠️ La feuille est en PAYSAGE (ratio 1,5182) — on la centre sur un A4
   couché, en respectant son ratio, sinon les ronds s'ovalisent.

⭐ NUMÉROTATION (règle de la maison, sceau Maeva 03/09) : le NUMÉRO DE
   SÉRIE va DANS CHAQUE CARTE, à la place que le ruban lui réserve, et le
   NUMÉRO DE PAGE en haut de feuille. Le dessin portait « Carte N° 120001 »
   à 120006 en dur : ces six numéros ont été EFFACÉS, le PDF écrit les
   vrais. Il n'y a PAS de numéro de planche.
"""
import io
import os as _os2
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_ra

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les planches sortent normalement, simplement sans microtexte.
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

GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.62, 0.62, 0.62)


# ══ DEUX GAMMES COMMERCIALES (vision Maeva) ══════════════════════════
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

_RATIO_PLANCHE = 1.5182

# ═══ 🌺 LES 54 RONDS ═══
# six colonnes (trois par carte, deux cartes côte à côte) …
COLONNES = [0.1329, 0.2596, 0.3903,      # la carte de GAUCHE
            0.6238, 0.7495, 0.8760]      # la carte de DROITE
# … et neuf lignes (trois par carte, trois cartes empilées), du haut vers le bas
LIGNES = [0.8451, 0.7825, 0.7193,        # rangée du HAUT
          0.5420, 0.4787, 0.4154,        # rangée du MILIEU
          0.2439, 0.1817, 0.1186]        # rangée du BAS
DIAM_ROND = 0.0400
HAUT_ROND = 0.0597

# 🌺 une plage par colonne de carte, dans l'ordre B-I · N-G · O-★
PLAGES = [(1, 30), (31, 60), (61, 90)]

# ⭐ LA PLACE DU NUMÉRO DE SÉRIE dans le ruban de chaque carte.
#    L'ordre suit celui de la planche de Maeva : on descend la colonne de
#    GAUCHE (cartes 1, 2, 3) puis celle de DROITE (cartes 4, 5, 6).
NUM_SERIE = [(0.1484, 0.9353), (0.1484, 0.6349), (0.1484, 0.3335),
             (0.6406, 0.9353), (0.6406, 0.6349), (0.6406, 0.3335)]
NUM_LARG = 0.0474


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


_IMAGE_PLANCHE = _choisir_image("ranihei_planche", _RATIO_PLANCHE)

# ⚠️ A4 COUCHÉ : c'est le seul jeu du catalogue en paysage.
PAGE_W, PAGE_H = landscape(A4)
MARGIN_X = 5 * mm
MARGIN_Y = 5 * mm
CARTES_PAR_PLANCHE = 6
# ⚠️ ON RESPECTE LE RATIO : les deux côtés ensemble, puis on centre.
_DISPO_W = PAGE_W - 2 * MARGIN_X
_DISPO_H = PAGE_H - 2 * MARGIN_Y
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_PLANCHE)
CARD_H = CARD_W / _RATIO_PLANCHE
MARGE_G = (PAGE_W - CARD_W) / 2
MARGE_B = (PAGE_H - CARD_H) / 2


def _gen_carte(rng):
    """🌺 Neuf numéros pour UNE carte : trois par colonne, tous différents.
    Les trois plages ne se chevauchent pas, il suffit donc de tirer trois
    numéros distincts dans chacune."""
    carte = []
    for lo, hi in PLAGES:
        carte.append(sorted(rng.sample(range(lo, hi + 1), 3)))
    return carte


def _dessiner_planche(c, nums_6, serie_debut, style="eco"):
    """🌺 Une planche entière : le dessin, puis les 54 numéros et les six
    numéros de série."""
    police_ch, gris_ch = _style_chiffres(style)
    _px, _py = MARGE_G, MARGE_B
    _pw, _ph = CARD_W, CARD_H
    if _os2.path.exists(_IMAGE_PLANCHE):
        try:
            c.drawImage(_IMAGE_PLANCHE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_r = _pw * DIAM_ROND
    _ht_r = _ph * HAUT_ROND
    _t_num = 40.0
    while _t_num > 6 and (_lg_ra("88", _POLICE_NUM, _t_num) > _lg_r * 0.80
                          or _t_num * 0.72 > _ht_r * 0.66):
        _t_num -= 0.5

    # ── les 54 numéros ──
    # carte k : colonnes 0-2 si elle est à gauche, 3-5 si à droite ;
    #           lignes 0-2, 3-5 ou 6-8 selon sa rangée.
    for k, carte in enumerate(nums_6):
        cote = 0 if k < 3 else 3          # k 0,1,2 = gauche · 3,4,5 = droite
        rangee = (k % 3) * 3
        for ic, colonne in enumerate(carte):
            for il, valeur in enumerate(colonne):
                _nx = _px + COLONNES[cote + ic] * _pw
                _ny = _py + LIGNES[rangee + il] * _ph - _t_num * 0.34
                c.setFillColor(gris_ch)
                c.setFont(_POLICE_NUM, _t_num)
                c.drawCentredString(_nx, _ny, str(valeur))

    # ── les six numéros de série, dans le ruban de chaque carte ──
    for k, (sx, sy) in enumerate(NUM_SERIE):
        _bl = "%06d" % (serie_debut + k)
        _tb = 12.0
        while _tb > 3.2 and _lg_ra(_bl, "Helvetica-Bold", _tb) > _pw * NUM_LARG:
            _tb -= 0.25
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", _tb)
        c.drawCentredString(_px + sx * _pw, _py + sy * _ph - _tb * 0.34, _bl)


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)
    rng = random.Random()
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    # ⚠️ une PAGE = une PLANCHE = six cartes
    nb_planches = (nb_cartes + CARTES_PAR_PLANCHE - 1) // CARTES_PAR_PLANCHE
    serie = int(serie_start)
    no_page = max(1, int(page_start))
    for _ in range(nb_planches):
        # ⭐ LE NUMÉRO DE PAGE EST AU CENTRE, EN HAUT (sceau Maeva 03/09) —
        #    c'est là qu'on le trouve d'un coup d'œil quand on feuillette
        #    une rame. Le nom de l'événement, s'il y en a un, passe à gauche
        #    pour ne pas lui marcher dessus.
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 9)
            c.drawString(MARGIN_X, PAGE_H - 4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 4 * mm, "Page %d" % no_page)
        _dessiner_planche(c, [_gen_carte(rng) for _ in range(CARTES_PAR_PLANCHE)],
                          serie, style)
        serie += CARTES_PAR_PLANCHE
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf
