from fastapi import Request


async def build_uri(request: Request, view_name: str, **kwargs) -> str:
    """Build URI for the view."""
    view_url = request.app.url_path_for(view_name, **kwargs)
    return str(request.base_url).removesuffix("/") + view_url
