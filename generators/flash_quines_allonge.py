# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur FLASH QUINES ALLONGÉ (format A4)

🚄 REFAIT LE 08/08 (sceau Maeva, sur son dessin de train) : la bande
devient un TRAIN LANCÉ À TOUTE ALLURE, et les NEUF NUMÉROS s'installent
dans ses NEUF FENÊTRES.

RÈGLE INCHANGÉE : 9 numéros, un par dizaine — 1-9, 10-19, …, 80-90.
Le sac du crieur ne change donc pas d'un chiffre.

⚡ ÉCONOMIE D'ENCRE : le train est DESSINÉ AU TRAIT, pas posé en image.
Aucun aplat, aucun dessin à décompresser — la bande reste aussi légère
qu'avant pour l'imprimante.
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgw
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
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GRIS_CLAIR = colors.Color(0.78, 0.78, 0.78)



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
DECADES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 49),
           (50, 59), (60, 69), (70, 79), (80, 90)]

CARTES_PAGE = 9
MARGIN_X = 6 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 6 * mm
GUTTER_Y = 2 * mm

CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (CARTES_PAGE - 1) * GUTTER_Y) / CARTES_PAGE


def _gen_carte(rng):
    """Un numéro par dizaine (9 numéros triés croissants)."""
    return [rng.randint(a, b) for (a, b) in DECADES]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, libelle_gauche="", titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # ---- En-tête (titre centré seulement) — le nom du jeu apparaît TOUJOURS ----
    htxt_y = y0 + CARD_H - 4.3 * mm
    centre = "FLASH QUINES ALLONGÉ"
    if titre_jeu and titre_jeu.strip().upper() != centre.upper():
        centre += "  —  " + titre_jeu.strip()
    if telephone:
        centre += "   " + telephone
    c.setFillColor(col); c.setFont(POLICE, 6.5)
    c.drawCentredString(x0 + CARD_W / 2, htxt_y, centre[:60])

    # ---- Zone des numéros ----
    zone_top = htxt_y - 3 * mm
    zone_bot = y0 + 2 * mm
    cymid = (zone_top + zone_bot) / 2
    y_haut = cymid + 2.3 * mm
    y_bas = cymid - 2.3 * mm

    # ═══ 🚄 LE TRAIN ET SES NEUF FENÊTRES ═══
    # Tout est dessiné au trait : le nez profilé, le toit, les fenêtres,
    # les roues et les traits de vitesse. Rien qu'un imprimante puisse
    # transformer en pâté noir, et pas un octet d'image à charger.
    gauche = x0 + 5.0 * mm
    droite = x0 + CARD_W - 26 * mm      # 26 mm réservés : boîte série + QR
    larg = droite - gauche
    bas = zone_bot + 1.2 * mm
    haut = zone_top - 0.4 * mm
    ht = haut - bas                      # hauteur du wagon
    NEZ = larg * 0.085                   # la pointe avant, à droite

    c.setStrokeColor(col)
    c.setLineWidth(0.7)      # ⚡ trait fin : le train ne doit rien coûter de plus
    # la caisse : plate à gauche, effilée à droite
    p = c.beginPath()
    p.moveTo(gauche, bas)
    p.lineTo(gauche, haut - ht * 0.18)
    p.curveTo(gauche + larg * 0.02, haut, gauche + larg * 0.06, haut,
              gauche + larg * 0.12, haut)
    p.lineTo(droite - NEZ, haut)
    p.curveTo(droite - NEZ * 0.35, haut - ht * 0.06,
              droite, bas + ht * 0.52, droite, bas + ht * 0.30)
    p.lineTo(droite, bas)
    p.close()
    c.drawPath(p, stroke=1, fill=0)

    # le museau, un arc qui répond au nez
    c.setLineWidth(0.5)
    p2 = c.beginPath()
    p2.moveTo(droite - NEZ, haut)
    p2.curveTo(droite - NEZ * 0.9, bas + ht * 0.34,
               droite - NEZ * 0.5, bas + ht * 0.16, droite, bas + ht * 0.30)
    c.drawPath(p2, stroke=1, fill=0)

    # ── les NEUF fenêtres, une par numéro ────────────────────────────────
    zone_fen = (droite - NEZ * 1.15) - (gauche + 2.2 * mm)
    fw = zone_fen / 9.0
    fen_w = fw * 0.86
    fen_h = ht * 0.62
    fen_y = bas + ht * 0.26
    taille = 30.0
    while taille > 14 and _lgw("88", "Helvetica-Bold", taille) > fen_w * 0.82:
        taille -= 0.5
    for i in range(9):
        fx = gauche + 2.2 * mm + i * fw + (fw - fen_w) / 2
        c.setStrokeColor(col)
        c.setLineWidth(0.55)
        c.setFillColor(colors.white)
        c.roundRect(fx, fen_y, fen_w, fen_h, fen_h * 0.22, stroke=1, fill=1)
        nx = fx + fen_w / 2
        ny = fen_y + fen_h * 0.5 - taille * 0.34
        if _sec:
            _sec.chiffre_micro(c, nums[i], nx, ny, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, taille)
            c.drawCentredString(nx, ny, str(nums[i]))

    # ── les roues, sous le wagon ─────────────────────────────────────────
    c.setStrokeColor(col)
    c.setLineWidth(0.5)
    rr = ht * 0.15
    for f in (0.12, 0.24, 0.62, 0.74):
        rx = gauche + larg * f
        c.circle(rx, bas, rr, stroke=1, fill=0)
        c.circle(rx, bas, rr * 0.30, stroke=1, fill=0)

    # ── les traits de vitesse, derrière le train ─────────────────────────
    c.setLineWidth(0.45)
    for k, (fy, fl) in enumerate(((0.86, 0.055), (0.70, 0.038), (0.54, 0.026))):
        ty = bas + ht * fy
        c.line(gauche - larg * fl - 1.0 * mm, ty, gauche - 1.0 * mm, ty)

    # Boîte série (bas droite)
    bw2, bh2 = 14 * mm, 4.6 * mm
    bx = x0 + CARD_W - bw2 - 3.5 * mm
    by = y0 + CARD_H - bh2 - 2.0 * mm  # boîte série remontée en haut-droite
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.roundRect(bx, by, bw2, bh2, 0.8 * mm, stroke=1, fill=0)
    c.setFillColor(GRIS); c.setFont(POLICE, 6.5)
    c.drawCentredString(bx + bw2 / 2, by + 1.4 * mm, "%06d" % serie)

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            # 🎯 QR dans la zone droite réservée (aucun rond dérangé)
            _q = 12.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 4.5 * mm, y0 + 5.6 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=9, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + CARTES_PAGE - 1) // CARTES_PAGE

    rng = random.Random(900000 + int(serie_start))
    serie = int(serie_start)
    faites = 0
    no_page = 1
    libelle_gauche = nom_evenement or date_lieu

    for _ in range(nb_pages):
        # petit numéro de page en haut
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 4.5 * mm, "%03d" % no_page)
        for row in range(CARTES_PAGE):
            if faites >= nb_cartes:
                break
            y0 = MARGIN_BOT + (CARTES_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
            x0 = MARGIN_X
            nums = _gen_carte(rng)
            coul = (couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
            _dessiner_carte(c, x0, y0, nums, coul, serie, libelle_gauche, titre_jeu, telephone, style=style, evenement_id=evenement_id)
            serie += 1
            faites += 1
        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=9, couleur=True,
                      nom_evenement="PAPEETE", titre_jeu="FLASH QUINES ALLONGÉ",
                      date_lieu="", telephone="89 22 23 05")
    with open("test_flash_quines.pdf", "wb") as f:
        f.write(pdf.read())
    print("FLASH QUINES ALLONGÉ généré")
