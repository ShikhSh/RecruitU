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
  undergrad?: any;
  current_company?: any;
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

const handleUserClick = async (user: User) => {
  setSelected(user);
  setSuggestions(null); // Reset suggestions for new user
  if (referenceUser) {
    // Fetch suggestions in the background
    fetch("/suggest_conversation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        userA: referenceUser,
        userB: user,
      }),
    })
      .then(res => res.json())
      .then(data => setSuggestions(data.suggestions))
      .catch(() => setSuggestions(["Could not fetch suggestions."]));
  }
};

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    console.log("Before Search");
    const res = await fetch("/search_nl", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, overrides: {} }),
    });
    const data = await res.json();
    console.log("Search results:", data);
    setUsers(
      data.results.results.map((r: any) => ({
        ...r.document,
        id: r.document.id,
        full_name: r.document.full_name,
        title: r.document.title,
        company_name: r.document.company_name || (r.document.current_company?.company ?? ""),
        city: r.document.city,
        linkedin: r.document.linkedin,
        previous_companies: r.document.previous_companies,
        school: r.document.school,
        country: r.document.country,
        undergrad: r.document.undergrad,
        current_company: r.document.current_company,
        previous_titles: r.document.previous_titles,
      }))
    );
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
          const res = await fetch(`/people?ids=${referenceUserId}`);
          const data = await res.json();
          setReferenceUser(data);
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