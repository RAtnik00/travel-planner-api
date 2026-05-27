import time

import httpx
from fastapi import HTTPException, status

ARTIC_API_BASE_URL = "https://api.artic.edu/api/v1"
CACHE_TTL_SECONDS = 300

_artwork_cache: dict[str, tuple[float, dict]] = {}


def get_artwork_by_id(external_id: str) -> dict:
    cached_artwork = _get_cached_artwork(external_id)

    if cached_artwork is not None:
        return cached_artwork

    artwork = _fetch_artwork_by_id(external_id)
    _artwork_cache[external_id] = (time.time(), artwork)

    return artwork


def _get_cached_artwork(external_id: str) -> dict | None:
    cached = _artwork_cache.get(external_id)

    if cached is None:
        return None

    cached_at, artwork = cached

    if time.time() - cached_at > CACHE_TTL_SECONDS:
        _artwork_cache.pop(external_id, None)
        return None

    return artwork


def _fetch_artwork_by_id(external_id: str) -> dict:
    url = f"{ARTIC_API_BASE_URL}/artworks/{external_id}"

    try:
        response = httpx.get(
            url,
            params={"fields": "id,title"},
            timeout=10,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="External place not found",
            )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Art Institute API returned an error",
        )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not connect to Art Institute API",
        )

    data = response.json().get("data")

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External place not found",
        )

    return {
        "external_id": str(data["id"]),
        "title": data["title"],
    }