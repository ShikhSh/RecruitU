import httpx
from typing import Dict, Optional
from app.config import Settings

class PeopleAPI:
    async def search(self, params: Dict, settings: Settings):
        # headers = {"Authorization": f"Bearer {settings.PEOPLE_API_KEY}"}
        headers = {}
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_SECONDS) as client:
            r = await client.get(f"{settings.PEOPLE_API_BASE}/search", params=params, headers=headers)
            r.raise_for_status()
            return r.json()

    async def people(self, ids: Optional[str], id: Optional[str], settings: Settings):
        # headers = {"Authorization": f"Bearer {settings.PEOPLE_API_KEY}"}
        headers = {}
        params = {}
        if ids: params["ids"] = ids
        if id: params["id"] = id
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_SECONDS) as client:
            r = await client.get(f"{settings.PEOPLE_API_BASE}/people", params=params, headers=headers)
            r.raise_for_status()
            return r.json()

people_api = PeopleAPI()