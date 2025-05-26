/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    domains: ["blob.v0.dev", "hebbkx1anhila5yf.public.blob.vercel-storage.com"],
    unoptimized: true,
  },
}

module.exports = nextConfig
