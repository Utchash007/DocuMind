import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: { root: path.resolve(__dirname) },
  experimental: { proxyClientMaxBodySize: 26 * 1024 * 1024 },
};

export default nextConfig;
