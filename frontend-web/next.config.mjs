/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "images.pexels.com" },
    ],
  },
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace("/api", "") || "http://localhost:8000";
    return process.env.NODE_ENV === "development"
      ? [
          { source: "/api/:path*", destination: `${backendUrl}/api/:path*` },
          { source: "/ws/:path*", destination: `${backendUrl}/ws/:path*` },
        ]
      : [];
  },
};

export default nextConfig;
