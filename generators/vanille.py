"""
🌼 VANILLE DE DONA — LE 136e JEU, REFAIT LE 05/08 EN MÉDAILLONS

Maeva, après un tirage papier : « la première image, pas très jolie » — le
dessin crayonné en filigrane rendait mal à l'impression. On reprend donc le
cadre ovale de son image : le mot du milieu est remplacé par la BOULE (le
numéro), et la fleur de vanille est DESSINÉE AU TRAIT contre chaque ovale.

RÈGLE INCHANGÉE (celle qu'elle avait validée) :
    5 numéros DISTINCTS dans 30-75, triés,
    + LE TRÉSOR : un montant en francs (5/10/15/20/50/100).
Le montant se gagne selon les règles de la salle.

CHIFFRES : 30 points, le calibre de la maison.
ENCRE : tout est au trait, aucun aplat, aucune image.
"""
import io
import math
import os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg

try:
    from generators import securite as _sec
except ImportError:
    try:
        import securite as _sec
    except ImportError:
        _sec = None

_POLICE_ECO = "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("DJBOLDVA", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    _POLICE_ECO = "DJBOLDVA"
except Exception:
    pass
_POLICE_P15 = _POLICE_ECO
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)     # imposé au boot par app.py
_GRIS_P15 = colors.Color(0.25, 0.25, 0.25)


def _style_chiffres(style):
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
COLS_PAGE, ROWS_PAGE = 2, 3               # 6 cartes / A4
MARGIN_X, MARGIN_TOP, MARGIN_BOT = 9 * mm, 6 * mm, 9 * mm
GUTTER_X, GUTTER_Y = 4 * mm, 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

# 🖼️ LE CADRE DE MAEVA — son propre dessin (le 3e modèle : l'ovale complet
# avec la fleur de vanille et ses gousses), duquel le mot « VANILLA » a été
# retiré lettre par lettre. Pâli une seule fois à la découpe : le chargeur
# ne le repâlit PAS (piège du double pâlissement, 22/07).
_DOSSIER = os.path.dirname(os.path.abspath(__file__))
_RATIO_CADRE = 900.0 / 884.0        # cadre ALLONGÉ vers le haut (05/08)


def _choisir_image(motif, ratio_attendu):
    """🛟 Retrouve le cadre, quel que soit son nom de fichier.

    Au téléversement, GitHub garde parfois le nom de livraison
    (« 2_TELEVERSER_vanille_cadre.png ») ou ajoute un « (1) ». Le nom ne
    suffit donc pas à départager. Les PROPORTIONS, elles, ne mentent
    pas : parmi tous les fichiers dont le nom contient `motif`, on garde
    celui dont le ratio colle au dessin attendu. (10/08 — le jeu sortait
    SANS SON IMAGE parce que le fichier portait un préfixe.)
    """
    exact = os.path.join(_DOSSIER, motif + ".png")
    candidats = []
    try:
        for f in os.listdir(_DOSSIER):
            if motif in f and f.lower().endswith(".png"):
                candidats.append(os.path.join(_DOSSIER, f))
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


_CADRE = _choisir_image("vanille_cadre", _RATIO_CADRE)

GRAINE = 986000
PLAGE = (30, 75)
MONTANTS = [5, 10, 15, 20, 50, 100]
TAILLE_CHIFFRE = 30                        # le calibre maison
MED_COLS, MED_ROWS = 2, 3                  # 6 médaillons : 5 numéros + le trésor

RAINBOW = ["#6A994E", "#2A9D8F", "#BC6C25", "#457B9D", "#E76F51", "#7209B7",
           "#E63946", "#F4A261", "#8E7DBE", "#264653", "#D62828", "#F72585"]


def _gen_carte(rng):
    """5 numéros distincts dans 30-75, triés, + le montant du trésor."""
    nums = sorted(rng.sample(range(PLAGE[0], PLAGE[1] + 1), 5))
    return nums, rng.choice(MONTANTS)


def _fleur(c, cx, cy, r, col):
    """🌼 La fleur de vanille AU TRAIT : cinq pétales en amande autour d'un
    cœur, et deux gousses qui s'échappent. Aucun aplat — juste des lignes."""
    c.setFillColor(colors.white)
    c.setStrokeColor(col)
    c.setLineWidth(0.7)
    for k in range(5):
        a = math.radians(90 + k * 72)
        px, py = cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.62
        c.saveState()
        c.translate(px, py)
        c.rotate(math.degrees(a) - 90)
        p = c.beginPath()                        # un pétale en amande
        p.moveTo(0, -r * 0.60)
        p.curveTo(r * 0.42, -r * 0.12, r * 0.30, r * 0.52, 0, r * 0.66)
        p.curveTo(-r * 0.30, r * 0.52, -r * 0.42, -r * 0.12, 0, -r * 0.60)
        c.drawPath(p, stroke=1, fill=1)
        c.restoreState()
    # le cœur de la fleur
    c.setFillColor(colors.white)
    c.setStrokeColor(col)
    c.setLineWidth(0.8)
    c.circle(cx, cy, r * 0.30, stroke=1, fill=1)
    c.setLineWidth(0.5)
    c.circle(cx, cy, r * 0.16, stroke=1, fill=0)


def _gousses(c, cx, cy, r, largeur, col):
    """Les gousses : deux courbes fines qui filent le long de l'ovale."""
    c.setStrokeColor(col)
    c.setLineWidth(0.8)
    # elles filent vers le BAS-DROITE et longent le bord de l'ovale :
    # jamais elles ne barrent le chiffre.
    for depart, portee, chute in ((-0.35, 1.00, -0.55), (-0.75, 0.78, -0.30)):
        x0, y0 = cx + r * 0.45, cy + r * depart
        x1 = x0 + largeur * portee
        y1 = y0 + r * chute
        p = c.beginPath()
        p.moveTo(x0, y0)
        p.curveTo(x0 + (x1 - x0) * 0.30, y0 - r * 0.45,
                  x0 + (x1 - x0) * 0.70, y1 - r * 0.18, x1, y1)
        c.drawPath(p, stroke=1, fill=0)
        c.setFillColor(colors.white)          # le bout de la gousse, arrondi
        c.circle(x1, y1, r * 0.09, stroke=1, fill=1)


def _medaillon(c, cx, cy, demi_l, demi_h, texte, col, gris_ch, police_ch,
               tresor=False, incline=0.0):
    """LE CADRE DE MAEVA, avec la boule (le numéro) à la place du mot.
    `incline` penche légèrement la boule, comme une fleur posée."""
    if incline:
        c.saveState()
        c.translate(cx, cy)
        c.rotate(incline)
        c.translate(-cx, -cy)
    larg = demi_l * 2
    haut = larg / _RATIO_CADRE
    if haut > demi_h * 2:
        haut = demi_h * 2
        larg = haut * _RATIO_CADRE
    if os.path.exists(_CADRE):
        try:
            c.drawImage(_CADRE, cx - larg / 2, cy - haut / 2, larg, haut,
                        mask="auto", preserveAspectRatio=True)
        except Exception:
            pass
    # la boule : le numéro EXACTEMENT là où était le mot. Cette bande
    # (de 12 % à 50 % de la hauteur du cadre) est la seule vraiment vide —
    # mesurée sur le dessin : 0,5 % d'encre contre 13 % au niveau de la
    # fleur. Les chiffres n'y rencontrent donc plus aucun pétale.
    nx = cx
    ny = cy + haut * 0.13 - TAILLE_CHIFFRE * 0.36
    if tresor:
        # le cadre étant allongé, le montant ET son mot tiennent tous les
        # deux DANS la bande vide, bien au-dessus de la fleur.
        c.setFillColor(col)
        c.setFont(police_ch, TAILLE_CHIFFRE)
        c.drawCentredString(nx, ny + 1.4 * mm, str(texte))
        c.setFont("Helvetica-Bold", 6.6)
        c.drawCentredString(nx, ny - 2.6 * mm, "FRANCS")
    elif _sec:
        _sec.chiffre_micro(c, texte, nx, ny, TAILLE_CHIFFRE, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch)
        c.setFont(police_ch, TAILLE_CHIFFRE)
        c.drawCentredString(nx, ny, str(texte))
    if incline:
        c.restoreState()


def _dessiner_carte(c, x0, y0, nums, montant, couleur_hex, serie,
                    titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ══ LE TITRE : « VANILLE DE D (le trésor) NA » ═════════════════════
    # Sceau Maeva : sur la première version, le O de DONA portait un
    # numéro. Ici c'est LE TRÉSOR qui prend sa place — la boule des
    # montants s'assied dans le mot, et « NA » la suit.
    T = 13.0
    gauche, droite = "VANILLE DE D", "NA"
    tres_l = 12.4 * mm                      # agrandie : le montant y tient au large
    tres_h = tres_l / _RATIO_CADRE
    wl = _lg(gauche, "Helvetica-Bold", T)
    wr = _lg(droite, "Helvetica-Bold", T)
    while (wl + 2 * tres_l + wr) > CARD_W - 8 * mm and T > 8.0:
        T -= 0.3
        wl = _lg(gauche, "Helvetica-Bold", T)
        wr = _lg(droite, "Helvetica-Bold", T)
    sx = x0 + (CARD_W - (wl + 2 * tres_l + wr)) / 2
    cy_t = y0 + CARD_H - 17.4 * mm
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", T)
    c.drawString(sx, cy_t - T * 0.34, gauche)
    c.drawString(sx + wl + 2 * tres_l, cy_t - T * 0.34, droite)
    _medaillon(c, sx + wl + tres_l, cy_t, tres_l, tres_h, montant,
               col, gris_ch, police_ch, tresor=True)

    if telephone:
        c.setFillColor(col)
        c.setFont("Helvetica", 5.6)
        c.drawCentredString(x0 + CARD_W / 2, y0 + 6.6 * mm,
                            str(telephone)[:16] +
                            (("  \u00b7  " + titre_jeu.strip()[:22]) if titre_jeu else ""))

    # ══ LES 5 BOULES DE VANILLE, SEMÉES DANS LA GRILLE ═════════════════
    # Elles ne sont pas alignées : elles se posent en quinconce, chacune
    # penchée d'un souffle — comme des fleurs tombées sur le carton.
    demi_l = 11.6 * mm
    demi_h = demi_l / _RATIO_CADRE
    # places calculées pour qu'aucune boule n'en touche une autre,
    # tout en gardant l'air d'un semis (rien n'est aligné)
    SEMIS = [(0.159, 0.750, -7.0),
             (0.484, 0.755, 4.5),
             (0.839, 0.510, -5.5),
             (0.215, 0.244, 6.5),
             (0.565, 0.258, -3.0)]
    zone_bas = y0 + 13.0 * mm
    zone_haut = y0 + CARD_H - 30.0 * mm
    for (fx, fy, ang), n in zip(SEMIS, nums):
        cx = x0 + CARD_W * fx
        cy = zone_bas + (zone_haut - zone_bas) * fy
        _medaillon(c, cx, cy, demi_l, demi_h, n, col, gris_ch, police_ch,
                   incline=ang)

    # ══ le pied ════════════════════════════════════════════════════════
    c.setFillColor(colors.Color(0.55, 0.55, 0.55))
    c.setFont("Helvetica", 4.4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + 9.0 * mm,
                        "COCHEZ \u00b7 le montant se gagne selon les r\u00e8gles de la salle")
    c.setFillColor(col)
    c.setFont("Helvetica", 5.4)
    c.drawString(x0 + 4.5 * mm, y0 + 3.6 * mm, "Carte N\u00b0 %05d" % serie)
    if _sec and evenement_id:
        try:
            q = 10.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - q - 4.0 * mm, y0 + 2.2 * mm,
                           q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", telephone="", date_lieu="",
                couleur_perso=None, style="eco", evenement_id="", motif=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    rng = random.Random(GRAINE + serie_start)
    serie, faites, no_page = serie_start, 0, 1

    while faites < nb_cartes:
        for row in range(ROWS_PAGE):
            for coln in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + coln * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                nums, montant = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, nums, montant, coul, serie,
                                titre_jeu, telephone, style=style,
                                evenement_id=evenement_id)
                serie += 1
                faites += 1
        c.setFillColor(colors.Color(0.72, 0.72, 0.72))
        c.setFont("Helvetica", 5.4)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, "%03d" % no_page)
        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    with open("test_vanille.pdf", "wb") as f:
        f.write(generer_pdf(nb_cartes=6, couleur=True, telephone="89 22 23 05").read())
    print("VANILLE DE DONA g\u00e9n\u00e9r\u00e9e")
