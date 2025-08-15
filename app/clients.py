import httpx
from typing import Dict, List
from app.config import Settings

class PeopleAPI:
    async def search(self, params: Dict, settings: Settings):
        headers = {}
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_SECONDS) as client:
            r = await client.get(f"{settings.PEOPLE_API_BASE}/search", params=params, headers=headers)
            r.raise_for_status()
            return r.json()

    async def people(self, ids: List[str], settings: Settings):
        headers = {}
        params = {"ids": ids}
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_SECONDS) as client:
            r = await client.get(f"{settings.PEOPLE_API_BASE}/people", params=params, headers=headers)
            r.raise_for_status()
            return r.json()

people_api = PeopleAPI()