# -*- coding: utf-8 -*-
"""
MANAPRINT — SMORFIA by 2KEA · le jeu des images (v4, 27/07/2026)
LE CHIFFRE DEVIENT L'IMAGE : sur chaque carton, UN des numéros est rendu
par son image de la smorfia du fenua (panthéon VALIDÉ par Maeva le 27/07) :
  11 TEPEA TOA ORUA  → deux silhouettes qui se tiennent
  16 TAIORO          → éclat de BD (l'explosion du juron)
  18 MON ÂGE         → gâteau d'anniversaire
  47 K7              → cassette audio
  54 GABILOU         → chanteur au micro (silhouette générique — JAMAIS un portrait)
Le numéro reste écrit en petit au coin (litiges + vérification).
"""
import hashlib
import hmac
from reportlab.lib import colors
from reportlab.lib.units import mm

ANNONCES = {
    11: "TEPEA TOA ORUA",
    16: "TAIORO",
    18: "MON \u00c2GE",
    47: "K7",
    54: "GABILOU",
}
_NUMS = sorted(ANNONCES)


def numero_pour_serie(serie):
    """La même carte porte toujours la même image (refab comprise)."""
    h = hmac.new(b"SMORFIA-2KEA", ("SMORFIA:%d" % int(serie)).encode(), hashlib.sha256)
    return _NUMS[int.from_bytes(h.digest()[:4], "big") % len(_NUMS)]


def choix_hote(serie, nb_choix):
    """Quand deux cases peuvent héberger le numéro, l'empreinte tranche."""
    h = hmac.new(b"SMORFIA-2KEA", ("HOTE:%d" % int(serie)).encode(), hashlib.sha256)
    return int.from_bytes(h.digest()[:4], "big") % max(1, nb_choix)


# ─────────────────────────── les 5 images (vectoriel maison) ──────────────────────────

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


_DESSINS = {11: _deux_silhouettes, 16: _eclat_juron, 18: _gateau, 47: _cassette, 54: _chanteur}


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
