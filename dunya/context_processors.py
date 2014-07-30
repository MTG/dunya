from carnatic import models
from django.core.urlresolvers import reverse

def navigation_header(request):
    displayhist = []
    for entity in request.session.get('carnatic_navigation_history', []):
        item_type = entity[0]
        id_ = entity[1]
        if item_type == 'artist':
            item = models.Artist.objects.get(mbid=id_)
        elif item_type == 'concert':
            item = models.Concert.objects.get(mbid=id_)
        elif item_type == 'instrument':
            item = models.Instrument.objects.get(id=id_)
        elif item_type == 'raaga':
            item = models.Raaga.objects.get(id=id_)
        elif item_type == 'taala':
            item = models.Taala.objects.get(id=id_)
        else:
            continue
        displayhist.append((item_type, item))

    return {"carnatic_navigation_history": displayhist}

def style_context(request):
    hindustani_prefix = reverse("hindustani-main")
    carnatic_prefix = reverse("carnatic-main")
    makam_prefix = reverse("makam-main")
    # andalusian_prefix = reverse("andalusian-main")
    path = request.path

    if path.startswith(hindustani_prefix):
        return {"style_root": hindustani_prefix, "style_name": "Hindustani"}
    elif path.startswith(carnatic_prefix):
        return {"style_root": carnatic_prefix, "style_name": "Carnatic"}
    elif path.startswith(makam_prefix):
        return {"style_root": makam_prefix, "style_name": "Makam"}
    # elif path.startswith(andalusian_prefix):
    #     return {"style_root": andalusian_prefix, "style_name": "Andalusian"}
    return {}
