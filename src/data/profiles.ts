export interface DnsProfile {
  id: string;
  name: string;
  endpoints: {
    protocol: "DoH" | "DoT";
    filename: string;
  }[];
}

export const PROFILES: DnsProfile[] = [
  {
    id: "cf-standard",
    name: "Cloudflare 1.1.1.1",
    endpoints: [
      { protocol: "DoH", filename: "cloudflare-doh.mobileconfig" },
      { protocol: "DoT", filename: "cloudflare-dot.mobileconfig" },
    ],
  },
  {
    id: "adguard-default",
    name: "AdGuard Default",
    endpoints: [
      { protocol: "DoH", filename: "adguard-doh.mobileconfig" },
      { protocol: "DoT", filename: "adguard-dot.mobileconfig" },
    ],
  },
];