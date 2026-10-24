import { useEffect, useState } from "react";
import type { DnsProfile } from "./data/profiles";

const BASE_URL = `${import.meta.env.VITE_CDN_URL}/profiles`;

function ProfileCard({ profile }: { profile: DnsProfile }) {
  return (
    <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}>
      <h3 style={{ margin: "0 0 12px" }}>{profile.name}</h3>
      {/* Direct link for native iOS Safari interception */}
      <div style={{ display: "flex", gap: 8 }}>
        {profile.endpoints.map((ep) => (
          <a
            key={ep.protocol}
            href={`${BASE_URL}/${ep.filename}`}
            style={{
              flex: 1,
              textAlign: "center",
              padding: "10px 16px",
              background: "#0070f3",
              color: "#fff",
              textDecoration: "none",
              borderRadius: 6,
              fontSize: 14,
              fontWeight: 600,
            }}
          >
            Get {ep.protocol}
          </a>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [profiles, setProfiles] = useState<DnsProfile[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    fetch(`${BASE_URL}/providers.json`)
      .then((res) => res.json())
      .then(setProfiles);
  }, []);

  const filtered = profiles.filter((p) =>
    p.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <main style={{ maxWidth: 480, margin: "0 auto", padding: 16, fontFamily: "sans-serif" }}>
      <header style={{ marginBottom: 20 }}>
        <h1 style={{ margin: "0 0 8px", fontSize: 24 }}>Bunniesnu iOS DNS Profiles</h1>
        <p style={{ color: "#64748b", margin: 0, fontSize: 14 }}>
          Download encrypted DNS profiles directly to iOS Safari.
        </p>
      </header>

      <input
        type="search"
        placeholder="Filter by name..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          width: "100%",
          padding: 10,
          borderRadius: 6,
          border: "1px solid #cbd5e1",
          boxSizing: "border-box",
          marginBottom: 16,
          fontSize: 16, // Prevents iOS Safari auto-zoom on focus
        }}
      />

      <div style={{ display: "grid", gap: 12 }}>
        {filtered.map((profile) => (
          <ProfileCard key={profile.id} profile={profile} />
        ))}
      </div>

      <footer
        style={{
          marginTop: 24,
          padding: 16,
          background: "#f8fafc",
          borderRadius: 8,
          fontSize: 13,
          color: "#475569",
        }}
      >
        <strong>How to install on iOS:</strong>
        <ol style={{ margin: "8px 0 0", paddingLeft: 20 }}>
          <li>Tap <strong>Get DoH / DoT</strong> and allow the download prompt in Safari.</li>
          <li>Open iOS <strong>Settings</strong> &rarr; tap <strong>Profile Downloaded</strong>.</li>
          <li>Tap <strong>Install</strong> in the top-right corner.</li>
        </ol>
      </footer>
    </main>
  );
}