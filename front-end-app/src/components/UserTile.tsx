import React from "react";

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
  undergrad?: any;
  current_company?: any;
  previous_titles?: string;
};

type Props = {
  user: User;
  onClick: () => void;
};

const UserTile: React.FC<Props> = ({ user, onClick }) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      width: "100%",
      maxWidth: 900,
      margin: "24px auto",
      padding: 32,
      borderRadius: 18,
      boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
      background: "linear-gradient(90deg, #f8fafc 0%, #e0e7ff 100%)",
      cursor: "pointer",
      transition: "box-shadow 0.2s, transform 0.2s",
      fontFamily: "'Montserrat', 'Segoe UI', Arial, sans-serif",
      border: "1.5px solid #d1d5db",
      fontSize: 18,
      fontWeight: 500,
      letterSpacing: 0.2,
    }}
    onClick={onClick}
  >
    {user.profile_pic_url && (
      <img
        src={user.profile_pic_url}
        alt={user.full_name}
        style={{
          width: 80,
          height: 80,
          borderRadius: "50%",
          objectFit: "cover",
          marginRight: 32,
          border: "3px solid #6366f1",
          boxShadow: "0 2px 12px #c7d2fe",
        }}
      />
    )}
    <div style={{ flex: 1 }}>
      <div style={{ fontSize: 28, fontWeight: 700, color: "#3730a3", marginBottom: 6 }}>
        {user.full_name}
      </div>
      <div style={{ fontSize: 20, fontWeight: 600, color: "#4f46e5", marginBottom: 2 }}>
        {user.title}
      </div>
      <div style={{ color: "#334155", fontWeight: 500, marginBottom: 2 }}>
        {user.company_name}
      </div>
      <div style={{ color: "#64748b", fontSize: 16, marginBottom: 2 }}>
        {user.city} &bull; {user.country}
      </div>
      <a
        href={user.linkedin}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          fontSize: 15,
          color: "#2563eb",
          textDecoration: "underline",
          fontWeight: 600,
        }}
      >
        LinkedIn Profile
      </a>
    </div>
  </div>
);

export default UserTile;