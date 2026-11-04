import importlib as _il

def _page_blanche_pdf(*_a, **_k):
    import io
    from reportlab.pdfgen import canvas as _c
    from reportlab.lib.pagesizes import A4 as _A4
    b = io.BytesIO(); cv = _c.Canvas(b, pagesize=_A4); cv.showPage(); cv.save(); b.seek(0)
    return b

class _GenerateurManquant(object):
    def __init__(self, nom): self._nom = nom
    def generer_pdf(self, *a, **k): return _page_blanche_pdf(*a, **k)
    def __getattr__(self, cle):
        if cle.startswith("__"): raise AttributeError(cle)
        return None

def __getattr__(name):
    try:
        return _il.import_module("." + name, __name__)
    except Exception as _e:
        print("[GEN MANQUANT] generators.%s -> page blanche (%r)" % (name, _e))
        return _GenerateurManquant(name)
