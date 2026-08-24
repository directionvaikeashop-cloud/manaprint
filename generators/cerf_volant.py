"""
MANAPRINT — Générateur CERF VOLANT (format A4)
6 cartes par feuille (2 colonnes × 3 rangées).
Disposition en QUEUE DE CERF-VOLANT :
  bloc 2×2 en haut-gauche : 2 numéros 1-15 et 2 numéros 16-30 (triés)
  puis, en diagonale descendante : 1 numéro 46-60, 1 numéro 61-75.
Aucun numéro 31-45 (plage morte). Un cerf-volant souriant décore la carte.
QR de sécurité au coin bas-gauche. Couleur arc-en-ciel / N&B. ÉCO / PREMIUM.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None


RAINBOW = [
    "#E53935", "#FF7043", "#FB8C00", "#F9A825",
    "#43A047", "#00ACC1", "#1E88E5", "#3949AB",
    "#8E24AA", "#D81B60", "#6D4C41", "#546E7A",
]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)
GRIS_GRILLE = colors.Color(0.60, 0.60, 0.60)

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


PAGE_W, PAGE_H = A4
# ═══ 🪁 LES SIX CERFS-VOLANTS (sceau Maeva 14/08) ═══
# « VOTRE JEU CERF VOLANT » : six cerfs-volants dans le ciel, chacun
# portant SA LETTRE sur un fanion et son disque pour le numéro.
# ⚠️ L'ORDRE suit les fanions : rangée du haut B·B·I, rangée du bas I·G·O.
#   B ×2 : 1-15 · I ×2 : 16-30 · G : 46-60 · O : 61-75
#   (pas de 31-45 — c'est la plage morte du jeu)
_RATIO_CERF = 1.5018
CERFS = [[0.3436, 0.7326], [0.5688, 0.7331], [0.7914, 0.7332], [0.3499, 0.3353], [0.5682, 0.3365], [0.7928, 0.3359]]
LARG_CERF = 0.104
HAUT_CERF = 0.104
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_c


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


_IMAGE_CERF = _choisir_image("cerf_six", _RATIO_CERF)


# ⚠️ 14/08 : le dessin est en PAYSAGE (ratio 1,50) — on passe de 6 cartes
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

FOOT_H = 3.5 * mm
CELL = 17 * mm   # élargie pour les chiffres 32 pts


def _gen_carte():
    """(col1 triée 1-15, col2 triée 16-30, n_a 46-60, n_b 61-75)"""
    c1 = sorted(random.sample(range(1, 16), 2))
    c2 = sorted(random.sample(range(16, 31), 2))
    return c1, c2, random.randint(46, 60), random.randint(61, 75)


def _cerf_volant(c, cx, cy, col):
    """Dessine un petit cerf-volant souriant avec sa queue ondulée."""
    h, w = 11 * mm, 8 * mm
    p = c.beginPath()
    p.moveTo(cx, cy + h * 0.55)
    p.lineTo(cx + w * 0.5, cy)
    p.lineTo(cx, cy - h * 0.45)
    p.lineTo(cx - w * 0.5, cy)
    p.close()
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.drawPath(p, stroke=1, fill=0)
    c.setLineWidth(0.4)
    c.line(cx, cy + h * 0.55, cx, cy - h * 0.45)
    c.line(cx - w * 0.5, cy, cx + w * 0.5, cy)
    # visage
    c.setFillColor(col)
    c.circle(cx - 1.2 * mm, cy + 1.6 * mm, 0.45 * mm, stroke=0, fill=1)
    c.circle(cx + 1.2 * mm, cy + 1.6 * mm, 0.45 * mm, stroke=0, fill=1)
    c.setLineWidth(0.5)
    c.arc(cx - 1.5 * mm, cy - 1.8 * mm, cx + 1.5 * mm, cy + 0.4 * mm,
          startAng=200, extent=140)
    # queue ondulée
    c.setLineWidth(0.5)
    b = c.beginPath()
    b.moveTo(cx, cy - h * 0.45)
    b.curveTo(cx - 4 * mm, cy - h * 0.45 - 5 * mm,
              cx + 3 * mm, cy - h * 0.45 - 9 * mm,
              cx - 2 * mm, cy - h * 0.45 - 13 * mm)
    b.curveTo(cx - 6 * mm, cy - h * 0.45 - 16 * mm,
              cx + 1 * mm, cy - h * 0.45 - 19 * mm,
              cx - 3 * mm, cy - h * 0.45 - 22 * mm)
    c.drawPath(b, stroke=1, fill=0)


def _dessiner_carte(c, x0, y0, donnees, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    c1, c2, n_a, n_b = donnees
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 🪁 LA PLAQUE AUX SIX CERFS-VOLANTS ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les six disques suivent, chacun à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_CERF):
        try:
            c.drawImage(_IMAGE_CERF, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS le disque, jamais en dur.
    # ⚠️ MESURER AVEC LA VRAIE POLICE (`police_ch`), pas Helvetica.
    # ⚠️⚠️ 14/08 (sceau Maeva : « je ne veux pas en rond, je veux en
    # triangle comme dans l'image originale ») : le rond agrandi mangeait
    # la forme du cerf-volant — il ressemblait à un ballon.
    # ⭐ L'INTÉRIEUR DU LOSANGE est vidé dans l'image, et le chiffre se
    # pose DEDANS. La forme en losange reste entière.
    # ⚠️ un losange se resserre vers ses pointes : le chiffre ne peut
    # occuper que sa TAILLE, la bande large du milieu.
    _lg_l = _pw * LARG_CERF
    _ht_l = _ph * HAUT_CERF
    _t_num = 25.0
    while _t_num > 6 and (_lg_c("88", police_ch, _t_num) > _lg_l * 1.12
                          or _t_num * 0.72 > _ht_l * 1.05):
        _t_num -= 0.5

    # ═══ les SIX numéros, au cœur de leur cerf-volant ═══
    # ⚠️ l'ordre suit les fanions : B·B·I en haut, I·G·O en bas.
    _plat = [c1[0], c1[1], c2[0], c2[1], n_a, n_b]
    for _k, _n in enumerate(_plat):
        if _k >= len(CERFS):
            break
        _cx0, _cy0 = CERFS[_k]
        _nx = _px + _cx0 * _pw
        # ⚠️ 14/08 : mesuré au rendu — le chiffre tombait 0,054 SOUS le
        # centre du losange. On le remonte d'autant pour qu'il se pose
        # bien dans la taille du cerf-volant.
        _ny = _py + _cy0 * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LE BANDEAU, écrit dans sa pastille creuse ═══
    # ⚠️ Il était NOIR PLEIN dans le dessin (51 % de sa surface en encre) :
    # il est désormais CREUX, et le PDF y écrit en gris.
    c.setFillColor(gris_ch)
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "   \u2605   " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_c(_bl, "Helvetica-Bold", _tb) > _pw * 0.31:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.515, _py + _ph * 0.030, _bl)


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
        titre_aff = titre_jeu if titre_jeu else "CERF VOLANT"
        # ⚠️ 14/08 : PLUS DE TITRE EN HAUT DE PAGE — le dessin porte déjà
        # « CERF VOLANT » en grand. Seul le numéro de page reste, discret.
        c.setFillColor(colors.Color(0.62,0.62,0.62)); c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 5 * mm, "Page %d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                donnees = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur
                        else "#999999")
                _dessiner_carte(c, x0, y0, donnees, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True, telephone="89 22 23 05")
    with open("test_cerf_volant.pdf", "wb") as f:
        f.write(pdf.read())
    print("CERF VOLANT g\u00e9n\u00e9r\u00e9")
