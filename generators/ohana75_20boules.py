"""
MANAPRINT — Générateur OHANA 75 · 20 BOULES (format A4)
5 bandes pleine largeur par feuille.
Chaque bande : 20 numéros en 2 rangées de 5 PAIRES — dans chaque quinzaine
(1-15 / 16-30 / 31-45 / 46-60 / 61-75) : un GRAND numéro + un numéro dans
un ROND POINTILLÉ, triés du plus petit au plus grand.
N° de série encadré à gauche. QR de sécurité dans la zone droite réservée.
Couleur arc-en-ciel (ou couleur_perso) / N&B. Gammes ÉCO / PREMIUM.
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
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#1E88E5",
    "#8E24AA", "#D81B60", "#00ACC1", "#6D4C41", "#546E7A",
]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)

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
ROWS_PAGE = 5
MARGIN_X = 6 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_Y = 3 * mm

CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

HDR_H = 6 * mm
ZONE_QR = 22 * mm  # zone droite réservée : la maison du QR

QUINZAINES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]


def _gen_carte():
    """2 rangées × 5 paires triées (grand, cerclé) — SANS DOUBLON sur le carton :
    4 numéros DISTINCTS par quinzaine, 2 en haut et 2 en bas (règle marathon)."""
    haut, bas = [], []
    for lo, hi in QUINZAINES:
        quatre = random.sample(range(lo, hi + 1), 4)
        a, b = sorted(quatre[:2])
        c2, d = sorted(quatre[2:])
        haut += [a, b]
        bas += [c2, d]
    return [haut, bas]


def _dessiner_carte(c, x0, y0, rangs, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure
    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.4 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête : série encadrée à gauche + titre centré
    hdr_y = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_y, x0 + CARD_W, hdr_y)
    c.rect(x0 + 2 * mm, hdr_y + 0.8 * mm, 16 * mm, HDR_H - 1.6 * mm, stroke=1, fill=0)
    c.setFillColor(GREY); c.setFont("Helvetica", 6)
    c.drawCentredString(x0 + 10 * mm, hdr_y + 2.2 * mm, f"{serie:06d}")
    # Le nom du jeu apparaît TOUJOURS, même avec un titre client
    if titre_jeu and titre_jeu.strip():
        if "OHANA" in titre_jeu.strip().upper():
            titre = titre_jeu.strip()
        else:
            titre = "OHANA 75 \u00b7 20 boules  \u2014  " + titre_jeu.strip()
    else:
        titre = "Le jeu OHANA 75 pour 20 boules"
    if telephone:
        titre += f" by TUKEA {telephone}"
    titre = titre[:60]
    c.setFillColor(col); c.setFont("Helvetica", 6)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y + 2.2 * mm, titre)

    # Les 2 rangées de 10 numéros (grand / cerclé alternés)
    gauche = x0 + 4 * mm
    droite = x0 + CARD_W - ZONE_QR
    pas = (droite - gauche) / 10.0
    zone_h = hdr_y - y0
    t_grand, t_cercle = 30, 24  # boules cerclées bien GROSSES

    for ri, rang in enumerate(rangs):
        cy = y0 + zone_h * (0.66 if ri == 0 else 0.18)
        for i, n in enumerate(rang):
            cx = gauche + (i + 0.5) * pas
            if i % 2 == 0:
                # GRAND numéro
                if _sec:
                    _sec.chiffre_micro(c, n, cx, cy, t_grand, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch); c.setFont(police_ch, t_grand)
                    c.drawCentredString(cx, cy, str(n))
            else:
                # numéro dans un ROND POINTILLÉ — aligné sur les grands numéros
                cyc = cy + (t_grand - t_cercle) * 0.35   # même centre optique que les grands
                c.setStrokeColor(col); c.setLineWidth(0.5)
                c.setDash(1.4, 1.6)
                c.circle(cx, cyc + t_cercle * 0.36, 7.4 * mm, stroke=1, fill=0)
                c.setDash()
                if _sec:
                    _sec.chiffre_micro(c, n, cx, cyc, t_cercle, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch); c.setFont(police_ch, t_cercle)
                    c.drawCentredString(cx, cyc, str(n))

    # 🎯 QR dans la zone droite réservée
    if _sec and evenement_id:
        try:
            _q = 13.0 * mm
            _xq = x0 + CARD_W - _q - 3.5 * mm
            _yq = y0 + (CARD_H - HDR_H - _q - 3.6 * mm) / 2 + 3.6 * mm
            _sec.carton_qr(c, _xq, _yq, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=5, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    serie = serie_start
    no_page = 1
    encre = NOIR if couleur else GRIS40

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        c.setFillColor(GREY); c.setFont("Helvetica", 7)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 7 * mm if not nom_evenement else PAGE_H - 8.5 * mm,
                            f"{no_page}")

        for row in range(ROWS_PAGE):
            x0 = MARGIN_X
            y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
            rangs = _gen_carte()
            coul = (couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur
                    else "#999999")
            _dessiner_carte(c, x0, y0, rangs, coul, serie, encre,
                            telephone, titre_jeu, style=style, evenement_id=evenement_id)
            serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=5, couleur=True, telephone="89 22 23 05")
    with open("test_ohana20b.pdf", "wb") as f:
        f.write(pdf.read())
    print("OHANA 75 20 boules g\u00e9n\u00e9r\u00e9")
