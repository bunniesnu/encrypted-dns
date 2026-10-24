export interface DnsProfile {
  id: string;
  name: string;
  endpoints: {
    protocol: "HTTPS" | "TLS";
    filename: string;
  }[];
}