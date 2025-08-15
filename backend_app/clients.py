import httpx
from typing import Dict, List, Optional
from backend_app.config import Settings

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

    def extract_user_information(self, user_data: Dict) -> Optional[Dict]:
        """
        Extract and format user information from the people API response.
        
        Args:
            user_data: Raw user data from the people API
            
        Returns:
            Formatted user information dictionary or None if invalid data
        """
        if not user_data:
            return None
            
        linkedin = user_data.get("linkedin", {})
        return {
            "education": linkedin.get("education"),
            "occupation": linkedin.get("occupation"),
            "city": linkedin.get("city"),
            "volunteer_work": linkedin.get("volunteer_work"),
            "summary": linkedin.get("summary"),
            "headline": linkedin.get("headline"),
            "groups": linkedin.get("groups"),
            "certifications": linkedin.get("certifications"),
            "experiences": linkedin.get("experiences"),
            "full_name": linkedin.get("full_name"),
        }

    async def get_user_information(self, user_id: str, settings: Settings) -> Optional[Dict]:
        """
        Get formatted user information by user ID.
        
        Args:
            user_id: The user ID to fetch information for
            settings: Application settings
            
        Returns:
            Formatted user information or None if user not found
        """
        try:
            response = await self.people(ids=[user_id], settings=settings)
            results = response.get("results", {})
            
            if not results or user_id not in results:
                return None
                
            user_data = results[user_id]
            return self.extract_user_information(user_data)
            
        except Exception as e:
            print(f"Error fetching user information for {user_id}: {e}")
            return None

    def extract_search_result_user(self, result_item: Dict) -> Optional[Dict]:
        """
        Extract and format user information from a single search result item.
        
        Args:
            result_item: Single result item from search API response
            
        Returns:
            Formatted user information dictionary or None if invalid data
        """
        if not result_item or "document" not in result_item:
            return None
            
        document = result_item.get("document", {})
        
        # Extract basic fields
        user_info = {
            "id": document.get("id"),
            "full_name": document.get("full_name"),
            "title": document.get("title"),
            "company_name": document.get("company_name"),
            "city": document.get("city"),
            "country": document.get("country"),
            "linkedin": document.get("linkedin"),
            "school": document.get("school"),
            "previous_companies": document.get("previous_companies"),
            "previous_titles": document.get("previous_titles"),
            "profile_pic_url": document.get("profile_pic_url"),
        }
        
        # Extract undergrad fields
        undergrad = document.get("undergrad", {})
        if undergrad:
            ends_at = undergrad.get("ends_at")
            ends_at_value = None
            if isinstance(ends_at, dict) and "year" in ends_at:
                ends_at_value = ends_at["year"]
            elif isinstance(ends_at, str):
                ends_at_value = ends_at
                
            user_info["undergrad"] = {
                "ends_at": ends_at_value,
                "school": undergrad.get("school"),
                "grade": undergrad.get("grade"),
                "activities_and_societies": undergrad.get("activities_and_societies"),
                "degree_name": undergrad.get("degree_name"),
                "field_of_study": undergrad.get("field_of_study"),
                "description": undergrad.get("description"),
            }
        else:
            user_info["undergrad"] = None
            
        # Extract current_company fields
        current_company = document.get("current_company", {})
        if current_company:
            ends_at = current_company.get("ends_at")
            ends_at_value = None
            if isinstance(ends_at, dict) and "year" in ends_at:
                ends_at_value = ends_at["year"]
            elif isinstance(ends_at, str):
                ends_at_value = ends_at
                
            user_info["current_company"] = {
                "ends_at": ends_at_value,
                "location": current_company.get("location"),
                "title": current_company.get("title"),
                "starts_at": current_company.get("starts_at"),
                "description": current_company.get("description"),
                "company": current_company.get("company"),
            }
        else:
            user_info["current_company"] = None
            
        return user_info

    def extract_search_results(self, search_response: Dict) -> List[Dict]:
        """
        Extract and format all user information from search API response.
        
        Args:
            search_response: Full response from search API
            
        Returns:
            List of formatted user information dictionaries
        """
        if not search_response or "results" not in search_response:
            return []
            
        results = search_response.get("results", [])
        formatted_results = []
        
        for result_item in results:
            formatted_user = self.extract_search_result_user(result_item)
            if formatted_user:
                formatted_results.append(formatted_user)
                
        return formatted_results

    async def search_with_formatted_results(self, params: Dict, settings: Settings) -> Dict:
        """
        Perform search and return formatted results.
        
        Args:
            params: Search parameters
            settings: Application settings
            
        Returns:
            Dictionary with formatted results and metadata
        """
        try:
            response = await self.search(params, settings)
            formatted_results = self.extract_search_results(response)
            
            return {
                "results": formatted_results,
                "total": response.get("total", len(formatted_results)),
                "page": response.get("page", 1),
                "count": response.get("count", len(formatted_results)),
                "filters": params
            }
            
        except Exception as e:
            print(f"Error in search with formatted results: {e}")
            return {
                "results": [],
                "total": 0,
                "page": 1,
                "count": 0,
                "filters": params,
                "error": str(e)
            }

people_api = PeopleAPI()