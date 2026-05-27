import httpx
from fastapi import HTTPException, status

ARTIC_API_BASE_URL = "https://api.artic.edu/api/v1"


def get_artwork_by_id(external_id: str) -> dict:
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
