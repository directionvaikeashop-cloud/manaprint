"""
MANAPRINT — Générateur FAN 90 (format A4)
8 cartes par feuille (2 colonnes × 4 rangées).
Chaque carte : 7 numéros en disposition libre « éventail » :
  • 1 numéro 1-10   dans un SOLEIL (haut gauche)
  • 1 numéro 20-30
  • 2 numéros 31-45
  • 1 numéro 46-59
  • 1 numéro 76-90  dans un CERCLE POINTILLÉ (au centre)
  • 1 numéro 60-75  dans un SOLEIL (bas droit)
Règle du jeu : toutes les boules de 1 à 90 SAUF le 11 à 19.
Cartes jaune soleil (ou couleur_perso / N&B). Gammes ÉCO / PREMIUM.
Microtexte + QR de sécurité.
"""
import io
import math
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


JAUNE_FAN = "#F2DE00"
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)

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
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4

COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

FOOT_H = 3 * mm

# Les 7 places de l'éventail : (plage, position x, position y, décor)
#   positions en fractions de la carte ; décor : "soleil", "cercle" ou ""
# ═══ 🗝️ LES SEPT CLÉS (sceau Maeva 14/08) ═══
# « VOTRE JEU FAN » : sept clés ouvragées, chacune portant SA LETTRE
# gravée sur son manche — B · I · N · N · N · G · O.
# ⚠️ Les numéros ne flottent plus : chacun vit dans l'anneau de SA clé,
# dans l'ordre du dessin (quatre en haut, trois en bas).
_RATIO_CLES = 1.5018
CLES = [[0.2844, 0.6698], [0.4658, 0.675], [0.6405, 0.6737], [0.8572, 0.6755], [0.3707, 0.3196], [0.5839, 0.3173], [0.797, 0.3118]]
DIAM_CLE = 0.118
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_f


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


_IMAGE_CLES = _choisir_image("fan_cles", _RATIO_CLES)

# ⚠️ L'ORDRE COMPTE : il suit les clés du dessin, de gauche à droite,
# la rangée du haut puis celle du bas.
#   clé 1 = B (1-10) · 2 = I (20-30) · 3 et 4 = N (31-45)
#   clé 5 = le 7e numéro (76-90) · 6 = G (46-59) · 7 = O (60-75)
PLACES = [
    ((1, 10),  0.28, 0.67, ""),
    ((20, 30), 0.46, 0.68, ""),
    ((31, 45), 0.63, 0.68, ""),
    ((31, 45), 0.84, 0.68, ""),
    ((76, 90), 0.38, 0.34, ""),
    ((46, 59), 0.55, 0.37, ""),
    ((60, 75), 0.73, 0.35, ""),
]


def _gen_carte():
    """Tire les 7 numéros (les deux 31-45 sont distincts)."""
    deux_3145 = random.sample(range(31, 46), 2)
    i31 = 0
    nums = []
    for (lo, hi), _, _, _ in PLACES:
        if (lo, hi) == (31, 45):
            nums.append(deux_3145[i31]); i31 += 1
        else:
            nums.append(random.randint(lo, hi))
    return nums


def _soleil(c, cx, cy, r, col):
    """Dessine un soleil (étoile à 12 branches) autour du point (cx, cy)."""
    p = c.beginPath()
    n = 12
    for i in range(2 * n):
        ang = math.pi / n * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.62
        x = cx + rr * math.cos(ang)
        y = cy + rr * math.sin(ang)
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    p.close()
    c.setStrokeColor(col); c.setLineWidth(1.0)
    c.drawPath(p, stroke=1, fill=0)


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme WIN, KAI, SUN,
    # WIZ, RAI, TAHAA, BAAM et PAPEARI. Maeva veut le carton net.

    # ═══ 🗝️ LA PLAQUE AUX SEPT CLÉS ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les sept anneaux suivent, chacun à sa place.
    # ⚠️ le dessin porte déjà son bandeau : il prend TOUTE la carte.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_CLES):
        try:
            c.drawImage(_IMAGE_CLES, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️⚠️ 14/08 : MAEVA VEUT 25 PT — on part de 25 et on ne descend que
    # si le chiffre ne tient vraiment pas.
    # ⚠️ LE PIÈGE : la police des chiffres n'est PAS Helvetica mais
    # « DJLECO », bien plus large. « 88 » à 25 pt fait 11,2 mm pour un
    # anneau de 7,6 — il faut donc une marge de 1,48, pas de 1,00.
    # Le chiffre déborde un peu de l'anneau et repose sur le médaillon
    # de la clé : c'est le prix de la lisibilité sur 8 cartes par feuille.
    _dia = _pw * DIAM_CLE
    _t_num = 25.0
    while _t_num > 6 and (_lg_f("88", police_ch, _t_num) > _dia * 1.50
                          or _t_num * 0.72 > _dia * 1.30):
        _t_num -= 0.5

    # ═══ les SEPT numéros, dans l'anneau de leur clé ═══
    for _k, _n in enumerate(nums[:7]):
        _cx0, _cy0 = CLES[_k]
        _nx = _px + _cx0 * _pw
        _ny = _py + _cy0 * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ⚠️ 14/08 : PAS DE BANDEAU ICI — le dessin de Maeva en porte déjà un,
    # « N° 00001 • 89 22 23 05 ». On écrit dedans, à sa place exacte.
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "  \u2022  " + telephone
    # ⚠️ le bandeau du dessin est LARGE : le texte peut prendre ses aises
    _tb = 9.0
    while _tb > 3.4 and _lg_f(_bl, "Helvetica-Bold", _tb) > _pw * 0.33:
        _tb -= 0.25
    # ⚠️ 14/08 (Maeva : « le numéro de série en blanc, pas en noir, pour
    # notre économie de toner ») : LE BANDEAU EST DEVENU CREUX dans
    # l'image — un simple contour au lieu d'un rectangle noir plein qui
    # buvait la moitié de sa surface. Le texte passe donc EN GRIS.
    c.setFillColor(gris_ch)
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.515, _py + _ph * 0.043, _bl)

def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
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
        # ⚠️ 14/08 : PLUS DE TITRE EN HAUT DE PAGE — le dessin de Maeva
        # porte déjà « FAN » en grand. Seul le numéro de page reste, très
        # discret, pour qu'elle s'y retrouve dans une grosse commande.
        c.setFillColor(GREY); c.setFont("Helvetica", 5)
        y2 = (PAGE_H - 8.5 * mm) if nom_evenement else (PAGE_H - 5 * mm)
        c.drawRightString(PAGE_W - 6 * mm, y2, f"Page {no_page}")

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                nums = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else JAUNE_FAN if couleur else "#999999")
                _dessiner_carte(c, x0, y0, nums, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=8, couleur=True, titre_jeu="")
    with open("test_fan90.pdf", "wb") as f:
        f.write(pdf.read())
    print("FAN 90 g\u00e9n\u00e9r\u00e9")
