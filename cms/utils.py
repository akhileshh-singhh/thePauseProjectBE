def absolute_media_url(request, file_field) -> str:
    if not file_field:
        return ""
    url = file_field.url
    if url.startswith(("http://", "https://")):
        return url
    if request is not None:
        return request.build_absolute_uri(url)
    return url
