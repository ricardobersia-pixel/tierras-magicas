import fs from "node:fs";

export const config = JSON.parse(fs.readFileSync("config.json", "utf8"));

export const env = {
  port: Number(process.env.PORT || 3000),
  baseUrl: (
    process.env.BASE_URL ||
    (process.env.RAILWAY_PUBLIC_DOMAIN ? `https://${process.env.RAILWAY_PUBLIC_DOMAIN}` : `http://localhost:${process.env.PORT || 3000}`)
  ).replace(/\/$/, ""),
  adminPassword: process.env.ADMIN_PASSWORD || "",
  mpAccessToken: process.env.MP_ACCESS_TOKEN || "",
  icalSyncMinutes: Number(process.env.ICAL_SYNC_MINUTES || 15),
  iaActiva: Boolean(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN),
};

export function cabanaPorId(id) {
  return config.cabanas.find((c) => c.id === id);
}
