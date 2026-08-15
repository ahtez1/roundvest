import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Next's dev server treats 127.0.0.1 and localhost as different origins
  // and blocks cross-origin asset/HMR requests by default. Since this app
  // gets accessed via both interchangeably, allow both explicitly.
  allowedDevOrigins: ["localhost", "127.0.0.1"],
};

export default nextConfig;
