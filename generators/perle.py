# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur PERLE (format A4)

🦪 NÉ LE 15/08 (sceau Maeva) : le frère habillé de ING. Une huître ouverte,
huit perles alignées dans sa nacre, et les trois lettres au-dessus.

RÈGLE — identique à ING, elle est écrite sur la coquille :
  I : 16-30 (×3, croissants) · N : 31-45 (×2, DÉCROISSANTS — la
  coquetterie du modèle) · G : 46-60 (×3, croissants)
⚠️ Huit numéros par carton, pas de case libre.

⚠️⚠️ ING garde son carton d'origine sous le nom « ING CLASSIC » :
les habillages vont ICI, jamais dans `ing.py`.

8 cartes par feuille A4 (2 colonnes × 4 rangées).
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgn
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgv
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
LETTRES = "ING"
# (min, max, nombre) par lettre — le N saute sa case centrale
COLONNES = [(16, 30, 3), (31, 45, 2), (46, 60, 3)]

# ═══ 🦪 L'HUÎTRE ET SES HUIT PERLES (sceau Maeva 15/08) ═══
# Les perles sont alignées dans la nacre, de gauche à droite :
#   I · I · I · N · N · G · G · G
_RATIO_HUITRE = 1.5018
PERLES = [[0.2559, 0.4049], [0.3345, 0.4056], [0.4152, 0.4049], [0.5152, 0.4055], [0.6013, 0.4054], [0.6995, 0.4055], [0.778, 0.4056], [0.8564, 0.4058]]
DIAM_PERLE = 0.0771
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_pe


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


_IMAGE_HUITRE = _choisir_image("perle_huitre", _RATIO_HUITRE)


# 15/08 : le dessin est en PAYSAGE (ratio 1,50) — 8 cartes-plaques (2x4).
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 6 * mm           # bande d'en-tête I | N | O
PIED_H = 4.4 * mm        # bande N° SERIE


def _gen_carte(rng):
    """8 numéros : I et G croissants, N décroissant (fidèle au modèle)."""
    cols = []
    for ci, (pmin, pmax, n) in enumerate(COLONNES):
        nums = sorted(rng.sample(range(pmin, pmax + 1), n), reverse=(ci == 1))
        cols.append(nums)
    return cols


# 🎰 LE JETON DE CASINO (sceau Maeva 01/08) : rondelle à créneaux alternés,
# anneau intérieur, le numéro au centre — dessiné au trait, jamais de pavé plein.
_CRENEAUX = 6          # créneaux du pourtour (6 = allure du jeton, encre légère)


def _jeton(c, cx, cy, r, valeur, col, gris_ch, police_ch):
    """Un pion de casino : le numéro trône au centre de la rondelle."""
    from reportlab.lib import colors as _c
    # rondelle
    c.setStrokeColor(col); c.setLineWidth(0.7)
    c.circle(cx, cy, r, stroke=1, fill=0)
    # créneaux : un arc épais un sur deux (l'alternance du jeton de casino)
    c.setLineWidth(r * 0.15)
    pas = 360.0 / _CRENEAUX
    for k in range(0, _CRENEAUX, 2):
        c.arc(cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86,
              k * pas + pas * 0.18, pas * 0.64)
    # anneau intérieur (la plage claire où s'inscrit la valeur)
    c.setLineWidth(0.5)
    c.circle(cx, cy, r * 0.66, stroke=1, fill=0)
    # le numéro, au calibre de la rondelle
    t = r * 1.02
    if _sec:
        _sec.chiffre_micro(c, valeur, cx, cy - t * 0.34, t, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch); c.setFont(police_ch, t)
        c.drawCentredString(cx, cy - t * 0.34, str(valeur))


# 💰 PIONS DE VALEUR (sceau Maeva 01/08) : 2 cases condamnées par carton
_PIONS_VALEURS = [5, 10, 15, 20, 50, 100]     # nos références, en francs
_PIONS_PAR_CARTE = 2


def _pions_de_la_carte(serie):
    """Deux cases condamnées + leur valeur — mêmes pour une même série."""
    import random as _r
    rng = _r.Random(932900 * 7 + serie * 131)
    postes = rng.sample(range(8), _PIONS_PAR_CARTE)      # toute carte a >= 8 cases
    return {p: rng.choice(_PIONS_VALEURS) for p in postes}


def _jeton_valeur(c, cx, cy, r, francs, col, gris_ch, police_ch):
    """Le pion de valeur : la rondelle, et la somme au centre."""
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.setLineWidth(r * 0.15)
    pas = 360.0 / _CRENEAUX
    for k in range(0, _CRENEAUX, 2):
        c.arc(cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86,
              k * pas + pas * 0.18, pas * 0.64)
    c.setLineWidth(0.6)
    c.circle(cx, cy, r * 0.70, stroke=1, fill=0)
    t = r * 0.66 if francs < 100 else r * 0.54
    c.setFillColor(col); c.setFont(police_ch, t)
    c.drawCentredString(cx, cy - t * 0.22, str(francs))
    c.setFont("Helvetica-Bold", r * 0.32)
    c.drawCentredString(cx, cy - r * 0.52, "FRANCS")


# 🫧 LA BULLE ET LA LETTRE CREUSE — la recette de BNG (11/08, sceau Maeva).
# La bulle est blanche au trait avec son reflet ; la lettre n'est plus un
# aplat plein mais un CONTOUR, le ventre en blanc. Aucun aplat que
# l'imprimante puisse transformer en pâté, et beaucoup moins d'encre.


def _bulle_ing(c, cx, cy, r, n, col, gris_ch, police_ch):
    """La bulle qui porte le chiffre : blanche, au trait, avec son reflet."""
    c.setFillColor(colors.white)
    c.setStrokeColor(col)
    c.setLineWidth(1.1)
    c.circle(cx, cy, r, stroke=1, fill=1)
    # ⚠️ le chiffre se cale sur SA bulle : sans cela il déborde du cercle.
    t = 38.0
    while t > 10 and _lgn("88", "Helvetica-Bold", t) > r * 2 * 0.76:
        t -= 0.5
    if _sec:
        _sec.chiffre_micro(c, n, cx, cy - t * 0.36, t, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch)
        c.setFont(police_ch, t)
        c.drawCentredString(cx, cy - t * 0.36, str(n))
    c.setStrokeColor(colors.Color(0.82, 0.82, 0.82))
    c.setLineWidth(0.45)
    rl = r * 0.30
    gx, gy = cx - r * 0.44, cy + r * 0.44
    c.arc(gx - rl, gy - rl, gx + rl, gy + rl, 20, 150)


def _lettre_creuse_ing(c, lettre, lx, ly, taille, col):
    """La lettre en CONTOUR, le ventre en blanc (recette de BNG)."""
    c.setFont("Helvetica-Bold", taille)
    c.setStrokeColor(col)
    c.setFillColor(colors.white)
    c.setLineWidth(max(0.5, taille * 0.022))
    t = c.beginText(lx, ly)
    t.setTextRenderMode(2)          # 2 = remplir PUIS tracer le contour
    t.setFont("Helvetica-Bold", taille)
    t.textOut(lettre)
    t.setTextRenderMode(0)          # ⚠️ on REFERME, sinon le chiffre suivant
    c.drawText(t)                   #    sort en couleur du trait


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id="", jetons=False):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # 15/08 : ni cadre, ni microtexte, ni QR — Maeva veut le carton net.

    # ═══ LA PLAQUE À L'HUÎTRE ═══
    # PAS de preserveAspectRatio : on VEUT l'etirer pour qu'elle epouse
    # la carte. Les huit perles suivent, chacune a sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_HUITRE):
        try:
            c.drawImage(_IMAGE_HUITRE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » (sceau Maeva 14/08).
    # Le secret n'est pas la taille, c'est LE GRAS — 58 % de chair contre
    # 24 % pour DJLECO : les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _dia = _pw * DIAM_PERLE
    _t_num = 34.0
    while _t_num > 6 and (_lg_pe("88", _POLICE_NUM, _t_num) > _dia * 0.96
                          or _t_num * 0.72 > _dia * 0.84):
        _t_num -= 0.5

    # ═══ les HUIT numeros, dans les perles ═══
    # `cols_nums` donne trois colonnes : I (3) · N (2) · G (3).
    # Les perles sont alignees dans cet ordre, de gauche a droite.
    _plat = [v for colonne in cols_nums for v in colonne]
    for _k, _n in enumerate(_plat[:8]):
        _bx, _by = PERLES[_k]
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
        _bl += "        \u2022        " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_pe(_bl, "Helvetica-Bold", _tb) > _pw * 0.32:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.545, _py + _ph * 0.040, _bl)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", jetons=False, page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(932900 + int(serie_start))
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
                                style=style, evenement_id=evenement_id, jetons=jetons)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf



def generer_pdf_casino(**kw):
    """🎰 Le jumeau CASINO : chaque numéro vit dans un pion de casino."""
    kw["jetons"] = True
    return generer_pdf(**kw)

if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89.22.23.05")
    with open("test_ing.pdf", "wb") as f:
        f.write(pdf.read())
    print("ING généré")
