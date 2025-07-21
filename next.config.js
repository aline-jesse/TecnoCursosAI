/** @type {import('next').NextConfig} */
const nextConfig = {
  // Habilitar experimental features para melhor performance
  experimental: {
    appDir: true,
  },
  
  // Configuração de imagens para assets do editor
  images: {
    domains: ['localhost', '127.0.0.1'],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Variables de ambiente públicas
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',
  },
  
  // Configuração de webpack para bibliotecas como Fabric.js
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Resolve para browser
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        canvas: false,
      };
    }
    
    // Configuração para Fabric.js
    config.module.rules.push({
      test: /fabric/,
      use: 'babel-loader',
    });
    
    return config;
  },
  
  // Configuração de transpilação
  transpilePackages: ['fabric'],
  
  // Headers para desenvolvimento
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ];
  },
  
  // Configuração de redirecionamentos
  async redirects() {
    return [
      {
        source: '/',
        destination: '/editor',
        permanent: false,
      },
    ];
  },
}

module.exports = nextConfig 