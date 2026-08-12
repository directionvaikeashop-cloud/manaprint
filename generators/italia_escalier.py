# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur ITALIA ESCALIER (format A4)

🪜 LE PREMIER ITALIA, RENDU À MAEVA LE 12/08 (« nos clients veulent le
premier jeu ITALIA que nous avons créé »). Il était né en juillet sur son
modèle de billet, puis la PIZZA avait pris sa place le 06/08. Les deux
vivent désormais côte à côte : la pizza garde son nom, l'escalier revient
en jumeau.

L'ESCALIER : cinq cases qui DESCENDENT de gauche à droite, une par
quinzaine — 1-15 · 16-30 · 31-45 · 46-60 · 61-75. Chaque marche porte
son numéro. Le sac du crieur est celui d'ITALIA : 1 à 75.

10 billets larges par feuille A4 (2 colonnes × 5 rangées).
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgi
import math
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)
PALE = colors.Color(0.86, 0.86, 0.86)
PALE2 = colors.Color(0.90, 0.90, 0.90)

try:
    pdfmetrics.registerFont(TTFont("DJLECO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    _POLICE_ECO = "DJLECO"
except Exception:
    _POLICE_ECO = "Helvetica"
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)


def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return "Helvetica-Bold", colors.Color(0.55, 0.55, 0.55)
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
COLS_PAGE = 2
ROWS_PAGE = 5
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

NB_NUMS = 5
TAILLE_CHIFFRE = 32
# 🍕 une tranche par part de pizza — ensemble, elles couvrent tout 1-75
# 🪜 les cinq quinzaines, une par marche
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]


def _gen_nums(rng):
    """5 numéros, un par quinzaine, marche après marche."""
    return [rng.randint(a, b) for a, b in PLAGES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure du billet
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.rect(x0, y0, CARD_W, CARD_H, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.6 * mm)

    # ═══ 🪜 L'ESCALIER — CINQ MARCHES QUI DESCENDENT ═══
    # Le modèle d'origine de Maeva : cinq cases qui descendent de gauche à
    # droite, une par quinzaine. Tout au trait, aucun aplat : le billet ne
    # coûte presque rien à imprimer.
    zone_g = x0 + 3.0 * mm
    zone_d = x0 + CARD_W - 19.0 * mm        # 16 mm réservés au titre et au QR
    zone_b = y0 + 5.5 * mm                  # ⚠️ on laisse la place au n° de série
    zone_h = y0 + CARD_H - 8.5 * mm
    larg = (zone_d - zone_g) / NB_NUMS
    # ⚠️ 12/08 : la descente se calcule sur (NB_NUMS - 1) marches, sinon la
    # DERNIÈRE case dépasse le bas du billet et mord le numéro de série.
    case_h = (zone_h - zone_b) * 0.40
    haut = (zone_h - zone_b - case_h) / (NB_NUMS - 1)

    # ⚠️ le chiffre se cale sur SA case : jamais de taille en dur, sinon il
    # déborde dès que le billet change de format.
    taille = TAILLE_CHIFFRE
    while taille > 10 and (_lgi("88", police_ch, taille) > larg * 0.80
                           or taille * 0.72 > case_h * 0.62):
        taille -= 0.5

    for i, n in enumerate(nums[:NB_NUMS]):
        cx = zone_g + i * larg
        # la marche descend : la première est en haut, la dernière en bas
        cy = zone_h - case_h - i * haut
        c.setFillColor(colors.white)
        c.setStrokeColor(col)
        c.setLineWidth(0.9)
        c.roundRect(cx, cy, larg, case_h, 1.2 * mm, stroke=1, fill=1)
        nx = cx + larg / 2
        ny = cy + case_h * 0.5 - taille * 0.34
        if _sec:
            _sec.chiffre_micro(c, n, nx, ny, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, taille)
            c.drawCentredString(nx, ny, str(n))

    # Le nom ITALIA s'écrit TOUJOURS (leçon du 25/07) ; le titre client vient EN PLUS
    c.setFillColor(col); c.setFont("Helvetica-Bold", 11)
    c.drawRightString(x0 + CARD_W - 3.5 * mm, y0 + CARD_H - 8.5 * mm, "ITALIA")
    ty = y0 + CARD_H - 12 * mm
    if titre_jeu and titre_jeu.strip().upper() != "ITALIA":
        c.setFillColor(col); c.setFont(POLICE, 5)
        c.drawRightString(x0 + CARD_W - 3.5 * mm, ty, titre_jeu.strip()[:30])
        ty -= 3.2 * mm
    if telephone:
        c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont(POLICE, 4.4)
        c.drawRightString(x0 + CARD_W - 3.5 * mm, ty, "T\u00e8l : " + telephone)

    # Série en bas à gauche (⚠️ l'ancien calcul partait du rayon `r` de la
    # pizza — cette variable n'existe plus dans l'escalier)
    c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont(POLICE, 4.6)
    c.drawString(x0 + 3.0 * mm, y0 + 1.4 * mm, "N\u00b0 %06d \u00b7 by 2KEA" % serie)
    if _sec and evenement_id:
        try:
            _q = 11.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 4.0 * mm, y0 + 3.0 * mm,
                           _q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=10, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif="", page_start=1):
    telephone = (telephone or "").strip() or "89 22 23 05"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    rng = random.Random(980000 + int(serie_start))
    serie = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0
    for _ in range(nb_pages):
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
                nums = _gen_nums(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, nums, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=10, couleur=True, nom_evenement="TEST", telephone="89.22.23.05")
    with open("test_italia.pdf", "wb") as f:
        f.write(pdf.read())
    print("ITALIA généré")
