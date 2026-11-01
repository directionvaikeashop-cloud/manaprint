# -*- coding: utf-8 -*-
"""MANAPRINT — RURUTU (RANIHEI SISTERS & SHOP), maquette fournie par Maeva (31/10).
8 cartons / feuille A4 PORTRAIT (grille 2 colonnes x 4 rangées).
Chaque carton : paysage de Rurutu + 6 cercles en UNE rangée = 2 groupes de 3.
  Groupe GAUCHE (cercles 1-2-3) : 1-15 · 16-45 · 46-75
  Groupe DROITE (cercles 4-5-6) : 1-15 · 16-45 · 46-75
  -> crieur 1 à 75 ; chaque groupe de 3 couvre tout le damier.
La maquette (carton complet, 6 cercles) est reprise TELLE QUELLE comme image de
fond, répétée 8 fois ; on ajoute seulement les chiffres dans les cercles."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

PAGE_W, PAGE_H = A4                 # portrait (595 x 842)
CARTES_PAGE = 8
POLICE = "Helvetica-Bold"
GRIS = colors.Color(0.20, 0.20, 0.20)
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]

# le carton-modèle (512 x 372) — centres des 6 cercles mesurés dessus.
_IMG_W, _IMG_H = 512.0, 372.0
_CX = [60.5, 137.5, 214.5, 291.5, 368.5, 445.5]     # centres X des 6 cercles (mesurés)
_CY = 193.3                                          # centre Y commun (depuis le haut)
_R = 34.9                                            # rayon des cercles
# les plages, cercle par cercle (gauche->droite) : 2 groupes de 3 identiques
PLAGES = [(1, 15), (16, 45), (46, 75), (1, 15), (16, 45), (46, 75)]

# grille 2 x 4 : on dimensionne le carton pour tenir en hauteur ET en largeur,
# puis on centre le bloc sur la page (le paysage est plus large que haut).
_MARGE = 14
_GAP_X = 10
_GAP_Y = 8
_avail_w = PAGE_W - 2 * _MARGE
_avail_h = PAGE_H - 2 * _MARGE
_cw_w = (_avail_w - _GAP_X) / 2.0
_ch_w = _cw_w * (_IMG_H / _IMG_W)
if 4 * _ch_w + 3 * _GAP_Y <= _avail_h:
    _CW, _CH = _cw_w, _ch_w
else:
    _CH = (_avail_h - 3 * _GAP_Y) / 4.0
    _CW = _CH * (_IMG_W / _IMG_H)
_BLOC_W = 2 * _CW + _GAP_X
_BLOC_H = 4 * _CH + 3 * _GAP_Y
_X0 = (PAGE_W - _BLOC_W) / 2.0                       # marge gauche (bloc centré)
_YTOP = (PAGE_H - _BLOC_H) / 2.0                     # marge haute (bloc centré)


def _fond():
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "rurutu_carton.png")
_IMG_FOND = _fond()


def _origine(idx):
    """Coin bas-gauche (x, y) du carton n° idx (0..7) : 2 colonnes, 4 rangées."""
    col = idx % 2
    rang = idx // 2                                  # 0 en haut
    x = _X0 + col * (_CW + _GAP_X)
    y = PAGE_H - _YTOP - (rang + 1) * _CH - rang * _GAP_Y
    return x, y


def _numeros(rng):
    """Un numéro tiré dans chaque plage, cercle par cercle."""
    return [rng.randint(a, b) for a, b in PLAGES]


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 757)
    serie = int(serie_start)
    faits = 0
    try:
        page_dep = max(1, int(page_start))
    except Exception:
        page_dep = 1

    col_imposee = None
    if couleur and couleur_perso:
        try:
            col_imposee = colors.HexColor(couleur_perso)
        except Exception:
            col_imposee = None

    while faits < n_:
        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            x0, y0 = _origine(idx)
            try:
                c.drawImage(_IMG_FOND, x0, y0, _CW, _CH,
                            preserveAspectRatio=False, mask="auto")
            except Exception:
                pass
            if couleur:
                col = col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])
            else:
                col = GRIS
            c.setFillColor(col)
            r_pt = _R / _IMG_W * _CW
            taille = r_pt * 1.5
            c.setFont(POLICE, taille)
            for i, num in enumerate(_numeros(rng)):
                cx = x0 + _CX[i] / _IMG_W * _CW
                cy = y0 + _CH * (1 - _CY / _IMG_H)
                c.drawCentredString(cx, cy - taille * 0.35, str(num))
            c.setFillColor(colors.Color(0.55, 0.55, 0.55))
            c.setFont("Helvetica", 6)
            c.drawCentredString(x0 + _CW / 2.0, y0 + 3, "N° %05d" % serie)
            serie += 1
            faits += 1
        if page_dep > 1 or faits > CARTES_PAGE:
            c.setFillColor(colors.Color(0.6, 0.6, 0.6))
            c.setFont("Helvetica", 6)
            nfe = page_dep + (faits - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 8, PAGE_H - 12, "%03d" % nfe)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf
