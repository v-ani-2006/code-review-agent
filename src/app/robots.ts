export default function robots() {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api/", "/monitoring", "/settings"],
    },
    sitemap: "https://codepilot.ai/sitemap.xml",
  };
}
