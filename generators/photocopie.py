# -*- coding: utf-8 -*-
"""MANAPRINT — VERSION « PHOTOCOPIE » (25/11/2026, sceau Maeva : « que l'impression soit fluide »).
Les jeux Canva contiennent des dessins très détaillés avec transparence : la Konica
et la Sharp sortaient 4 feuilles puis s'arrêtaient longtemps pour tout recalculer.
On transforme chaque page en UNE image noir & blanc 300 dpi (compression CCITT G4,
celle des fax et des photocopieurs) : l'imprimante n'a plus rien à calculer, les
feuilles sortent d'une traite. Billets, numéros, séries et n° de page identiques.
Utilise pypdfium2 + Pillow (déjà installés). Page par page : peu de mémoire."""
import io

DPI = 300
SEUIL = 200          # en dessous = noir : les traits fins gris des dessins Canva restent (noircis)


def _g4(im):
    """Image PIL mode '1' -> (largeur, hauteur, octets CCITT G4 bruts)."""
    from PIL import Image  # noqa
    b = io.BytesIO()
    im.save(b, format="TIFF", compression="group4", tiffinfo={278: im.height})
    b.seek(0)
    from PIL import Image as _I
    t = _I.open(b)
    off = t.tag_v2[273]; cnt = t.tag_v2[279]
    off = off[0] if isinstance(off, (tuple, list)) else off
    cnt = cnt[0] if isinstance(cnt, (tuple, list)) else cnt
    return im.width, im.height, b.getvalue()[off:off + cnt]


def convertir(pdf_bytes, dpi=DPI, seuil=SEUIL):
    """PDF (bytes) -> PDF « photocopie » (bytes)."""
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(pdf_bytes)
    out = io.BytesIO()
    w = out.write
    w(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = {}
    n = len(doc)
    # objets : 1 catalogue, 2 pages, puis par page : page, contenu, image
    kids = [3 + 3 * i for i in range(n)]

    def obj(num, data):
        offsets[num] = out.tell()
        w(b"%d 0 obj\n" % num); w(data); w(b"\nendobj\n")

    obj(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    obj(2, b"<< /Type /Pages /Count %d /Kids [%s] >>" % (n, b" ".join(b"%d 0 R" % k for k in kids)))
    for i in range(n):
        page = doc[i]
        wpt, hpt = page.get_size()
        bmp = page.render(scale=dpi / 72.0, grayscale=True)
        im = bmp.to_pil().convert("L").point(lambda v: 255 if v >= seuil else 0, mode="1")
        page.close()
        W, H, data = _g4(im)
        p, c, x = kids[i], kids[i] + 1, kids[i] + 2
        obj(p, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.4f %.4f] /Contents %d 0 R "
               b"/Resources << /XObject << /Im0 %d 0 R >> >> >>" % (wpt, hpt, c, x))
        cont = b"q %.4f 0 0 %.4f 0 0 cm /Im0 Do Q" % (wpt, hpt)
        obj(c, b"<< /Length %d >>\nstream\n" % len(cont) + cont + b"\nendstream")
        obj(x, b"<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceGray "
               b"/BitsPerComponent 1 /Filter /CCITTFaxDecode "
               b"/DecodeParms << /K -1 /Columns %d /Rows %d /BlackIs1 true >> /Length %d >>\nstream\n"
               % (W, H, W, H, len(data)) + data + b"\nendstream")
    doc.close()
    xref = out.tell(); tot = 3 + 3 * n
    w(b"xref\n0 %d\n0000000000 65535 f \n" % tot)
    for k in range(1, tot):
        w(b"%010d 00000 n \n" % offsets[k])
    w(b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (tot, xref))
    return out.getvalue()
