# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur MABUHAÏ (planche A4 paysage)

🙏 NÉ LE 03/09 (sceau Maeva) — LA PLANCHE MABUHAÏ de RANIHEI SISTERS & SHOP.
Une feuille entière qui porte SIX CARTES. Chaque carte montre DEUX MAINS
JOINTES entre deux bouquets d'hibiscus, et SEPT RONDS disposés en éventail
autour d'elles : un au sommet, trois qui descendent à gauche, trois à droite.

RÈGLE — sept numéros par carte, tous différents (sceau Maeva 03/09) :
  🔺 le SOMMET            : 1-15
  ↙️ le GAUCHE-BAS        : 1-15
  ⬅️ le GAUCHE-MILIEU     : 31-46
  ➡️ le DROITE-MILIEU     : 31-46
  ↖️ le GAUCHE-HAUT       : 47-60
  ↗️ le DROITE-HAUT       : 47-60
  ↘️ le DROITE-BAS        : 61-75
⚠️⚠️ TROIS PLAGES SONT PARTAGÉES PAR DEUX RONDS (1-15, 31-46, 47-60) : les
   deux numéros d'une même plage sont donc tirés D'UN SEUL COUP, sinon la
   même carte pourrait porter deux fois le même chiffre.
⚠️⚠️ IL Y A UN TROU DANS LE SAC : rien entre 16 et 30. Sur un sac de 1 à 75,
   quinze boules ne serviraient à personne. Signalé à Maeva le 03/09 ; en
   attendant sa décision, le crieur est réglé sur 1-75.

⚠️⚠️ CE JEU EST UNE PLANCHE, comme RANIHEI : le dessin n'est PAS un carton
   qu'on répète, c'est UNE FEUILLE ENTIÈRE. Une page du PDF = une planche
   = SIX cartes. D'où `cartes_par_feuille = 6`.
⚠️ La feuille est en PAYSAGE (ratio 1,5198) — centrée sur un A4 couché.

⭐ NUMÉROTATION (règle de la maison) : le NUMÉRO DE SÉRIE va dans le
   « N° ____ » de chaque carte, et le NUMÉRO DE PAGE au CENTRE, en haut de
   feuille. La mention « Planche N° 30006 » du dessin a été EFFACÉE : il n'y
   a pas de numéro de planche.
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
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_ma

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

_RATIO_PLANCHE = 1.5198

# ═══ 🙏 LES 42 RONDS — six cartes de sept ═══
# ⚠️ L'ORDRE DE CHAQUE CARTE EST TOUJOURS LE MÊME, et il suit les PLAGES :
#    sommet · G-haut · G-milieu · G-bas · D-haut · D-milieu · D-bas
RONDS = [
    [[0.2560, 0.8612], [0.2040, 0.8227], [0.1677, 0.7639], [0.1830, 0.6890],
     [0.3103, 0.8237], [0.3447, 0.7639], [0.3290, 0.6900]],   # carte 1
    [[0.2560, 0.5780], [0.2030, 0.5360], [0.1670, 0.4767], [0.1833, 0.4022],
     [0.3097, 0.5365], [0.3450, 0.4767], [0.3283, 0.4027]],   # carte 2
    [[0.2567, 0.2903], [0.2037, 0.2487], [0.1670, 0.1884], [0.1833, 0.1140],
     [0.3097, 0.2482], [0.3443, 0.1890], [0.3273, 0.1140]],   # carte 3
    [[0.7773, 0.8612], [0.7247, 0.8227], [0.6890, 0.7634], [0.7050, 0.6895],
     [0.8313, 0.8232], [0.8657, 0.7639], [0.8487, 0.6900]],   # carte 4
    [[0.7777, 0.5775], [0.7243, 0.5355], [0.6890, 0.4762], [0.7043, 0.4022],
     [0.8307, 0.5360], [0.8660, 0.4767], [0.8487, 0.4027]],   # carte 5
    [[0.7770, 0.2893], [0.7243, 0.2487], [0.6880, 0.1879], [0.7040, 0.1135],
     [0.8313, 0.2482], [0.8660, 0.1879], [0.8490, 0.1135]],   # carte 6
]
DIAM_ROND = 0.0478
HAUT_ROND = 0.0686

# 🙏 les plages, DANS L'ORDRE des sept ronds ci-dessus.
#    ⚠️ Trois plages reviennent deux fois : le tirage les traite ensemble.
PLAGES = [
    (1, 15),     # 0 · sommet
    (47, 60),    # 1 · G-haut
    (31, 46),    # 2 · G-milieu
    (1, 15),     # 3 · G-bas      ┐ même plage que le sommet
    (47, 60),    # 4 · D-haut     ┐ même plage que G-haut
    (31, 46),    # 5 · D-milieu   ┐ même plage que G-milieu
    (61, 75),    # 6 · D-bas
]

# ⭐ LA PLACE DU NUMÉRO DE SÉRIE : au-dessus du trait du « N° ____ »
NUM_SERIE = [(0.1182, 0.6489), (0.1182, 0.3611), (0.1182, 0.0742),
             (0.6330, 0.6489), (0.6330, 0.3611), (0.6330, 0.0742)]
NUM_LARG = 0.075


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


_IMAGE_PLANCHE = _choisir_image("mabuhai_planche", _RATIO_PLANCHE)

# ⚠️ A4 COUCHÉ, comme RANIHEI.
PAGE_W, PAGE_H = landscape(A4)
MARGIN_X = 5 * mm
MARGIN_Y = 5 * mm
CARTES_PAR_PLANCHE = 6
_DISPO_W = PAGE_W - 2 * MARGIN_X
_DISPO_H = PAGE_H - 2 * MARGIN_Y
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_PLANCHE)
CARD_H = CARD_W / _RATIO_PLANCHE
MARGE_G = (PAGE_W - CARD_W) / 2
MARGE_B = (PAGE_H - CARD_H) / 2


def _gen_carte(rng):
    """🙏 Sept numéros pour UNE carte, tous différents.

    ⚠️ Trois plages sont partagées par deux ronds. On regroupe donc les
    positions PAR PLAGE et on tire chaque paquet d'un seul coup : deux ronds
    d'une même plage ne peuvent jamais porter le même chiffre.
    """
    nums = [None] * 7
    par_plage = {}
    for i, plage in enumerate(PLAGES):
        par_plage.setdefault(plage, []).append(i)
    for (lo, hi), postes in par_plage.items():
        tirage = rng.sample(range(lo, hi + 1), len(postes))
        for poste, valeur in zip(postes, tirage):
            nums[poste] = valeur
    return nums


def _dessiner_planche(c, cartes_7, serie_debut, style="eco"):
    """🙏 Une planche entière : le dessin, les 42 numéros, les six séries."""
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
    while _t_num > 6 and (_lg_ma("88", _POLICE_NUM, _t_num) > _lg_r * 0.80
                          or _t_num * 0.72 > _ht_r * 0.66):
        _t_num -= 0.5

    for k, nums in enumerate(cartes_7):
        for i, (fx, fy) in enumerate(RONDS[k]):
            _nx = _px + fx * _pw
            _ny = _py + fy * _ph - _t_num * 0.34
            c.setFillColor(gris_ch)
            c.setFont(_POLICE_NUM, _t_num)
            c.drawCentredString(_nx, _ny, str(nums[i]))

    # ── les six numéros de série, au-dessus du trait du « N° ____ » ──
    for k, (sx, sy) in enumerate(NUM_SERIE):
        _bl = "%05d" % (serie_debut + k)
        _tb = 12.0
        while _tb > 3.2 and _lg_ma(_bl, "Helvetica-Bold", _tb) > _pw * NUM_LARG:
            _tb -= 0.25
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", _tb)
        c.drawCentredString(_px + sx * _pw, _py + sy * _ph, _bl)


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)
    rng = random.Random()
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_planches = (nb_cartes + CARTES_PAR_PLANCHE - 1) // CARTES_PAR_PLANCHE
    serie = int(serie_start)
    no_page = max(1, int(page_start))
    for _ in range(nb_planches):
        # ⭐ le numéro de page AU CENTRE, en haut (règle Maeva 03/09)
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
