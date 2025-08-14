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
  onClose: () => void;
};

const accent = "#6366f1";
const accentLight = "#a5b4fc";

const UserDetail: React.FC<Props> = ({ user, onClose }) => (
  <div
    style={{
      position: "fixed",
      top: 0,
      left: 0,
      width: "100vw",
      height: "100vh",
      background: "rgba(24,24,27,0.92)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000,
    }}
    onClick={onClose}
  >
    <div
      style={{
        background: "#23272f",
        borderRadius: 20,
        padding: 44,
        minWidth: 350,
        maxWidth: 500,
        boxShadow: "0 8px 32px rgba(49,46,129,0.25)",
        position: "relative",
        textAlign: "center",
        color: "#f3f4f6",
        fontFamily: "'Montserrat', 'Segoe UI', Arial, sans-serif",
        border: `2.5px solid ${accent}`,
      }}
      onClick={e => e.stopPropagation()}
    >
      <button
        onClick={onClose}
        style={{
          position: "absolute",
          top: 18,
          right: 18,
          background: "none",
          border: "none",
          fontSize: 32,
          color: accentLight,
          cursor: "pointer",
        }}
        aria-label="Close"
      >
        ×
      </button>
      {user.profile_pic_url && (
        <img
          src={user.profile_pic_url}
          alt={user.full_name}
          style={{
            width: 120,
            height: 120,
            borderRadius: "50%",
            objectFit: "cover",
            marginBottom: 22,
            border: `4px solid ${accent}`,
            boxShadow: `0 2px 16px ${accent}`,
          }}
        />
      )}
      <h2 style={{ fontSize: 32, fontWeight: 800, color: accentLight, margin: "18px 0 8px" }}>
        {user.full_name}
      </h2>
      <div style={{ fontSize: 22, fontWeight: 600, color: "#c7d2fe", marginBottom: 8 }}>
        {user.title}
      </div>
      <div style={{ color: "#818cf8", fontWeight: 500, marginBottom: 8 }}>
        {user.company_name}
      </div>
      <div style={{ color: "#a1a1aa", fontSize: 16, marginBottom: 8 }}>
        {user.city} &bull; {user.country}
      </div>
      <div style={{ margin: "18px 0 8px", borderTop: `1px solid ${accentLight}`, paddingTop: 16 }}>
        <div style={{ marginBottom: 8 }}>
          <strong style={{ color: accentLight }}>School:</strong> {user.school}
        </div>
        <div style={{ marginBottom: 8 }}>
          <strong style={{ color: accentLight }}>Previous Companies:</strong> {user.previous_companies}
        </div>
        <div style={{ marginBottom: 8 }}>
          <strong style={{ color: accentLight }}>Previous Titles:</strong> {user.previous_titles}
        </div>
        <div style={{ marginBottom: 8 }}>
          <strong style={{ color: accentLight }}>LinkedIn:</strong>{" "}
          <a href={user.linkedin} target="_blank" rel="noopener noreferrer" style={{ color: accent }}>
            {user.linkedin}
          </a>
        </div>
        {user.current_company && (
          <div style={{ marginBottom: 8 }}>
            <strong style={{ color: accentLight }}>Current Company Details:</strong>
            <div>
              {user.current_company.title} at {user.current_company.company}
            </div>
            <div>
              <em>{user.current_company.description}</em>
            </div>
          </div>
        )}
        {user.undergrad && (
          <div>
            <strong style={{ color: accentLight }}>Undergraduate:</strong> {user.undergrad.school} (
            {user.undergrad.ends_at?.year})
          </div>
        )}
      </div>
    </div>
  </div>
);

export default UserDetail;