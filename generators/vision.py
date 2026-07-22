# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur VISION (format A4)
8 billets larges/page — le télescope à gauche, le cône de visée,
le titre V·I·S·I·O·N espacé, 6 numéros en CERCLES : 1-15 · 16-30 · 2×46-60 · 2×61-75.
QR de sécurité · série · microtexte · Tèl par défaut 89 22 23 05.
"""
import io
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
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

NB_NUMS = 6
# chemin du regard décodé sur le billet modèle (13/20/54/58/63/64) :
# bas-1 = 1-15 · bas-2 = 16-30 · haut-1 puis bas-3 = 2 triés dans 46-60 ·
# haut-2 puis bas-4 = 2 triés dans 61-75 (la tranche 31-45 est absente du modèle)
POSITIONS = [(0.22, 0.33), (0.42, 0.33), (0.60, 0.64), (0.62, 0.33), (0.84, 0.66), (0.84, 0.33)]
# la 1re boule DANS le cône (haut-1) est plus petite pour tenir entre les
# deux traits de visée, comme sur le billet modèle — chiffre réduit avec elle
RAYONS_MM =  [7.5, 7.5, 5.5, 7.5, 7.5, 7.5]
TAILLES_CH = [32,  32,  22,  32,  32,  32]
TAILLE_CHIFFRE = 32


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── le TÉLESCOPE, dessiné maison sur son trépied, pointé vers le ciel droit ──
    gris_trait = colors.Color(0.60, 0.60, 0.60)
    c.setStrokeColor(gris_trait); c.setLineWidth(0.75)
    import math as _math
    # axe du tube : de l'oculaire (arrière-bas-gauche) vers l'objectif (avant-haut-droit)
    ax0, ay0 = x0 + CARD_W * 0.040, y0 + CARD_H * 0.455
    ax1, ay1 = x0 + CARD_W * 0.150, y0 + CARD_H * 0.600
    dxu, dyu = ax1 - ax0, ay1 - ay0
    Lt = (dxu * dxu + dyu * dyu) ** 0.5
    ux, uy = dxu / Lt, dyu / Lt          # le long du tube
    nx, ny = -uy, ux                     # perpendiculaire
    def _quad(t0, t1, demi):
        pts = [(ax0 + ux * Lt * t0 + nx * demi, ay0 + uy * Lt * t0 + ny * demi),
               (ax0 + ux * Lt * t1 + nx * demi, ay0 + uy * Lt * t1 + ny * demi),
               (ax0 + ux * Lt * t1 - nx * demi, ay0 + uy * Lt * t1 - ny * demi),
               (ax0 + ux * Lt * t0 - nx * demi, ay0 + uy * Lt * t0 - ny * demi)]
        p = c.beginPath(); p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close(); c.drawPath(p, stroke=1, fill=0)
    _quad(0.00, 0.22, 1.1 * mm)   # l'oculaire (petit tube arrière)
    _quad(0.22, 0.86, 1.9 * mm)   # le corps du tube
    _quad(0.86, 1.00, 2.5 * mm)   # l'objectif (évasé vers l'avant)
    # le trépied : trois jambes depuis la rotule sous le tube
    pvx = ax0 + ux * Lt * 0.50; pvy = ay0 + uy * Lt * 0.50
    c.line(pvx, pvy - 1.9 * mm, x0 + CARD_W * 0.045, y0 + CARD_H * 0.230)
    c.line(pvx, pvy - 1.9 * mm, x0 + CARD_W * 0.100, y0 + CARD_H * 0.215)
    c.line(pvx, pvy - 1.9 * mm, x0 + CARD_W * 0.150, y0 + CARD_H * 0.240)

    # ── le CÔNE de visée : deux traits fins depuis l'objectif, qui S'INTERROMPENT
    #    avant chaque boule (aucun trait ne touche un cercle) ──
    def _ligne_evitant_cercles(xa, ya, xb, yb):
        dx, dy = xb - xa, yb - ya
        L2 = dx * dx + dy * dy
        coupures = [(0.0, 0.0)]
        for (cpx, cpy), rmm in zip(POSITIONS, RAYONS_MM):
            garde = rmm * mm + 1.2 * mm
            ccx2 = x0 + CARD_W * cpx; ccy2 = y0 + CARD_H * cpy
            # projection du centre sur la ligne + intersection avec le disque gonflé
            t0 = ((ccx2 - xa) * dx + (ccy2 - ya) * dy) / L2
            px2, py2 = xa + t0 * dx, ya + t0 * dy
            d2 = (px2 - ccx2) ** 2 + (py2 - ccy2) ** 2
            if d2 < garde * garde:
                demi = (garde * garde - d2) ** 0.5 / (L2 ** 0.5)
                coupures.append((max(0.0, t0 - demi), min(1.0, t0 + demi)))
        coupures.sort()
        t = 0.0
        for (ca, cb) in coupures:
            if ca > t:
                c.line(xa + t * dx, ya + t * dy, xa + ca * dx, ya + ca * dy)
            t = max(t, cb)
        if t < 1.0:
            c.line(xa + t * dx, ya + t * dy, xa + dx, ya + dy)

    c.setLineWidth(0.45)
    oeil_x, oeil_y = ax1 + nx * 0, ay1 + ny * 0  # la bouche de l'objectif
    _ligne_evitant_cercles(oeil_x, oeil_y, x0 + CARD_W * 0.965, y0 + CARD_H * 0.86)
    _ligne_evitant_cercles(oeil_x, oeil_y, x0 + CARD_W * 0.965, y0 + CARD_H * 0.48)

    # ── le titre V·I·S·I·O·N espacé, gris (façon modèle) ──
    c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont(POLICE, 11)
    lettres = "VISION"
    lx = x0 + CARD_W * 0.17
    for L in lettres:
        c.drawString(lx, y0 + CARD_H * 0.80, L)
        lx += 8.2 * mm

    # en-tête : nom + signature + N° de carte
    titre = "VISION 6 boules"
    if titre_jeu and titre_jeu.strip().upper() != titre.upper():
        titre += "  —  " + titre_jeu.strip()
    titre += "  by TUKEA " + (telephone or "")
    c.setFillColor(col); c.setFont(POLICE, 4.6)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 4.2 * mm, titre[:64])
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 8.4 * mm, "Carte N° %05d" % serie)

    # le téléphone en pied gauche (comme les billets du fenua)
    c.setFillColor(colors.Color(0.45, 0.45, 0.45)); c.setFont(POLICE, 4.5)
    c.drawString(x0 + 2.5 * mm, y0 + 2.2 * mm, "Tèl : " + (telephone or ""))

    # ── les 6 numéros en CERCLES (fond blanc pour passer devant le cône) ──
    for i, (px, py) in enumerate(POSITIONS[:len(nums)]):
        r = RAYONS_MM[i] * mm
        taille = TAILLES_CH[i]
        ccx = x0 + CARD_W * px
        cy = y0 + CARD_H * py
        c.setFillColor(colors.white); c.setStrokeColor(gris_trait); c.setLineWidth(0.7)
        c.ellipse(ccx - r, cy - r, ccx + r, cy + r, stroke=1, fill=1)
        if _sec:
            _sec.chiffre_micro(c, nums[i], ccx, cy - taille * 0.36, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, taille)
            c.drawCentredString(ccx, cy - taille * 0.36, str(nums[i]))

    # QR de vérification (anti-duplication) — bas-droit
    if _sec and evenement_id:
        try:
            _q = 8.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.2 * mm, y0 + 1.8 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif=""):
    telephone = (telephone or "").strip() or "89 22 23 05"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    rng = random.Random(956000 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
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
                za = rng.randint(1, 15)                    # bas-1
                zb = rng.randint(16, 30)                   # bas-2
                zc = sorted(rng.sample(range(46, 61), 2))  # haut-1 puis bas-3
                zd = sorted(rng.sample(range(61, 76), 2))  # haut-2 puis bas-4
                nums = [za, zb, zc[0], zc[1], zd[0], zd[1]]
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
