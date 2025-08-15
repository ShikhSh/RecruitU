import React, { useState } from "react";
import UserTile from "./components/UserTile";
import UserDetail from "./components/UserDetail";

type User = {
  id: string;
  full_name: string;
  title: string;
  company_name: string;
  city: string;
  linkedin: string;
  previous_companies: string;
  school: string;
  country: string;
  profile_pic_url?: string;
  undergrad?: {
    ends_at?: { year?: number };
    school?: string;
    grade?: string;
    activities_and_societies?: string;
    degree_name?: string;
    field_of_study?: string;
    description?: string;
  } | null;
  current_company?: {
    ends_at?: { year?: number };
    location?: string;
    title?: string;
    starts_at?: string;
    description?: string;
    company?: string;
  } | null;
  previous_titles?: string;
};

const App: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [referenceUserId, setReferenceUserId] = useState("");
  const [referenceUser, setReferenceUser] = useState<User | null>(null);
  const [selected, setSelected] = useState<User | null>(null);
  const [suggestions, setSuggestions] = useState<string[] | null>(null);
  
  // Cache for conversation suggestions - key: "referenceUserId-targetUserId"
  const [suggestionsCache, setSuggestionsCache] = useState<Map<string, string[]>>(new Map());

const handleUserClick = async (user: User) => {
  setSelected(user);
  setSuggestions(null); // Reset suggestions for new user
  
  if (referenceUser) {
    // Create cache key for this user pair
    const cacheKey = `${referenceUser.id}-${user.id}`;
    
    // Check if we already have cached suggestions for this pair
    if (suggestionsCache.has(cacheKey)) {
      console.log("Using cached suggestions for", cacheKey);
      setSuggestions(suggestionsCache.get(cacheKey) || []);
      return;
    }
    
    // Show loading state
    setSuggestions(null);
    
    // Fetch suggestions from API
    fetch("/suggest_conversation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        currentUser: referenceUser,
        inquiredUser: user,
      }),
    })
      .then(res => res.json())
      .then(data => {
        console.log("Raw suggestion data:", data);
        
        // Ensure suggestions is an array of strings
        let finalSuggestions: string[] = [];
        if (data.suggestions && Array.isArray(data.suggestions)) {
          finalSuggestions = data.suggestions.map((suggestion: any) => {
            if (typeof suggestion === 'string') {
              return suggestion;
            } else if (typeof suggestion === 'object' && suggestion !== null) {
              // If it's an object, try to extract meaningful text
              if (suggestion.message) return String(suggestion.message);
              if (suggestion.topic) return String(suggestion.topic);
              if (suggestion.context) return String(suggestion.context);
              return String(suggestion);
            } else {
              return String(suggestion);
            }
          });
        } else {
          finalSuggestions = ["Could not generate suggestions."];
        }
        
        // Cache the suggestions
        setSuggestionsCache(prev => new Map(prev).set(cacheKey, finalSuggestions));
        setSuggestions(finalSuggestions);
      })
      .catch((error) => {
        console.error("Error fetching suggestions:", error);
        const errorSuggestions = ["Could not fetch suggestions."];
        // Don't cache error responses
        setSuggestions(errorSuggestions);
      });
  }
};

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    console.log("Before Search");
    try {
      const res = await fetch("/search_nl", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, overrides: {} }),
      });
      const data = await res.json();
      console.log("Search results:", data);
      
      // The new API structure returns formatted results directly
      if (data.results && Array.isArray(data.results)) {
        setUsers(data.results);
      } else {
        console.error("Unexpected data structure:", data);
        setUsers([]);
      }
    } catch (error) {
      console.error("Search error:", error);
      setUsers([]);
    }
    setLoading(false);
  };
  return (
  <div style={{ background: "#f6f8fa", minHeight: "100vh", padding: 32 }}>
    <h1 style={{ textAlign: "center" }}>RecruitU — LateralGPT</h1>

    {/* Step 1: Show fetch form if referenceUser is not set */}
    {!referenceUser && (
      <form
        onSubmit={async e => {
          e.preventDefault();
          try {
            const res = await fetch(`/people?ids=${referenceUserId}`);
            const data = await res.json();
            console.log("Reference user data:", data);
            if (data.error) {
              alert(`Error: ${data.error}`);
            } else {
              setReferenceUser(data);
            }
          } catch (error) {
            console.error("Error fetching reference user:", error);
            alert("Failed to fetch user details");
          }
        }}
        style={{ marginBottom: 24, textAlign: "center" }}
      >
        <input
          type="text"
          value={referenceUserId}
          onChange={e => setReferenceUserId(e.target.value)}
          placeholder="Enter User ID for reference"
          style={{ padding: 8, width: 220, marginRight: 8 }}
        />
        <button type="submit" style={{ padding: "8px 16px" }}>
          Fetch Current User Details
        </button>
      </form>
    )}

    {/* Step 2: Show current user name and search only if referenceUser is set */}
    {referenceUser && (
      <>
        <div style={{ textAlign: "center", marginBottom: 24, fontWeight: 600, fontSize: 20 }}>
          Hi, {referenceUser.full_name || "User"}
        </div>
        <form onSubmit={handleSearch} style={{ textAlign: "center", marginBottom: 24 }}>
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search for users (e.g. Analyst in New York)..."
            style={{ padding: 8, width: 320, fontSize: 16, borderRadius: 4, border: "1px solid #ccc" }}
          />
          <button type="submit" style={{ marginLeft: 12, padding: "8px 20px", fontSize: 16 }}>
            Search
          </button>
        </form>
        {loading && <div style={{ textAlign: "center" }}>Loading...</div>}
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center" }}>
          {users.map(user => (
            <UserTile key={user.id} user={user} onClick={() => handleUserClick(user)} />
          ))}
        </div>
        {selected && (
          <UserDetail user={selected} onClose={() => setSelected(null)} suggestions={suggestions} />
        )}
      </>
    )}
  </div>
);
};

export default App;