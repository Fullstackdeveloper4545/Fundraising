import type { NextConfig } from "next";

function getAllowedDevOrigins(): string[] | undefined {
  const raw =
    process.env.NEXT_DEV_ALLOWED_ORIGINS ||
    process.env.NEXT_PUBLIC_APP_URL ||
    process.env.FRONTEND_URL;

  if (!raw) {
    return undefined;
  }

  const origins = raw
    .split(",")
    .map((origin) => origin.trim())
    .filter(Boolean);

  return origins.length ? origins : undefined;
}

const nextConfig: NextConfig = {
  allowedDevOrigins: getAllowedDevOrigins(),
};

export default nextConfig;
