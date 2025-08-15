"""
HTTP Client Module for External API Integration

This module provides HTTP client functionality for interacting with external APIs,
specifically the people search and profile APIs. It includes error handling,
data formatting, and result extraction utilities.
"""

import httpx
from typing import Dict, List, Optional
from ..config import Settings


class PeopleAPI:
    """
    HTTP client for the People API.
    
    This class provides methods for searching people and retrieving detailed
    user information from the external people API. It includes comprehensive
    error handling and data formatting capabilities.
    """
    
    async def search(self, params: Dict, settings: Settings) -> Dict:
        """
        Perform a search request to the people API.
        
        Args:
            params (Dict): Search parameters to send to the API
            settings (Settings): Application configuration settings
            
        Returns:
            Dict: Raw response from the people API
            
        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        headers = {}
        
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{settings.PEOPLE_API_BASE}/search", 
                params=params, 
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    async def people(self, ids: List[str], settings: Settings) -> Dict:
        """
        Retrieve detailed information for specific people by their IDs.
        
        Args:
            ids (List[str]): List of user IDs to retrieve
            settings (Settings): Application configuration settings
            
        Returns:
            Dict: Raw response containing user information
            
        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        headers = {}
        params = {"ids": ids}
        
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{settings.PEOPLE_API_BASE}/people", 
                params=params, 
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    def extract_user_information(self, user_data: Dict) -> Optional[Dict]:
        """
        Extract and format user information from the people API response.
        
        This method processes raw user data from the API and extracts relevant
        information into a standardized format for the application.
        
        Args:
            user_data (Dict): Raw user data from the people API
            
        Returns:
            Optional[Dict]: Formatted user information dictionary or None if invalid data
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
            "id": linkedin.get("id"),
            "profile_pic_url": linkedin.get("profile_pic_url"),
        }

    async def get_user_information(self, user_id: str, settings: Settings) -> Optional[Dict]:
        """
        Get formatted user information by user ID.
        
        This method retrieves detailed user information for a specific user ID
        and returns it in a formatted structure suitable for the application.
        
        Args:
            user_id (str): The user ID to fetch information for
            settings (Settings): Application configuration settings
            
        Returns:
            Optional[Dict]: Formatted user information or None if user not found
        """
        try:
            response = await self.people(ids=[user_id], settings=settings)
            results = response.get("results", {})
            
            if not results or user_id not in results:
                print(f"User {user_id} not found in API response")
                return None
                
            user_data = results[user_id]
            return self.extract_user_information(user_data)
            
        except Exception as e:
            print(f"Error fetching user information for {user_id}: {e}")
            return None

    def extract_search_result_user(self, result_item: Dict) -> Optional[Dict]:
        """
        Extract and format user information from a single search result item.
        
        This method processes a single search result item and extracts relevant
        user information into a standardized format.
        
        Args:
            result_item (Dict): Single result item from search API response
            
        Returns:
            Optional[Dict]: Formatted user information dictionary or None if invalid data
        """
        if not result_item or "document" not in result_item:
            return None
            
        document = result_item.get("document", {})
        
        # Extract basic user information
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
        
        # Extract undergraduate education information
        undergrad = document.get("undergrad", {})
        if undergrad:
            ends_at = undergrad.get("ends_at")
            ends_at_value = None
            
            # Handle different date formats
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
            
        # Extract current company information
        current_company = document.get("current_company", {})
        if current_company:
            ends_at = current_company.get("ends_at")
            ends_at_value = None
            
            # Handle different date formats
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
        
        This method processes the complete search response and extracts user
        information for all results into a standardized format.
        
        Args:
            search_response (Dict): Full response from search API
            
        Returns:
            List[Dict]: List of formatted user information dictionaries
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
        Perform search and return formatted results with metadata.
        
        This method combines search execution with result formatting to provide
        a complete search response including metadata and error handling.
        
        Args:
            params (Dict): Search parameters
            settings (Settings): Application configuration settings
            
        Returns:
            Dict: Dictionary with formatted results, metadata, and error information
        """
        try:
            # Execute the search
            response = await self.search(params, settings)
            
            # Format the results
            formatted_results = self.extract_search_results(response)
            
            return {
                "results": formatted_results,
                "total": response.get("total", len(formatted_results)),
                "page": response.get("page", params.get("page", 1)),
                "count": response.get("count", len(formatted_results)),
                "filters": params,
                "success": True
            }
            
        except httpx.HTTPStatusError as http_error:
            print(f"HTTP error in search: {http_error.response.status_code} - {http_error}")
            return {
                "results": [],
                "total": 0,
                "page": params.get("page", 1),
                "count": 0,
                "filters": params,
                "success": False,
                "error": f"API request failed: {http_error.response.status_code}"
            }
            
        except Exception as e:
            print(f"Error in search with formatted results: {e}")
            return {
                "results": [],
                "total": 0,
                "page": params.get("page", 1),
                "count": 0,
                "filters": params,
                "success": False,
                "error": str(e)
            }


# Global instance for use throughout the application
people_api = PeopleAPI()
