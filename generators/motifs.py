# -*- coding: utf-8 -*-
"""
MANAPRINT — LA BIBLIOTHÈQUE DES MOTIFS EN FILIGRANE 🖼️
Des décors vectoriels gris très pâle, dessinés DERRIÈRE les numéros
(inspirés du billet « HEI NI SAM » aimé de Maeva) : les chiffres restent
parfaitement lisibles, le toner est épargné (esprit ÉCO), la sécurité
microtexte est intacte, et tout est dessiné maison — zéro droit d'auteur.

Usage par un générateur :
    from generators import motifs as _motifs
    _motifs.dessiner_filigrane(c, x0, y0, w, h, motif, graine=serie)
Le placement est DÉTERMINISTE par graine (série) : une refabrication 📬
redonne exactement le même carton, filigrane compris.
"""
import math
import random
from reportlab.lib import colors

GRIS_MOTIF = colors.Color(0.845, 0.845, 0.845)   # visible mais jamais gênant
GRIS_LIGNE = colors.Color(0.80, 0.80, 0.80)

MOTIFS_DISPONIBLES = ("des", "hibiscus", "tortue", "palmier", "poisson", "boules", "etoiles",
                      "coeur", "trefle", "soleil", "lune", "vague", "diamant", "couronne",
                      "ananas", "varie")


def _de(c, t, points):
    c.setFillColor(colors.white); c.setStrokeColor(GRIS_LIGNE); c.setLineWidth(1.3)
    c.roundRect(-t / 2, -t / 2, t, t, t * 0.18, stroke=1, fill=1)
    c.setFillColor(GRIS_MOTIF)
    pos = {2: [(-.25, -.25), (.25, .25)],
           3: [(-.28, -.28), (0, 0), (.28, .28)],
           4: [(-.28, -.28), (.28, -.28), (-.28, .28), (.28, .28)],
           5: [(-.28, -.28), (.28, -.28), (0, 0), (-.28, .28), (.28, .28)]}
    for px, py in pos[points]:
        c.circle(px * t, py * t, t * 0.095, stroke=0, fill=1)


def _hibiscus(c, t, _v):
    r = t * 0.52
    c.setFillColor(GRIS_MOTIF)
    for i in range(5):
        c.saveState(); c.rotate(i * 72)
        p = c.beginPath()
        p.moveTo(0, 0)
        p.curveTo(-r * 0.5, r * 0.35, -r * 0.4, r * 0.95, 0, r)
        p.curveTo(r * 0.4, r * 0.95, r * 0.5, r * 0.35, 0, 0)
        c.drawPath(p, stroke=0, fill=1)
        c.restoreState()
    c.setFillColor(colors.white); c.circle(0, 0, r * 0.18, stroke=0, fill=1)


def _tortue(c, t, _v):
    r = t * 0.42
    c.setFillColor(GRIS_MOTIF)
    c.ellipse(-r, -r * 0.82, r, r * 0.82, stroke=0, fill=1)      # carapace
    c.circle(0, r * 1.02, r * 0.30, stroke=0, fill=1)            # tête
    for sx in (-1, 1):
        for sy in (-1, 1):
            c.ellipse(sx * r * 0.55 - r * 0.22, sy * r * 0.70 - r * 0.14,
                      sx * r * 0.55 + r * 0.22, sy * r * 0.70 + r * 0.14, stroke=0, fill=1)
    c.setStrokeColor(colors.white); c.setLineWidth(1)
    c.line(-r * 0.5, 0, r * 0.5, 0)
    c.line(-r * 0.25, -r * 0.55, -r * 0.25, r * 0.55)
    c.line(r * 0.25, -r * 0.55, r * 0.25, r * 0.55)


def _palmier(c, t, _v):
    c.setStrokeColor(GRIS_MOTIF); c.setLineWidth(t * 0.075); c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(0, -t * 0.5); p.curveTo(t * 0.05, -t * 0.15, t * 0.10, t * 0.1, t * 0.16, t * 0.34)
    c.drawPath(p, stroke=1, fill=0)
    c.setLineWidth(t * 0.05)
    for ang in (35, 80, 125, 165, -5):
        c.saveState(); c.translate(t * 0.16, t * 0.34); c.rotate(ang)
        pf = c.beginPath()
        pf.moveTo(0, 0); pf.curveTo(t * 0.16, t * 0.10, t * 0.30, t * 0.08, t * 0.40, -t * 0.02)
        c.drawPath(pf, stroke=1, fill=0)
        c.restoreState()


def _poisson(c, t, _v):
    r = t * 0.42
    c.setFillColor(GRIS_MOTIF)
    c.ellipse(-r, -r * 0.55, r * 0.55, r * 0.55, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(r * 0.45, 0); p.lineTo(r * 1.0, r * 0.5); p.lineTo(r * 1.0, -r * 0.5); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(colors.white); c.circle(-r * 0.55, r * 0.12, r * 0.09, stroke=0, fill=1)


def _boule(c, t, _v):
    r = t * 0.42
    c.setFillColor(GRIS_MOTIF); c.circle(0, 0, r, stroke=0, fill=1)
    c.setFillColor(colors.white); c.circle(0, 0, r * 0.55, stroke=0, fill=1)
    c.setFillColor(GRIS_MOTIF)
    c.setFont("Helvetica-Bold", max(5.0, t * 0.34))
    c.drawCentredString(0, -t * 0.12, str(_v or 7))


def _etoile(c, t, _v):
    r = t * 0.5
    c.setFillColor(GRIS_MOTIF)
    p = c.beginPath()
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        x, y = rr * math.cos(ang), rr * math.sin(ang)
        (p.moveTo if i == 0 else p.lineTo)(x, y)
    p.close()
    c.drawPath(p, stroke=0, fill=1)



def _coeur(c, t, _v):
    r = t * 0.45
    c.setFillColor(GRIS_MOTIF)
    p = c.beginPath()
    p.moveTo(0, -r)
    p.curveTo(-r * 1.15, -r * 0.1, -r * 0.85, r * 0.85, 0, r * 0.28)
    p.curveTo(r * 0.85, r * 0.85, r * 1.15, -r * 0.1, 0, -r)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def _trefle(c, t, _v):
    r = t * 0.24
    c.setFillColor(GRIS_MOTIF)
    for ang in (90, 210, 330):
        c.circle(r * 1.05 * math.cos(math.radians(ang)),
                 r * 1.05 * math.sin(math.radians(ang)), r, stroke=0, fill=1)
    c.setStrokeColor(GRIS_MOTIF); c.setLineWidth(t * 0.07); c.setLineCap(1)
    c.line(0, -r * 0.4, r * 0.22, -t * 0.5)


def _soleil(c, t, _v):
    r = t * 0.26
    c.setFillColor(GRIS_MOTIF); c.circle(0, 0, r, stroke=0, fill=1)
    c.setStrokeColor(GRIS_MOTIF); c.setLineWidth(t * 0.06); c.setLineCap(1)
    for i in range(8):
        ang = math.radians(i * 45)
        c.line(r * 1.25 * math.cos(ang), r * 1.25 * math.sin(ang),
               r * 1.85 * math.cos(ang), r * 1.85 * math.sin(ang))


def _lune(c, t, _v):
    r = t * 0.45
    c.setFillColor(GRIS_MOTIF); c.circle(0, 0, r, stroke=0, fill=1)
    c.setFillColor(colors.white); c.circle(r * 0.42, r * 0.18, r * 0.82, stroke=0, fill=1)


def _vague(c, t, _v):
    c.setStrokeColor(GRIS_MOTIF); c.setLineCap(1)
    for k, ep in ((0, 0.09), (1, 0.07), (2, 0.05)):
        c.setLineWidth(t * ep)
        y0 = -t * 0.18 * k
        p = c.beginPath()
        p.moveTo(-t * 0.5, y0)
        p.curveTo(-t * 0.25, y0 + t * 0.28, 0, y0 - t * 0.10, t * 0.12, y0 + t * 0.16)
        p.curveTo(t * 0.22, y0 + t * 0.34, t * 0.10, y0 + t * 0.38, t * 0.02, y0 + t * 0.30)
        c.drawPath(p, stroke=1, fill=0)


def _diamant(c, t, _v):
    r = t * 0.45
    c.setFillColor(GRIS_MOTIF)
    p = c.beginPath()
    p.moveTo(-r, r * 0.35); p.lineTo(-r * 0.5, r * 0.85); p.lineTo(r * 0.5, r * 0.85)
    p.lineTo(r, r * 0.35); p.lineTo(0, -r * 0.9); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setStrokeColor(colors.white); c.setLineWidth(1)
    c.line(-r, r * 0.35, r, r * 0.35)
    c.line(-r * 0.45, r * 0.35, 0, -r * 0.9); c.line(r * 0.45, r * 0.35, 0, -r * 0.9)


def _couronne(c, t, _v):
    r = t * 0.45
    c.setFillColor(GRIS_MOTIF)
    p = c.beginPath()
    p.moveTo(-r, -r * 0.5); p.lineTo(-r, r * 0.35); p.lineTo(-r * 0.5, -r * 0.05)
    p.lineTo(0, r * 0.6); p.lineTo(r * 0.5, -r * 0.05); p.lineTo(r, r * 0.35)
    p.lineTo(r, -r * 0.5); p.close()
    c.drawPath(p, stroke=0, fill=1)
    for px in (-r, 0, r):
        c.circle(px, (r * 0.35 if px else r * 0.6) + r * 0.16, r * 0.12, stroke=0, fill=1)


def _ananas(c, t, _v):
    r = t * 0.34
    c.setFillColor(GRIS_MOTIF)
    c.ellipse(-r * 0.72, -r * 1.05, r * 0.72, r * 0.55, stroke=0, fill=1)
    c.setStrokeColor(colors.white); c.setLineWidth(0.9)
    for k in (-1, 0, 1):
        c.line(-r * 0.72 + (k + 1) * r * 0.48, -r * 1.0, -r * 0.20 + (k + 1) * r * 0.48, r * 0.5)
        c.line(r * 0.72 - (k + 1) * r * 0.48, -r * 1.0, r * 0.20 - (k + 1) * r * 0.48, r * 0.5)
    c.setStrokeColor(GRIS_MOTIF); c.setLineWidth(t * 0.055); c.setLineCap(1)
    for ang in (60, 90, 120):
        c.line(0, r * 0.5, r * 0.62 * math.cos(math.radians(ang)), r * 0.5 + r * 0.75 * math.sin(math.radians(ang)))

_DESSINS = {"des": _de, "hibiscus": _hibiscus, "tortue": _tortue,
            "palmier": _palmier, "poisson": _poisson, "boules": _boule, "etoiles": _etoile,
            "coeur": _coeur, "trefle": _trefle, "soleil": _soleil, "lune": _lune,
            "vague": _vague, "diamant": _diamant, "couronne": _couronne, "ananas": _ananas}

# positions relatives possibles (JAMAIS le centre : le sanctuaire du QR est sacré)
_COINS = [(0.24, 0.74), (0.76, 0.72), (0.22, 0.28), (0.78, 0.26), (0.50, 0.82), (0.50, 0.18)]


def dessiner_filigrane(c, x0, y0, w, h, motif, graine=1, nb=3, echelle=1.0):
    """Sème 2-3 motifs pâles dans le rectangle de la carte, loin du centre.
    Déterministe par graine : la refabrication redonne le même décor."""
    motif = (motif or "").strip().lower()
    if motif != "varie" and motif not in _DESSINS:
        return False
    rng = random.Random(778899 + int(graine))
    places = rng.sample(_COINS, min(nb, len(_COINS)))
    base = min(w, h)
    for i, (px, py) in enumerate(places):
        t = base * (0.30 + 0.10 * rng.random()) * echelle
        c.saveState()
        c.translate(x0 + w * px, y0 + h * py)
        c.rotate(rng.uniform(-28, 28))
        # 🎨 « varie » : un motif différent à chaque emplacement (déterministe)
        dessin = rng.choice(sorted(_DESSINS)) if motif == "varie" else motif
        valeur = rng.choice([2, 3, 4, 5]) if dessin == "des" else rng.randint(1, 90)
        _DESSINS[dessin](c, t, valeur)
        c.restoreState()
    return True
