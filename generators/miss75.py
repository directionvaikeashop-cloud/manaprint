# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur MISS 75 (format A4 PAYSAGE)
4 grandes cartes pleine largeur par feuille A4 paysage (1 colonne × 4 rangées).
Chaque carte : 5 sections M | I | S | S | 75 — les 5 familles de quinze :
  M = 1-15 · I = 16-30 · S = 31-45 · S = 46-60 · 75 = 61-75
Chaque section porte 6 numéros TRIÉS disposés en TRIANGLE, avec l'alternance
élégante du modèle :  △ ▽ △ ▽ △  (1-2-3 puis 3-2-1, en pyramides).
Petites cases claires autour de chaque numéro (fidèle au modèle).
30 numéros par carte ! Pied : « N° SERIE | 010001 ». Le QR de vérification
se niche dans le coin vide bas-gauche de la section I (▽).
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris (2 gammes ÉCO/PREMIUM).
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
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

PAGE_W, PAGE_H = landscape(A4)
LETTRES = ["M", "I", "S", "S", "75"]
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
# l'alternance des triangles : △ = (1,2,3) numéros par rangée ; ▽ = (3,2,1)
TRIANGLES = [(1, 2, 3), (3, 2, 1), (1, 2, 3), (3, 2, 1), (1, 2, 3)]

COLS_PAGE = 1
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 7 * mm
GUTTER_Y = 3 * mm

CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 5 * mm
PIED_H = 4.2 * mm


def _gen_carte(rng):
    """30 numéros : 6 triés par section, une section par famille de quinze."""
    return [sorted(rng.sample(range(pmin, pmax + 1), 6)) for pmin, pmax in PLAGES]


def _dessiner_carte(c, x0, y0, sections, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    sect_w = CARD_W / 5

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête M | I | S | S | 75 (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    for i in range(1, 5):
        c.line(x0 + i * sect_w, y0 + PIED_H, x0 + i * sect_w, y0 + CARD_H)
    c.setFillColor(col); c.setFont(POLICE, 6.5)
    for i, lettre in enumerate(LETTRES):
        c.drawCentredString(x0 + (i + 0.5) * sect_w, hdr_bas + 1.5 * mm, lettre)

    # Pied : « N° SERIE » + signature (le nom du jeu apparaît TOUJOURS) + série
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + PIED_H, x0 + CARD_W, y0 + PIED_H)
    c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.4)
    c.drawString(x0 + 2.5 * mm, y0 + 1.4 * mm, "N\u00b0 SERIE")
    signature = "MISS 75 by TUKEA"
    if titre_jeu and "MISS" not in titre_jeu.strip().upper():
        signature += " \u00b7 " + titre_jeu.strip()
    if telephone:
        signature += " \u00b7 " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + 1.4 * mm, signature[:70])
    c.setFont(POLICE, 6)
    c.drawRightString(x0 + CARD_W - 2.5 * mm, y0 + 1.3 * mm, "%06d" % serie)

    # Les 5 sections en triangles alternés △ ▽ △ ▽ △
    z_top = hdr_bas
    z_bot = y0 + PIED_H
    row_h = (z_top - z_bot) / 3
    taille = 30
    case_w = sect_w * 0.30
    for si, (nums, forme) in enumerate(zip(sections, TRIANGLES)):
        sx = x0 + si * sect_w
        idx = 0
        for ri, n_rangee in enumerate(forme):
            cyc = z_top - (ri + 0.5) * row_h
            # positions centrées : 1 -> [0.5] ; 2 -> [0.32, 0.68] ; 3 -> [0.18, 0.5, 0.82]
            fxs = {1: (0.50,), 2: (0.32, 0.68), 3: (0.18, 0.50, 0.82)}[n_rangee]
            for fx in fxs:
                val = nums[idx]; idx += 1
                cx = sx + sect_w * fx
                # la petite case claire autour du numéro (fidèle au modèle)
                c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
                c.rect(cx - case_w / 2, cyc - row_h * 0.44, case_w, row_h * 0.88, stroke=1, fill=0)
                if _sec:  # chiffres "billet de banque" remplis de microtexte
                    _sec.chiffre_micro(c, val, cx, cyc - taille * 0.36, taille, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch); c.setFont(police_ch, taille)
                    c.drawCentredString(cx, cyc - taille * 0.36, str(val))

    # QR de vérification — niché dans le coin vide bas-gauche de la section I (▽)
    if _sec and evenement_id:
        try:
            _q = min(row_h - 1.6 * mm, 11.5 * mm)
            _sec.carton_qr(c, x0 + sect_w + 2.0 * mm,
                           z_bot + (row_h - _q) / 2, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=4, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(933400 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 8)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 6.4 * mm, "%03d" % no_page)

        for row in range(ROWS_PAGE):
            if faites >= nb_cartes:
                break
            x0 = MARGIN_X
            y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
            sections = _gen_carte(rng)
            coul = (couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
            _dessiner_carte(c, x0, y0, sections, coul, serie, titre_jeu, telephone,
                            style=style, evenement_id=evenement_id)
            serie += 1
            faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=4, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_miss75.pdf", "wb") as f:
        f.write(pdf.read())
    print("MISS 75 généré")
