const nextConfig = {
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: "https" as const,
        hostname: "avatars.githubusercontent.com",
      },
      {
        protocol: "https" as const,
        hostname: "images.unsplash.com",
      },
    ],
  },
  webpack(config: any, { dev }: { dev: boolean }) {
    if (dev) {
      config.devtool = false;
    }
    return config;
  },
  async rewrites() {
    return [
      {
        source: "/api/proxy/:path*",
        destination: "http://127.0.0.1:8000/:path*",
      },
    ];
  },
};

export default nextConfig;
