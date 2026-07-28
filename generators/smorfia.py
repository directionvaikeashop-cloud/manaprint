# -*- coding: utf-8 -*-
"""
MANAPRINT — SMORFIA by 2KEA · le jeu des images (v6, 28/07/2026)
LE CHIFFRE DEVIENT L'IMAGE : sur chaque carton, UN des numéros est rendu
par son image de la smorfia du fenua (panthéon 22, vague 3 du 28/07).
Chaque jeu passe SES numéros jouables à numero_pour_serie (univers respecté).
Vague 3 :  1 la jouissance ·  4 LA DÉCHIRURE (cri changé, image gardée) ·
28 met de l'huile · 41 le paari dur · 45 huahua le mauiui des femmes ·
46 le sac à pute · 56 pakalolo (SOUS RÉSERVE DU JURISTE) · 59 elle est
grosse et énorme · 64 grand-père · 65 grand-mère · 66 la queue en l'air.
Vague 2 :
   2 PETEA               → silhouette moitié pantalon / moitié robe, fleur
   4 MAHAE               → papier déchiré en deux
   8 FIRIFIRI CHAUD      → le beignet torsadé et sa vapeur
  11 TAPEA TO ORUA       → deux silhouettes qui se tiennent
  16 TAIORO              → éclat de BD (l'explosion du juron)
  18 MON ÂGE             → gâteau d'anniversaire
  47 K7                  → cassette audio
  54 GABILOU             → chanteur au micro (silhouette générique — JAMAIS un portrait)
  55 LES REINES DE LA NUIT → couronne sous croissant et étoiles
  61 UA POTO             → le trait court (sous le long)
  69 MANGEZ-VOUS         → deux fourchettes tête-bêche
  71 TIAPAI              → le trait gros (sous le fin)
Le numéro reste écrit en petit au coin (litiges + vérification).
"""
import hashlib
import hmac
from reportlab.lib import colors
from reportlab.lib.units import mm

ANNONCES = {
    1: "LA JOUISSANCE LE BONHEUR DES FEMMES",
    2: "PETEA",
    4: "LA D\u00c9CHIRURE",
    8: "FIRIFIRI CHAUD",
    11: "TAPEA TO ORUA",
    16: "TAIORO",
    18: "MON \u00c2GE",
    28: "MET DE L'HUILE",
    41: "LE PAARI DUR",
    45: "HUAHUA LE MAUIUI DES FEMMES",
    46: "LE SAC \u00c0 PUTE",
    47: "K7",
    54: "GABILOU",
    55: "LES REINES DE LA NUIT",
    56: "PAKALOLO",
    59: "ELLE EST GROSSE ET \u00c9NORME",
    61: "UA POTO",
    64: "GRAND-P\u00c8RE",
    65: "GRAND-M\u00c8RE",
    66: "LA QUEUE EN L'AIR",
    69: "MANGEZ-VOUS",
    71: "TIAPAI",
}
_NUMS = sorted(ANNONCES)


def numero_pour_serie(serie, eligibles=None):
    """La même carte porte toujours la même image (refab comprise).
    eligibles = les numéros du panthéon JOUABLES dans l'univers du jeu
    (un jeu ne doit jamais porter une image d'un numéro que son sac ne tire pas)."""
    nums = sorted(eligibles) if eligibles else _NUMS
    h = hmac.new(b"SMORFIA-2KEA", ("SMORFIA:%d" % int(serie)).encode(), hashlib.sha256)
    return nums[int.from_bytes(h.digest()[:4], "big") % len(nums)]


def choix_hote(serie, nb_choix):
    """Quand deux cases peuvent héberger le numéro, l'empreinte tranche."""
    h = hmac.new(b"SMORFIA-2KEA", ("HOTE:%d" % int(serie)).encode(), hashlib.sha256)
    return int.from_bytes(h.digest()[:4], "big") % max(1, nb_choix)


# ─────────────────────────── les 22 images (vectoriel maison) ──────────────────────────

def _gateau(c, cx, cy, w, h, enc):
    """18 — gâteau d'anniversaire : deux étages, trois bougies."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.65)
    c.line(cx - w * 0.48, cy - h * 0.42, cx + w * 0.48, cy - h * 0.42)          # le plat
    c.roundRect(cx - w * 0.40, cy - h * 0.42, w * 0.80, h * 0.30, h * 0.06, stroke=1, fill=1)
    c.roundRect(cx - w * 0.27, cy - h * 0.12, w * 0.54, h * 0.26, h * 0.06, stroke=1, fill=1)
    for fx in (-0.16, 0.0, 0.16):
        bx = cx + w * fx
        c.setLineWidth(0.7)
        c.line(bx, cy + h * 0.14, bx, cy + h * 0.30)                            # bougies
        c.setFillColor(enc)
        c.ellipse(bx - w * 0.022, cy + h * 0.30, bx + w * 0.022, cy + h * 0.42, stroke=0, fill=1)
        c.setFillColor(colors.white)


def _cassette(c, cx, cy, w, h, enc):
    """47 — la K7 : boîtier, deux bobines, fenêtre."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.7)
    c.roundRect(cx - w * 0.48, cy - h * 0.40, w * 0.96, h * 0.80, h * 0.10, stroke=1, fill=1)
    c.setLineWidth(0.55)
    c.roundRect(cx - w * 0.34, cy - h * 0.16, w * 0.68, h * 0.36, h * 0.07, stroke=1, fill=0)
    for fx in (-0.17, 0.17):
        bx = cx + w * fx
        c.circle(bx, cy + 0.02 * h, h * 0.115, stroke=1, fill=0)
        c.circle(bx, cy + 0.02 * h, h * 0.035, stroke=1, fill=0)
    c.line(cx - w * 0.30, cy - h * 0.27, cx + w * 0.30, cy - h * 0.27)          # l'étiquette


def _eclat_juron(c, cx, cy, w, h, enc):
    """16 — TAIORO : l'ÉCLAT de bande dessinée — l'explosion étoilée du juron
    (candidat A, choisi par Maeva le 27/07)."""
    import math
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.7)
    pointes = 10
    p = c.beginPath()
    for i in range(pointes * 2):
        ang = math.pi / 2 + i * math.pi / pointes
        r = 0.5 if i % 2 == 0 else 0.30
        x, y = cx + math.cos(ang) * w * r, cy + math.sin(ang) * h * r
        (p.moveTo if i == 0 else p.lineTo)(x, y)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.setFillColor(enc)
    c.setFont("Helvetica-Bold", h * 0.55)
    c.drawCentredString(cx, cy - h * 0.55 * 0.36, "!")


def _deux_silhouettes(c, cx, cy, w, h, enc):
    """11 — TEPEA TOA ORUA : deux silhouettes qui se tiennent."""
    c.setStrokeColor(enc); c.setLineWidth(0.75); c.setFillColor(colors.white)
    for sgn in (-1, 1):
        bx = cx + sgn * w * 0.18
        c.circle(bx, cy + h * 0.28, h * 0.13, stroke=1, fill=1)                 # têtes
        c.line(bx, cy + h * 0.15, bx, cy - h * 0.14)                            # troncs
        c.line(bx, cy - h * 0.14, bx - sgn * w * 0.10, cy - h * 0.44)          # jambes
        c.line(bx, cy - h * 0.14, bx + sgn * w * 0.10, cy - h * 0.44)
        c.line(bx, cy + h * 0.08, bx + sgn * w * 0.16, cy - h * 0.10)          # bras extérieurs
    c.setLineWidth(0.9)
    c.line(cx - w * 0.18, cy + h * 0.06, cx + w * 0.18, cy + h * 0.06)          # ils SE TIENNENT


def _chanteur(c, cx, cy, w, h, enc):
    """54 — GABILOU : un chanteur au micro (silhouette générique)."""
    c.setStrokeColor(enc); c.setLineWidth(0.75); c.setFillColor(colors.white)
    bx = cx - w * 0.06
    c.circle(bx, cy + h * 0.28, h * 0.13, stroke=1, fill=1)                     # tête
    c.line(bx, cy + h * 0.15, bx, cy - h * 0.16)                                # tronc
    c.line(bx, cy - h * 0.16, bx - w * 0.12, cy - h * 0.46)                     # jambes
    c.line(bx, cy - h * 0.16, bx + w * 0.12, cy - h * 0.46)
    c.line(bx, cy + h * 0.08, bx - w * 0.17, cy - h * 0.06)                     # bras libre
    c.line(bx, cy + h * 0.06, bx + w * 0.20, cy + h * 0.22)                     # bras au micro
    c.setFillColor(enc)
    c.circle(bx + w * 0.245, cy + h * 0.255, h * 0.055, stroke=0, fill=1)       # le micro
    c.setLineWidth(0.55)
    c.line(bx + w * 0.245, cy + h * 0.20, bx + w * 0.245, cy + h * 0.10)


def _petea(c, cx, cy, w, h, enc):
    """2 — PETEA : un homme devenu femme (moitié pantalon / moitié robe, la fleur)."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.7)
    c.circle(cx, cy + h * 0.30, h * 0.13, stroke=1, fill=1)                     # la tête
    c.rect(cx - h * 0.13, cy - h * 0.10, h * 0.13, h * 0.30, stroke=1, fill=1)  # moitié buste droit
    p = c.beginPath()                                                            # moitié robe évasée
    p.moveTo(cx, cy + h * 0.20); p.lineTo(cx + h * 0.24, cy - h * 0.10); p.lineTo(cx, cy - h * 0.10)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.line(cx - h * 0.065, cy - h * 0.10, cx - h * 0.065, cy - h * 0.44)        # jambe pantalon
    c.line(cx + h * 0.075, cy - h * 0.10, cx + h * 0.075, cy - h * 0.44)        # jambe sous la robe
    c.setLineWidth(0.5)
    import math
    fx, fy = cx + h * 0.15, cy + h * 0.38                                       # la fleur à l'oreille
    for a in range(5):
        ang = a * 2 * math.pi / 5
        c.circle(fx + math.cos(ang) * h * 0.035, fy + math.sin(ang) * h * 0.035, h * 0.024, stroke=1, fill=1)


def _mahae(c, cx, cy, w, h, enc):
    """4 — MAHAE : un papier déchiré en deux."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.65)
    top, bot, gap = cy + h * 0.44, cy - h * 0.44, w * 0.06
    for sens, xb in ((-1, cx - w * 0.46), (1, cx + w * 0.46)):
        zig = []
        for i in range(7):                                                       # le bord déchiré
            y = top - (top - bot) * i / 6.0
            zig.append((cx + sens * gap + sens * w * 0.05 * ((-1) ** i), y))
        p = c.beginPath()
        p.moveTo(xb, top); p.lineTo(zig[0][0], zig[0][1])
        for x, y in zig[1:]:
            p.lineTo(x, y)
        p.lineTo(xb, bot); p.close()
        c.drawPath(p, stroke=1, fill=1)
    c.setLineWidth(0.45)
    for yy in (cy + h * 0.20, cy, cy - h * 0.20):                                # les lignes de texte
        c.line(cx - w * 0.38, yy, cx - w * 0.18, yy)
        c.line(cx + w * 0.18, yy, cx + w * 0.38, yy)


def _firifiri(c, cx, cy, w, h, enc):
    """8 — FIRIFIRI CHAUD : le beignet torsadé en 8, sa vapeur au-dessus."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.75)
    r = h * 0.20
    y8 = cy - h * 0.24
    c.ellipse(cx - r * 2.1, y8 - r, cx + r * 0.1, y8 + r, stroke=1, fill=1)      # boucle gauche
    c.ellipse(cx - r * 0.1, y8 - r, cx + r * 2.1, y8 + r, stroke=1, fill=1)      # boucle droite
    c.setLineWidth(0.45)
    for fx in (-1.5, -0.6, 0.6, 1.5):                                            # les stries de torsade
        c.line(cx + fx * r, y8 - r * 0.55, cx + fx * r * 0.72, y8 + r * 0.55)
    c.setLineWidth(0.55)
    for fx in (-w * 0.16, 0.0, w * 0.16):                                        # la vapeur : CHAUD
        x0, y0 = cx + fx, y8 + r + h * 0.08
        p = c.beginPath()
        p.moveTo(x0, y0)
        p.curveTo(x0 - w * 0.05, y0 + h * 0.12, x0 + w * 0.05, y0 + h * 0.22, x0, y0 + h * 0.34)
        c.drawPath(p, stroke=1, fill=0)


def _reines_nuit(c, cx, cy, w, h, enc):
    """55 — LES REINES DE LA NUIT : la couronne sous le croissant et les étoiles."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.7)
    bw, bh, by = w * 0.60, h * 0.15, cy - h * 0.44
    c.rect(cx - bw / 2, by, bw, bh, stroke=1, fill=1)                            # le bandeau
    p = c.beginPath()                                                             # les pointes
    p.moveTo(cx - bw / 2, by + bh); p.lineTo(cx - bw * 0.32, by + bh + h * 0.28)
    p.lineTo(cx - bw * 0.16, by + bh); p.lineTo(cx, by + bh + h * 0.34)
    p.lineTo(cx + bw * 0.16, by + bh); p.lineTo(cx + bw * 0.32, by + bh + h * 0.28)
    p.lineTo(cx + bw / 2, by + bh); p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.setFillColor(enc)
    for fx, fy in ((-bw * 0.32, h * 0.28), (0.0, h * 0.34), (bw * 0.32, h * 0.28)):
        c.circle(cx + fx, by + bh + fy + h * 0.035, h * 0.026, stroke=0, fill=1)  # les perles
    mr, mx, my = h * 0.155, cx - w * 0.24, cy + h * 0.28                          # le croissant : LA NUIT
    p = c.beginPath(); p.arc(mx - mr, my - mr, mx + mr, my + mr, 300, 250); c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath(); p.arc(mx - mr * 0.35, my - mr * 0.95, mx + mr * 1.25, my + mr * 1.05, 295, 245)
    c.drawPath(p, stroke=1, fill=0)
    c.setLineWidth(0.5)
    for sx, sy, sr in ((cx + w * 0.14, cy + h * 0.33, h * 0.05), (cx + w * 0.31, cy + h * 0.20, h * 0.035)):
        c.line(sx - sr, sy, sx + sr, sy); c.line(sx, sy - sr, sx, sy + sr)        # les étoiles


def _ua_poto(c, cx, cy, w, h, enc):
    """61 — UA POTO : le trait COURT, sous le long (c'est le court qui gagne)."""
    c.setStrokeColor(enc); c.setLineWidth(0.8)
    c.line(cx - w * 0.42, cy + h * 0.20, cx + w * 0.42, cy + h * 0.20)           # le long, témoin
    c.setLineWidth(1.6)
    c.line(cx - w * 0.13, cy - h * 0.20, cx + w * 0.13, cy - h * 0.20)           # le COURT


def _mangez_vous(c, cx, cy, w, h, enc):
    """69 — MANGEZ-VOUS : deux fourchettes tête-bêche (la symétrie du chiffre)."""
    c.setStrokeColor(enc); c.setLineWidth(0.8)
    for fx, sens in ((cx - w * 0.14, 1), (cx + w * 0.14, -1)):
        c.line(fx, cy - sens * h * 0.42, fx, cy + sens * h * 0.42)               # le manche
        for dx in (-h * 0.06, 0.0, h * 0.06):
            c.line(fx + dx, cy + sens * h * 0.42, fx + dx, cy + sens * h * 0.20)  # les dents


def _tiapai(c, cx, cy, w, h, enc):
    """71 — TIAPAI (c'est gros) : le trait GROS, sous le fin. Miroir du 61."""
    c.setStrokeColor(enc); c.setLineWidth(0.55)
    c.line(cx - w * 0.38, cy + h * 0.26, cx + w * 0.38, cy + h * 0.26)           # le fin, témoin
    c.setLineWidth(3.4); c.setLineCap(1)
    c.line(cx - w * 0.34, cy - h * 0.14, cx + w * 0.34, cy - h * 0.14)           # le GROS
    c.setLineCap(0)


def _bonheur(c, cx, cy, w, h, enc):
    """1 — LA JOUISSANCE, LE BONHEUR DES FEMMES : la femme aux bras levés."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.7)
    c.circle(cx, cy + h * 0.28, h * 0.11, stroke=1, fill=1)
    p = c.beginPath()
    p.moveTo(cx, cy + h * 0.17); p.lineTo(cx - h * 0.20, cy - h * 0.18); p.lineTo(cx + h * 0.20, cy - h * 0.18)
    p.close(); c.drawPath(p, stroke=1, fill=1)
    c.line(cx - w * 0.05, cy - h * 0.18, cx - w * 0.05, cy - h * 0.44)
    c.line(cx + w * 0.05, cy - h * 0.18, cx + w * 0.05, cy - h * 0.44)
    c.line(cx - w * 0.03, cy + h * 0.12, cx - w * 0.20, cy + h * 0.42)          # les bras au ciel
    c.line(cx + w * 0.03, cy + h * 0.12, cx + w * 0.20, cy + h * 0.42)
    c.setLineWidth(0.5)
    for sx in (-0.27, 0.27):                                                     # les éclats de joie
        c.line(cx + sx * w - h * 0.03, cy + h * 0.46, cx + sx * w + h * 0.03, cy + h * 0.46)
        c.line(cx + sx * w, cy + h * 0.43, cx + sx * w, cy + h * 0.49)


def _huile(c, cx, cy, w, h, enc):
    """28 — MET DE L'HUILE : la bouteille penchée verse sa goutte."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.7)
    c.saveState(); c.translate(cx - w * 0.08, cy + h * 0.06); c.rotate(-35)
    c.roundRect(-w * 0.10, -h * 0.02, w * 0.20, h * 0.40, w * 0.04, stroke=1, fill=1)
    c.rect(-w * 0.045, h * 0.38, w * 0.09, h * 0.15, stroke=1, fill=1)
    c.restoreState()
    gx, gy = cx + w * 0.24, cy - h * 0.10
    p = c.beginPath()                                                            # la goutte
    p.moveTo(gx, gy + h * 0.14)
    p.curveTo(gx - h * 0.08, gy + h * 0.02, gx - h * 0.07, gy - h * 0.07, gx, gy - h * 0.11)
    p.curveTo(gx + h * 0.07, gy - h * 0.07, gx + h * 0.08, gy + h * 0.02, gx, gy + h * 0.14)
    c.setFillColor(enc); c.drawPath(p, stroke=1, fill=1); c.setFillColor(colors.white)
    c.setLineWidth(0.55)
    c.line(cx - w * 0.30, cy - h * 0.42, cx + w * 0.40, cy - h * 0.42)           # le sol


def _caillou(c, cx, cy, w, h, enc):
    """41 — LE PAARI DUR : le caillou, dur comme la pierre."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.75)
    pts = [(-0.34, 0.05), (-0.22, 0.34), (0.02, 0.42), (0.26, 0.28),
           (0.35, -0.02), (0.22, -0.32), (-0.06, -0.40), (-0.29, -0.26)]
    p = c.beginPath()
    for i, (fx, fy) in enumerate(pts):
        (p.moveTo if i == 0 else p.lineTo)(cx + fx * w, cy + fy * h)
    p.close(); c.drawPath(p, stroke=1, fill=1)
    c.setLineWidth(0.5)
    c.line(cx - w * 0.13, cy + h * 0.30, cx - w * 0.02, cy + h * 0.02)           # les facettes
    c.line(cx - w * 0.02, cy + h * 0.02, cx + w * 0.15, cy - h * 0.10)


def _mauiui(c, cx, cy, w, h, enc):
    """45 — HUAHUA LE MAUIUI DES FEMMES : la femme, mains au ventre."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.7)
    c.circle(cx, cy + h * 0.28, h * 0.11, stroke=1, fill=1)
    p = c.beginPath()
    p.moveTo(cx, cy + h * 0.17); p.lineTo(cx - h * 0.20, cy - h * 0.18); p.lineTo(cx + h * 0.20, cy - h * 0.18)
    p.close(); c.drawPath(p, stroke=1, fill=1)
    c.line(cx - w * 0.05, cy - h * 0.18, cx - w * 0.05, cy - h * 0.44)
    c.line(cx + w * 0.05, cy - h * 0.18, cx + w * 0.05, cy - h * 0.44)
    c.line(cx - w * 0.15, cy + h * 0.10, cx - w * 0.03, cy - h * 0.04)           # les mains au ventre
    c.line(cx + w * 0.15, cy + h * 0.10, cx + w * 0.03, cy - h * 0.04)
    c.setLineWidth(0.5)
    for dx, dy in ((-0.30, 0.06), (0.0, 0.16), (0.30, 0.06)):                    # les éclairs de douleur
        c.line(cx + dx * w, cy + dy * h - h * 0.03, cx + dx * w, cy + dy * h + h * 0.03)


def _sac(c, cx, cy, w, h, enc):
    """46 — LE SAC À PUTE : le sac à main, tout simplement."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.75)
    p = c.beginPath()                                                            # l'anse d'abord
    p.arc(cx - w * 0.15, cy - h * 0.02, cx + w * 0.15, cy + h * 0.46, 0, 180)
    c.drawPath(p, stroke=1, fill=0)
    c.roundRect(cx - w * 0.25, cy - h * 0.36, w * 0.50, h * 0.42, h * 0.07, stroke=1, fill=1)
    c.setLineWidth(0.5)
    c.line(cx - w * 0.25, cy - h * 0.08, cx + w * 0.25, cy - h * 0.08)           # le rabat
    c.setFillColor(enc)
    c.circle(cx, cy - h * 0.16, h * 0.032, stroke=0, fill=1)                     # le fermoir
    c.setFillColor(colors.white)


def _feuille(c, cx, cy, w, h, enc):
    """56 — PAKALOLO : la feuille palmée (⚠️ SOUS RÉSERVE DU JURISTE)."""
    import math
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.6)
    base_y = cy - h * 0.12
    for i, a in enumerate((90, 62, 118, 34, 146, 10, 170)):
        L = h * 0.44 * (1.0 if i == 0 else 0.86 if i < 3 else 0.68 if i < 5 else 0.46)
        ang = math.radians(a)
        tx, ty = cx + math.cos(ang) * L, base_y + math.sin(ang) * L
        p = c.beginPath()
        p.moveTo(cx, base_y)
        p.curveTo(cx + math.cos(ang) * L * 0.4 - h * 0.05, base_y + math.sin(ang) * L * 0.4,
                  tx - math.cos(ang) * L * 0.2 - h * 0.04, ty - math.sin(ang) * L * 0.15, tx, ty)
        p.curveTo(tx - math.cos(ang) * L * 0.2 + h * 0.04, ty - math.sin(ang) * L * 0.15,
                  cx + math.cos(ang) * L * 0.4 + h * 0.05, base_y + math.sin(ang) * L * 0.4, cx, base_y)
        c.drawPath(p, stroke=1, fill=0)
    c.line(cx, base_y, cx, cy - h * 0.44)                                        # la tige


def _enorme(c, cx, cy, w, h, enc):
    """59 — ELLE EST GROSSE ET ÉNORME : l'énorme boule, la petite à côté."""
    c.setStrokeColor(enc); c.setLineWidth(0.8)
    c.setFillColor(enc)
    c.circle(cx + w * 0.08, cy - h * 0.02, h * 0.40, stroke=1, fill=1)
    c.setFillColor(colors.white)
    c.circle(cx - w * 0.34, cy - h * 0.30, h * 0.09, stroke=1, fill=1)


def _pepe(c, cx, cy, w, h, enc):
    """64 — GRAND-PÈRE : chapeau, dos penché, canne."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.7)
    bx = cx - w * 0.08
    c.circle(bx, cy + h * 0.26, h * 0.11, stroke=1, fill=1)
    c.line(bx - h * 0.15, cy + h * 0.35, bx + h * 0.15, cy + h * 0.35)           # le chapeau
    c.rect(bx - h * 0.085, cy + h * 0.35, h * 0.17, h * 0.09, stroke=1, fill=1)
    c.line(bx, cy + h * 0.15, bx + w * 0.05, cy - h * 0.14)                      # le dos penché
    c.line(bx + w * 0.05, cy - h * 0.14, bx - w * 0.05, cy - h * 0.44)
    c.line(bx + w * 0.05, cy - h * 0.14, bx + w * 0.13, cy - h * 0.44)
    c.line(bx, cy + h * 0.06, bx + w * 0.26, cy - h * 0.10)                      # le bras → la canne
    c.line(cx + w * 0.18, cy - h * 0.10, cx + w * 0.18, cy - h * 0.44)


def _meme(c, cx, cy, w, h, enc):
    """65 — GRAND-MÈRE : chignon, robe, canne."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.7)
    bx = cx - w * 0.08
    c.circle(bx, cy + h * 0.26, h * 0.11, stroke=1, fill=1)
    c.circle(bx, cy + h * 0.40, h * 0.05, stroke=1, fill=1)                      # le chignon
    p = c.beginPath()
    p.moveTo(bx, cy + h * 0.15); p.lineTo(bx - h * 0.20, cy - h * 0.18); p.lineTo(bx + h * 0.20, cy - h * 0.18)
    p.close(); c.drawPath(p, stroke=1, fill=1)                                   # la robe
    c.line(bx - w * 0.05, cy - h * 0.18, bx - w * 0.05, cy - h * 0.44)
    c.line(bx + w * 0.05, cy - h * 0.18, bx + w * 0.05, cy - h * 0.44)
    c.line(bx, cy + h * 0.06, bx + w * 0.26, cy - h * 0.10)                      # le bras → la canne
    c.line(cx + w * 0.18, cy - h * 0.10, cx + w * 0.18, cy - h * 0.44)


def _queue(c, cx, cy, w, h, enc):
    """66 — LA QUEUE EN L'AIR : le chat de dos, la queue dressée."""
    c.setStrokeColor(enc); c.setFillColor(colors.white); c.setLineWidth(0.7)
    c.ellipse(cx - w * 0.30, cy - h * 0.42, cx + w * 0.08, cy + h * 0.02, stroke=1, fill=1)
    c.circle(cx - w * 0.11, cy + h * 0.06, h * 0.13, stroke=1, fill=1)           # la tête de dos
    for sgn in (-1, 1):                                                          # les oreilles
        ex = cx - w * 0.11 + sgn * h * 0.09
        p = c.beginPath()
        p.moveTo(ex - h * 0.045, cy + h * 0.14); p.lineTo(ex, cy + h * 0.26); p.lineTo(ex + h * 0.045, cy + h * 0.15)
        p.close(); c.drawPath(p, stroke=1, fill=1)
    p = c.beginPath()                                                            # LA QUEUE EN L'AIR
    p.moveTo(cx + w * 0.06, cy - h * 0.10)
    p.curveTo(cx + w * 0.24, cy - h * 0.02, cx + w * 0.28, cy + h * 0.22, cx + w * 0.20, cy + h * 0.42)
    c.setLineWidth(1.5); c.setLineCap(1)
    c.drawPath(p, stroke=1, fill=0)
    c.setLineCap(0)


_DESSINS = {1: _bonheur, 2: _petea, 4: _mahae, 8: _firifiri, 11: _deux_silhouettes,
            16: _eclat_juron, 18: _gateau, 28: _huile, 41: _caillou, 45: _mauiui,
            46: _sac, 47: _cassette, 54: _chanteur, 55: _reines_nuit, 56: _feuille,
            59: _enorme, 61: _ua_poto, 64: _pepe, 65: _meme, 66: _queue,
            69: _mangez_vous, 71: _tiapai}


def poser_numero_image(c, num, cx, cy, w_mm, h_mm, enc_color, coin="bd"):
    """L'image à la place du chiffre + le numéro en petit au coin."""
    w, h = w_mm * mm, h_mm * mm
    _DESSINS[num](c, cx, cy + 0.06 * h, w, h * 0.92, enc_color)
    px = cx + (w / 2 - 1.0 * mm) * (1 if "d" in coin else -1)
    py = cy - h / 2 + 0.6 * mm
    c.setFillColor(enc_color)
    c.setFont("Helvetica-Bold", 4.6)
    (c.drawRightString if "d" in coin else c.drawString)(px, py, str(num))


def credit_pied(c, page_w):
    """Le crédit, une seule fois, au pied de chaque page."""
    c.setFillColor(colors.Color(0.55, 0.55, 0.55))
    c.setFont("Helvetica", 4)
    c.drawCentredString(page_w / 2, 2.2 * mm, "SMORFIA by 2KEA \u00b7 le jeu des images \u2014 d'apr\u00e8s la smorfia napolitaine")
