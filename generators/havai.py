"""
MANAPRINT — Générateur HAVAI (format A4)

🌺 REFAIT LE 08/08 (sceau Maeva) : la CARTE DE RAIATEA, l'île sacrée,
prend place à gauche du carton — avec ses six villages — et les HUIT
NUMÉROS s'alignent à droite, chacun sous la LETTRE de sa quinzaine.

RÈGLE INCHANGÉE : 8 numéros, cinq familles comme les cinq lettres —
  H : 1-15 (deux numéros) · A : 16-30 (un) · V : 31-45 (deux)
  A : 46-60 (un)          · I : 61-75 (deux)
Le sac du crieur ne change donc pas d'un chiffre.
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
    "#E53935", "#FF7043", "#FB8C00", "#F9A825",
    "#43A047", "#00ACC1", "#1E88E5", "#3949AB",
    "#8E24AA", "#D81B60", "#6D4C41", "#546E7A",
]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)
GRIS_GRILLE = colors.Color(0.62, 0.62, 0.62)

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
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

# 🗺️ LA CARTE DE RAIATEA (dessin de Maeva) — l'emblème du jeu.
_RATIO_ILE = 900.0 / 745.0
import os as _os2


def _choisir_image(motif, ratio_attendu):
    """🛟 Retrouve la carte, quel que soit son nom de fichier."""
    dossier = _os2.path.dirname(_os2.path.abspath(__file__))
    exact = _os2.path.join(dossier, motif + ".png")
    candidats = []
    try:
        for f in _os2.listdir(dossier):
            if motif in f and f.lower().endswith(".png"):
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


_IMAGE_ILE = _choisir_image("raiatea_ile", _RATIO_ILE)

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

FOOT_H = 3 * mm
BANDEAU_H = 2.6 * mm
HDR_H = 4.2 * mm
GRID_N = 5        # 5 colonnes H·A·V·A·I
GRID_ROWS = 3     # 3 rangées (compact façon BROWN 8)

LETTRES = ["H", "A", "V", "A", "I"]
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
# Motif HAVAI : cases pleines (ligne, colonne), lignes numérotées du HAUT
# Motif COMPACT en quinconce (décision Maeva) : H·V·I / A·A / H·V·I
# sur 3 rangées — la case CENTRALE accueille le QR.
POSITIONS = {
    (0, 0), (0, 2), (0, 4),
    (1, 1), (1, 3),
    (2, 0), (2, 2), (2, 4),
}
_NB_PAR_COL = [2, 1, 2, 1, 2]


def _gen_carte():
    """8 numéros TRIÉS par colonne selon le motif HAVAI."""
    carte = {}
    for ci, (lo, hi) in enumerate(RANGES):
        nums = sorted(random.sample(range(lo, hi + 1), _NB_PAR_COL[ci]))
        lignes = sorted(r for (r, c) in POSITIONS if c == ci)
        for k, ri in enumerate(lignes):
            carte[(ri, ci)] = nums[k]
    return carte


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / GRID_N

    # Bordure
    c.setStrokeColor(col)
    c.setLineWidth(1.0)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # Mini-bandeau
    bandeau = "LE JEU \u00ab HAVAI \u00bb"
    if titre_jeu:
        bandeau += "  \u2014  " + titre_jeu
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 2.2 * mm, bandeau[:60])

    # ═══ LA CARTE DE RAIATEA À GAUCHE, LES HUIT NUMÉROS À DROITE ═══
    hdr_y = y0 + CARD_H - BANDEAU_H - 1.0 * mm
    z_bot = y0 + FOOT_H + 1.4 * mm
    z_top = hdr_y - 1.0 * mm
    z_h = z_top - z_bot

    # ── la carte de l'île sacrée ─────────────────────────────────────────
    PLACE_QR = 11.0 * mm
    part = 0.40
    ilw = CARD_W * part - 3.5 * mm
    ilh = ilw / _RATIO_ILE
    if ilh > z_h - PLACE_QR:
        ilh = z_h - PLACE_QR
        ilw = ilh * _RATIO_ILE
    ilx = x0 + 2.5 * mm
    ily = z_bot + PLACE_QR + (z_h - PLACE_QR - ilh) / 2
    if _os2.path.exists(_IMAGE_ILE):
        try:
            c.drawImage(_IMAGE_ILE, ilx, ily, ilw, ilh, mask="auto",
                        preserveAspectRatio=True)
        except Exception:
            pass

    # ── les huit numéros, en deux colonnes de quatre ─────────────────────
    # Chaque case porte la LETTRE de sa quinzaine : H A V A I, les cinq
    # familles du jeu. La règle n'a pas bougé, seul l'habillage a changé.
    ordre = sorted(carte.items(), key=lambda kv: (kv[0][1], kv[0][0]))
    gx = x0 + CARD_W * part + 1.0 * mm
    gw = CARD_W - (gx - x0) - 2.5 * mm
    ECART = 1.3 * mm
    cw = (gw - ECART) / 2.0
    lh = z_h / 4.0
    taille = min(32.0, (lh * 0.84 - 3.4 * mm) / 0.72 * 72 / 25.4,
                 cw * 0.58 / 0.60 * 72 / 25.4)
    for k, ((ri, ci), n) in enumerate(ordre):
        colonne, rangee = k % 2, k // 2
        bx = gx + colonne * (cw + ECART)
        by = z_top - (rangee + 1) * lh
        c.setFillColor(colors.white)
        c.setStrokeColor(col)
        c.setLineWidth(0.55)
        c.roundRect(bx, by + lh * 0.08, cw, lh * 0.84, 1.3 * mm, stroke=1, fill=1)
        nx = bx + cw / 2
        ny = by + lh * 0.5 - taille * 0.28 + 0.9 * mm
        if _sec:
            _sec.chiffre_micro(c, n, nx, ny, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, taille)
            c.drawCentredString(nx, ny, str(n))
        # la lettre de sa quinzaine, sous le numéro
        c.setFillColor(col)
        c.setFont("Helvetica-Bold", 6.0)
        c.drawCentredString(nx, by + lh * 0.16, LETTRES[ci])

    # ── le QR, sous la carte ─────────────────────────────────────────────
    if _sec and evenement_id:
        try:
            _q = min(9.5 * mm, ilw * 0.55)
            _sec.carton_qr(c, ilx + (ilw - _q) / 2, z_bot + (PLACE_QR - _q) / 2,
                           _q, evenement_id, serie, avec_code=False)
        except Exception:
            pass

    # Pied : série centrée (façon maquette) + Resp.
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY); c.setFont("Helvetica", 5)
    c.drawCentredString(x0 + CARD_W / 2, y0 + 1.2 * mm, f"{serie:06d}")
    if telephone:
        c.setFont("Helvetica", 4.5)
        c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, f"Resp. {telephone}")


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    serie = serie_start
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    encre = NOIR if couleur else GRIS40

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        titre_aff = titre_jeu if titre_jeu else "HAVAI"
        ligne2 = titre_aff
        if date_lieu: ligne2 += "  \u00b7  " + date_lieu
        ligne2 += f"  \u00b7  Page {no_page}"
        c.setFillColor(GREY); c.setFont("Helvetica", 7)
        y2 = (PAGE_H - 8.5 * mm) if nom_evenement else (PAGE_H - 6 * mm)
        c.drawCentredString(PAGE_W / 2, y2, ligne2)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur
                        else "#999999")
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True)
    with open("test_havai.pdf", "wb") as f:
        f.write(pdf.read())
    print("HAVAI g\u00e9n\u00e9r\u00e9")
