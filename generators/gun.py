# -*- coding: utf-8 -*-
"""MANAPRINT — GUN (RANIHEI SISTERS & SHOP), maquette fournie par Maeva (31/10).
8 cartons / feuille A4 PORTRAIT (grille 2 colonnes x 4 rangées).
Chaque carton : 5 cercles « viseur » en haut = les plages du B I N G O.
  B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75  (un numéro par cercle).
La maquette (carton de gauche, 5 cercles) est reprise TELLE QUELLE comme image
de fond, répétée 8 fois ; on ajoute seulement les chiffres dans les cercles.
(Décision Maeva 31/10 : 5 cercles PARTOUT — les cartons de droite de la
 maquette, qui n'en avaient que 4, deviennent identiques à ceux de gauche.)"""
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

# le carton-modèle (578 x 372) — centres des 5 cercles mesurés dessus.
_IMG_W, _IMG_H = 578.0, 372.0
_CX = [72, 180, 287, 395, 504]      # centres X des cercles (px image)
_CY = 72                            # centre Y commun (px image, depuis le haut)
_R = 47                             # rayon des cercles (px image)
# les 5 plages du BINGO, de gauche à droite : B · I · N · G · O
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

# grille 2 x 4 sur la page
_MARGE = 12
_GAP_X = 8
_GAP_Y = 8
_CW = (PAGE_W - 2 * _MARGE - _GAP_X) / 2.0          # largeur d'un carton
_CH = _CW * (_IMG_H / _IMG_W)                       # hauteur (aspect conservé)
_BLOC_H = 4 * _CH + 3 * _GAP_Y
_Y0 = (PAGE_H - _BLOC_H) / 2.0                      # bloc centré verticalement


def _fond():
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "gun_carton.png")
_IMG_FOND = _fond()


def _origine(idx):
    """Coin bas-gauche (x, y) du carton n° idx (0..7) : 2 colonnes, 4 rangées."""
    col = idx % 2
    rang = idx // 2                                  # 0 en haut
    x = _MARGE + col * (_CW + _GAP_X)
    y = _Y0 + (3 - rang) * (_CH + _GAP_Y)
    return x, y


def _numeros(rng):
    """Un numéro tiré dans chaque plage B · I · N · G · O."""
    return [rng.randint(a, b) for a, b in PLAGES]


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 911)
    serie = int(serie_start)
    faits = 0
    try:
        page_dep = max(1, int(page_start))
    except Exception:
        page_dep = 1

    # couleur imposée (option partenaire) : un seul code #RRGGBB pour tout le lot
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
            # 1) le carton-modèle (art de Maeva), tel quel
            try:
                c.drawImage(_IMG_FOND, x0, y0, _CW, _CH,
                            preserveAspectRatio=False, mask="auto")
            except Exception:
                pass
            # 2) les chiffres dans les 5 cercles
            if couleur:
                col = col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])
            else:
                col = GRIS
            c.setFillColor(col)
            r_pt = _R / _IMG_W * _CW
            taille = r_pt * 1.5          # chiffres bien remplissants dans le cercle
            c.setFont(POLICE, taille)
            for i, num in enumerate(_numeros(rng)):
                cx = x0 + _CX[i] / _IMG_W * _CW
                cy = y0 + _CH * (1 - _CY / _IMG_H)
                c.drawCentredString(cx, cy - taille * 0.35, str(num))
            # 3) numéro de série, discret, en bas du carton
            c.setFillColor(colors.Color(0.55, 0.55, 0.55))
            c.setFont("Helvetica", 6)
            c.drawCentredString(x0 + _CW / 2.0, y0 + 3, "N° %05d" % serie)
            serie += 1
            faits += 1
        # numéro de feuille (quand le lot dépasse une page)
        if page_dep > 1 or faits > CARTES_PAGE:
            c.setFillColor(colors.Color(0.6, 0.6, 0.6))
            c.setFont("Helvetica", 6)
            nfe = page_dep + (faits - 1) // CARTES_PAGE
            c.drawRightString(PAGE_W - 8, PAGE_H - 12, "%03d" % nfe)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf
