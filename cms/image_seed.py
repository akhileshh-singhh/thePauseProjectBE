import urllib.request
from urllib.parse import urlparse

from django.core.files.base import ContentFile


def assign_image_from_url(instance, field_name: str, url: str) -> bool:
    if not url or not url.startswith(("http://", "https://")):
        return False
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read()
    except OSError:
        return False

    path = urlparse(url).path
    name = path.rsplit("/", 1)[-1].split("?")[0] or "image.jpg"
    if "." not in name:
        name = f"{name}.jpg"

    field = getattr(instance, field_name)
    field.save(name, ContentFile(content), save=False)
    return True
