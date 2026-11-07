/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Data read at runtime via fs must be bundled into the serverless functions on Vercel.
  outputFileTracingIncludes: {
    "/**": ["./assets/**/*.txt", "./outputs/**/*", "./config/**/*"],
  },
};

export default nextConfig;
