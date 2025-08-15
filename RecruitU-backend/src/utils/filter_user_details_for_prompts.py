from typing import Dict, Any

def filter_search_user_data_for_suggestions(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter user data to include only relevant fields for conversation suggestions.
    
    This function extracts only the essential professional and educational information
    needed for generating meaningful conversation suggestions while protecting privacy
    and reducing token usage in LLM calls.
    
    The filtered fields include:
    - Basic info: full_name, title, company_name, city, country, school
    - Work history: previous_companies, previous_titles
    - Education: undergrad school, degree, field of study, graduation year
    - Current role: current company details
    
    This filtering approach:
    1. Reduces LLM token usage and costs
    2. Protects sensitive personal information
    3. Focuses on professionally relevant data for networking
    4. Improves cache consistency by using normalized data
    
    Args:
        user_data (Dict[str, Any]): Complete user profile data
        
    Returns:
        Dict[str, Any]: Filtered user data with only relevant fields
    """
    if not user_data:
        return {}
    
    filtered_data = {}
    
    # Extract basic professional information
    for field in ["full_name", "title", "company_name", "school"]:
        if field in user_data:
            filtered_data[field] = user_data[field]
    
    # Extract work history for finding commonalities
    for field in ["previous_companies", "previous_titles"]:
        if field in user_data:
            filtered_data[field] = user_data[field]
    
    # Extract education information if available
    undergrad = user_data.get("undergrad")
    if undergrad and isinstance(undergrad, dict):
        filtered_data["undergrad"] = {
            "school": undergrad.get("school"),
            "degree_name": undergrad.get("degree_name"),
            "field_of_study": undergrad.get("field_of_study"),
            "ends_at": undergrad.get("ends_at")
        }
    
    # Extract current company details if available
    current_company = user_data.get("current_company")
    if current_company and isinstance(current_company, dict):
        filtered_data["current_company"] = {
            "company": current_company.get("company"),
            "title": current_company.get("title"),
            "location": current_company.get("location")
        }
    
    return filtered_data

def filter_user_profile_for_suggestions(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter user profile data to include only relevant fields for conversation suggestions.
    
    This function handles the format returned by the /people endpoint, which has a different
    structure than search results. It extracts essential professional and educational 
    information while protecting privacy and reducing LLM token usage.
    
    The filtered fields include:
    - Basic info: full_name, occupation, city, headline
    - Education: school names, degrees, fields of study, graduation years
    - Work experience: company names, titles, locations, dates
    - Professional info: certifications (names only)
    
    This filtering approach:
    1. Reduces LLM token usage and costs
    2. Protects sensitive personal information (no IDs, URLs, etc.)
    3. Focuses on professionally relevant data for networking
    4. Maintains structured data for better LLM understanding
    
    Args:
        user_profile (Dict[str, Any]): User profile data from /people endpoint
        
    Returns:
        Dict[str, Any]: Filtered user profile with only relevant fields
    """
    if not user_profile:
        return {}
    
    filtered_profile = {}
    
    # Extract basic professional information
    basic_fields = ["full_name", "occupation", "city", "headline"]
    for field in basic_fields:
        if field in user_profile and user_profile[field]:
            filtered_profile[field] = user_profile[field]
    
    # Extract and filter education information
    education = user_profile.get("education", [])
    if education and isinstance(education, list):
        filtered_education = []
        for edu in education:
            if isinstance(edu, dict):
                filtered_edu = {}
                # Include relevant education fields
                edu_fields = ["school", "degree_name", "field_of_study", "ends_at", "grade"]
                for field in edu_fields:
                    if field in edu and edu[field]:
                        filtered_edu[field] = edu[field]
                if filtered_edu:
                    filtered_education.append(filtered_edu)
        if filtered_education:
            filtered_profile["education"] = filtered_education
    
    # Extract and filter work experiences
    experiences = user_profile.get("experiences", [])
    if experiences and isinstance(experiences, list):
        filtered_experiences = []
        for exp in experiences:
            if isinstance(exp, dict):
                filtered_exp = {}
                # Include relevant experience fields
                exp_fields = ["company", "title", "location", "starts_at", "ends_at"]
                for field in exp_fields:
                    if field in exp and exp[field]:
                        filtered_exp[field] = exp[field]
                if filtered_exp:
                    filtered_experiences.append(filtered_exp)
        if filtered_experiences:
            filtered_profile["experiences"] = filtered_experiences
    
    # Extract and filter certifications (names only for privacy)
    certifications = user_profile.get("certifications", [])
    if certifications and isinstance(certifications, list):
        filtered_certifications = []
        for cert in certifications:
            if isinstance(cert, dict) and "name" in cert and cert["name"]:
                filtered_certifications.append({"name": cert["name"]})
            elif isinstance(cert, str):
                filtered_certifications.append({"name": cert})
        if filtered_certifications:
            filtered_profile["certifications"] = filtered_certifications
    
    return filtered_profile

# Export list for module imports
__all__ = ['filter_search_user_data_for_suggestions', 'filter_user_profile_for_suggestions']