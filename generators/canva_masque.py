# -*- coding: utf-8 -*-
"""MANAPRINT — dessin posé en « pochoir » (26/11).
Une image noir & blanc (trait sur fond blanc ou transparent) est posée comme
MASQUE : seul le trait est peint, avec la couleur de remplissage en cours.
  · en N&B le trait sort en noir, comme avant ;
  · en couleur, MANAPRINT repeint le billet dans la couleur de la grille
    (les chiffres restent noirs) — demande de Maeva du 26/11.
Le masque est rangé UNE fois par document (fichier léger, impression rapide)."""
import io
import zlib
from reportlab.pdfbase import pdfdoc


class _Masque(pdfdoc.PDFImageXObject):
    def format(self, document):
        S = pdfdoc.PDFStream(content=self.streamContent)
        d = S.dictionary
        d["Type"] = pdfdoc.PDFName("XObject")
        d["Subtype"] = pdfdoc.PDFName("Image")
        d["Width"] = self.width
        d["Height"] = self.height
        d["ImageMask"] = b"true"
        d["BitsPerComponent"] = 1
        d["Filter"] = pdfdoc.PDFArray([pdfdoc.PDFName("FlateDecode")])
        d["Length"] = len(self.streamContent)
        return S.format(document)


class _Vrai(object):
    def format(self, document):
        return b"true"


def _ouvrir(source):
    from PIL import Image
    if isinstance(source, (bytes, bytearray)):
        return Image.open(io.BytesIO(source))
    if isinstance(source, str):
        return Image.open(source)
    return source


def poser(c, nom, source, x, y, w, h, seuil=160):
    """Pose l'image `source` (chemin, octets PNG ou image PIL) en pochoir dans (x, y, w, h)."""
    reg = c._doc.getXObjectName(nom)
    if not c._doc.idToObject.get(reg, None):
        from PIL import Image, ImageChops
        im = _ouvrir(source)
        L = im.convert("L")
        encre = L.point(lambda v: 255 if v < seuil else 0)
        if im.mode in ("LA", "RGBA", "PA") or "transparency" in im.info:
            a = im.convert("RGBA").getchannel("A").point(lambda v: 255 if v >= 128 else 0)
            encre = ImageChops.multiply(encre, a)
        # masque 1 bit : 0 = on peint le trait, 1 = on laisse le papier
        m = encre.point(lambda v: 0 if v else 255).convert("1", dither=Image.NONE)
        obj = _Masque(nom)
        obj.width, obj.height = m.size
        obj.streamContent = zlib.compress(m.tobytes(), 9)
        obj.mask = None
        obj.name = nom
        c._setXObjects(obj)
        c._doc.Reference(obj, reg)
        c._doc.addForm(nom, obj)
    c.saveState()
    c._code.append("0 0 0 rg")
    c.translate(x, y)
    c.scale(w, h)
    c._code.append("/%s Do" % reg)
    c.restoreState()
    c._formsinuse.append(nom)
